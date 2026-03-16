import requests
from config import Config

class SmardApiClient:
    @staticmethod
    def get_timestamps(module_ids, regions):
        """Tries multiple IDs and Regions until it finds a working endpoint."""
        for mod_id in module_ids:
            for region in regions:
                url = f"https://www.smard.de/app/chart_data/{mod_id}/{region}/index_{Config.RESOLUTION}.json"
                try:
                    resp = requests.get(url, headers=Config.HEADERS, timeout=10)
                    if resp.status_code == 200:
                        # Success! Return the ID and Region that actually worked
                        return mod_id, region, resp.json().get('timestamps', [])
                except Exception as e:
                    pass # Ignore connection errors and try the next combination
                
        print(f"      [!] Error: Could not find valid index for IDs {module_ids} in regions {regions}")
        return None, None, []

    @staticmethod
    def fetch_chunk(module_id, region, timestamp):
        url = f"https://www.smard.de/app/chart_data/{module_id}/{region}/{module_id}_{region}_{Config.RESOLUTION}_{timestamp}.json"
        try:
            resp = requests.get(url, headers=Config.HEADERS, timeout=5)
            if resp.status_code == 200:
                return resp.json().get('series', [])
        except:
            pass
        return []