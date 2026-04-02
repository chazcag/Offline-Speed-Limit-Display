# map_manager.py - OSM loading and speed limit query
import psycopg2
from pyproj import Transformer
import re
from logger import get_logger
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, SPEED_FALLBACK

logger = get_logger(__name__)

class MapManager:
    def __init__(self):
        self.transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        self.conn = None
        self.cursor = None
        self._connect()

    def _connect(self):
        """Establish or re-establish DB connection"""
        try:
            if self.conn is not None:
                self.conn.close()
            self.conn = psycopg2.connect(
                host=DB_HOST,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                connect_timeout=10
            )
            self.cursor = self.conn.cursor()
            logger.debug("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.conn = None
            self.cursor = None
            raise

    def get_speed_limit(self, lat, lon):
        if self.conn is None or self.cursor is None:
            try:
                self._connect()
            except:
                return {'speed_limit': None, 'dist': None, 'is_fallback': False, 'highway_type': None}

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
                speed_limit = 0
                is_fallback = False

                if maxspeed_str:
                    # Improved parsing: extract first number, handle "55 mph", "none", etc.
                    m = re.search(r'(\d+)', str(maxspeed_str))
                    if m:
                        speed_limit = int(m.group(1))
                
                if speed_limit == 0 and highway_type in ['service', 'residential']:
                    speed_limit = SPEED_FALLBACK
                    is_fallback = True
                
                return {
                    'speed_limit': speed_limit,
                    'dist': float(dist) if dist is not None else None,
                    'is_fallback': is_fallback,
                    'highway_type': highway_type
                }
            else:
                logger.warning("No road found near coordinates")
                return {'speed_limit': None, 'dist': None, 'is_fallback': False, 'highway_type': None}

        except Exception as e:
            logger.error(f"Database query error: {e}")
            # Try to reconnect once
            try:
                self._connect()
            except:
                pass
            return {'speed_limit': None, 'dist': None, 'is_fallback': False, 'highway_type': None}

    def __del__(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()