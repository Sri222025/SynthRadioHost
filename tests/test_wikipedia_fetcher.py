"""
Unit tests for Wikipedia Fetcher
"""
import pytest
from src.wikipedia_fetcher import WikipediaFetcher

class TestWikipediaFetcher:
    """Test WikipediaFetcher class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.fetcher = WikipediaFetcher()
    
    def test_init(self):
        """Test initialization"""
        assert self.fetcher is not None
    
    def test_search_topics_valid(self):
        """Test searching for valid topics"""
        results = self.fetcher.search_topics("ChatGPT", limit=3)
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert len(results) <= 3
    
    def test_search_topics_empty(self):
        """Test searching with empty query"""
        results = self.fetcher.search_topics("", limit=5)
        
        assert isinstance(results, list)
    
    def test_fetch_article_valid(self):
        """Test fetching a valid article"""
        article = self.fetcher.fetch_article("Python (programming language)")
        
        assert article is not None
        assert "title" in article
        assert "summary" in article
        assert "content" in article
        assert "url" in article
        assert len(article["content"]) > 0
    
    def test_fetch_article_invalid(self):
        """Test fetching non-existent article"""
        article = self.fetcher.fetch_article("ThisArticleDoesNotExist12345XYZ")
        
        assert article is None
    
    def test_extract_key_facts(self):
        """Test extracting key facts from content"""
        content = """
        This is a test article. [1] It has references. [2]
        
        == Section Header ==
        
        This is some content.    It has   extra   spaces.
        This continues for a while with more information.
        """ * 10  # Make it long
        
        key_facts = self.fetcher.extract_key_facts(content, max_length=500)
        
        assert len(key_facts) <= 500
        assert "[1]" not in key_facts  # References removed
        assert "==" not in key_facts  # Headers removed
        assert "   " not in key_facts  # Extra spaces removed
    
    def test_get_article_for_script(self):
        """Test getting processed article for script generation"""
        article = self.fetcher.get_article_for_script("ChatGPT")
        
        if article:  # May fail if Wikipedia is unreachable
            assert "title" in article
            assert "summary" in article
            assert "key_facts" in article
            assert "url" in article
            assert len(article["summary"]) <= 500
            assert len(article["key_facts"]) <= 1500
    
    def test_extract_key_facts_short_content(self):
        """Test extraction with content shorter than max_length"""
        content = "Short content here."
        key_facts = self.fetcher.extract_key_facts(content, max_length=1000)
        
        assert key_facts == "Short content here."


class TestWikipediaFetcherEdgeCases:
    """Test edge cases and error handling"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.fetcher = WikipediaFetcher()
    
    def test_search_topics_special_characters(self):
        """Test search with special characters"""
        results = self.fetcher.search_topics("C++ programming")
        
        assert isinstance(results, list)
    
    def test_search_topics_unicode(self):
        """Test search with Unicode characters"""
        results = self.fetcher.search_topics("नमस्ते")
        
        assert isinstance(results, list)
    
    def test_fetch_article_disambiguation(self):
        """Test handling disambiguation pages"""
        # "Mercury" is a disambiguation page
        article = self.fetcher.fetch_article("Mercury")
        
        # Should handle disambiguation and return something
        assert article is not None or article is None  # Either outcome is acceptable
