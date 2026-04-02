# main.py - Entry point for the speed limit dash display (FIXED v4 - one-time GPS time sync)

import serial
import time
import subprocess
import datetime
import signal
import sys
from gps_decoder import NazaDecoder, get_decoded_message
from map_manager import MapManager
from display import start_display, stop_display, set_speed, set_animation
from logger import get_logger
from config import SERIAL_PORT, BAUD_RATE, MIN_FIX_TYPE, MIN_SATS

logger = get_logger(__name__)

# Global hardware objects
ser = None
decoder = None
map_manager = None
last_speed_limit = None
time_synced = False   # ← NEW: one-time flag

def sync_system_time(gps_result):
    global time_synced
    try:
        dt_str = f"{gps_result['date']} {gps_result['time']}"
        dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

        # Quick sanity check — GPS modules sometimes report garbage years
        if dt.year < 2024 or dt.year > 2035:
            logger.warning(f"GPS date looks invalid ({dt_str}) — skipping time sync")
            return

        # Disable NTP so timedatectl set-time is allowed
        subprocess.run(["sudo", "timedatectl", "set-ntp", "false"],
                       check=True, capture_output=True)

        # Now set the time
        subprocess.run(["sudo", "timedatectl", "set-time", dt.strftime("%Y-%m-%d %H:%M:%S")],
                       check=True, capture_output=True)

        logger.info(f"System time set from GPS (one-time) → {dt_str}")
        time_synced = True

    except Exception as e:
        logger.warning(f"GPS time sync failed: {e}")
        # Do NOT mark as synced so we can try again on next boot if needed

def graceful_shutdown(signum, frame):
    logger.info(f"Received signal {signum} — shutting down gracefully")
    stop_display()
    if ser and ser.is_open:
        ser.close()
    logger.info("Speed limit display shutdown complete")
    sys.exit(0)

def main():
    global ser, decoder, map_manager, last_speed_limit, time_synced

    last_speed_limit = None
    time_synced = False

    # Register shutdown handlers
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)

    logger.info("=== Offline Speed Limit Display starting ===")

    # Initialize hardware
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        decoder = NazaDecoder()
        map_manager = MapManager()
    except Exception as e:
        logger.critical(f"Hardware init failed: {e}")
        sys.exit(1)

    start_display()
    set_animation("power_on_hi")
    logger.info("Display started — showing power-on animation")
    time.sleep(6)

    logger.info("Waiting for GPS fix...")

    while True:
        try:
            result = get_decoded_message(ser, decoder)

            if (result['fix_type'] >= MIN_FIX_TYPE and 
                result['sats'] >= MIN_SATS):
                
                # ONE-TIME GPS time sync (only on first good fix)
                if not time_synced:
                    sync_system_time(result)

                # Query speed limit
                query_result = map_manager.get_speed_limit(result['lat'], result['lon'])
                speed_limit = query_result.get('speed_limit')
                dist = query_result.get('dist', 0)
                is_fallback = query_result.get('is_fallback', False)
                highway_type = query_result.get('highway_type', 'unknown')

                if speed_limit is not None and speed_limit > 0:
                    if speed_limit != last_speed_limit:
                        logger.info(f"Speed limit: {speed_limit} mph "
                                    f"(Dist: {dist:.1f}m, Fallback: {is_fallback}, Road: {highway_type})")
                        set_speed(speed_limit)
                        last_speed_limit = speed_limit
                else:
                    logger.debug(f"No speed limit tag (closest road: {highway_type}, dist: {dist:.1f}m)")

            else:
                logger.debug(f"Waiting for GPS fix (Fix:{result['fix_type']} Sats:{result['sats']})")
                set_animation("spinner")
                if last_speed_limit is not None:
                    last_speed_limit = None

            time.sleep(2)  # 0.5 Hz update rate is perfect

        except Exception as e:
            logger.error(f"Main loop exception: {e}", exc_info=True)
            time.sleep(5)

if __name__ == "__main__":
    main()