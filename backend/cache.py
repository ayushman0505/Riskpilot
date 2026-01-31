import os
import hashlib
import redis
from dotenv import load_dotenv

load_dotenv()

# Setup Redis Client
# We use a default fallback for local dev if REDIS_URL isn't set
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    # Test connection
    redis_client.ping()
    print(" Connected to Redis")
except Exception as e:
    print(f" Redis Connection Failed: {e}")
    redis_client = None

class CacheSystem:
    def __init__(self, ttl_seconds=3600):
        self.ttl = ttl_seconds # Default 1 hour cache

    def _generate_key(self, project_id: str, query: str) -> str:
        """Create a unique hash for the query within a project."""
        raw = f"{project_id}:{query.strip().lower()}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get_cached_response(self, project_id: str, query: str) -> str:
        if not redis_client: return None
        
        key = self._generate_key(project_id, query)
        cached = redis_client.get(key)
        if cached:
            print(f"⚡ Cache Hit for query: '{query}'")
            return cached
        return None

    def set_cached_response(self, project_id: str, query: str, response: str):
        if not redis_client: return
        
        key = self._generate_key(project_id, query)
        redis_client.setex(key, self.ttl, response)
        print(f" Saved to Cache: '{query}'")
