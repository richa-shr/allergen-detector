from typing import Optional
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def clean_nykaa_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

# def scrape_nykaa(url: str) -> Optional[str]:
#     clean_url = clean_nykaa_url(url)
#     print(f"Cleaned URL: {clean_url}")

#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless=False,
#             args=["--disable-blink-features=AutomationControlled"]
#         )
        
#         context = browser.new_context(
#             user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#             viewport={"width": 1280, "height": 800},
#             locale="en-IN",
#         )
        
#         page = context.new_page()
#         page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

#         print(f"Opening: {clean_url}")
#         page.goto(clean_url, wait_until="domcontentloaded", timeout=60000)
        
#         # Wait for the tab bar to appear
#         page.wait_for_timeout(3000)

#         # Find and click the Ingredients tab
#         # We look for an h3 whose text is exactly "Ingredients"
#         try:
#             ingredients_tab = page.locator("h3", has_text="Ingredients").first
#             ingredients_tab.click()
#             print("Clicked Ingredients tab")
            
#             # Wait for content to load after click
#             page.wait_for_timeout(2000)
#         except Exception as e:
#             print(f"Could not click Ingredients tab: {e}")

#         html = page.content()
#         browser.close()

#     soup = BeautifulSoup(html, "html.parser")

#     # Now content-details div should have ingredient content
#     ingredient_section = None
#     content_div = soup.find("div", id="content-details")
#     if content_div:
#         ingredient_section = content_div.get_text(strip=True)

#     if ingredient_section:
#         print(f"Found ingredients: {ingredient_section[:100]}...")
#         return ingredient_section

#     print("No ingredients found on this page")
#     return None

# def scrape_nykaa(url: str) -> Optional[str]:
#     clean_url = clean_nykaa_url(url)
#     print(f"Cleaned URL: {clean_url}")

#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless=False,
#             args=["--disable-blink-features=AutomationControlled"]
#         )
        
#         context = browser.new_context(
#             user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#             viewport={"width": 1280, "height": 800},
#             locale="en-IN",
#         )
        
#         page = context.new_page()
#         page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

#         page.goto(clean_url, wait_until="domcontentloaded", timeout=60000)
#         page.wait_for_timeout(3000)

#         # h3 is always in DOM — just click it directly
#         try:
#             ingredients_tab = page.locator("h3:has-text('Ingredients')").first
#             ingredients_tab.scroll_into_view_if_needed()
#             ingredients_tab.click(force=True)
#             print("Clicked Ingredients tab")
#         except Exception as e:
#             print(f"Could not click Ingredients tab: {e}")

#         # Wait for content-details div to appear after click
#         try:
#             page.wait_for_selector("div#content-details", timeout=10000)
#             print("Ingredients content appeared")
#         except:
#             print("Ingredients content never appeared after click")

#         html = page.content()
#         browser.close()

#     soup = BeautifulSoup(html, "html.parser")

#     ingredient_section = None
#     content_div = soup.find("div", id="content-details")
#     if content_div:
#         ingredient_section = content_div.get_text(strip=True)

#     if ingredient_section:
#         print(f"Found ingredients: {ingredient_section[:100]}...")
#         return ingredient_section

#     print("No ingredients found on this page")
#     return None

# def scrape_nykaa(url: str) -> Optional[str]:
#     clean_url = clean_nykaa_url(url)
#     print(f"Cleaned URL: {clean_url}")

#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless=False,
#             args=["--disable-blink-features=AutomationControlled"]
#         )
        
#         context = browser.new_context(
#             user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#             viewport={"width": 1280, "height": 800},
#             locale="en-IN",
#         )
        
#         page = context.new_page()
#         page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

#         page.goto(clean_url, wait_until="domcontentloaded", timeout=60000)
#         page.wait_for_timeout(3000)

#         # Scroll down gradually until h3 appears in DOM
#         print("Scrolling to trigger lazy rendering...")
#         for scroll_attempt in range(10):
#             page.evaluate("window.scrollBy(0, 400)")
#             page.wait_for_timeout(800)

#             h3_count = page.locator("h3:has-text('Ingredients')").count()
#             print(f"Scroll {scroll_attempt + 1}: h3 count = {h3_count}")

#             if h3_count > 0:
#                 print("H3 found in DOM — stopping scroll")
#                 break

#         # Now click it
#         try:
#             ingredients_tab = page.locator("h3:has-text('Ingredients')").first
#             ingredients_tab.scroll_into_view_if_needed()
#             page.wait_for_timeout(1500)
#             ingredients_tab.click(force=True)
#             print("Clicked Ingredients tab")

#             # Wait for content to appear
#             page.wait_for_selector("div#content-details", timeout=10000)
#             print("Ingredients content appeared")

#         except Exception as e:
#             print(f"Error: {e}")

#         html = page.content()
#         browser.close()

#     soup = BeautifulSoup(html, "html.parser")

#     ingredient_section = None
#     content_div = soup.find("div", id="content-details")
#     if content_div:
#         ingredient_section = content_div.get_text(strip=True)

#     if ingredient_section:
#         print(f"Found ingredients: {ingredient_section[:100]}...")
#         return ingredient_section

#     print("No ingredients found on this page")
#     return None
def scrape_nykaa(url: str) -> Optional[str]:
    clean_url = clean_nykaa_url(url)
    print(f"Cleaned URL: {clean_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
    headless=True,
    args=[
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--window-size=1280,800",
        "--disable-gpu",
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
)
        context = browser.new_context(
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    viewport={"width": 1280, "height": 800},
    locale="en-IN",
    timezone_id="Asia/Kolkata",
    extra_http_headers={
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "sec-ch-ua": '"Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"'
    }
        )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            page.goto(clean_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)

            # Scroll to trigger lazy rendering
            for scroll_attempt in range(10):
                page.evaluate("window.scrollBy(0, 400)")
                page.wait_for_timeout(800)
                h3_count = page.locator("h3:has-text('Ingredients')").count()
                if h3_count > 0:
                    print("H3 found — stopping scroll")
                    break

            # Click ingredients tab
            ingredients_tab = page.locator("h3:has-text('Ingredients')").first
            ingredients_tab.scroll_into_view_if_needed()
            page.wait_for_timeout(1500)
            ingredients_tab.click(force=True)
            print("Clicked Ingredients tab")

            # Wait for content
            page.wait_for_selector("div#content-details", timeout=10000)
            print("Ingredients content appeared")

            html = page.content()

        except Exception as e:
            print(f"Error during scraping: {e}")
            html = ""

        finally:
            browser.close()  # ← guaranteed to run no matter what
            print("Browser closed")

    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    ingredient_section = None
    content_div = soup.find("div", id="content-details")
    if content_div:
        ingredient_section = content_div.get_text(strip=True)

    if ingredient_section:
        print(f"Found ingredients: {ingredient_section[:100]}...")
        return ingredient_section

    print("No ingredients found on this page")
    return None