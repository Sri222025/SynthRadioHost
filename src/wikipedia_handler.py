# src/wikipedia_handler.py
"""
Wikipedia API Handler
Searches and fetches Wikipedia articles
"""

import requests
from typing import List, Dict, Optional
import json

class WikipediaHandler:
    """Handle Wikipedia API interactions"""
    
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/w/api.php"
        self.session = requests.Session()
    
    def search_topics(self, keyword: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Search Wikipedia for topics related to keyword
        
        Args:
            keyword: Search term
            limit: Maximum number of results
            
        Returns:
            List of dicts with 'title', 'snippet', 'pageid'
        """
        try:
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': keyword,
                'srlimit': limit,
                'srprop': 'snippet',
                'format': 'json',
                'utf8': 1
            }
            
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('query', {}).get('search', []):
                # Clean HTML tags from snippet
                snippet = item.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', '')
                snippet = snippet.replace('&quot;', '"').replace('&#039;', "'")
                
                results.append({
                    'title': item.get('title', ''),
                    'snippet': snippet,
                    'pageid': item.get('pageid', 0)
                })
            
            return results
        
        except Exception as e:
            print(f"Wikipedia search error: {e}")
            return []
    
    def get_article_content(self, title: str, sentences: int = 10) -> Dict[str, str]:
        """
        Fetch article content and summary
        
        Args:
            title: Wikipedia article title
            sentences: Number of sentences for summary
            
        Returns:
            Dict with 'title', 'summary', 'url', 'full_text'
        """
        try:
            # Get extract (summary)
            params = {
                'action': 'query',
                'prop': 'extracts|info',
                'exsentences': sentences,
                'exintro': True,
                'explaintext': True,
                'inprop': 'url',
                'titles': title,
                'format': 'json',
                'utf8': 1
            }
            
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            page = list(pages.values())[0]
            
            # Get full content for longer podcasts
            full_params = {
                'action': 'query',
                'prop': 'extracts',
                'explaintext': True,
                'titles': title,
                'format': 'json',
                'utf8': 1
            }
            
            full_response = self.session.get(self.base_url, params=full_params)
            full_data = full_response.json()
            full_pages = full_data.get('query', {}).get('pages', {})
            full_page = list(full_pages.values())[0]
            
            return {
                'title': page.get('title', title),
                'summary': page.get('extract', ''),
                'url': page.get('fullurl', ''),
                'full_text': full_page.get('extract', ''),
                'pageid': page.get('pageid', 0)
            }
        
        except Exception as e:
            print(f"Wikipedia fetch error: {e}")
            return {
                'title': title,
                'summary': f"Error fetching content: {e}",
                'url': '',
                'full_text': '',
                'pageid': 0
            }
    
    def test_connection(self) -> bool:
        """Test Wikipedia API connection"""
        try:
            params = {
                'action': 'query',
                'meta': 'siteinfo',
                'format': 'json'
            }
            response = self.session.get(self.base_url, params=params, timeout=5)
            return response.status_code == 200
        except:
            return False


# Test function
if __name__ == "__main__":
    wiki = WikipediaHandler()
    
    print("Testing Wikipedia API...")
    print(f"Connection: {'✅ OK' if wiki.test_connection() else '❌ Failed'}")
    
    print("\nSearching for 'Artificial Intelligence'...")
    results = wiki.search_topics("Artificial Intelligence", limit=5)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   {result['snippet'][:100]}...")
    
    if results:
        print(f"\nFetching article: {results[0]['title']}")
        content = wiki.get_article_content(results[0]['title'])
        print(f"Summary: {content['summary'][:200]}...")
