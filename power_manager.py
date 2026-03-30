# Power Manager
# - Sets GPIO 17 HIGH immediately to hold the MOSFET
# - Monitors GPIO 27 for ACC OFF (LOW signal)
# - Starts configurable timer then issues clean shutdown
# - Runs as a systemd service (starts very early on boot)

import time
from threading import Thread
from subprocess import check_call
from gpiozero import DigitalOutputDevice, DigitalInputDevice
import config

# Initialize immediately
power_hold = DigitalOutputDevice(config.POWER_HOLD_PIN, initial_value=True, active_high=True)
acc_input = DigitalInputDevice(config.ACC_PIN, pull_up=True)

print("=== Power Manager Started ===")
print(f"  Hold pin (GPIO {config.POWER_HOLD_PIN}) = HIGH (MOSFET clamped)")
print(f"  Monitoring ACC pin (GPIO {config.ACC_PIN}):")

def monitor_acc():
    """Background thread that watches for ACC cut — continuous polling, instant cancel"""
    while True:
        if acc_input.value == 0:  # LOW = ACC OFF
            print("ACC OFF detected! Starting shutdown timer...")
            start_time = time.time()
            
            # Continuous check during the delay
            while time.time() - start_time < config.SHUTDOWN_DELAY_SECONDS:
                if acc_input.value == 1:  # ACC came back ON
                    print("ACC came back on during delay — aborting shutdown and resuming monitoring.")
                    break  # exit inner loop immediately
                time.sleep(0.2)  # poll every 200 ms
            
            else:
                # Inner loop finished naturally → timer expired and ACC is still OFF
                print(f"Timer expired — issuing clean shutdown now.")
                try:
                    check_call(['sudo', 'shutdown', '-h', 'now'])
                except Exception as e:
                    print(f"Shutdown command failed: {e}")
            
        
        time.sleep(0.2)  # normal polling when ACC is ON

# Start monitor in background thread
monitor_thread = Thread(target=monitor_acc, daemon=True)
monitor_thread.start()

# Keep the main script alive forever
try:
    while True:
        time.sleep(60)  # heartbeat
except KeyboardInterrupt:
    print("Power manager shutting down (dev mode)")
    power_hold.close()
    acc_input.close()