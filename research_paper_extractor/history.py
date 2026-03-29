import os
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any

class SearchHistory:
    """Manages persistent search history for the CLI."""

    def __init__(self, history_file: str = None):
        if history_file is None:
            home = str(Path.home())
            self.history_file = os.path.join(home, ".arxiv_search_history.json")
        else:
            self.history_file = history_file
        
        self.history = self._load_history()

    def _load_history(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.history_file):
            return []
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _save_history(self):
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=4)
        except IOError:
            pass

    def add_entry(self, query: str, filters: Dict[str, Any] = None, results_count: int = 0):
        entry = {
            "query": query,
            "filters": filters or {},
            "timestamp": datetime.datetime.now().isoformat(),
            "results_count": results_count
        }
        # Avoid duplicate consecutive entries
        if self.history and self.history[0]["query"] == query and self.history[0]["filters"] == (filters or {}):
            return
        
        self.history.insert(0, entry)
        self.history = self.history[:100]  # Keep last 100 searches
        self._save_history()

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self.history[:limit]

    def clear(self):
        self.history = []
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
        self._save_history()

    def format_history(self, limit: int = 20) -> str:
        if not self.history:
            return "No search history found."
        
        lines = ["\n── Recent Search History ─────────────────"]
        for i, entry in enumerate(self.history[:limit], 1):
            ts = datetime.datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M")
            filters_str = ""
            if entry.get("filters"):
                active_filters = {k: v for k, v in entry["filters"].items() if v}
                if active_filters:
                    filters_str = f" [Filters: {active_filters}]"
            
            lines.append(f"{i:>2}. [{ts}] '{entry['query']}' ({entry.get('results_count', 0)} papers){filters_str}")
        
        lines.append("──────────────────────────────────────────")
        return "\n".join(lines)
    def get_stats(self) -> Dict[str, Any]:
        """Return search history statistics."""
        if not self.history:
            return {}
        
        queries = [entry['query'] for entry in self.history]
        import collections
        common = collections.Counter(queries).most_common(5)
        
        return {
            "total_searches": len(self.history),
            "unique_queries": len(set(queries)),
            "top_queries": common
        }
