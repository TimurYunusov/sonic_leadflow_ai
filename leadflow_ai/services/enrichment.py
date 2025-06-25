import os
import httpx
import logging
import urllib.parse
import asyncio
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from ..db.supabase import create_supabase

load_dotenv()

logging.basicConfig(level=logging.INFO)

async def reverse_geocode(lat, lng):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json"
    headers = {"User-Agent": "YourAppNameHere"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("display_name", "Unknown")

async def enrich_target(target: dict) -> dict:
    logging.info(f"Enriching target: {target}")
    name = target.get('name', 'business')
    address = target.get('address', '')
    lat = target.get('lat')
    lng = target.get('lng')
    source = target.get('source', 'unknown')

    if address == 'Unknown':
        address = await reverse_geocode(lat, lng)
        logging.info(f"Reverse geocoded address: {address}")
        # Log the updated address
        logging.info(f"Updated address from reverse geocoding: {address}")
        # Update Supabase with the new address
        unique_hash = hash((name, lat, lng))
        supabase = await create_supabase()
        await supabase.table("local_targets").update({
            "address": address
        }).match({"unique_hash": unique_hash}).execute()
        logging.info(f"Address updated in Supabase for hash={unique_hash}")

    # Normalize name and address
    name = name.strip().title()
    address = address.strip().title()

    # Primary Enrichment with DuckDuckGo
    query = f"{name} {address} website".strip().replace(' ', '+')
    url = f"https://duckduckgo.com/html/?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('a', {'class': 'result__a'}, limit=5)
            valid_domains = []
            skip_domains = ["wikipedia.org", "realtor.com", "trulia.com", "yelp.com", "zillow.com", "booking.com", "apartments.com"]

            for result in results:
                link = result.get('href')
                if link and "uddg=" in link:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
                    url_clean = parsed.get("uddg", [None])[0]
                    if not url_clean:
                        url_clean = link
                else:
                    url_clean = link

                domain = urllib.parse.urlparse(url_clean).netloc if url_clean else "Unknown"

                if not url_clean or not domain or any(spam in domain for spam in skip_domains):
                    logging.info(f"Skipped domain: {domain} from link: {url_clean}")
                    continue

                logging.info(f"Selected domain: {domain} from link: {url_clean}")
                valid_domains.append((domain, url_clean))

            if valid_domains:
                domain, url_clean = valid_domains[0]
            else:
                raise ValueError("No valid domain found, triggering fallback.")

    except (httpx.HTTPStatusError, ValueError) as e:
        logging.warning(f"Primary enrichment failed, error: {e}. Triggering fallback to Firecrawl.")
        # Fallback Enrichment with Firecrawl
        url = "https://api.firecrawl.dev/v1/scrape"
        headers = {
            "Authorization": f"Bearer {os.getenv('FIRECRAWL_API_KEY')}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": f"{name} {address}",
            "include": ["urls", "metatags", "socials", "description"],
            "numResults": 1
        }

        async def fetch_with_retry(url, headers, json, retries=3, backoff_factor=0.3):
            for attempt in range(retries):
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(url, headers=headers, json=json)
                        response.raise_for_status()
                        return response.json()
                except (httpx.HTTPStatusError, httpx.RequestError) as e:
                    if attempt < retries - 1:
                        sleep_time = backoff_factor * (2 ** attempt)
                        logging.warning(f"Retrying in {sleep_time} seconds due to error: {e}")
                        await asyncio.sleep(sleep_time)
                    else:
                        logging.error(f"Failed after {retries} attempts: {e}")
                        raise

        try:
            data = await fetch_with_retry(url, headers, payload)
            website = data.get('urls', [None])[0]
            domain = urllib.parse.urlparse(website).netloc if website else "Unknown"

            if not website or not domain or any(spam in domain for spam in skip_domains):
                logging.info(f"Fallback skipped domain: {domain} from link: {website}")
                return target

            logging.info(f"Fallback selected domain: {domain} from link: {website}")

        except Exception as e:
            logging.error(f"Error during Firecrawl fallback: {e}", exc_info=True)
            return target

    # Update Supabase
    unique_hash = hash((name, lat, lng))
    logging.info(f"Updating record: domain={domain}, website={url_clean} for hash={unique_hash}")
    supabase = await create_supabase()
    res = await supabase.table("local_targets").update({
        "address": address,
        "domain": domain,
        "website": url_clean
    }).match({"unique_hash": unique_hash}).execute()
    logging.info(f"Supabase update response: {res}")

    # Return the enriched target
    return {
        "name": name,
        "address": address,
        "lat": lat,
        "lng": lng,
        "type": target.get('type', 'office'),
        "source": source,
        "domain": domain,
        "website": url_clean
    }
