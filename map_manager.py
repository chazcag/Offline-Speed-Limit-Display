# map_manager.py - OSM loading and speed limit query

import psycopg2
from pyproj import Transformer

from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, speed_fallback

class MapManager:
    def __init__(self):
        self.transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        self.conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        self.cursor = self.conn.cursor()

    def get_speed_limit(self, lat, lon):
        try:
            x, y = self.transformer.transform(lon, lat)
            query = """
                SELECT tags->'highway', tags->'maxspeed', ST_Distance(geom, ST_GeomFromText('POINT(%s %s)', 3857)) AS dist
                FROM lines
                WHERE tags->'highway' IS NOT NULL
                ORDER BY geom <-> ST_GeomFromText('POINT(%s %s)', 3857)
                LIMIT 1;
            """
            self.cursor.execute(query, (x, y, x, y))
            result = self.cursor.fetchone()
            if result:
                highway_type, maxspeed_str, dist = result
                speed_limit = int(''.join(filter(str.isdigit, maxspeed_str))) if maxspeed_str else 0
                is_fallback = False
                if speed_limit == 0 and highway_type in ['service', 'residential']:
                    speed_limit = speed_fallback  # Fallback for service or residential roads
                    is_fallback = True
                return {'speed_limit': speed_limit, 'dist': dist, 'is_fallback': is_fallback, 'highway_type': highway_type}
            else:
                print("No road found within query")
                return {'speed_limit': 0, 'dist': None, 'is_fallback': False, 'highway_type': None}
        except Exception as e:
            print(f"Query error: {e}")
            return {'speed_limit': 0, 'dist': None, 'is_fallback': False, 'highway_type': None}
    def __del__(self):
        self.cursor.close()
        self.conn.close()

 # Test the map manager standalone
if __name__ == "__main__":
    manager = MapManager()
    result = manager.get_speed_limit(00.0000000, -00.0000000)  # Example lat/lon"
    print(f"Speed limit: {result['speed_limit']} mph, Distance: {result['dist']} m, Fallback: {result['is_fallback']}, Highway type: {result['highway_type']}")