# config.py - Constants for the project

SERIAL_PORT = '/dev/ttyAMA0'
BAUD_RATE = 115200
MIN_FIX_TYPE = 3  # Lowered for indoor testing; set to 3 for outdoor
MIN_SATS = 5

DB_HOST = 'localhost'
DB_NAME = 'osm_db'
DB_USER = 'USERNAME'
DB_PASSWORD = '****************'