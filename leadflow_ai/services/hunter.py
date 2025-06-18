import os
import requests
from dotenv import load_dotenv
from typing import List, Dict
import logging

load_dotenv()

HUNTER_API_KEY = os.getenv('HUNTER_API_KEY')

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def get_contacts(domain: str) -> List[Dict[str, str]]:
    url = f'https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_API_KEY}'
    logging.debug(f'Request URL: {url}')
    response = requests.get(url)
    logging.debug(f'Response Status Code: {response.status_code}')
    data = response.json()
    logging.debug(f'Response Data: {data}')

    contacts = []
    if 'data' in data and 'emails' in data['data']:
        for email_info in data['data']['emails']:
            if email_info['confidence'] >= 80 and 'Director' in email_info['position']:
                logging.debug(f'Email Info: {email_info}')
                contact = {
                    'full_name': email_info.get('first_name', '') + ' ' + email_info.get('last_name', ''),
                    'email': email_info.get('value', ''),
                    'position': email_info.get('position', ''),
                    'confidence': email_info.get('confidence', '')
                }
                contacts.append(contact)
    return contacts 