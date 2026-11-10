from modules.web_scraper import scrape_webpage, scrape_webpage_selenium, is_selenium_available

print(f"Is Selenium JS Scraper available? {is_selenium_available()}")

# Test static vs dynamic scraping on Wikipedia or Python docs
test_url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
print(f"\nTesting Web Scraper on: {test_url}")

text = scrape_webpage(test_url)
print(f"Extracted Text Length: {len(text)} characters")
print(f"Preview: {text[:250]}...")

assert len(text) > 100, "Failed to extract web text from test URL"
print("\nSUCCESS: Web scraper verification passed!")
