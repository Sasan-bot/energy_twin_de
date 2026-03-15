import requests
import pandas as pd
from datetime import datetime, timedelta
import config  # Centralized configuration for global constants

def fetch_historical_weather(lat, lon, years=3):
    """
    Fetches multi-year historical weather data from Open-Meteo Archive API.
    Essential for training the XGBoost ML Engine with real-world climate patterns.
    
    Args:
        lat (float): Latitude of the target location.
        lon (float): Longitude of the target location.
        years (int): Number of years to look back (linked to config.HISTORY_YEARS).
    """
    # Open-Meteo Archive has a 2-day delay for finalized historical records.
    # We calculate the window based on the current date.
    end_date = (datetime.now() - timedelta(days=2)).date()
    start_date = end_date - timedelta(days=years * 365)
    
    # API Parameters selection:
    # 1. Shortwave Radiation: Direct solar energy hitting the panels.
    # 2. Cloud Cover: The primary factor reducing solar efficiency.
    # 3. Temperature: High ambient heat can slightly reduce PV efficiency.
    # 4. Snowfall: Physical obstruction that can temporarily zero out production.
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&"
        f"start_date={start_date}&end_date={end_date}&"
        f"hourly=temperature_2m,shortwave_radiation,snowfall,cloud_cover&"
        f"timezone=Europe%2FBerlin"
    )
    
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status() # Check for HTTP errors
        data = response.json()
        
        # Structure the hourly data into a Pandas DataFrame
        df = pd.DataFrame(data['hourly'])
        df['time'] = pd.to_datetime(df['time'])
        
        # PERSISTENCE LAYER: Save the data using the filename defined in config.py.
        # This ensures the ML Engine and Data Fetcher are always synced.
        df.to_csv(config.HISTORICAL_DATA_FILE, index=False)
        
        print(f"✅ SUCCESS: {len(df)} records saved to {config.HISTORICAL_DATA_FILE}")
        return df
    except Exception as e:
        print(f"❌ Data Fetching Error: {e}")
        return None

def fetch_smard_prices():
    """
    Fetches real-time German electricity market prices from SMARD.de.
    Used for dynamic financial modeling and ROI calculations.
    """
    try:
        # Step 1: Get the latest available timestamp index
        index_url = "https://www.smard.de/app/chart_data/4169/DE/index_hour.json"
        last_ts = requests.get(index_url).json()['timestamps'][-1]
        
        # Step 2: Fetch the hourly price series for that timestamp
        price_url = f"https://www.smard.de/app/chart_data/4169/DE/4169_DE_hour_{last_ts}.json"
        series = requests.get(price_url).json()['series']
        
        # Convert MWh price to kWh price (divide by 1000)
        return [val[1] / 1000 for val in series[-24:]]
    except Exception as e:
        # Fallback to config default if SMARD API is unreachable
        print(f"⚠️ Price Fetching Failed: Using fallback ({config.AVG_GRID_PRICE} €/kWh)")
        return [config.AVG_GRID_PRICE] * 24

def fetch_satellite_image(lat, lon, mapbox_token):
    """
    Retrieves high-resolution satellite imagery from Mapbox Static API.
    Standardized at Zoom 19 for a consistent pixel-to-meter ratio.
    """
    # 800x800 resolution ensures we have a large enough canvas for roof mapping
    url = (
        f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
        f"{lon},{lat},19,0/800x800?access_token={mapbox_token}"
    )
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            filename = "roof_top.png"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"✅ Mapbox Satellite image captured and saved as {filename}")
            return filename
        else:
            print(f"❌ Mapbox API Error: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Connection Error during image retrieval: {e}")
        return None