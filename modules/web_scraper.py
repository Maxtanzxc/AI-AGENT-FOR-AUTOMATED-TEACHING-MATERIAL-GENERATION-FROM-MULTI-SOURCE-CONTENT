import requests
from bs4 import BeautifulSoup
import re
import time
from config import SELENIUM_HEADLESS, SELENIUM_PAGE_TIMEOUT, IS_SELENIUM_AVAILABLE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Block non-educational domains
BLOCKED_DOMAINS = ["facebook.com", "twitter.com", "instagram.com", "reddit.com", "tiktok.com"]


def is_valid_url(url: str) -> bool:
    return url.startswith("http") and not any(d in url for d in BLOCKED_DOMAINS)


def is_selenium_available() -> bool:
    """Return True if Selenium library and browser drivers are ready."""
    return IS_SELENIUM_AVAILABLE


def scrape_webpage_selenium(url: str, wait_seconds: int = 3) -> str:
    """
    Scrape JavaScript-rendered educational web pages using headless Chrome / Edge browser.
    Renders dynamic DOM content before parsing text.
    """
    if not IS_SELENIUM_AVAILABLE:
        print("Selenium is not installed or available.")
        return ""

    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions

    driver = None
    try:
        # Try Chrome Headless first
        try:
            chrome_options = ChromeOptions()
            if SELENIUM_HEADLESS:
                chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={HEADERS['User-Agent']}")
            chrome_options.add_argument("--log-level=3")

            driver = webdriver.Chrome(options=chrome_options)
        except Exception as chrome_err:
            # Fallback to Edge Headless
            edge_options = EdgeOptions()
            if SELENIUM_HEADLESS:
                edge_options.add_argument("--headless=new")
            edge_options.add_argument("--disable-gpu")
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument(f"user-agent={HEADERS['User-Agent']}")
            edge_options.add_argument("--log-level=3")

            driver = webdriver.Edge(options=edge_options)

        driver.set_page_load_timeout(SELENIUM_PAGE_TIMEOUT)
        driver.get(url)
        time.sleep(wait_seconds)  # Wait for JS execution / client-side rendering

        page_source = driver.page_source
        return clean_html_to_text(page_source)

    except Exception as e:
        print(f"Selenium web scraping error for {url}: {e}")
        return ""
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def clean_html_to_text(html_content: str) -> str:
    """Parse HTML and extract clean, meaningful text paragraphs."""
    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove noise and non-content tags
        for tag in soup(["script", "style", "nav", "footer",
                         "header", "aside", "advertisement", "noscript", "iframe"]):
            tag.decompose()

        content_tags = soup.find_all(["p", "h1", "h2", "h3", "h4", "li", "article", "section"])
        paragraphs = [tag.get_text(separator=" ").strip() for tag in content_tags]

        # Filter out very short lines (navigation items, buttons)
        paragraphs = [p for p in paragraphs if len(p) > 35]

        text = " ".join(paragraphs)
        text = re.sub(r"\s+", " ", text).strip()
        return text
    except Exception as e:
        print(f"HTML parsing error: {e}")
        return ""


def scrape_webpage(url: str, use_selenium_fallback: bool = True) -> str:
    """
    Scrape clean educational text from a webpage.
    Attempts fast static HTTP request first; if text is sparse or requires JS,
    automatically falls back to Selenium headless browser rendering.
    """
    if not is_valid_url(url):
        return ""

    text = ""
    # 1. Try fast static requests
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            text = clean_html_to_text(response.text)
    except Exception as e:
        print(f"Static request error for {url}: {e}")

    # Check if static extraction is insufficient or requires JS
    js_keywords = ["javascript is required", "enable javascript", "please turn on javascript"]
    needs_js = any(kw in text.lower() for kw in js_keywords)

    if (len(text) < 200 or needs_js) and use_selenium_fallback and IS_SELENIUM_AVAILABLE:
        print(f"Triggering Selenium JS scraper for: {url}")
        selenium_text = scrape_webpage_selenium(url)
        if len(selenium_text) > len(text):
            text = selenium_text

    return text