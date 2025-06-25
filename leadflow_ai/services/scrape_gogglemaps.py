import asyncio
from playwright.async_api import async_playwright
import time, csv

async def scrape_google_maps(search_query="spas near South Loop Chicago", max_links=30):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}")
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
        for i in range(min(await anchors.count(), max_links)):
            href = await anchors.nth(i).get_attribute("href")
            if href and "/maps/place/" in href:
                links.append(href)

        business_details = []
        for link in links:
            details = await scrape_business_details(link)
            business_details.append(details)

        await browser.close()
        return business_details

async def scrape_business_details(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await asyncio.sleep(3)  # wait for content to load

        try:
            name = (await page.title()).split(" - Google Maps")[0]
        except:
            name = ""

        try:
            location = await page.locator('//*/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div[3]/button/div/div[2]/div[1]').first.inner_text()
        except:
            location = ""

        try:
            website = await page.locator('//*[@data-item-id="authority"]').first.get_attribute("href")
        except:
            website = ""

        await browser.close()
        return {"name": name, "location": location, "website": website, "url": url}

# ✅ Main Script
if __name__ == "__main__":
    asyncio.run(scrape_google_maps("massage therapy South Loop Chicago", max_links=15))

    # Save to CSV
    with open("google_maps_scrape.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "location", "website", "url"])
        writer.writeheader()
        writer.writerows(results)
