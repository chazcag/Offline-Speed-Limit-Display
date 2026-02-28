# update_db.py - Update the OSM database with fresh data

import os
import subprocess
import requests
from datetime import datetime, timedelta
import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD

# Download and filter (same as tiling script)
pbf_url = 'https://download.geofabrik.de/north-america/us/texas-latest.osm.pbf'
pbf_file = '/home/sys-car/gps_project/data/texas-latest.osm.pbf'
two_weeks_ago = datetime.now() - timedelta(weeks=2)
should_download = False

if not os.path.exists(pbf_file):
    print("PBF file not found — downloading fresh copy.")
    should_download = True
else:
    file_mtime = datetime.fromtimestamp(os.path.getmtime(pbf_file))
    if file_mtime < two_weeks_ago:
        print(f"PBF file is older than 2 weeks (last modified {file_mtime.isoformat()}) — downloading new version.")
        should_download = True
    else:
        print(f"PBF file is recent (modified {file_mtime.isoformat()}) — skipping download.")

if should_download:
    print("Downloading fresh PBF with wget...")
    if os.path.exists(pbf_file):
        os.remove(pbf_file)
    
    subprocess.run([
        'wget', '-O', pbf_file, pbf_url, '--progress=bar'
        # Add '--continue' if you want resume support
        # Add '--progress=bar' for nice terminal progress
    ], check=True)
    print("Download complete.")
else:
    print("Using existing PBF file.")


filtered_pbf = '/home/sys-car/gps_project/data/texas-roads.osm.pbf'

# Always remove the old filtered file if we're downloading a new source
# or if the filtered file doesn't exist
should_filter = should_download or not os.path.exists(filtered_pbf)

if should_filter:
    print("Filtering roads from PBF...")
    # Ensure old filtered file is gone
    if os.path.exists(filtered_pbf):
        os.remove(filtered_pbf)
    
    subprocess.run(['osmium', 'tags-filter', pbf_file, 'w/highway','-o', filtered_pbf, '--overwrite'], check=True)
    print("Filtering complete.")
else:
    print("Filtered PBF is up-to-date — skipping filtering.")

# Drop old tables and re-import
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host='localhost',      # forces TCP connection on 127.0.0.1
    port=5432
)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS planet_osm_line, planet_osm_point, planet_osm_polygon, planet_osm_ways, planet_osm_nodes, planet_osm_rels, planet_osm_roads CASCADE;")
conn.commit()
cursor.close()
conn.close()

subprocess.run([
    'osm2pgsql', '-d', DB_NAME, '-U', DB_USER, '-H', 'localhost',
    '-c', filtered_pbf,
    '--style', '/usr/share/osm2pgsql/default.style',
    '--output=pgsql'
], check=True)

print("DB update complete at " + datetime.now().isoformat())