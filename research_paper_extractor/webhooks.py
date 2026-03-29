import requests
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class WebhookManager:
    """Sends notifications to Discord or Slack webhooks."""

    def __init__(self, url: Optional[str] = None):
        self.url = url

    def send_notification(self, title: str, message: str, papers: List[Any] = None) -> bool:
        """Sends a notification with optional paper details."""
        if not self.url:
            return False

        payload = {
            "content": f"**{title}**\n{message}"
        }

        # Format papers as Discord embeds if possible
        if papers:
            embeds = []
            for paper in papers[:10]: # Limit to 10 embeds per message
                authors = paper.authors[:3]
                author_str = ", ".join(authors) + ("..." if len(paper.authors) > 3 else "")
                
                embed = {
                    "title": paper.title,
                    "url": paper.abs_url,
                    "description": paper.summary[:200] + "...",
                    "fields": [
                        {"name": "Authors", "value": author_str, "inline": True},
                        {"name": "Published", "value": paper.published.strftime("%Y-%m-%d"), "inline": True}
                    ],
                    "footer": {"text": f"ID: {paper.id}"}
                }
                embeds.append(embed)
            payload["embeds"] = embeds

        try:
            response = requests.post(self.url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False

    def send_simple_message(self, text: str) -> bool:
        """Sends a simple text message."""
        if not self.url:
            return False
        try:
            response = requests.post(self.url, json={"content": text}, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send simple message: {e}")
            return False
