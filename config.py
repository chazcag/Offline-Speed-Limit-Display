# config.py - Single source of truth for the entire Offline Speed Limit Display project

import os

# PROJECT / PATHS
# ==========================
PROJECT_ROOT = "/home/sys-car/gps_project"
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
LOG_DIR = os.path.join(PROJECT_ROOT, "log")

# GPS MODULE
# ==========================
SERIAL_PORT = '/dev/ttyAMA0'
BAUD_RATE = 115200
MIN_FIX_TYPE = 3          # 3 = 3D fix (recommended for outdoor use)
MIN_SATS = 5

# DISPLAY (7-segment)
# ==========================
SGMT_GPIO = [16, 21, 8, 1, 7, 20, 12]   # a b c d e f g
COMMON_D1_PIN = 24                      # Left digit (tens)
COMMON_D2_PIN = 23                      # Right digit (units)

# DATABASE
# ==========================
DB_HOST = 'localhost'
DB_NAME = 'osm_db'
DB_USER = 'REMOVED'
DB_PASSWORD = 'REMOVED'
DB_PORT = 5432

# OSM MAP & UPDATE
# ==========================
PBF_URL = 'https://download.geofabrik.de/north-america/us/texas-latest.osm.pbf'
PBF_FILE = os.path.join(DATA_DIR, 'texas-latest.osm.pbf')
FILTERED_PBF = os.path.join(DATA_DIR, 'texas-roads.osm.pbf')
OSM2PGSQL_STYLE = '/usr/share/osm2pgsql/default.style'

SPEED_FALLBACK = 30          # mph for residential/service roads with no maxspeed tag

# POWER MANAGEMENT
# ==========================
POWER_HOLD_PIN = 17
ACC_PIN = 27
SHUTDOWN_DELAY_SECONDS = 30

# LOGGING
# ==========================
LOG_LEVEL = "INFO"                    # DEBUG / INFO / WARNING / ERROR
LOG_FILE = os.path.join(LOG_DIR, "speed-limit_core.log")
LOG_MAX_MB = 20
LOG_BACKUP_COUNT = 5

# NETWORK / WIFI (for auto map updates)
# ==========================
HOME_WIFI_SSID = "YOUR_HOME_SSID"     # ← change to your home network name
HOME_WIFI_PASSWORD = "YOUR_PASSWORD"  # ← change (or use nmcli keyfile if preferred)

# HOME GEOFENCE (optional — for smarter WiFi updates)
# ==========================
HOME_LAT = 00.0000000                 # ← your approximate home latitude
HOME_LON = -00.0000000                # ← your approximate home longitude
HOME_RADIUS_METERS = 55               # trigger WiFi/update only inside this circle
 
# UPDATE SCHEDULER
# ==========================
UPDATE_INTERVAL_DAYS = 14

# ANIMATIONS
# ==========================
DEFAULT_ANIMATION = "spinner"