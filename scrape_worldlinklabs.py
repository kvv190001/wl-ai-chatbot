from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
import os
import re

BASE_URL = "https://worldlink-us.com"
# BASE_URL = "https://worldlinklabs.ai/"

visited = set()
to_visit = [BASE_URL]
scraped_pages = []

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def is_internal(url):
    """Check if URL is inside the same domain."""
    return urlparse(url).netloc.replace("www.", "") == urlparse(BASE_URL).netloc.replace("www.", "")


def normalize_url(url):
    """Normalize URL to prevent duplicates & loops."""
    parsed = urlparse(url)

    # FORCE HTTPS
    url = "https://" + parsed.netloc + parsed.path

    # Remove fragments (#)
    url = url.split("#")[0]

    # Remove query params (?)
    url = url.split("?")[0]

    # Remove trailing slash (except root)
    if url.endswith("/") and url != BASE_URL + "/":
        url = url[:-1]

    url = url.lower()

    return url


def clean_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style", "noscript", "footer", "header", "nav"]):
        element.extract()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def is_static_file(url):
    """Block images, PDFs, docs, zip, assets, etc."""
    return re.search(r"\.(png|jpg|jpeg|gif|svg|webp|css|js|pdf|zip|rar|tar|gz|woff|woff2|ttf|eot)$", url)


def is_pagination(url):
    """Block Wordpress pagination pages."""
    return "/page/" in url


# ---------------------------------------------------------
# Main Crawler
# ---------------------------------------------------------

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    while to_visit:
        MAX_PAGES = 50
        if len(visited) >= MAX_PAGES:
            break

        url = to_visit.pop(0)
        url = normalize_url(url)

        if url in visited:
            continue

        # Skip static files
        if is_static_file(url):
            continue

        # Skip pagination loops
        if is_pagination(url):
            continue

        visited.add(url)
        print("Scraping:", url)

        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
        except:
            print("❌ Failed:", url)
            continue

        time.sleep(1)

        html = page.content()
        text = clean_text(html)

        scraped_pages.append(
            f"URL: {url}\n{text}\n\n" + "-"*60 + "\n\n"
        )

        soup_links = BeautifulSoup(html, "html.parser")
        for a in soup_links.find_all("a", href=True):

            new_url = urljoin(url, a["href"])
            new_url = normalize_url(new_url)

            # Internal only
            if not is_internal(new_url):
                continue

            # No static files
            if is_static_file(new_url):
                continue

            # No pagination
            if is_pagination(new_url):
                continue

            if new_url not in visited and new_url not in to_visit:
                to_visit.append(new_url)

    browser.close()


# ---------------------------------------------------------
# Save Output
# ---------------------------------------------------------

os.makedirs("data", exist_ok=True)

output = "data/worldlink-us-full-text.txt"
# output = "data/worldlinklabs_full_text.txt"
with open(output, "w", encoding="utf-8") as f:
    f.write("\n".join(scraped_pages))

print(f"\n✅ DONE — Scraped", len(scraped_pages), "pages.")
print(f"📄 Saved output to {output}")
