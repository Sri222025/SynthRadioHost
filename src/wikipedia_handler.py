"""
Wikipedia API Handler
Searches and fetches Wikipedia article content
"""

import requests
from typing import List, Dict, Optional
import re

class WikipediaHandler:
    """Handler for Wikipedia API interactions"""
    
    def __init__(self):
        """Initialize Wikipedia handler"""
        self.base_url = "https://en.wikipedia.org/api/rest_v1"
        self.headers = {
            "User-Agent": "SynthRadioHost/1.0 (Educational Podcast Generator)"
        }
    
    def search_topics(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search Wikipedia for topics
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of dicts with title, description, url
        """
        try:
            # Use MediaWiki API for search
            search_url = "https://en.wikipedia.org/w/api.php"
            
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srlimit": limit,
                "srprop": "snippet"
            }
            
            response = requests.get(
                search_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            
            results = []
            for item in data.get("query", {}).get("search", []):
                # Clean HTML tags from snippet
                snippet = re.sub(r'<.*?>', '', item.get("snippet", ""))
                
                results.append({
                    "title": item.get("title", ""),
                    "description": snippet,
                    "url": f"https://en.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}"
                })
            
            return results
        
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_article_content(self, title: str, max_chars: int = 5000) -> str:
        """
        Get article content as plain text
        
        Args:
            title: Article title
            max_chars: Maximum characters to return
            
        Returns:
            Plain text content (string)
        """
        try:
            # Use REST API for content
            url = f"{self.base_url}/page/summary/{title.replace(' ', '_')}"
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract text content
                content = data.get('extract', '')
                
                # Limit to max_chars
                if len(content) > max_chars:
                    content = content[:max_chars] + "..."
                
                # Return as string
                return content
            else:
                return ""
        
        except Exception as e:
            print(f"Error fetching article: {e}")
            return ""

# Test function
if __name__ == "__main__":
    handler = WikipediaHandler()
    
    # Test search
    print("Testing search...")
    results = handler.search_topics("ISRO", limit=5)
    print(f"Found {len(results)} results")
    
    if results:
        print(f"\nFirst result: {results[0]['title']}")
        
        # Test content fetch
        print("\nTesting content fetch...")
        content = handler.get_article_content(results[0]['title'])
        print(f"Content length: {len(content)} chars")
        print(f"Content type: {type(content)}")
        print(f"First 200 chars: {content[:200]}")
