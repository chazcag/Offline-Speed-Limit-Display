# animations/power_on.py

POWER_ON_HI = {
    "frames": [
        [0,0,0,0,0,1,0,  0,0,0,0,0,0,0],        # 1: left f (upper left vertical start)
        [0,1,0,0,0,1,0,  0,0,0,0,0,0,0],        # 2: add left b (upper right)
        [0,1,1,0,0,1,0,  0,0,0,0,0,0,0],        # 3: add left c (lower right)
        [0,1,1,0,1,1,1,  0,0,0,0,0,0,0],        # 4: add left g + e (middle + lower left) → full H
        [0,1,1,0,1,1,1,  0,1,0,0,0,0,0],        # 5: start right b
        [0,1,1,0,1,1,1,  0,1,1,0,0,0,0],        # 6: add right c → full I
        [0,1,1,0,1,1,1,  0,1,1,0,0,0,0],        # 7: hold "HI" (pulse g on D1)
        [0,1,1,0,1,1,0,  0,1,1,0,0,0,0],        # 8: g off
        [0,1,1,0,1,1,1,  0,1,1,0,0,0,0],        # 9: g on
        [0,1,1,0,1,1,0,  0,1,1,0,0,0,0],        # 10: g off
        [0,1,1,0,1,1,1,  0,1,1,0,0,0,0]         # 11: g on
    ],
    "step": 11,
    "delay": 0.013,
    "one_shot": False,
    "description": "progressively displays 'HI' and blinks D1-G segment"
}
