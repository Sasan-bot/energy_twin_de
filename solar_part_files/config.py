import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- 1. API KEYS & TOKENS (DYNAMIC ACCESS) ---
# Ensure MAPBOX_TOKEN is set in your .env file
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "your_mapbox_token_here")
GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY", "YOUR_KEY") 
OPEN_WEATHER_KEY = os.getenv("OPEN_WEATHER_KEY")

# --- 2. PHYSICAL PV CONSTANTS (2026 TECHNOLOGY SPECS) ---
# Efficiency metrics for N-Type TOPCon solar modules
TEMP_COEFFICIENT = -0.0035    # Power loss per degree Celsius above 25°C
SNOW_THRESHOLD = 0.5          # Snow depth (meters) that halts production
SYSTEM_LOSSES = 0.12          # 12% loss factor (Inverters, cabling, soiling)
PV_LIFESPAN_YEARS = 25        # Standard warranty for high-end German modules

# --- 3. MACHINE LEARNING & LOCATION HISTORY ---
HISTORY_YEARS = 5                      
HISTORICAL_DATA_FILE = "solar_data.csv" 
MODEL_CONFIDENCE_THRESHOLD = 0.85      

# --- 4. SPATIAL CALIBRATION (MAPBOX ZOOM 19) ---
# Crucial: Area covered by a single pixel at Zoom Level 19 in Germany
MAP_ZOOM = 19                          
PIXEL_TO_SQM_COEFF = 0.008264           

# --- 5. PANEL DIMENSIONS (REQUIRED FOR GEOMETRY ENGINE) ---
# Standard 430W-450W Residential Module Dimensions
PANEL_WIDTH = 1.134           
PANEL_HEIGHT = 1.722          
PANEL_GAP = 0.02              # 2cm spacing for mounting and expansion
PANEL_AREA_SQM = PANEL_WIDTH * PANEL_HEIGHT
WATT_PER_PANEL = 440          # High-efficiency 2026 average

# --- 6. DYNAMIC ECONOMIC DATA (GERMANY 2026 FOCUS) ---
AVG_GRID_PRICE = 0.42          # Default German grid price (€/kWh)
FEED_IN_TARIFF = 0.082         # Export remuneration (EEG 2026)
INSTALLATION_COST_PER_KW = 1550.0 
BATTERY_COST_PER_KWH = 580.0   

# Integration Fix: Calculate total upgrade cost for a standard 10kWh ESS
# This matches the variable name used in solar_engine.py
BATTERY_UPGRADE_COST = BATTERY_COST_PER_KWH * 10 

MAINTENANCE_RATE_STD = 0.01    # 1% annual OpEx for PV system
MAINTENANCE_RATE_BATT = 0.015  # 1.5% annual OpEx including battery cycling

# --- 7. ENVIRONMENTAL METRICS ---
CO2_FACTOR_KG_KWH = 0.35       # kg of CO2 per kWh (German Energy Mix 2026)
TREE_CO2_ABSORPTION_KG = 22.0  

# --- 8. DASHBOARD UI AESTHETICS (ENERGY-TWIN THEME) ---
DASH_THEME_DARK = "#050505"    
DASH_CARD_BG = "rgba(25, 25, 25, 0.75)" 
DASH_ACCENT_NEON = "#d4ff00"   
DASH_TEXT_COLOR = "#ffffff"
DASH_GRID_COLOR = "#222222"    
DASH_PORT = 8050               

# --- 9. LOGIC NOTES ---
# 1. BATTERY_UPGRADE_COST is required by solar_engine.py for Scenario B.
# 2. PANEL_AREA_SQM is used to translate ml_yield to total production.