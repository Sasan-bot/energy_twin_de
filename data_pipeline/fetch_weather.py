import requests
import pandas as pd
import os

def fetch_weather_data():
    print("🌤️ Starting Weather Data Fetcher (Frankfurt, Germany)...")
    
    # Coordinates for Frankfurt (Central Germany)
    lat = 50.1109
    lon = 8.6821
    
    # We match the exact timeline of your SMARD data
    start_date = "2024-01-01"
    end_date = "2025-12-31"
    
    # Open-Meteo Historical API URL
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&"
        f"start_date={start_date}&end_date={end_date}&"
        f"hourly=temperature_2m,shortwave_radiation&"
        f"timezone=UTC" # CRITICAL: Matches SMARD's UTC timestamps
    )
    
    print(f"📡 Requesting data from Open-Meteo API...")
    response = requests.get(url)
    
    if response.status_code == 200:
        print("✅ Data received successfully!")
        data = response.json()
        
        # Extract the hourly data
        hourly = data['hourly']
        
        # Create a Pandas DataFrame
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(hourly['time']),
            'temperature_2m_C': hourly['temperature_2m'],
            'solar_radiation_W_m2': hourly['shortwave_radiation']
        })
        
        # Set timestamp as index
        df.set_index('timestamp', inplace=True)
        
        # Create the data folder if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Save to CSV
        filename = "data/weather_data_2024_2025.csv"
        df.to_csv(filename)
        
        print(f"💾 Saved {len(df)} hours of weather data to: {filename}")
        print("\n📊 Quick preview:")
        print(df.head(3))
        
    else:
        print(f"❌ Failed to fetch data. Status Code: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    fetch_weather_data()