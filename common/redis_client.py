import redis
from django.conf import settings

class RedisClient:
    def __init__(self):
        self.redis_host = settings.REDIS_HOST
        self.redis_port = settings.REDIS_PORT
        self.redis_db = settings.REDIS_DB
        self.redis_password = settings.REDIS_PASSWORD
        self.is_connected = False
        self.connection = self._create_connection()

    def _create_connection(self):
        try:
            conn = redis.StrictRedis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                password=self.redis_password,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_keepalive=True,
            )
            # Test connection
            conn.ping()
            self.is_connected = True
            return conn
        except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
            print(f"Redis connection failed: {str(e)}. App will continue without caching.")
            self.is_connected = False
            return None

    def set_value(self, key, value, ttl=None):
        if not self.is_connected or not self.connection:
            return False
        try:
            self.connection.set(key, value)
            if ttl:
                self.connection.expire(key, ttl)
            return True
        except Exception as e:
            print(f"Redis set_value error: {str(e)}")
            return False

    def get_value(self, key):
        if not self.is_connected or not self.connection:
            return None
        try:
            return self.connection.get(key)
        except Exception as e:
            print(f"Redis get_value error: {str(e)}")
            return None

    def delete_key(self, key):
        if not self.is_connected or not self.connection:
            return False
        try:
            self.connection.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete_key error: {str(e)}")
            return False

    def increment_value(self, key):
        if not self.is_connected or not self.connection:
            return 0
        try:
            return self.connection.incr(key)
        except Exception as e:
            print(f"Redis increment_value error: {str(e)}")
            return 0

    def decrement_value(self, key):
        if not self.is_connected or not self.connection:
            return 0
        try:
            return self.connection.decr(key)
        except Exception as e:
            print(f"Redis decrement_value error: {str(e)}")
            return 0

    def hset_value(self, hash_name, key, value, ttl=None):
        if not self.is_connected or not self.connection:
            return False
        try:
            self.connection.hset(hash_name, key, value)
            if ttl:
                self.connection.expire(hash_name, ttl)
            return True
        except Exception as e:
            print(f"Redis hset_value error: {str(e)}")
            return False

    def hget_value(self, hash_name, key):
        if not self.is_connected or not self.connection:
            return None
        try:
            return self.connection.hget(hash_name, key)
        except Exception as e:
            print(f"Redis hget_value error: {str(e)}")
            return None

    def delete_hash_key(self, hash_name, key):
        if not self.is_connected or not self.connection:
            return False
        try:
            self.connection.hdel(hash_name, key)
            return True
        except Exception as e:
            print(f"Redis delete_hash_key error: {str(e)}")
            return False

    def set_ttl(self, key, ttl):
        if not self.is_connected or not self.connection:
            return False
        try:
            self.connection.expire(key, ttl)
            return True
        except Exception as e:
            print(f"Redis set_ttl error: {str(e)}")
            return False


redis_client = RedisClient()