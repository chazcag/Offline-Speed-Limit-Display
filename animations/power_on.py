# animations/figure_eight.py

POWER_ON_HI = {
    "frames": [
        [0,0,0,0,0,0,0,  0,0,0,0,0,0,0],         # 0: blank
        [0,0,0,0,0,1,0,  0,0,0,0,0,0,0],        # 1: left f (upper left vertical start)
        [0,1,0,0,0,1,0,  0,0,0,0,0,0,0],        # 2: add left b (upper right)
        [0,1,1,0,0,1,0,  0,0,0,0,0,0,0],        # 3: add left c (lower right)
        [0,1,1,0,1,1,1,  0,0,0,0,0,0,0],        # 4: add left g + e (middle + lower left) → full H
        [0,1,1,0,1,1,1,  0,1,0,0,0,0,0],        # 5: start right b
        [0,1,1,0,1,1,1,  0,1,1,0,0,0,0],        # 6: add right c → full I
        [0,1,1,0,1,1,1,  0,1,1,0,0,0,0],        # 7–10: hold "HI" (maybe pulse g on both for flair)
        [0,1,1,0,1,1,0,  0,1,1,0,0,0,0],        # g off
        [0,1,1,0,1,1,1,  0,1,1,0,0,0,0],        # g on
        [0,1,1,0,1,1,0,  0,1,1,0,0,0,0],        # 11: hold full
        [0,1,1,0,1,1,1,  0,1,1,0,0,0,0]        # Optional 12: quick spin or blank to transition
    ],
    "step": 13,
    "delay": 0.012,
    "one_shot": False,
    "description": "figure eight chase pattern"
}
