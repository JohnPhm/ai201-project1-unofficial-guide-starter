import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import re

LINKS_FILE = "links.txt"
OUTPUT_FILE = "scraped_results.txt"

def parse_links(filepath):
    links = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split(" ", 1)
                url = parts[1].strip() if len(parts) == 2 else parts[0].strip()
                links.append(url)
    return links

def fetch(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser"), None
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP error: {e}"
    except requests.exceptions.ConnectionError:
        return None, "Connection failed — site may be blocking scrapers or unreachable."
    except requests.exceptions.Timeout:
        return None, "Request timed out."
    except Exception as e:
        return None, f"Unexpected error: {e}"

# ── Formatters ────────────────────────────────────────────────

def format_reddit(soup):
    """Extract post title and top-level comments from a Reddit thread."""
    lines = []

    title_tag = soup.find("h1")
    if title_tag:
        lines.append(f"THREAD: {title_tag.get_text(strip=True)}\n")

    # Reddit comment text sits in <p> tags inside shreddit-comment elements
    comments = soup.find_all("p")
    seen = set()
    count = 0
    for p in comments:
        text = p.get_text(strip=True)
        if text and len(text) > 30 and text not in seen:
            seen.add(text)
            lines.append(f"  • {text}")
            count += 1
            if count >= 30:
                break

    if not lines:
        lines.append("  (Reddit may require login or JavaScript to load comments.)")
    return lines

def format_dine_on_campus(soup):
    """Extract menu items and categories from DineOnCampus pages."""
    lines = []

    title = soup.find("h1") or soup.find("h2")
    if title:
        lines.append(f"MENU: {title.get_text(strip=True)}\n")

    # Station/category headings
    stations = soup.find_all(["h2", "h3", "h4"])
    seen_stations = set()
    for station in stations:
        name = station.get_text(strip=True)
        if name and name not in seen_stations and len(name) > 2:
            seen_stations.add(name)
            lines.append(f"\n  [ {name} ]")
            # Grab list items or paragraphs following the station heading
            sibling = station.find_next_sibling()
            while sibling and sibling.name not in ("h2", "h3", "h4"):
                if sibling.name in ("ul", "ol"):
                    for li in sibling.find_all("li"):
                        item = li.get_text(strip=True)
                        if item:
                            lines.append(f"    - {item}")
                elif sibling.name == "p":
                    text = sibling.get_text(strip=True)
                    if text:
                        lines.append(f"    {text}")
                sibling = sibling.find_next_sibling()

    if len(lines) <= 1:
        lines.append("  (Menu data may require JavaScript to load.)")
    return lines

def format_yelp(soup):
    """Extract business listings or a single business page from Yelp."""
    lines = []

    # Single business page
    name_tag = soup.find("h1")
    if name_tag:
        lines.append(f"BUSINESS: {name_tag.get_text(strip=True)}\n")

    # Rating
    rating = soup.find(attrs={"aria-label": re.compile(r"star rating", re.I)})
    if rating:
        lines.append(f"  Rating : {rating.get('aria-label', '').strip()}")

    # Address
    address_tag = soup.find("address")
    if address_tag:
        lines.append(f"  Address: {address_tag.get_text(separator=' ', strip=True)}")

    # Reviews
    review_texts = soup.find_all("p", attrs={"lang": True})
    if not review_texts:
        review_texts = soup.find_all("span", class_=re.compile(r"raw__"))
    seen = set()
    count = 0
    if review_texts:
        lines.append("\n  REVIEWS:")
    for r in review_texts:
        text = r.get_text(strip=True)
        if text and len(text) > 40 and text not in seen:
            seen.add(text)
            lines.append(f"    • {text}")
            count += 1
            if count >= 10:
                break

    if len(lines) <= 1:
        lines.append("  (Yelp heavily restricts scraping; limited data may be available.)")
    return lines

def format_asi_fullerton(soup):
    """Extract numbered spots list from the ASI Fullerton article."""
    lines = []

    title = soup.find("h1")
    if title:
        lines.append(f"ARTICLE: {title.get_text(strip=True)}\n")

    headings = soup.find_all("h2")
    for heading in headings:
        text = heading.get_text(strip=True)

        if text and text[0].isdigit():
            lines.append(f"\n  {text}")
            sibling = heading.find_next_sibling()
            while sibling and sibling.name not in ("h2", "h3"):
                if sibling.name == "p":
                    body = sibling.get_text(strip=True)
                    if body:
                        lines.append(f"    {body}")
                sibling = sibling.find_next_sibling()

        elif "Honorable" in text:
            lines.append(f"\n  {text}")
            ul = heading.find_next("ul")
            if ul:
                for li in ul.find_all("li"):
                    lines.append(f"    - {li.get_text(strip=True)}")

    return lines

def format_oc_register(soup):
    """Extract article body and any embedded lists from OC Register."""
    lines = []

    title = soup.find("h1")
    if title:
        lines.append(f"ARTICLE: {title.get_text(strip=True)}\n")

    # Article body is usually in <p> tags inside an article tag
    article = soup.find("article") or soup.find("div", class_=re.compile(r"article|body|content", re.I))
    container = article if article else soup

    seen = set()
    for tag in container.find_all(["h2", "h3", "p", "li"]):
        text = tag.get_text(strip=True)
        if text and len(text) > 20 and text not in seen:
            seen.add(text)
            prefix = "  • " if tag.name == "li" else "  "
            lines.append(f"{prefix}{text}")

    if len(lines) <= 1:
        lines.append("  (Article may be behind a paywall or require JavaScript.)")
    return lines

def format_grubhub(soup):
    """Extract restaurant listings from a Grubhub delivery page."""
    lines = []
    lines.append("GRUBHUB DELIVERY LISTINGS\n")

    # Restaurant names typically appear in h3 or anchor tags with restaurant data
    restaurants = soup.find_all(["h3", "h4"])
    seen = set()
    count = 0
    for tag in restaurants:
        name = tag.get_text(strip=True)
        if name and len(name) > 3 and name not in seen:
            seen.add(name)
            lines.append(f"  • {name}")
            count += 1
            if count >= 30:
                break

    if count == 0:
        lines.append("  (Grubhub requires JavaScript to render listings — static scraping unavailable.)")
    return lines

def format_daily_titan(soup):
    """Extract article content from the Daily Titan student newspaper."""
    lines = []

    title = soup.find("h1")
    if title:
        lines.append(f"ARTICLE: {title.get_text(strip=True)}\n")

    # Byline / date
    byline = soup.find(class_=re.compile(r"byline|author|date", re.I))
    if byline:
        lines.append(f"  {byline.get_text(strip=True)}\n")

    article = soup.find("div", class_=re.compile(r"article-body|entry-content|story", re.I))
    container = article if article else soup

    seen = set()
    for tag in container.find_all(["h2", "h3", "p"]):
        text = tag.get_text(strip=True)
        if text and len(text) > 20 and text not in seen:
            seen.add(text)
            lines.append(f"  {text}")

    if len(lines) <= 1:
        lines.append("  (No article content found — page may require JavaScript.)")
    return lines

def format_yelp_business(soup):
    """Same as format_yelp — reused for individual Yelp business pages."""
    return format_yelp(soup)

def format_fullerton_housing(soup):
    """Extract payment information tables and sections from CSUF Housing page."""
    lines = []

    title = soup.find("h1")
    if title:
        lines.append(f"PAGE: {title.get_text(strip=True)}\n")

    # Extract section headings and their content
    for tag in soup.find_all(["h2", "h3", "h4", "p", "li", "td", "th"]):
        text = tag.get_text(strip=True)
        if text and len(text) > 5:
            if tag.name in ("h2", "h3", "h4"):
                lines.append(f"\n  [ {text} ]")
            elif tag.name in ("th", "td"):
                lines.append(f"    | {text}")
            elif tag.name == "li":
                lines.append(f"    • {text}")
            else:
                lines.append(f"    {text}")

    if len(lines) <= 1:
        lines.append("  (No content found.)")
    return lines

# ── Router ────────────────────────────────────────────────────

def route_formatter(url, soup):
    """Pick the right formatter based on the URL domain/path."""
    domain = urlparse(url).netloc.lower()
    path = urlparse(url).path.lower()

    if "reddit.com" in domain:
        return format_reddit(soup)
    elif "dineoncampus.com" in domain:
        return format_dine_on_campus(soup)
    elif "yelp.com" in domain and "/search" in path:
        return format_yelp(soup)
    elif "yelp.com" in domain and "/biz" in path:
        return format_yelp_business(soup)
    elif "asi.fullerton.edu" in domain:
        return format_asi_fullerton(soup)
    elif "ocregister.com" in domain:
        return format_oc_register(soup)
    elif "grubhub.com" in domain:
        return format_grubhub(soup)
    elif "dailytitan.com" in domain:
        return format_daily_titan(soup)
    elif "fullerton.edu" in domain and "housing" in path:
        return format_fullerton_housing(soup)
    else:
        return format_generic(soup)

def format_generic(soup):
    """Fallback: strip noise and extract all readable text."""
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()
    seen = set()
    lines = []
    for tag in soup.find_all(["h1", "h2", "h3", "p", "li"]):
        text = tag.get_text(strip=True)
        if text and len(text) > 20 and text not in seen:
            seen.add(text)
            lines.append(f"  {text}")
    return lines if lines else ["  (No readable content extracted.)"]

# ── Main ──────────────────────────────────────────────────────

def main():
    urls = parse_links(LINKS_FILE)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("SCRAPED RESULTS FROM LINKS\n")
        out.write("=" * 60 + "\n\n")

        for i, url in enumerate(urls, start=1):
            print(f"[{i}/10] Scraping: {url}")
            domain = urlparse(url).netloc

            out.write(f"LINK {i}: {url}\n")
            out.write(f"Domain : {domain}\n")
            out.write("-" * 60 + "\n")

            soup, error = fetch(url)

            if error:
                out.write(f"  ERROR: {error}\n")
            else:
                lines = route_formatter(url, soup)
                for line in lines:
                    out.write(line + "\n")

            out.write("\n" + "=" * 60 + "\n\n")
            time.sleep(1)

    print(f"\nDone! Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()