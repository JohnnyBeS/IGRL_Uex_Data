import requests
import json
from datetime import datetime

def get_uex_data(service, config):
    headers = {
        'Authorization': f'Bearer {config['api']['token']}',
        'Accept': 'application/json'
    }
    
    try:
        print(f"\nVersuche Download von {service}...")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        response = requests.get(f"{config['api']['base_url']}{service}", headers=headers)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Download von {service}: {e}")
        return None
    except Exception as e:
        print(f"Fehler beim Download von {service}: {e}")
        return None