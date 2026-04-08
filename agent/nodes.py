from agent.state import AllergenState
from agent.llm import detect_allergens
from scrapers.nykaa import scrape_nykaa
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import google.generativeai as genai
import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# gemini = genai.GenerativeModel(
#     model_name="gemini-2.0-flash",
#     generation_config={"temperature": 0}
# )

# def extract_search_query(slug: str) -> str:
#     prompt = f"""
#     Given this product URL slug: "{slug}"
#     Extract a short 2-3 word search query describing the product type.
#     Ignore brand names, ingredients, and marketing words.
    
#     Examples:
#     "mamaearth-ubtan-face-wash-with-turmeric" → "face wash"
#     "minimalist-10-niacinamide-face-serum-zinc" → "niacinamide face serum"
#     "dot-key-watermelon-cooling-gel-moisturiser" → "gel moisturiser"
    
#     Respond with the search query only. No extra text.
#     """
    
#     response = gemini.generate_content(prompt)
#     return response.text.strip()

def extract_search_query(slug: str) -> str:
    prompt = f"""
    Given this product URL slug: "{slug}"
    Extract a short 2-3 word search query describing the product type.
    Ignore brand names, ingredients, and marketing words.
    
    Examples:
    "mamaearth-ubtan-face-wash-with-turmeric" → "face wash"
    "minimalist-10-niacinamide-face-serum-zinc" → "niacinamide face serum"
    "dot-key-watermelon-cooling-gel-moisturiser" → "gel moisturiser"
    
    Respond with the search query only. No extra text.
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    result= response.choices[0].message.content.strip()
    print(f"\n\nresult:{result}\n\n")
    return result

def scrape_node(state: AllergenState) -> AllergenState:
    """Scrapes ingredients from the product URL"""
    print(f"[scrape_node] Scraping: {state['url']}")
    
    ingredients = scrape_nykaa(state["url"])
    
    return {
        **state,
        "ingredients": ingredients
    }

def detect_node(state:AllergenState)-> AllergenState:
    """Checks ingredients against user allergens"""
    print(f"[detect_node] Checking ingredients...")

    # If scraping failed, mark as unknown
    if not state["ingredients"]:
        return {
            **state,
            "is_safe": None,
            "allergens_found": [],
            "reason": "Could not extract ingredients from this page"
        }

    result = detect_allergens(state["ingredients"], state["user_allergens"])

    return {
        **state,
        "is_safe": result["is_safe"],
        "allergens_found": result["allergens_found"],
        "reason": result["reason"]
    }

def search_alternatives_node(state: AllergenState) -> AllergenState:
    print(f"[search_alternatives_node] Finding alternatives...")

    url_path = urlparse(state["url"]).path
    slug = url_path.strip("/").split("/")[0]
    
    # Use LLM instead of heuristic
    search_query = extract_search_query(slug)
    print(f"[search_alternatives_node] Searching for: {search_query}")

    search_url = f"https://www.nykaa.com/search/result/?q={search_query.replace(' ', '+')}"
    print(f"\n\nsearch url {search_url}\n\n")
    alternative_urls = scrape_nykaa_search_results(search_url)

    return {
        **state,
        "alternative_urls": alternative_urls
    }

def validate_node(state: AllergenState) -> AllergenState:
    """Scrapes and checks each alternative product"""
    print(f"[validate_node] Validating {len(state['alternative_urls'])} alternatives...")

    safe_alternatives = []
    print(f"\n[validate_node] Alternative URLs received: {state['alternative_urls']}\n")
    print(f"\n[validate_node] Total: {len(state['alternative_urls'])}\n")
    for url in state["alternative_urls"][:5]:  # check max 5
        # Skip the original product
        if url == state["url"]:
            continue

        print(f"[validate_node] Checking: {url}")
        ingredients = scrape_nykaa(url)

        if not ingredients:
            print("\n\n no ingredients found in alternate product\n\n")
            continue

        result = detect_allergens(ingredients, state["user_allergens"])

        if result["is_safe"]:
            safe_alternatives.append({
                "url": url,
                "reason": result["reason"]
            })

        # Stop once we have 3 safe alternatives
        if len(safe_alternatives) >= 3:
            break
        
    return {
        **state,
        "safe_alternatives": safe_alternatives
    }

def scrape_nykaa_search_results(search_url: str) -> list[str]:
    """Scrapes product URLs from Nykaa search results page"""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-IN",
     
       )
#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#     headless=False,
#     args=[
#         "--disable-blink-features=AutomationControlled",
#         "--disable-dev-shm-usage",
#         "--no-sandbox",
#         "--window-size=1280,800",
#         "--disable-gpu",
#         "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
#     ]
# )

#         context = browser.new_context(
#     user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     viewport={"width": 1280, "height": 800},
#     locale="en-IN",
#     timezone_id="Asia/Kolkata",
#     extra_http_headers={
#         "Accept-Language": "en-IN,en;q=0.9",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
#         "sec-ch-ua": '"Chromium";v="120", "Google Chrome";v="120"',
#         "sec-ch-ua-mobile": "?0",
#         "sec-ch-ua-platform": '"macOS"'
#     }
# )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print(f"[scrape_nykaa_search_results] Opening: {search_url}")
        page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    # Extract product links from search results
    product_urls = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        # Nykaa product URLs contain /p/ 
        if "/p/" in href:
            # Make sure it's a full URL
            if href.startswith("http"):
                product_urls.append(href)
            else:
                product_urls.append(f"https://www.nykaa.com{href}")

    # Deduplicate
    product_urls = list(dict.fromkeys(product_urls))

    print(f"[scrape_nykaa_search_results] Found {len(product_urls)} products")
    return product_urls[:5]

# # def create_browser(p):
# #     """Returns a configured stealth browser + context"""
# #     browser = p.chromium.launch(
# #         headless=True,
# #         args=[
# #             "--disable-blink-features=AutomationControlled",
# #             "--disable-dev-shm-usage",
# #             "--no-sandbox",
# #             "--window-size=1280,800",
# #             "--disable-gpu",
# #         ]
# #     )
# #     context = browser.new_context(
# #         user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# #         viewport={"width": 1280, "height": 800},
# #         locale="en-IN",
# #         timezone_id="Asia/Kolkata",
# #         extra_http_headers={
# #             "Accept-Language": "en-IN,en;q=0.9",
# #             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
# #             "sec-ch-ua": '"Chromium";v="120", "Google Chrome";v="120"',
# #             "sec-ch-ua-mobile": "?0",
# #             "sec-ch-ua-platform": '"macOS"'
# #         }
# #     )
# #     return browser, context

# # def scrape_nykaa_search_results(search_url: str) -> list[str]:
# #     """Scrapes product URLs from Nykaa search results page"""
# #     with sync_playwright() as p:
# #         browser, context = create_browser(p)
# #         page = context.new_page()
# #         page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# #         html = ""
# #         try:
# #             print(f"[scrape_nykaa_search_results] Opening: {search_url}")
# #             page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
# #             page.wait_for_timeout(3000)

# #             # Scroll to load products
# #             for _ in range(3):
# #                 page.evaluate("window.scrollBy(0, 600)")
# #                 page.wait_for_timeout(800)

# #             html = page.content()

# #         except Exception as e:
# #             print(f"[scrape_nykaa_search_results] Error: {e}")

# #         finally:
# #             browser.close()
# #             print("[scrape_nykaa_search_results] Browser closed")

# #     if not html:
# #         return []

# #     soup = BeautifulSoup(html, "html.parser")

# #     product_urls = []
# #     for a_tag in soup.find_all("a", href=True):
# #         href = a_tag["href"]
# #         if "/p/" in href:
# #             if href.startswith("http"):
# #                 product_urls.append(href)
# #             else:
# #                 product_urls.append(f"https://www.nykaa.com{href}")

# #     product_urls = list(dict.fromkeys(product_urls))
# #     print(f"[scrape_nykaa_search_results] Found {len(product_urls)} products")
# #     return product_urls[:5]











# def scrape_nykaa_search_results(search_url: str) -> list[str]:
#     """Scrapes product URLs from Nykaa search results page"""
#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless=False,
#             args=[
#                 "--disable-blink-features=AutomationControlled",
#                 "--disable-dev-shm-usage",
#                 "--no-sandbox",
#                 "--window-size=1280,800",
#                 "--disable-gpu",
#             ]
#         )
#         context = browser.new_context(
#             user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#             viewport={"width": 1280, "height": 800},
#             locale="en-IN",
#             timezone_id="Asia/Kolkata",
#             extra_http_headers={
#                 "Accept-Language": "en-IN,en;q=0.9",
#                 "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
#                 "sec-ch-ua": '"Chromium";v="120", "Google Chrome";v="120"',
#                 "sec-ch-ua-mobile": "?0",
#                 "sec-ch-ua-platform": '"macOS"'
#             }
#         )
#         page = context.new_page()
#         page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

#         html = ""
#         try:
#             print(f"[scrape_nykaa_search_results] Opening: {search_url}")
#             page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
#             page.wait_for_timeout(3000)

#             for _ in range(3):
#                 page.evaluate("window.scrollBy(0, 600)")
#                 page.wait_for_timeout(800)

#             html = page.content()

#         except Exception as e:
#             print(f"[scrape_nykaa_search_results] Error: {e}")

#         finally:
#             browser.close()
#             print("[scrape_nykaa_search_results] Browser closed")

#     if not html:
#         return []

#     soup = BeautifulSoup(html, "html.parser")

#     product_urls = []
#     for a_tag in soup.find_all("a", href=True):
#         href = a_tag["href"]
#         if "/p/" in href:
#             if href.startswith("http"):
#                 product_urls.append(href)
#             else:
#                 product_urls.append(f"https://www.nykaa.com{href}")

#     product_urls = list(dict.fromkeys(product_urls))
#     print(f"[scrape_nykaa_search_results] Found {len(product_urls)} products")
#     return product_urls[:5]