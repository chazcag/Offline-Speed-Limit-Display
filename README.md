# Offline Speed Limit Display

A privacy focused speed limit display for your old car. 

Utilizing a GPS module, a Raspberry Pi, and a 7-segment display, this project shows the speed limit of whatever road you're currently on, in real-time without an active internet connection. No telemetry, no subscriptions, no BS, you are in control!

This is made possible by [OpenStreetMap (and their region downloads)](https://download.geofabrik.de/), [osm2pgsql](https://github.com/osm2pgsql-dev/osm2pgsql) for converting to a PostgreSQL/postGIS database, and the 31 GPS sats flying over our heads. 

### Hardware Used
  - Phantom 2 GPS module (DJI 11-22 V2)
    - Substitute and rework gps_decoder.py as you please
  - Orange 2 digit 7-segment display (Lite-On LTD-482EC)
    - Direct driven & wired with multiplexed digits
  - Raspberry Pi 5 4GB
    - Untested on other models though overhead is low, should work fine on weaker hardware
  - PCI-Hat NVMe SSD for boot
    - Optional, microSD card boot would work fine too 
  - Yahboom USB-PD Power Expansion board (SKU: 6000400431)
  - DIY power monitor/switching board
  
### Python Modules Used (Conda)
  - datetime
  - gpiozero
  - math
  - os
  - psycopg2
  - pyproj
  - pyserial
  - requests
  - subprocess
  - threading
  - time

### Status
Still in progress. Home stretch, only a few features left to add, however the current code works well as is. 
