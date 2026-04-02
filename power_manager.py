# power_manager.py - ACC monitoring + ACC-triggered map update

import time
import subprocess
from threading import Thread
from gpiozero import DigitalOutputDevice, DigitalInputDevice
from logger import get_logger
from config import POWER_HOLD_PIN, ACC_PIN, SHUTDOWN_DELAY_SECONDS
from map_update_utils import needs_map_update, is_on_home_wifi, is_within_home_geofence, mark_map_update_complete

logger = get_logger("power_manager")

# Initialize immediately
power_hold = DigitalOutputDevice(POWER_HOLD_PIN, initial_value=True, active_high=True)
acc_input = DigitalInputDevice(ACC_PIN, pull_up=True)

logger.info("=== Power Manager Started ===")
logger.info(f"  Hold pin (GPIO {POWER_HOLD_PIN}) = HIGH (MOSFET clamped)")
logger.info(f"  Monitoring ACC pin (GPIO {ACC_PIN})")

def monitor_acc():
    """Background thread that watches for ACC OFF and handles map update."""
    while True:
        if acc_input.value == 0:  # LOW = ACC OFF
            logger.info("ACC OFF detected! Starting shutdown sequence...")

            # Check for map update (only at home + overdue)
            update_needed = (needs_map_update() and
                             is_on_home_wifi() and
                             is_within_home_geofence())

            if update_needed:
                logger.info("Home + WiFi + overdue → starting map update (this will delay shutdown)")
                try:
                    # Stop main display service so DB import is safe
                    logger.info("Stopping speed-limit_core.service...")
                    subprocess.run(["sudo", "systemctl", "stop", "speed-limit_core.service"], check=True)

                    # Run the full map update
                    logger.info("Running update_db.py...")
                    subprocess.run([
                        "/home/sys-car/miniforge3/envs/gps_env/bin/python",
                        "/home/sys-car/gps_project/update_db.py"
                    ], cwd="/home/sys-car/gps_project", check=True)

                    mark_map_update_complete()
                    logger.info("Map update finished successfully")

                except Exception as e:
                    logger.error(f"Map update failed: {e}", exc_info=True)
                finally:
                    # Always restart main service (even if update failed)
                    try:
                        logger.info("Restarting speed-limit_core.service...")
                        subprocess.run(["sudo", "systemctl", "start", "speed-limit_core.service"], check=True)
                        logger.info("Main display restarted")
                    except Exception as restart_e:
                        logger.error(f"Failed to restart main service: {restart_e}")

            else:
                logger.info("Map update not required (not at home, not overdue, or no WiFi)")

            # Normal shutdown delay (ACC must stay OFF)
            start_time = time.time()
            while time.time() - start_time < SHUTDOWN_DELAY_SECONDS:
                if acc_input.value == 1:  # ACC came back ON
                    logger.info("ACC came back on during delay — aborting shutdown")
                    break
                time.sleep(0.2)
            else:
                # Timer expired and ACC still OFF → shutdown
                logger.info(f"Shutdown delay expired — issuing clean shutdown now")
                try:
                    subprocess.check_call(['sudo', 'shutdown', '-h', 'now'])
                except Exception as e:
                    logger.error(f"Shutdown command failed: {e}")

        time.sleep(0.2)  # normal polling rate

# Start monitor
monitor_thread = Thread(target=monitor_acc, daemon=True)
monitor_thread.start()

# Keep main script alive
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    logger.info("Power manager shutting down (dev mode)")
    power_hold.close()
    acc_input.close()