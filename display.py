# display.py - Stable version with flicker-free multiplexing and multiple animations

import threading
import time
from animations import ANIMATIONS, DEFAULT_ANIMATION
from gpiozero import LED
from time import sleep
from logger import get_logger
from config import SGMT_GPIO, COMMON_D1_PIN, COMMON_D2_PIN

logger = get_logger(__name__)

# Segment patterns for 0-9 (1 = on, meaning segment should be lit)
DIGITS = [
    [1,1,1,1,1,1,0],  # 0
    [0,1,1,0,0,0,0],  # 1
    [1,1,0,1,1,0,1],  # 2
    [1,1,1,1,0,0,1],  # 3
    [0,1,1,0,0,1,1],  # 4
    [1,0,1,1,0,1,1],  # 5
    [1,0,1,1,1,1,1],  # 6
    [1,1,1,0,0,0,0],  # 7
    [1,1,1,1,1,1,1],  # 8
    [1,1,1,1,0,1,1]   # 9
]

# Pin mappings
SEGMENT_PINS = [LED(SGMT_GPIO[0]), LED(SGMT_GPIO[1]), LED(SGMT_GPIO[2]), LED(SGMT_GPIO[3]), LED(SGMT_GPIO[4]), LED(SGMT_GPIO[5]), LED(SGMT_GPIO[6])]  # a b c d e f g
COMMON_DIGIT1 = LED(COMMON_D1_PIN)  # Left digit (tens)
COMMON_DIGIT2 = LED(COMMON_D2_PIN)  # Right digit (units)

# Global state
current_speed = 0
display_mode = "loading"  # "number", "loading", or "animation"
current_frame = 0
frame_counter = 0   # For slowing down animation without hurting refresh rate
lock = threading.Lock()
display_thread = None
current_animation_name = DEFAULT_ANIMATION
digit_delay_number = 0.01


def start_display():
    """Start the display thread if not already running."""
    global display_thread
    with lock:
        if display_thread is None:
            display_thread = threading.Thread(target=_display_loop, daemon=True)
            display_thread.start()
            logger.info("Display thread started")

def stop_display():
    """Stop the display and clean up GPIO pins."""
    global display_thread
    with lock:
        if display_thread:
            display_thread = None
    blank = [0] * 14
    _set_segments(blank, delay=digit_delay_number)
    for pin in SEGMENT_PINS + [COMMON_DIGIT1, COMMON_DIGIT2]:
        pin.close()
    logger.info("Display stopped and GPIO cleaned")

def set_speed(speed):
    """Set the speed to display (0-99), switching to number mode. Falls back to loading on invalid input."""
    global current_speed, display_mode
    with lock:
        try:
            current_speed = max(0, min(99, int(speed)))  # Clamp to 0–99
            display_mode = "number"
        except ValueError:
            set_animation("spinner")  # Fallback to loading on invalid input

def set_no_signal():
    """Switch to loading spinner animation."""
    set_animation("spinner")

def set_animation(name: str):
    global current_animation_name, current_frame, frame_counter, display_mode
    with lock:
        if name not in ANIMATIONS:
            raise ValueError(f"Unknown animation: {name}")
        current_animation_name = name
        current_frame = 0
        frame_counter = 0
        display_mode = "animation"

def _set_segments(pattern, delay):
    """Set segments for both digits."""

    if len(pattern) != 14:
        raise ValueError("Pattern must be 14 elements for two digits.")

    left_pattern = pattern[0:7]
    right_pattern = pattern[7:14]

    # Actively turn all segments OFF to discharge capacitance
    for pin in SEGMENT_PINS:
        pin.value = 1  # High = segment off (no current)

    # Left digit
    for i, on in enumerate(left_pattern):
        SEGMENT_PINS[i].value = 0 if on else 1
    COMMON_DIGIT1.on()
    sleep(delay)
    COMMON_DIGIT1.off()

    # Right digit
    for i, on in enumerate(right_pattern):
        SEGMENT_PINS[i].value = 0 if on else 1
    COMMON_DIGIT2.on()
    sleep(delay)
    COMMON_DIGIT2.off()


def _display_loop():
    """Main display loop"""
    global current_frame, frame_counter

    while True:
        start_time = time.perf_counter()

        with lock:
            mode = display_mode
            speed = current_speed
            anim_name = current_animation_name
            frame = current_frame

        if mode == "number":
            tens = speed // 10
            ones = speed % 10
            _set_segments(DIGITS[tens] + DIGITS[ones], delay=digit_delay_number)

        elif mode == "animation":
            anim = ANIMATIONS[current_animation_name]
            delay = anim["delay"]
            frames = anim["frames"]
            step = anim["step"]

            _set_segments(frames[frame], delay=delay)

            frame_counter += 1
            if frame_counter >= step:
                current_frame = (current_frame + 1) % len(frames)
                frame_counter = 0

                # one-shot handling
                if anim.get("one_shot", False) and current_frame == 0:
                    # animation finished → switch to default (e.g. spinner or blank)
                    set_animation("spinner")
        else: 
            continue



# Test the display standalone
if __name__ == "__main__":
    start_display()

    print("Displaying 72 for 3 seconds...")
    set_speed(72)
    time.sleep(3)
    print("Switching to HELLO animation...")
    set_animation("power_on_hi")
    time.sleep(8)
    print("Switching to spinner animation for 10 seconds...")
    set_animation("spinner")
    time.sleep(5)
    print("Switching to figure 8 animation for 10 seconds...")
    set_animation("figure_eight")
    time.sleep(5)
    print("88...")
    set_speed(88)
    time.sleep(5)
    
    # Cleanup on exit
    stop_display()
    print("Test complete – display cleared.")