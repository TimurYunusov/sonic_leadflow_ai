import httpx
from bs4 import BeautifulSoup
from ..db.supabase import create_supabase
import logging
import urllib.parse

logging.basicConfig(level=logging.INFO)

async def reverse_geocode(lat, lng):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json"
    headers = {"User-Agent": "YourAppNameHere"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("display_name", "Unknown")

async def enrich_target_duckduckgo(target: dict):
    logging.info(f"Enriching target: {target}")
    name = target.get('name')
    address = target.get('address', '')
    lat = target.get('lat')
    lng = target.get('lng')

    if not name:
        logging.warning("No name provided, skipping target.")
        return  # Skip if no name is provided

    # Use reverse geocoding to get a full address if needed
    if address == 'Unknown':
        address = await reverse_geocode(lat, lng)
        logging.info(f"Reverse geocoded address: {address}")

    # Use fallback city context if address is still missing
    location_fallback = "Chicago IL"
    query = f"{name} website {address if address != 'Unknown' else location_fallback}".strip().replace(' ', '+')
    url = f"https://duckduckgo.com/html/?q={query}"

    # Log the modified query string
    logging.info(f"Modified DuckDuckGo query: {query}")

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            # Parse HTML response
            soup = BeautifulSoup(response.text, 'html.parser')
            logging.info(f"Parsed HTML: {soup.prettify()[:1000]}")  # Log first 1000 characters of parsed HTML
            result = soup.find('a', {'class': 'result__a'})
            if result:
                link = result.get('href')
                logging.info(f"Parsed link: {link}")  # Log the parsed link
                # Improved domain extraction
                if link and "uddg=" in link:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
                    url_clean = parsed.get("uddg", [None])[0]
                else:
                    url_clean = link

                domain = urllib.parse.urlparse(url_clean).netloc if url_clean else "Unknown"

                # Sanitize domain and website
                if not url_clean or not domain:
                    logging.warning("Skipping update due to missing domain or website.")
                    return

                # Create unique hash
                unique_hash = hash((name, lat, lng))

                # Log the update payload
                logging.info(f"Updating record: domain={domain}, website={url_clean} for hash={unique_hash}")

                # Update local_targets with domain and website
                supabase = await create_supabase()
                await supabase.table("local_targets").update({
                    "domain": domain,
                    "website": url_clean
                }).match({"unique_hash": unique_hash}).execute()
            else:
                logging.warning("No result found in DuckDuckGo response.")
    except Exception as e:
        logging.error(f"Error enriching target: {e}", exc_info=True)  # Add proper logging in production
