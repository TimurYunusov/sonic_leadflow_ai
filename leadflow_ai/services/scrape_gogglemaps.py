import asyncio
from playwright.async_api import async_playwright
import time, csv
import logging
from leadflow_ai.schemas.lead import AppState, Business

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def scrape_google_maps(state: AppState):
    logging.info(f"Starting Google Maps scrape for query: {state.search_query}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.google.com/maps/search/{state.search_query.replace(' ', '+')}")
        await page.wait_for_selector('//div[@role="feed"]', timeout=10000)

        # Scroll to load more cards by scrolling the feed container
        for _ in range(15):
            await page.evaluate("""
            const el = document.querySelector('div[role="feed"]');
            if (el) el.scrollBy(0, 1000);
            """)
            await asyncio.sleep(2)

        # Extract place URLs from search results
        anchors = page.locator('//div[@role="feed"]/div/div/a')
        links = []
        for i in range(min(await anchors.count(), state.max_links)):
            href = await anchors.nth(i).get_attribute("href")
            if href and "/maps/place/" in href:
                links.append(href)

        logging.info(f"Found {len(links)} business links")

        business_details = []
        for link in links:
            logging.info(f"Scraping details for: {link}")
            details = await scrape_business_details(link)
            business_details.append(details)

        await browser.close()
        logging.info("Completed Google Maps scrape")
        return business_details

async def scrape_business_details(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=60000)  # Increase timeout to 60 seconds
        except Exception as e:
            logging.error(f"Failed to load {url}: {e}")
            return None  # Return None or handle as needed to skip this URL

        await asyncio.sleep(3)  # wait for content to load

        try:
            name = (await page.title()).split(" - Google Maps")[0]
        except:
            name = ""

        # try:
        #     location = await page.locator('//*/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div[3]/button/div/div[2]/div[1]').first.inner_text()
        # except:
        #     location = ""
        try:
            address_button = page.locator('//button[contains(@aria-label, "Address:")]').first
            aria_label = await address_button.get_attribute("aria-label")
            location = aria_label.split("Address:")[1].strip() if aria_label else ""
        except Exception as e:
            logging.error(f"[Warning] Failed to extract address: {e}")
            location = ""

        try:
            website = await page.locator('//*[@data-item-id="authority"]').first.get_attribute("href")
        except:
            website = ""

        await browser.close()
        # 🚫 Skip businesses without a website
        if not website:
            logging.info(f"⏭️ Skipping '{name}' — no website found.")
            return None
        return {"name": name, "location": location, "website": website, "url": url}

async def scrape_google_maps_node(state: AppState) -> dict:
    """
    Node function for LangChain/LangGraph workflow to scrape Google Maps 
    and store results in the graph state, skipping entries without websites.
    """
    raw_details = await scrape_google_maps(state)
    
    # Filter out any None results (e.g., businesses without websites)
    valid_details = [details for details in raw_details if details is not None]

    # Convert to Business dataclass instances
    state.businesses = [Business(**details) for details in valid_details]

    logging.info(f"✅ {len(state.businesses)} valid businesses saved to state (skipped {len(raw_details) - len(valid_details)} invalid)")
    
    return {"businesses": state.businesses}

