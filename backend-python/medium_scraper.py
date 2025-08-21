import requests
import csv
import os
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
from csv_utils import load_processed_to_dict, load_scrapped_to_dict
from nltk.corpus import stopwords
from lexicon_utils import load_lexicon
from update_barrels import add_scraped_article_to_index

# Field size limit for CSV
csv.field_size_limit(100_000_000)

def is_medium_or_freedium_url(url):
    """
    Check if the URL is a Medium or Freedium article
    Returns: 'medium', 'freedium', or None
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
        if domain == 'freedium.cfd':
            return 'freedium'
            
        return None
    except:
        return None

def check_if_already_processed(url, title, processed_articles_dict):
    """
    Check if article has already been processed based on URL or title
    Returns: True if already processed, False otherwise
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

def scrape_medium_article(url):
    """
    Scrape a Medium article and extract all relevant information
    Returns: dict with article data or None if failed
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = None
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
        content_parts = []
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
            if article:
                content_parts = [p.get_text().strip() for p in article.find_all('p') if p.get_text().strip()]
        
        text = '\\n'.join(content_parts) if content_parts else ""
        
        # Extract authors
        authors = []
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
                    author_text = elem.get('content', '').strip()
                else:
                    author_text = elem.get_text().strip()
                
                if author_text and author_text not in authors:
                    authors.append(author_text)
        
        # Extract timestamp
        timestamp = None
        time_selectors = [
            'time[datetime]',
            'span[data-testid="storyPublishDate"]',
            'meta[property="article:published_time"]'
        ]
        
        for selector in time_selectors:
            time_elem = soup.select_one(selector)
            if time_elem:
                if time_elem.name == 'meta':
                    timestamp = time_elem.get('content', '')
                elif time_elem.has_attr('datetime'):
                    timestamp = time_elem['datetime']
                else:
                    timestamp = time_elem.get_text().strip()
                break
        
        # Extract tags
        tags = []
        
        # Try meta keywords first
        meta_keywords = soup.find('meta', {'name': 'keywords'})
        if meta_keywords:
            keywords = meta_keywords.get('content', '')
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
        thumbnail = None
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
                    thumbnail = img_elem.get('content', '')
                else:
                    thumbnail = img_elem.get('src', '')
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
                description = desc_elem.get('content', '').strip()
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
        return {'error': f'Request failed: {str(e)}', 'status_code': getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0}
    except Exception as e:
        return {'error': f'Scraping failed: {str(e)}', 'status_code': 0}

def add_to_processed_dict(article_data, doc_id, processed_articles_dict):
    """
    Add article to the processed articles dictionary
    """
    processed_articles_dict[doc_id] = {
        'ID': doc_id,
        'title': article_data['title'],
        'url': article_data['url'],
        'authors': article_data['authors'],
        'timestamp': article_data['timestamp'],
        'tags': article_data['tags']
    }

def add_to_scraped_dict(article_data, doc_id, scraped_articles_dict):
    """
    Add article scraping metadata to the scraped articles dictionary
    """
    scraped_articles_dict[doc_id] = {
        'url': article_data.get('url', ''),
        'description': article_data.get('description', ''),
        'member only': 'Yes' if article_data.get('members_only', False) else 'No',
        'code': article_data.get('status_code', 0)
    }

def add_to_lengths_dict(doc_id, lengths_dict, article_length):
    lengths_dict[doc_id] = article_length

def append_to_processed_csv(article_data, doc_id, processed_file):
    """
    Append article to processed CSV file
    """
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

def append_to_scraped_csv(article_data, doc_id, scraped_file):
    """
    Append article to scraped CSV file with scraping metadata
    """
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

def update_latest_doc_id(latest_doc_id, doc_id_file):
    """
    Update the latest document ID file
    """
    
    with open(doc_id_file, 'w') as file:
        file.write(str(latest_doc_id))

def update_lengths(latest_doc_id, lengths_file, article_length):
    """
    Update the latestdocument length
    """
    with open(lengths_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['ID', 'length'])
        writer.writerow({'ID': latest_doc_id, 'length': article_length})

def scrape_and_add_article(url, processed_articles_dict, scraped_articles_dict, lengths_dict, latest_doc_id, processed_file, scraped_file, lengths_file, doc_id_file):
    """
    Main function to scrape and add an article if it's valid and not already processed
    
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'data': dict or None,
            'doc_id': int or None
        }
    """
    # Check if it's a Medium or Freedium URL
    site_type = is_medium_or_freedium_url(url)
    if not site_type:
        return {
            'success': False,
            'message': 'URL is not a Medium or Freedium article',
            'data': None,
            'doc_id': None
        }
    
    # Scrape the article
    article_data = scrape_medium_article(url)
    
    # Check for scraping errors
    if not article_data or 'error' in article_data:
        error_msg = article_data.get('error', 'Unknown scraping error') if article_data else 'Failed to scrape article'
        return {
            'success': False,
            'message': error_msg,
            'data': article_data,
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
    if check_if_already_processed(url, article_data['title'], processed_articles_dict):
        return {
            'success': False,
            'message': 'Article has already been processed',
            'data': article_data,
            'doc_id': None
        }
    
    # Increment document ID
    new_doc_id = latest_doc_id + 1
    
    # Add to processed dictionary
    add_to_processed_dict(article_data, new_doc_id, processed_articles_dict)
    add_to_scraped_dict(article_data, new_doc_id, scraped_articles_dict)
    
    # Append to CSV files
    append_to_processed_csv(article_data, new_doc_id, processed_file)
    append_to_scraped_csv(article_data, new_doc_id, scraped_file)
    
    # Update latest doc ID
    update_latest_doc_id(new_doc_id, doc_id_file)
    
    # Update latest doc length
    add_to_lengths_dict(new_doc_id, lengths_dict, len(article_data['text']))
    update_lengths(new_doc_id, lengths_file, len(article_data['text']))
    
    return {
        'success': True,
        'message': f'Successfully processed article: {article_data["title"][:50]}...',
        'data': article_data,
        'doc_id': new_doc_id
    }