# config.py - Constants for the project

# GPS module
SERIAL_PORT = '/dev/ttyAMA0'
BAUD_RATE = 115200
MIN_FIX_TYPE = 3  # set to 3 for outdoor
MIN_SATS = 5


# Display GPIO pin mappings (multiplexed common anode LTD-482EC)
SGMT_GPIO = [16, 21, 8, 1, 7, 20, 12]  # a b c d e f g
COMMON_D1_PIN = 24  # Left digit (tens)
COMMON_D2_PIN = 23  # Right digit (units)

# Database
DB_HOST = 'localhost'
DB_NAME = 'osm_db'
DB_USER = 'USERNAME'
DB_PASSWORD = 'PASSWORD'
DB_PORT = 5432

# OSM map
pbf_url = 'https://download.geofabrik.de/north-america/us/texas-latest.osm.pbf'
pbf_file = '/home/sys-car/gps_project/data/texas-latest.osm.pbf'
filtered_pbf = '/home/sys-car/gps_project/data/texas-roads.osm.pbf'

# Map manager
speed_fallback = 30   # Should this even be here? Probably should be handled in main