# animations/spinner.py

# Spinner frames (14 segments total: left 0-6, right 7-13)
SPINNER = {
    "frames": [
        [1,0,0,0,0,1,0,  0,0,0,0,0,0,0],  # Frame 0: left a + f
        [1,0,0,0,0,0,0,  1,0,0,0,0,0,0],  # Frame 1: left a + right a  ← fixed
        [0,0,0,0,0,0,0,  1,1,0,0,0,0,0],  # Frame 2: right a + b
        [0,0,0,0,0,0,0,  0,1,1,0,0,0,0],  # Frame 3: right b + c
        [0,0,0,0,0,0,0,  0,0,1,1,0,0,0],  # Frame 4: right c + d
        [0,0,0,1,0,0,0,  0,0,0,1,0,0,0],  # Frame 5: left d + right d  ← fixed
        [0,0,0,1,1,0,0,  0,0,0,0,0,0,0],  # Frame 6: left d + e
        [0,0,0,0,1,1,0,  0,0,0,0,0,0,0]   # Frame 7: left e + f
    ],
    "step": 8,
    "delay": 0.0085,
    "one_shot": False,
    "description": "clockwise perimeter chase"
}
