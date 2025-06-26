import time
from typing import Any, Dict, Optional

class LocalCache:
    """
    A simple in-memory cache with Time-To-Live (TTL) support.
    """
    def __init__(self, default_ttl: int = 300): # Default TTL: 5 minutes
        self._cache: Dict[str, Any] = {}
        self._ttl: Dict[str, float] = {}
        self.default_ttl: int = default_ttl
        print(f"LocalCache initialized with default TTL: {default_ttl} seconds.")

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves an item from the cache. Returns None if the item
        does not exist or has expired.
        """
        if key not in self._cache:
            return None

        # Check if item has expired
        if time.time() > self._ttl.get(key, 0):
            self.delete(key) # Remove expired item
            print(f"Cache: Item '{key}' expired and removed.")
            return None

        print(f"Cache: Item '{key}' retrieved.")
        return self._cache[key]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Adds an item to the cache with a specific TTL.
        If ttl is not provided, default_ttl is used.
        """
        current_ttl = ttl if ttl is not None else self.default_ttl
        self._cache[key] = value
        self._ttl[key] = time.time() + current_ttl
        print(f"Cache: Item '{key}' set with TTL: {current_ttl}s.")

    def delete(self, key: str) -> bool:
        """
        Removes an item from the cache.
        Returns True if the item was found and removed, False otherwise.
        """
        if key in self._cache:
            del self._cache[key]
            if key in self._ttl:
                del self._ttl[key]
            print(f"Cache: Item '{key}' deleted.")
            return True
        print(f"Cache: Item '{key}' not found for deletion.")
        return False

    def clear(self) -> None:
        """
        Clears all items from the cache.
        """
        self._cache.clear()
        self._ttl.clear()
        print("Cache: All items cleared.")

    def __contains__(self, key: str) -> bool:
        """
        Checks if a key is in the cache and not expired.
        """
        return self.get(key) is not None

# Example Usage (can be removed or kept for testing):
if __name__ == '__main__':
    cache = LocalCache(default_ttl=2) # Short TTL for testing

    cache.set("my_key", "my_value")
    assert "my_key" in cache
    assert cache.get("my_key") == "my_value"

    cache.set("another_key", {"data": [1, 2, 3]}, ttl=5)
    assert cache.get("another_key") == {"data": [1, 2, 3]}

    print("Waiting for 'my_key' to expire (2s)...")
    time.sleep(2.5)
    assert cache.get("my_key") is None
    assert "my_key" not in cache
    assert cache.get("another_key") is not None # Should still be there

    print("Waiting for 'another_key' to expire (another 2.5s)...")
    time.sleep(2.5)
    assert cache.get("another_key") is None

    cache.set("temp", 123)
    cache.delete("temp")
    assert "temp" not in cache

    cache.set("a",1)
    cache.set("b",2)
    cache.clear()
    assert "a" not in cache
    assert "b" not in cache

    print("LocalCache example usage complete.")
