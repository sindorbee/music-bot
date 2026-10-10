import time
import uuid
from typing import Dict, Any, Optional, List

class SearchCache:
    """Qidiruv natijalarini xotirada saqlash va sahifalash uchun kesh"""
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds

    def save_search(self, items: List[Dict[str, Any]], query: str) -> str:
        self._cleanup()
        search_id = uuid.uuid4().hex[:8]
        self.cache[search_id] = {
            "items": items,
            "query": query,
            "created_at": time.time()
        }
        return search_id

    def get_search(self, search_id: str) -> Optional[Dict[str, Any]]:
        data = self.cache.get(search_id)
        if not data:
            return None
        if time.time() - data["created_at"] > self.ttl:
            del self.cache[search_id]
            return None
        return data

    def _cleanup(self):
        now = time.time()
        expired = [k for k, v in self.cache.items() if now - v["created_at"] > self.ttl]
        for k in expired:
            del self.cache[k]

search_cache = SearchCache()
