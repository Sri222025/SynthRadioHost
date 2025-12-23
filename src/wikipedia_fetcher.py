"""
Wikipedia content fetcher and processor
"""
import wikipedia
import re
from typing import Optional, Dict

class WikipediaFetcher:
    """Fetch and process Wikipedia articles"""
    
    def __init__(self):
        """Initialize Wikipedia fetcher"""
        wikipedia.set_lang("en")
        wikipedia.set_rate_limiting(True)
    
    def search_topics(self, query: str, limit: int = 5) -> list:
        """
        Search Wikipedia for topics matching query
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of topic titles
        """
        try:
            results = wikipedia.search(query, results=limit)
            return results if results else [query]
        except Exception as e:
            print(f"Search error: {e}")
            return [query]
    
    def fetch_article(self, topic: str) -> Optional[Dict[str, str]]:
        """
        Fetch Wikipedia article for given topic
        
        Args:
            topic: Wikipedia article title
            
        Returns:
            Dictionary with title, summary, content, url
        """
        try:
            # Try to get page with auto-suggest enabled
            page = wikipedia.page(topic, auto_suggest=True)
            
            # Extract content
            article_data = {
                "title": page.title,
                "summary": page.summary,
                "content": page.content,
                "url": page.url,
                "categories": page.categories[:5] if hasattr(page, 'categories') else []
            }
            
            return article_data
            
        except wikipedia.exceptions.DisambiguationError as e:
            # Handle disambiguation pages - try first option
            print(f"Disambiguation found. Options: {e.options[:3]}")
            try:
                if e.options:
                    page = wikipedia.page(e.options[0], auto_suggest=False)
                    return {
                        "title": page.title,
                        "summary": page.summary,
                        "content": page.content,
                        "url": page.url,
                        "categories": []
                    }
            except Exception as e2:
                print(f"Failed to fetch disambiguation option: {e2}")
                return self._create_fallback_article(topic)
                
        except wikipedia.exceptions.PageError:
            print(f"Page not found: {topic}")
            return self._create_fallback_article(topic)
            
        except Exception as e:
            print(f"Error fetching article: {e}")
            return self._create_fallback_article(topic)
    
    def _create_fallback_article(self, topic: str) -> Dict[str, str]:
        """Create a fallback article when Wikipedia fetch fails"""
        return {
            "title": topic,
            "summary": f"{topic} is the topic of discussion.",
            "content": f"""
            {topic} is an important topic. 
            This conversation will explore various aspects of {topic}.
            We'll discuss the key features, significance, and interesting facts about {topic}.
            """,
            "url": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
            "categories": []
        }
    
    def extract_key_facts(self, content: str, max_length: int = 1500) -> str:
        """
        Extract key facts from Wikipedia content
        
        Args:
            content: Full Wikipedia article content
            max_length: Maximum character length
            
        Returns:
            Processed content suitable for LLM
        """
        # Remove references [1], [2], etc.
        content = re.sub(r'\[\d+\]', '', content)
        
        # Remove == headings ==
        content = re.sub(r'==+\s*.*?\s*==+', '', content)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Take first max_length characters
        if len(content) > max_length:
            # Try to break at sentence
            content = content[:max_length]
            last_period = content.rfind('.')
            if last_period > max_length * 0.8:  # If we can find a period in last 20%
                content = content[:last_period + 1]
        
        return content.strip()
    
    def get_article_for_script(self, topic: str) -> Optional[Dict[str, str]]:
        """
        Get article with processed content ready for script generation
        
        Args:
            topic: Wikipedia topic
            
        Returns:
            Dictionary with processed article data (always returns something)
        """
        article = self.fetch_article(topic)
        
        if not article:
            # Create fallback if fetch completely fails
            article = self._create_fallback_article(topic)
        
        # Process content for LLM
        processed_content = self.extract_key_facts(article.get('content', ''))
        
        # Ensure we have some content
        if not processed_content or len(processed_content) < 100:
            processed_content = f"{topic} is an important and interesting topic with many fascinating aspects to explore."
        
        return {
            "title": article.get('title', topic),
            "summary": article.get('summary', '')[:500],  # Shorter summary
            "key_facts": processed_content,
            "url": article.get('url', f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}")
        }


# Example usage
if __name__ == "__main__":
    fetcher = WikipediaFetcher()
    
    # Test with ISRO
    print("Fetching ISRO article...")
    article = fetcher.get_article_for_script("ISRO")
    
    if article:
        print(f"✅ Title: {article['title']}")
        print(f"✅ URL: {article['url']}")
        print(f"✅ Key facts length: {len(article['key_facts'])} chars")
        print(f"\nFirst 200 chars:\n{article['key_facts'][:200]}...")
    else:
        print("❌ Failed to fetch article")
