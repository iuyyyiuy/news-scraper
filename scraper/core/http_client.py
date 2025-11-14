"""
HTTP client for fetching web pages with retry logic and rate limiting.
"""
import time
import logging
from typing import Optional
import requests
from requests import Response, RequestException


logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP client with retry logic and rate limiting."""
    
    def __init__(self, timeout: int = 30, request_delay: float = 2.0, max_retries: int = 3):
        """
        Initialize HTTP client.
        
        Args:
            timeout: Request timeout in seconds
            request_delay: Delay between requests in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.request_delay = request_delay
        self.max_retries = max_retries
        self.last_request_time: Optional[float] = None
        
        # Set up session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; NewsScraperBot/1.0; +https://github.com/scraper)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def fetch(self, url: str) -> Response:
        """
        Fetch a URL with timeout and proper headers.
        
        Args:
            url: URL to fetch
            
        Returns:
            Response object
            
        Raises:
            RequestException: If the request fails
        """
        # Apply rate limiting
        self._apply_rate_limit()
        
        logger.info(f"Fetching URL: {url}")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Update last request time
            self.last_request_time = time.time()
            
            logger.info(f"Successfully fetched {url} (status: {response.status_code})")
            return response
            
        except RequestException as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            raise
    
    def fetch_with_retry(self, url: str, max_retries: Optional[int] = None) -> Response:
        """
        Fetch a URL with exponential backoff retry logic.
        
        Args:
            url: URL to fetch
            max_retries: Maximum number of retry attempts (uses instance default if None)
            
        Returns:
            Response object
            
        Raises:
            RequestException: If all retry attempts fail
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return self.fetch(url)
                
            except RequestException as e:
                last_exception = e
                
                if attempt < max_retries:
                    # Calculate exponential backoff delay
                    backoff_delay = 2 ** attempt
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed for {url}. "
                        f"Retrying in {backoff_delay} seconds..."
                    )
                    time.sleep(backoff_delay)
                else:
                    logger.error(
                        f"All {max_retries + 1} attempts failed for {url}"
                    )
        
        # If we get here, all retries failed
        raise last_exception
    
    def _apply_rate_limit(self) -> None:
        """
        Apply rate limiting by waiting if necessary.
        
        Ensures minimum delay between requests.
        """
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.request_delay:
                sleep_time = self.request_delay - elapsed
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
    
    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
