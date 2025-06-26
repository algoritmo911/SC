# storage/caching.py
import asyncio
import time
from typing import Any, Optional, Dict
from collections import OrderedDict # For LRU cache implementation

# --- Cache Interface (Optional but good practice) ---
class CacheInterface:
    async def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        raise NotImplementedError

    async def delete(self, key: str) -> None:
        raise NotImplementedError

    async def clear(self) -> None:
        raise NotImplementedError

# --- Simple In-Memory LRU Cache Implementation ---
class InMemoryLRUCache(CacheInterface):
    """
    A simple asynchronous in-memory LRU (Least Recently Used) cache.
    Supports Time-To-Live (TTL) for cache entries.
    """
    def __init__(self, max_size: int = 128):
        if max_size <= 0:
            raise ValueError("Cache max_size must be positive.")
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.max_size = max_size
        self._lock = asyncio.Lock() # To handle concurrent access safely

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key not in self.cache:
                return None

            entry = self.cache[key]
            # Check TTL
            if entry["ttl"] is not None and entry["expires_at"] < time.monotonic():
                # Expired entry
                del self.cache[key]
                return None

            # Move to end to mark as recently used
            self.cache.move_to_end(key)
            return entry["value"]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.
        Args:
            key: The cache key.
            value: The value to store.
            ttl: Time-to-live in seconds. If None, lives indefinitely (until evicted by LRU).
        """
        async with self._lock:
            expires_at = (time.monotonic() + ttl) if ttl is not None else None
            if key in self.cache:
                # Update existing entry
                del self.cache[key] # Remove to re-insert at the end ( OrderedDict behavior)

            self.cache[key] = {"value": value, "ttl": ttl, "expires_at": expires_at}
            self.cache.move_to_end(key) # Mark as recently used

            # Enforce max_size (LRU eviction)
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False) # Remove the oldest item

    async def delete(self, key: str) -> None:
        async with self._lock:
            if key in self.cache:
                del self.cache[key]

    async def clear(self) -> None:
        async with self._lock:
            self.cache.clear()

    async def size(self) -> int:
        async with self._lock:
            return len(self.cache)

# --- Cache Manager (Optional - to manage multiple cache instances or types) ---
class CacheManager:
    """
    Manages different cache instances.
    For now, it just provides a default in-memory cache.
    Could be extended to support Redis, Memcached, etc., based on configuration.
    """
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._caches: Dict[str, CacheInterface] = {}
        self._default_cache_name = "default_lru"

        # Initialize a default cache
        default_cache_max_size = self.config.get("DEFAULT_CACHE_MAX_SIZE", 256)
        self._caches[self._default_cache_name] = InMemoryLRUCache(max_size=default_cache_max_size)

    def get_cache(self, name: Optional[str] = None) -> CacheInterface:
        """
        Gets a cache instance by name. Returns the default cache if name is None.
        """
        if name is None:
            name = self._default_cache_name

        cache_instance = self._caches.get(name)
        if not cache_instance:
            # Optionally, create on-demand if specific config exists for 'name'
            # For now, just raise an error if a non-default, non-existent cache is requested.
            if name == self._default_cache_name: # Should not happen if constructor ran
                 raise RuntimeError("Default cache not initialized.")
            raise ValueError(f"Cache with name '{name}' not found.")
        return cache_instance

# --- Validation Logic (Placeholder) ---
# Caching and validation often go hand-in-hand.
# For example, validating data integrity of cached items or external resources.

async def validate_cached_data(cache_key: str, data_to_validate: Any, validation_rules: Dict) -> bool:
    """
    Placeholder for data validation logic.
    This could be used to validate data retrieved from cache or before caching.
    Args:
        cache_key: The key associated with the data.
        data_to_validate: The data itself.
        validation_rules: Rules for validation (e.g., schema, checksum).
    Returns:
        True if data is valid, False otherwise.
    """
    print(f"Validating data for key: {cache_key} (rules: {validation_rules})")
    # Example: Checksum validation
    # if "checksum" in validation_rules:
    #     expected_checksum = validation_rules["checksum"]
    #     calculated_checksum = hashlib.md5(str(data_to_validate).encode()).hexdigest()
    #     if calculated_checksum != expected_checksum:
    #         print(f"Checksum mismatch for {cache_key}")
    #         return False

    # Example: Schema validation (e.g., using Pydantic)
    # if "schema_model" in validation_rules:
    #     try:
    #         validation_rules["schema_model"](**data_to_validate) # If data is a dict
    #     except Exception as e: # Catch Pydantic ValidationError or similar
    #         print(f"Schema validation failed for {cache_key}: {e}")
    #         return False

    return True # Placeholder: always valid

# Example Usage
# async def main():
#     # Using the InMemoryLRUCache directly
#     lru_cache = InMemoryLRUCache(max_size=2)
#
#     await lru_cache.set("key1", "value1", ttl=5) # Expires in 5 seconds
#     await lru_cache.set("key2", {"data": "value2"})
#
#     print(f"Cache size: {await lru_cache.size()}")
#
#     val1 = await lru_cache.get("key1")
#     print(f"Get key1: {val1}")
#
#     await lru_cache.set("key3", "value3") # This should evict key1 if max_size=2 (if key1 was oldest)
#                                         # Actually, key2 is older if key1 was accessed by get.
#                                         # Let's test eviction properly.
#
#     print(f"Cache state after adding key3: {lru_cache.cache}")
#     print(f"Cache size: {await lru_cache.size()}") # Should be 2
#
#     # Test TTL expiration
#     print("Waiting for key1 to expire (5s)...")
#     await asyncio.sleep(6)
#     val1_expired = await lru_cache.get("key1")
#     print(f"Get key1 after TTL: {val1_expired}") # Should be None
#     print(f"Cache size after TTL check: {await lru_cache.size()}") # Should be 1 if key1 expired and was removed
#
#     # Using CacheManager
#     manager = CacheManager()
#     default_cache = manager.get_cache()
#
#     await default_cache.set("user:123:profile", {"name": "Alice", "email": "alice@example.com"}, ttl=60)
#     profile = await default_cache.get("user:123:profile")
#     print(f"User profile from CacheManager: {profile}")
#
#     if profile:
#         is_valid = await validate_cached_data("user:123:profile", profile, {"schema_model": "UserProfileModel"})
#         print(f"Profile data is valid: {is_valid}")
#
#     await default_cache.clear()
#     print(f"Default cache size after clear: {await default_cache.size()}")

# if __name__ == "__main__":
#     asyncio.run(main())
