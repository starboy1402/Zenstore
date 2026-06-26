import time

_cache: dict = {}

def get_cache(key: str):
    entry = _cache.get(key)
    # Check if it exists and hasn't expired yet
    if entry and time.time() < entry["expires_at"]:
        return entry["data"]  # Cache Hit!
    return None               # Cache Miss or Expired!

def set_cache(key: str, value, ttl: int = 60):
    # Store the data and set an expiration time (current time + 60 seconds)
    _cache[key] = {
        "data": value,
        "expires_at": time.time() + ttl
    }

def invalidate_cache(key: str):
    # Delete the key if it exists, do nothing if it doesn't
    _cache.pop(key, None)
