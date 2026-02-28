# animations/__init__.py

from .spinner       import SPINNER
from .figure_eight  import FIGURE_EIGHT
from .power_on      import POWER_ON_HI
#from .power_off      import POWER_OFF
#from .status        import GPS_LOST, SPEED_NOT_FOUND, NO_ROADWAY

ANIMATIONS = {
    "spinner":        SPINNER,
    "figure_eight":   FIGURE_EIGHT,
    "power_on_hi":    POWER_ON_HI,
#    "gps_lost":       GPS_LOST,
#    "speed_not_found": SPEED_NOT_FOUND,
#    "no_roadway":     NO_ROADWAY,
    # etc.
}

DEFAULT_ANIMATION = "spinner"