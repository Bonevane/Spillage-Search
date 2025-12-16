import requests  # type: ignore[import-untyped]
import csv
import os
import json
import re
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse
from datetime import datetime
from typing import Any, Optional, Dict, List, Union, Set
from classes import ArticleData

# Field size limit for CSV
csv.field_size_limit(100_000_000)

class MediumScraper:
    """
    A scraper for Medium and Freedium articles.
    
    Attributes:
        session (requests.Session): The HTTP session for making requests.
    """
    
    def __init__(self) -> None:
        """Initialize the MediumScraper with a requests session."""
        self.session = requests.Session()

    @staticmethod
    def is_medium_or_freedium_url(url: str) -> Optional[str]:
        """
        Check if the URL is a Medium or Freedium article.
        
        Args:
            url: The URL to check.
            
        Returns:
            'medium', 'freedium', or None.
        """
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc
            
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check for Medium domains
            medium_domains = [
                'medium.com',
                'towardsdatascience.com',
                'hackernoon.com',
                'levelup.gitconnected.com',
                'betterprogramming.pub',
                'javascript.plainenglish.io',
                'python.plainenglish.io'
            ]
            
            # Check if it's a Medium subdomain (like @username.medium.com)
            if domain.endswith('.medium.com') or domain == 'medium.com':
                return 'medium'
            
            # Check for other Medium publication domains
            for medium_domain in medium_domains:
                if domain == medium_domain:
                    return 'medium'
            
            # Check for Freedium
            if domain == 'freedium-mirror.cfd':
                return 'freedium'
                
            return None
        except Exception:
            return None

    def scrape_article(self, url: str) -> Optional[ArticleData]:
        """
        Scrape a Medium article and extract all relevant information.
        
        Args:
            url: The URL of the article to scrape.
            
        Returns:
            ArticleData dict with article data or None if failed.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
        
            # Use session to handle cookies/redirects better
            try:
                response = self.session.get(url, headers=headers, timeout=15)
                response.raise_for_status()
            except requests.HTTPError as e:
                if e.response.status_code == 403 and 'freedium-mirror.cfd' not in url:
                    print(f"DEBUG: 403 Forbidden on {url}. Retrying via Freedium...")
                    freedium_url = f"https://freedium-mirror.cfd/{url}"
                    response = self.session.get(freedium_url, headers=headers, timeout=15)
                    response.raise_for_status()
                else:
                    raise e
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title: Optional[str] = None
            title_selectors = [
                'h1[data-testid="storyTitle"]',
                'h1.graf--title',
                'h1',
                'title'
            ]
            
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text().strip()
                    if title and title != 'Medium':
                        break
            
            if not title:
                return None
            
            # Extract content/text
            content_parts: List[str] = []
            content_selectors = [
                'article section p',
                'div[data-testid="storyContent"] p',
                '.postArticle-content p',
                'article p',
                '.section-content p'
            ]
            
            for selector in content_selectors:
                paragraphs = soup.select(selector)
                if paragraphs:
                    content_parts = [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
                    break
            
            # If no content found, try alternative approach
            if not content_parts:
                article = soup.find('article')
                if article and isinstance(article, Tag):
                    content_parts = [p.get_text().strip() for p in article.find_all('p') if p.get_text().strip()]
            
            text = '\\n'.join(content_parts) if content_parts else ""
            
            # Extract authors
            authors: List[str] = []
            author_selectors = [
                'a[rel="author"]',
                'a[data-testid="authorName"]',
                '.author-name a',
                'meta[name="author"]',
                'span[data-testid="authorName"]'
            ]
            
            for selector in author_selectors:
                author_elems = soup.select(selector)
                for elem in author_elems:
                    if elem.name == 'meta':
                        content_attr = elem.get('content', '')
                        author_text = str(content_attr).strip() if content_attr else ''
                    else:
                        author_text = elem.get_text().strip()
                    
                    if author_text and author_text not in authors:
                        authors.append(author_text)
            
            # Extract timestamp
            timestamp: Optional[str] = None
            time_selectors = [
                'time[datetime]',
                'span[data-testid="storyPublishDate"]',
                'meta[property="article:published_time"]'
            ]
            
            for selector in time_selectors:
                time_elem = soup.select_one(selector)
                if time_elem:
                    if time_elem.name == 'meta':
                        content_attr = time_elem.get('content', '')
                        timestamp = str(content_attr) if content_attr else ''
                    elif time_elem.has_attr('datetime'):
                        timestamp = str(time_elem['datetime'])
                    else:
                        timestamp = time_elem.get_text().strip()
                    break
            
            # Extract tags
            tags: List[str] = []
            
            # Try meta keywords first
            meta_keywords = soup.find('meta', {'name': 'keywords'})
            if meta_keywords and isinstance(meta_keywords, Tag):
                keywords_attr = meta_keywords.get('content', '')
                keywords = str(keywords_attr) if keywords_attr else ''
                tags.extend([tag.strip() for tag in keywords.split(',') if tag.strip()])
            
            # Try tag links
            tag_selectors = [
                'a[href*="/tag/"]',
                '.tags a',
                'a[data-testid="tag"]'
            ]
            
            for selector in tag_selectors:
                tag_elems = soup.select(selector)
                for elem in tag_elems:
                    tag_text = elem.get_text().strip()
                    if tag_text and tag_text not in tags:
                        tags.append(tag_text)
            
            # Extract thumbnail/image
            thumbnail: Optional[str] = None
            img_selectors = [
                'meta[property="og:image"]',
                'meta[name="twitter:image"]',
                'article img',
                'figure img'
            ]
            
            for selector in img_selectors:
                img_elem = soup.select_one(selector)
                if img_elem:
                    if img_elem.name == 'meta':
                        content_attr = img_elem.get('content', '')
                        thumbnail = str(content_attr) if content_attr else ''
                    else:
                        src_attr = img_elem.get('src', '')
                        thumbnail = str(src_attr) if src_attr else ''
                    if thumbnail:
                        break
            
            # Extract description
            description = ""
            desc_selectors = [
                'meta[property="og:description"]',
                'meta[name="description"]',
                'meta[name="twitter:description"]'
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    content_attr = desc_elem.get('content', '')
                    description = str(content_attr).strip() if content_attr else ''
                    if description:
                        break
            
            # Check if members only
            members_only = False
            
            # Look for member paywall indicators
            paywall_indicators = [
                '.paywall',
                '[data-testid="paywall"]',
                'div:contains("Member-only")',
                'div:contains("This story is published in")',
                '.meteredContent'
            ]
            
            for indicator in paywall_indicators:
                if soup.select(indicator):
                    members_only = True
                    break
            
            # Check for "Member" text in various places
            if not members_only:
                body_text = soup.get_text().lower()
                if 'member-only story' in body_text or 'members only' in body_text:
                    members_only = True
            
            return {
                'title': title,
                'text': text,
                'url': url,
                'authors': authors,
                'timestamp': timestamp,
                'tags': tags,
                'thumbnail': thumbnail,
                'description': description,
                'members_only': members_only,
                'status_code': response.status_code
            }
            
        except requests.RequestException as e:
            # Log error or handle it
            print(f"Request failed: {str(e)}")
            return None
        except Exception as e:
            print(f"Scraping failed: {str(e)}")
            return None

class ArticleProcessor:
    """
    Handles the processing and storage of scraped articles.
    """
    
    @staticmethod
    def check_if_already_processed(url: str, title: Optional[str], processed_articles_dict: Dict[int, Dict[str, Any]]) -> bool:
        """
        Check if article has already been processed based on URL or title.
        """
        # Check by URL first (most reliable)
        for article in processed_articles_dict.values():
            if article.get('url') == url:
                return True
        
        # Check by title as backup (in case URL format changed)
        if title:
            title_lower = title.lower().strip()
            for article in processed_articles_dict.values():
                if article.get('title', '').lower().strip() == title_lower:
                    return True
        
        return False

    @staticmethod
    def add_to_processed_dict(article_data: ArticleData, doc_id: int, processed_articles_dict: Dict[int, Dict[str, Any]]) -> None:
        """Add article to the processed articles dictionary."""
        processed_articles_dict[doc_id] = {
            'ID': doc_id,
            'title': article_data['title'],
            'url': article_data['url'],
            'authors': article_data['authors'],
            'timestamp': article_data['timestamp'],
            'tags': article_data['tags']
        }

    @staticmethod
    def add_to_scraped_dict(article_data: ArticleData, doc_id: int, scraped_articles_dict: Dict[int, Dict[str, Any]]) -> None:
        """Add article scraping metadata to the scraped articles dictionary."""
        scraped_articles_dict[doc_id] = {
            'url': article_data.get('url', ''),
            'description': article_data.get('description', ''),
            'member only': 'Yes' if article_data.get('members_only', False) else 'No',
            'code': article_data.get('status_code', 0)
        }

    @staticmethod
    def add_to_lengths_dict(doc_id: int, lengths_dict: Dict[int, int], article_length: int) -> None:
        lengths_dict[doc_id] = article_length

    @staticmethod
    def append_to_processed_csv(article_data: ArticleData, doc_id: int, processed_file: str) -> None:
        """Append article to processed CSV file."""
        os.makedirs("indexes", exist_ok=True)
        
        # Prepare row data
        new_entry = [
            doc_id,
            article_data['title'],
            article_data['url'],
            json.dumps(article_data['authors']) if article_data['authors'] else '[]',
            article_data['timestamp'] or '',
            json.dumps(article_data['tags']) if article_data['tags'] else '[]'
        ]
        
        # Check if file exists and write header if needed
        file_exists = os.path.exists(processed_file) and os.path.getsize(processed_file) > 0
        
        with open(processed_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['ID', 'title', 'url', 'authors', 'timestamp', 'tags'])
            writer.writerow(new_entry)

    @staticmethod
    def append_to_scraped_csv(article_data: ArticleData, doc_id: int, scraped_file: str) -> None:
        """Append article to scraped CSV file with scraping metadata."""
        os.makedirs("indexes", exist_ok=True)
        
        # Prepare row data
        status_code = article_data.get('status_code', 0)
        description = article_data.get('description', '')
        members_only = article_data.get('members_only', False)
        
        new_entry = [
            doc_id,
            article_data['thumbnail'],
            description,
            'Yes' if members_only else 'No',
            status_code
        ]
        
        # Check if file exists and write header if needed
        file_exists = os.path.exists(scraped_file) and os.path.getsize(scraped_file) > 0
        
        with open(scraped_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['ID', 'URL', 'Description', 'Member Only', 'Code'])
            writer.writerow(new_entry)

    @staticmethod
    def update_latest_doc_id(latest_doc_id: int, doc_id_file: str) -> None:
        """Update the latest document ID file."""
        with open(doc_id_file, 'w') as file:
            file.write(str(latest_doc_id))

    @staticmethod
    def update_lengths(latest_doc_id: int, lengths_file: str, article_length: int) -> None:
        """Update the latest document length."""
        with open(lengths_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['ID', 'length'])
            writer.writerow({'ID': latest_doc_id, 'length': article_length})

def scrape_and_add_article(
    url: str, 
    processed_articles_dict: Dict[int, Dict[str, Any]], 
    scraped_articles_dict: Dict[int, Dict[str, Any]], 
    lengths_dict: Dict[int, int], 
    latest_doc_id: int, 
    processed_file: str, 
    scraped_file: str, 
    lengths_file: str, 
    doc_id_file: str
) -> Dict[str, Any]:
    """
    Main function to scrape and add an article if it's valid and not already processed.
    Uses MediumScraper and ArticleProcessor.
    """
    scraper = MediumScraper()
    processor = ArticleProcessor()
    
    # Check if it's a Medium or Freedium URL
    site_type = scraper.is_medium_or_freedium_url(url)
    if not site_type:
        return {
            'success': False,
            'message': 'URL is not a Medium or Freedium article',
            'data': None,
            'doc_id': None
        }
    
    # Scrape the article
    article_data = scraper.scrape_article(url)
    
    # Check for scraping errors
    if not article_data:
        return {
            'success': False,
            'message': 'Failed to scrape article',
            'data': None,
            'doc_id': None
        }
    
    # Check if article was successfully scraped
    if not article_data.get('title') or not article_data.get('text'):
        return {
            'success': False,
            'message': 'Could not extract title or content from article',
            'data': article_data,
            'doc_id': None
        }
    
    # Check if already processed
    if processor.check_if_already_processed(url, article_data['title'], processed_articles_dict):
        return {
            'success': False,
            'message': 'Article has already been processed',
            'data': article_data,
            'doc_id': None
        }
    
    # Increment document ID
    new_doc_id = latest_doc_id + 1
    
    # Add to processed dictionary
    processor.add_to_processed_dict(article_data, new_doc_id, processed_articles_dict)
    processor.add_to_scraped_dict(article_data, new_doc_id, scraped_articles_dict)
    
    # Append to CSV files
    processor.append_to_processed_csv(article_data, new_doc_id, processed_file)
    processor.append_to_scraped_csv(article_data, new_doc_id, scraped_file)
    
    # Update latest doc ID
    processor.update_latest_doc_id(new_doc_id, doc_id_file)
    
    # Update latest doc length
    processor.add_to_lengths_dict(new_doc_id, lengths_dict, len(article_data['text']))
    processor.update_lengths(new_doc_id, lengths_file, len(article_data['text']))
    
    return {
        'success': True,
        'message': f'Successfully processed article: {article_data["title"][:50]}...',
        'data': article_data,
        'doc_id': new_doc_id
    }
