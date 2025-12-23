# src/wikipedia_handler.py
"""
Wikipedia API Handler - Using Wikimedia REST API
Searches and fetches Wikipedia articles
"""

import requests
from typing import List, Dict, Optional
import json

class WikipediaHandler:
    """Handle Wikipedia API interactions using Wikimedia REST API"""
    
    def __init__(self, language_code: str = 'en'):
        """
        Initialize Wikipedia handler
        
        Args:
            language_code: Language code (e.g., 'en', 'es', 'fr')
        """
        self.language_code = language_code
        self.base_url = f'https://api.wikimedia.org/core/v1/wikipedia/{language_code}'
        self.old_api_url = f'https://{language_code}.wikipedia.org/w/api.php'
        
        # User-Agent is REQUIRED by Wikipedia API
        self.headers = {
            'User-Agent': 'SynthRadioHost/1.0 (Hackathon Project; Educational Purpose)'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search_topics(self, keyword: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Search Wikipedia for topics related to keyword
        
        Args:
            keyword: Search term
            limit: Maximum number of results (default: 10)
            
        Returns:
            List of dicts with 'title', 'snippet', 'description', 'thumbnail'
        """
        try:
            # Use Wikimedia REST API search endpoint
            endpoint = '/search/page'
            url = self.base_url + endpoint
            
            params = {
                'q': keyword,
                'limit': limit
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            
            for page in data.get('pages', []):
                # Clean excerpt (remove HTML tags)
                excerpt = page.get('excerpt', '')
                excerpt = excerpt.replace('<span class="searchmatch">', '').replace('</span>', '')
                excerpt = excerpt.replace('&quot;', '"').replace('&#039;', "'")
                excerpt = excerpt.replace('<b>', '').replace('</b>', '')
                
                # Get thumbnail URL
                thumbnail = None
                if page.get('thumbnail'):
                    thumbnail = page['thumbnail'].get('url', '')
                    if thumbnail and not thumbnail.startswith('http'):
                        thumbnail = 'https:' + thumbnail
                
                results.append({
                    'title': page.get('title', ''),
                    'snippet': excerpt[:300] + '...' if len(excerpt) > 300 else excerpt,
                    'description': page.get('description', 'No description available'),
                    'key': page.get('key', ''),
                    'thumbnail': thumbnail
                })
            
            return results
        
        except requests.exceptions.RequestException as e:
            print(f"Wikipedia REST API search error: {e}")
            # Fallback to old API
            return self._search_topics_fallback(keyword, limit)
        
        except Exception as e:
            print(f"Wikipedia search error: {e}")
            return []
    
    def _search_topics_fallback(self, keyword: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Fallback search using old MediaWiki API
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
            
            response = self.session.get(self.old_api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('query', {}).get('search', []):
                snippet = item.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', '')
                snippet = snippet.replace('&quot;', '"').replace('&#039;', "'")
                
                results.append({
                    'title': item.get('title', ''),
                    'snippet': snippet,
                    'description': snippet[:100] + '...' if len(snippet) > 100 else snippet,
                    'key': item.get('title', '').replace(' ', '_'),
                    'thumbnail': None
                })
            
            return results
        
        except Exception as e:
            print(f"Fallback search error: {e}")
            return []
    
    def get_article_content(self, title: str, max_chars: int = 5000) -> Dict[str, str]:
        """
        Fetch article content and summary
        
        Args:
            title: Wikipedia article title
            max_chars: Maximum characters to fetch (default: 5000)
            
        Returns:
            Dict with 'title', 'summary', 'url', 'full_text', 'extract'
        """
        try:
            # Get page content using old API (more reliable for full text)
            params = {
                'action': 'query',
                'prop': 'extracts|info',
                'exintro': False,  # Get full article, not just intro
                'explaintext': True,
                'inprop': 'url',
                'titles': title,
                'format': 'json',
                'utf8': 1
            }
            
            response = self.session.get(self.old_api_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            page = list(pages.values())[0]
            
            # Check if page exists
            if 'missing' in page:
                return {
                    'title': title,
                    'summary': 'Article not found',
                    'url': '',
                    'full_text': '',
                    'extract': ''
                }
            
            full_text = page.get('extract', '')
            
            # Create summary (first 500 chars)
            summary = full_text[:500] + '...' if len(full_text) > 500 else full_text
            
            # Limit full text to max_chars
            if len(full_text) > max_chars:
                full_text = full_text[:max_chars] + '...'
            
            article_url = page.get('fullurl', f'https://{self.language_code}.wikipedia.org/wiki/{title.replace(" ", "_")}')
            
            return {
                'title': page.get('title', title),
                'summary': summary,
                'url': article_url,
                'full_text': full_text,
                'extract': full_text,
                'pageid': page.get('pageid', 0)
            }
        
        except Exception as e:
            print(f"Wikipedia fetch error: {e}")
            return {
                'title': title,
                'summary': f"Error fetching content: {e}",
                'url': '',
                'full_text': f"Unable to fetch article content. Error: {e}",
                'extract': '',
                'pageid': 0
            }
    
    def test_connection(self) -> Dict[str, any]:
        """Test Wikipedia API connection"""
        try:
            # Test REST API
            url = self.base_url + '/search/page'
            params = {'q': 'test', 'limit': 1}
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'api': 'Wikimedia REST API',
                    'message': 'Connection successful'
                }
            else:
                raise Exception(f"Status code: {response.status_code}")
        
        except Exception as e:
            # Try fallback API
            try:
                params = {
                    'action': 'query',
                    'meta': 'siteinfo',
                    'format': 'json'
                }
                response = self.session.get(self.old_api_url, params=params, timeout=5)
                
                if response.status_code == 200:
                    return {
                        'success': True,
                        'api': 'MediaWiki API (fallback)',
                        'message': 'Connection successful'
                    }
            except:
                pass
            
            return {
                'success': False,
                'api': 'None',
                'message': f'Connection failed: {e}'
            }


# Test function
if __name__ == "__main__":
    print("Testing Wikipedia Handler...")
    print("=" * 60)
    
    wiki = WikipediaHandler()
    
    # Test connection
    print("\n1. Testing connection...")
    result = wiki.test_connection()
    print(f"   Status: {'✅' if result['success'] else '❌'} {result['message']}")
    print(f"   API: {result['api']}")
    
    # Test search
    print("\n2. Testing search for 'Artificial Intelligence'...")
    results = wiki.search_topics("Artificial Intelligence", limit=5)
    
    if results:
        print(f"   ✅ Found {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"\n   {i}. {result['title']}")
            print(f"      Description: {result['description']}")
            print(f"      Snippet: {result['snippet'][:100]}...")
    else:
        print("   ❌ No results found")
    
    # Test fetch article
    if results:
        print(f"\n3. Testing fetch article: '{results[0]['title']}'...")
        content = wiki.get_article_content(results[0]['title'])
        print(f"   Title: {content['title']}")
        print(f"   URL: {content['url']}")
        print(f"   Summary length: {len(content['summary'])} chars")
        print(f"   Full text length: {len(content['full_text'])} chars")
        print(f"\n   First 200 chars of summary:")
        print(f"   {content['summary'][:200]}...")
    
    print("\n" + "=" * 60)
    print("✅ Testing complete!")
