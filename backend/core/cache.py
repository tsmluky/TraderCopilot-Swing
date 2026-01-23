import time
import os
import json
from typing import Any, Optional


class CacheService:
    """
    Servicio de caché híbrido (Memoria + Redis opcional).
    Por defecto usa memoria para cero-configuración.
    """

    _instance = None
    _memory_storage = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheService, cls).__new__(cls)
            cls._instance._init_redis()
        return cls._instance

    def _init_redis(self):
        self.redis_client = None
        redis_url = os.getenv("REDIS_URL")
        # Solo intentar conectar si hay URL explícita y librería instalada
        if redis_url:
            try:
                import redis

                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                print(f"[CACHE] Connected to Redis at {redis_url}")
            except ImportError:
                print(
                    "[CACHE] Redis URL found but 'redis' lib not installed. Using Memory."
                )
            except Exception as e:
                print(f"[CACHE] Redis connection failed: {e}. Using Memory.")
        else:
            print("[CACHE] runs in In-Memory mode (No REDIS_URL).")

    def get(self, key: str) -> Optional[Any]:
        # 1. Redis
        if self.redis_client:
            try:
                val = self.redis_client.get(key)
                if val:
                    return json.loads(val)
            except Exception as e:
                print(f"[CACHE] Redis GET Error: {e}")

        # 2. Memory
        data = self._memory_storage.get(key)
        if data:
            val, expiry = data
            if time.time() < expiry:
                return val
            else:
                del self._memory_storage[key]  # Expired
        return None

    def set(self, key: str, value: Any, ttl: int = 60):
        # 1. Redis
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, json.dumps(value))
                return
            except Exception as e:
                print(f"[CACHE] Redis SET Error: {e}")

        # 2. Memory
        expiry = time.time() + ttl
        self._memory_storage[key] = (value, expiry)

        # Cleanup ocasional (muy simple)
        if len(self._memory_storage) > 1000:
            self._cleanup()

    def _cleanup(self):
        now = time.time()
        keys_to_del = [k for k, v in self._memory_storage.items() if now > v[1]]
        for k in keys_to_del:
            del self._memory_storage[k]


# Global Instance
cache = CacheService()
