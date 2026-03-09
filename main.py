# main.py - Entry point for the speed limit dash display

import serial
import time
from gps_decoder import NazaDecoder, get_decoded_message
from map_manager import MapManager
from display import start_display, stop_display, set_speed, set_animation, display_mode, current_animation_name
from config import SERIAL_PORT, BAUD_RATE, MIN_FIX_TYPE, MIN_SATS

# Initialize serial connection for GPS
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
decoder = NazaDecoder()

# Initialize map manager for speed limit queries
map_manager = MapManager()

# Track last displayed speed limit to avoid unnecessary updates
last_speed_limit = None

print("Speed limit display starting...")
print("Waiting for GPS fix...")

# Start the 7-segment display thread, display "hello" animation twice
start_display()
set_animation("power_on_hi")
time.sleep(6)

while True:
    # Get latest decoded GPS message
    result = get_decoded_message(ser, decoder)

    # Check if we have a sufficient GPS fix
    if result['fix_type'] >= MIN_FIX_TYPE and result['sats'] >= MIN_SATS:
        # Valid position — query the database for speed limit
        query_result = map_manager.get_speed_limit(result['lat'], result['lon'])

        speed_limit = query_result.get('speed_limit')  # May be None if no road found
        dist = query_result.get('dist', 0)
        is_fallback = query_result.get('is_fallback', False)
        highway_type = query_result.get('highway_type', 'unknown')

        if speed_limit is not None:
            # We have a real speed limit — display it
            if speed_limit != last_speed_limit:
                print(f"Speed limit: {speed_limit} mph "
                      f"(Dist: {dist:.1f}m, Fallback: {is_fallback}, Road: {highway_type})")
                set_speed(speed_limit)
                last_speed_limit = speed_limit
                current_animation_name = None
            # Even if same, ensure we're out of loading mode
            # (safe to call set_speed repeatedly)
        else:
            # On a road but no maxspeed tag
            # For now, keep showing last valid limit
            print(f"No speed limit tag found (closest road: {highway_type}, dist: {dist:.1f}m)")

    else:
        # Poor or no GPS fix - show spinner animation
        print("Waiting for GPS fix "
              f"(Fix: {result['fix_type']}, Sats: {result['sats']})...")
        if current_animation_name != "spinner":   # prevents skipping effect from resetting animation
            set_animation("spinner")
            last_speed_limit = None   # Reset so next valid limit triggers update
            current_animation_name = "spinner" 

    # Loop delay — 0.5 Hz is plenty for speed limit changes
    time.sleep(2)