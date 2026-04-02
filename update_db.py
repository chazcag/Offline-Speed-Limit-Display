# update_db.py - Map DB updater (now logger-aware, called by power_manager)

import os
import subprocess
import psycopg2
from datetime import datetime, timedelta
from logger import get_logger
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, PBF_URL, PBF_FILE, FILTERED_PBF, OSM2PGSQL_STYLE

logger = get_logger("map_updater")

# Download and filter logic (unchanged behavior, now logged)
two_weeks_ago = datetime.now() - timedelta(weeks=2)
should_download = False

if not os.path.exists(PBF_FILE):
    logger.info("PBF file not found — downloading fresh copy.")
    should_download = True
else:
    file_mtime = datetime.fromtimestamp(os.path.getmtime(PBF_FILE))
    if file_mtime < two_weeks_ago:
        logger.info(f"PBF file is older than 2 weeks (last modified {file_mtime.isoformat()}) — downloading new version.")
        should_download = True
    else:
        logger.info(f"PBF file is recent (modified {file_mtime.isoformat()}) — skipping download.")

if should_download:
    logger.info("Downloading fresh PBF...")
    if os.path.exists(PBF_FILE):
        os.remove(PBF_FILE)
    subprocess.run(['wget', '-q', '-O', PBF_FILE, PBF_URL], check=True)
    logger.info("Download complete.")
else:
    logger.info("Using existing PBF file.")

should_filter = should_download or not os.path.exists(FILTERED_PBF)

if should_filter:
    logger.info("Filtering roads from PBF...")
    if os.path.exists(FILTERED_PBF):
        os.remove(FILTERED_PBF)
    subprocess.run(['osmium', 'tags-filter', PBF_FILE, 'w/highway', '-o', FILTERED_PBF, '--overwrite'], check=True)
    logger.info("Filtering complete.")
else:
    logger.info("Filtered PBF is up-to-date — skipping filtering.")

# Drop old tables and re-import
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS planet_osm_line, planet_osm_point, planet_osm_polygon, planet_osm_ways, planet_osm_nodes, planet_osm_rels, planet_osm_roads CASCADE;")
conn.commit()
cursor.close()
conn.close()

logger.info("Starting osm2pgsql import...")
subprocess.run([
    'osm2pgsql', '-d', DB_NAME, '-U', DB_USER, '-H', 'localhost',
    '-c', FILTERED_PBF, '--style', OSM2PGSQL_STYLE, '--output=pgsql'
], check=True)

logger.info("DB update complete at " + datetime.now().isoformat())