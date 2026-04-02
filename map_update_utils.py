# map_update_utils.py - Helper checks for ACC-triggered map updates
import os
import math
import time
import subprocess
from datetime import datetime
from logger import get_logger
from config import HOME_WIFI_SSID, HOME_LAT, HOME_LON, HOME_RADIUS_METERS, UPDATE_INTERVAL_DAYS, LAST_UPDATE_FILE

logger = get_logger("map_updater")

def get_days_since_last_update():
    """Return days since last successful map update (999 if never run)."""
    if not os.path.exists(LAST_UPDATE_FILE):
        return 999.0
    try:
        with open(LAST_UPDATE_FILE, 'r') as f:
            ts = float(f.read().strip())
        days = (time.time() - ts) / 86400
        return days
    except Exception as e:
        logger.warning(f"Failed to read last update timestamp: {e}")
        return 999.0

def needs_map_update():
    days = get_days_since_last_update()
    if days > UPDATE_INTERVAL_DAYS:
        logger.info(f"Map update needed — {days:.1f} days since last update")
        return True
    logger.debug(f"Map update not due yet ({days:.1f} days)")
    return False

def mark_map_update_complete():
    try:
        with open(LAST_UPDATE_FILE, 'w') as f:
            f.write(str(time.time()))
        logger.info("Marked map update as complete")
    except Exception as e:
        logger.error(f"Failed to mark update complete: {e}")

def is_on_home_wifi():
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "NAME", "connection", "show", "--active"],
            capture_output=True, text=True, check=True
        )
        return HOME_WIFI_SSID in result.stdout.strip().splitlines()
    except Exception as e:
        logger.warning(f"WiFi check failed: {e}")
        return False

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (math.sin(delta_phi/2)**2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def is_within_home_geofence():
    try:
        from gps_decoder import NazaDecoder, get_decoded_message
        import serial
        ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=0.5)
        decoder = NazaDecoder()
        logger.debug("Polling GPS for home geofence check...")
        for _ in range(12):  # ~6 seconds max
            result = get_decoded_message(ser, decoder)
            if result.get('fix_type', 0) >= 3 and result.get('sats', 0) >= 5:
                dist = haversine(HOME_LAT, HOME_LON, result['lat'], result['lon'])
                logger.debug(f"GPS fix — distance to home: {dist:.0f}m")
                ser.close()
                return dist <= HOME_RADIUS_METERS
            time.sleep(0.5)
        ser.close()
        logger.warning("No solid GPS fix during geofence check")
        return False
    except Exception as e:
        logger.warning(f"Geofence GPS check failed: {e}")
        return False