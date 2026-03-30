# update_db.py - Update the local OSM database with fresh data

import os
import subprocess
import requests
import psycopg2
from datetime import datetime, timedelta
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, PBF_URL, PBF_FILE, FILTERED_PBF, OSM2PGSQL_STYLE

# Download and filter
two_weeks_ago = datetime.now() - timedelta(weeks=2)
should_download = False

if not os.path.exists(PBF_FILE):
    print("PBF file not found — downloading fresh copy.")
    should_download = True
else:
    file_mtime = datetime.fromtimestamp(os.path.getmtime(PBF_FILE))
    if file_mtime < two_weeks_ago:
        print(f"PBF file is older than 2 weeks (last modified {file_mtime.isoformat()}) — downloading new version.")
        should_download = True
    else:
        print(f"PBF file is recent (modified {file_mtime.isoformat()}) — skipping download.")

if should_download:
    print("Downloading fresh PBF with wget...")
    if os.path.exists(PBF_FILE):
        os.remove(PBF_FILE)
    
    subprocess.run([
        'wget', '-O', PBF_FILE, PBF_URL, '--progress=bar'
        # Add '--continue' if you want resume support
    ], check=True)
    print("Download complete.")
else:
    print("Using existing PBF file.")


# Always remove the old filtered file if downloading a new source or if the filtered file doesn't exist
should_filter = should_download or not os.path.exists(FILTERED_PBF)

if should_filter:
    print("Filtering roads from PBF...")
    # Ensure old filtered file is gone
    if os.path.exists(FILTERED_PBF):
        os.remove(FILTERED_PBF)
    
    subprocess.run(['osmium', 'tags-filter', PBF_FILE, 'w/highway','-o', FILTERED_PBF, '--overwrite'], check=True)
    print("Filtering complete.")
else:
    print("Filtered PBF is up-to-date — skipping filtering.")

# Drop old tables and re-import
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS planet_osm_line, planet_osm_point, planet_osm_polygon, planet_osm_ways, planet_osm_nodes, planet_osm_rels, planet_osm_roads CASCADE;")
conn.commit()
cursor.close()
conn.close()

subprocess.run([
    'osm2pgsql', '-d', DB_NAME, '-U', DB_USER, '-H', 'localhost',
    '-c', FILTERED_PBF,
    '--style', OSM2PGSQL_STYLE,
    '--output=pgsql'
], check=True)

print("DB update complete at " + datetime.now().isoformat())