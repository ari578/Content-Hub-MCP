"""
Content scraper for RoomPriceGenie website.
Fetches pages from urls.json, extracts main article content,
and saves as structured JSON files in the content/ directory.
"""

import json
import os
import re
import sys
import time
import hashlib
import asyncio
from pathlib import Path
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup, Comment

# Directories
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
CONTENT_DIR = PROJECT_DIR / "content"
URLS_FILE = SCRIPT_DIR / "urls.json"

# Rate limiting
REQUEST_DELAY = 1.0  # seconds between requests
TIMEOUT = 30.0


def clean_text(text: str) -> str:
    """Clean extracted text: normalize whitespace, remove junk."""
    # Remove zero-width characters
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace per line
    lines = [line.strip() for line in text.split('\n')]
    # Remove empty lines (but keep paragraph breaks)
    cleaned_lines = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                cleaned_lines.append('')
                prev_empty = True
        else:
            cleaned_lines.append(line)
            prev_empty = False
    return '\n'.join(cleaned_lines).strip()


def extract_article_content(html: str, url: str) -> dict:
    """Extract structured content from an HTML page."""
    soup = BeautifulSoup(html, 'html.parser')

    # Remove unwanted elements
    for tag in soup.find_all(['script', 'style', 'noscript', 'iframe', 'svg']):
        tag.decompose()

    # Remove HTML comments
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    # Remove cookie banners, nav, footer, popups
    selectors_to_remove = [
        'nav', 'footer', 'header',
        '.cookie', '.cookies', '#cookie', '#cookies',
        '.consent', '#consent',
        '.popup', '.modal',
        '.sidebar', '.widget',
        '[class*="cookie"]', '[class*="consent"]', '[class*="popup"]',
        '[class*="banner"]', '[id*="cookie"]', '[id*="consent"]',
        '.wpml-ls-statics-footer',
        '.elementor-location-footer',
        '.elementor-location-header',
        '[data-elementor-type="header"]',
        '[data-elementor-type="footer"]',
        '.language-switcher',
        '#wt-cli-cookie-banner',
    ]
    for selector in selectors_to_remove:
        for el in soup.select(selector):
            el.decompose()

    # Extract title
    title = ''
    # Try og:title first
    og_title = soup.find('meta', property='og:title')
    if og_title and og_title.get('content'):
        title = og_title['content'].strip()
    # Fall back to h1
    if not title:
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)
    # Fall back to <title>
    if not title:
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

    # Clean title - remove site name suffix
    title = re.sub(r'\s*\|\s*RoomPriceGenie\s*$', '', title)
    title = re.sub(r'\s*-\s*RoomPriceGenie\s*$', '', title)

    # Extract meta description
    description = ''
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        description = meta_desc['content'].strip()
    if not description:
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            description = og_desc['content'].strip()

    # Extract main content
    # Try common content containers
    content_el = None
    content_selectors = [
        'article',
        '.entry-content',
        '.post-content',
        '.article-content',
        '.elementor-widget-theme-post-content',
        'main .elementor-section',
        'main',
        '#content',
        '.page-content',
    ]
    for selector in content_selectors:
        content_el = soup.select_one(selector)
        if content_el:
            break

    if not content_el:
        content_el = soup.find('body')

    # Extract text content preserving some structure
    paragraphs = []
    if content_el:
        for el in content_el.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote', 'td']):
            text = el.get_text(strip=True)
            if not text or len(text) < 3:
                continue
            # Skip navigation-like text
            if text in ['Learn more', 'Read more', 'Read story', 'View more posts',
                        'Start Free Trial', 'Watch Demo', 'Book a meeting',
                        'Start free trial', 'Login', 'Sign up now',
                        'Cookie Settings', 'Reject', 'Accept All',
                        'Close and do not switch language', 'Change Language']:
                continue
            # Skip very short repetitive CTA text
            if len(text) < 10 and any(kw in text.lower() for kw in ['cookie', 'accept', 'reject', 'close']):
                continue

            tag_name = el.name
            if tag_name.startswith('h'):
                paragraphs.append(f"\n## {text}\n")
            elif tag_name == 'li':
                paragraphs.append(f"- {text}")
            elif tag_name == 'blockquote':
                paragraphs.append(f'> "{text}"')
            else:
                paragraphs.append(text)

    full_text = clean_text('\n'.join(paragraphs))

    # Remove the "Start your 14-day free trial" boilerplate at the end
    boilerplate_markers = [
        "Start your14-day free trial",
        "Start your 14-day free trial",
        "No credit card required. No obligation.",
        "We've detected you might be speaking a different language",
        "We andour {{count}} partners",
        "Privacy & Cookies Policy",
    ]
    for marker in boilerplate_markers:
        idx = full_text.find(marker)
        if idx > 0:
            full_text = full_text[:idx].strip()

    return {
        'title': title,
        'url': url,
        'description': description,
        'content': full_text,
    }


def chunk_content(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split content into overlapping word-based chunks."""
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start = end - overlap
        if start >= len(words):
            break

    return chunks


def url_to_filename(url: str) -> str:
    """Convert a URL to a safe filename."""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    # Use last path segment as base
    segments = path.split('/')
    name = segments[-1] if segments[-1] else segments[-2] if len(segments) > 1 else 'index'
    # Clean the name
    name = re.sub(r'[^a-zA-Z0-9_-]', '-', name)
    name = re.sub(r'-+', '-', name).strip('-')
    # Ensure uniqueness with a short hash
    url_hash = hashlib.md5(url.encode()).hexdigest()[:6]
    return f"{name}_{url_hash}"


async def fetch_page(client: httpx.AsyncClient, url: str) -> str | None:
    """Fetch a single page with error handling."""
    try:
        response = await client.get(url, follow_redirects=True, timeout=TIMEOUT)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  ERROR fetching {url}: {e}")
        return None


async def scrape_category(client: httpx.AsyncClient, urls: list[str],
                          category: str, output_dir: Path):
    """Scrape all URLs in a category and save as JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    total = len(urls)
    success = 0
    errors = 0

    for i, url in enumerate(urls, 1):
        # Skip already scraped URLs
        filename = url_to_filename(url)
        output_path = output_dir / f"{filename}.json"
        if output_path.exists():
            print(f"  [{i}/{total}] SKIP (already scraped): {url}")
            success += 1
            continue

        print(f"  [{i}/{total}] {url}")

        html = await fetch_page(client, url)
        if not html:
            errors += 1
            continue

        data = extract_article_content(html, url)
        data['category'] = category

        # Generate chunks
        if data['content']:
            data['chunks'] = chunk_content(data['content'])
        else:
            data['chunks'] = []
            print(f"    WARNING: No content extracted from {url}")

        # Generate filename and save
        filename = url_to_filename(url)
        output_path = output_dir / f"{filename}.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        success += 1
        content_words = len(data['content'].split()) if data['content'] else 0
        safe_title = data['title'][:60].encode('ascii', 'replace').decode('ascii')
        print(f"    OK: \"{safe_title}\" ({content_words} words, {len(data['chunks'])} chunks)")

        # Rate limiting
        await asyncio.sleep(REQUEST_DELAY)

    return success, errors


async def main():
    """Main scraper entry point."""
    print("=" * 60)
    print("RoomPriceGenie Content Scraper")
    print("=" * 60)

    # Load URLs
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        url_data = json.load(f)

    category_dirs = {
        'articles': CONTENT_DIR / 'articles',
        'glossary': CONTENT_DIR / 'glossary',
        'case_studies': CONTENT_DIR / 'case-studies',
        'guides': CONTENT_DIR / 'guides',
        'pages': CONTENT_DIR / 'pages',
    }

    total_success = 0
    total_errors = 0

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    async with httpx.AsyncClient(headers=headers) as client:
        for category, urls in url_data.items():
            output_dir = category_dirs.get(category, CONTENT_DIR / category)
            print(f"\n--- Scraping {category} ({len(urls)} URLs) ---")
            success, errors = await scrape_category(client, urls, category, output_dir)
            total_success += success
            total_errors += errors
            print(f"  {category}: {success} success, {errors} errors")

    print(f"\n{'=' * 60}")
    print(f"DONE: {total_success} pages scraped, {total_errors} errors")
    print(f"Content saved to: {CONTENT_DIR}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    asyncio.run(main())
