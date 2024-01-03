import redis
from django.conf import settings

class RedisClient:
    def __init__(self):
        self.redis_host = settings.REDIS_HOST
        self.redis_port = settings.REDIS_PORT
        self.redis_db = settings.REDIS_DB
        self.redis_password = settings.REDIS_PASSWORD

        self.connection = self._create_connection()

    def _create_connection(self):
        return redis.StrictRedis(
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
            password=self.redis_password,
            decode_responses=True,  # Decode responses to strings
        )

    def set_value(self, key, value, ttl=None): #ttl value is in seconds
        self.connection.set(key, value)
        if ttl:
            self.connection.expire(key, ttl)

    def get_value(self, key):
        return self.connection.get(key)

    def delete_key(self, key):
        self.connection.delete(key)

    def increment_value(self, key):
        return self.connection.incr(key)

    def decrement_value(self, key):
        return self.connection.decr(key)

    def hset_value(self, hash_name, key, value, ttl=None):
        self.connection.hset(hash_name, key, value)
        if ttl:
            self.connection.expire(hash_name, ttl)

    def hget_value(self, hash_name, key):
        return self.connection.hget(hash_name, key)

    def delete_hash_key(self, hash_name, key):
        self.connection.hdel(hash_name, key)

    def set_ttl(self, key, ttl):
        self.connection.expire(key, ttl)


redis_client = RedisClient()