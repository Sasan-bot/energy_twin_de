import config 
from data_fetcher import (
    fetch_historical_weather, 
    fetch_smard_prices, 
    fetch_satellite_image, 
    get_coordinates_from_address
)
from roof_analyser import select_roof_manually
from ml_engine import SasanSolarAI
from solar_engine import calculate_architect_analysis
from dashboard import create_professional_dashboard 
import os
import pandas as pd

def main():
    print("\n" + "="*60)
    print("🌍 ENERGY-TWIN: SASAN'S AI SOLAR STRATEGY PLATFORM (v2.0)")
    print("="*60)
    
    # Ensure assets directory exists for dashboard icons and generated images
    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    # --- 1. Dynamic Location & Token Acquisition ---
    mapbox_token = os.getenv('MAPBOX_TOKEN') or getattr(config, 'MAPBOX_TOKEN', None)
    
    if not mapbox_token or "your_" in mapbox_token:
        print("❌ Error: Valid Mapbox Token not found in .env or config.py")
        return

    user_address = input("📍 Enter the installation address (e.g., Street, City): ")
    if not user_address:
        print("⚠️ No address entered. Falling back to default: Bonn, Germany.")
        lat, lon = 50.720966, 7.114855 
    else:
        lat, lon = get_coordinates_from_address(user_address, mapbox_token)
        
    if lat is None or lon is None:
        print("❌ Error: Could not verify location coordinates.")
        return

    # --- 2. Real-Time Market Data Integration (SMARD) ---
    print(f"\n[STEP 1] 📊 Fetching real-time electricity prices from SMARD API...")
    fetch_smard_prices() 

    # --- 3. Satellite Image Acquisition ---
    img_path = fetch_satellite_image(lat, lon, mapbox_token)
    if not img_path: 
        print("❌ Error: Failed to download satellite imagery.")
        return

    # --- 4. Visual Roof Mapping & Geometry ---
    print("\n[STEP 2] 🖱️ ACTION REQUIRED: A window will open. Please define roof boundaries.")
    # Now using the optimized angle-fitting logic from roof_analyser.py
    area_sqm, shadow_sqm, num_panels = select_roof_manually(img_path)
    
    if num_panels == 0:
        print("⚠️ Analysis cancelled or no panels could be fitted.")
        return

    # --- 5. Customer Profile & Consumption Personalization ---
    print("\n[STEP 3] --- PROJECT PERSONALIZATION ---")
    
    # Set defaults
    h_size, e_rating, bill = 4, "D", 200.0
    
    try:
        val_h = input("  > Number of residents (default 4): ")
        if val_h: h_size = int(val_h)
        
        val_e = input("  > Building Energy Rating (A-G, default D): ")
        if val_e: e_rating = val_e.upper()
        
        val_b = input("  > Avg. monthly electricity bill in € (default 200): ")
        if val_b: bill = float(val_b)
        
        # --- Grid Price Management ---
        grid_p_input = input(f"  > Current Grid Price per kWh in € (default {config.AVG_GRID_PRICE}): ")
        if grid_p_input:
            config.AVG_GRID_PRICE = float(grid_p_input)
            print(f"    ✅ Grid Price updated to: {config.AVG_GRID_PRICE} €/kWh")
            
    except ValueError:
        print("  ⚠️ Invalid input detected. Using system defaults for stability.")
    
    # --- 6. Climate Data Synchronization ---
    print(f"\n[STEP 4] ⏳ Fetching {config.HISTORY_YEARS} years of climate data...")
    historical_df = fetch_historical_weather(lat, lon, years=config.HISTORY_YEARS)
    if historical_df is None: 
        print("❌ Error: Climate data synchronization failed.")
        return
    
    # --- 7. AI Engine: XGBoost Training & Yield Forecasting ---
    print("\n[STEP 5] 🧠 AI ENGINE: Training local XGBoost model on historical data...")
    ai_advisor = SasanSolarAI(config.HISTORICAL_DATA_FILE)
    
    # Using our new deterministic prepare_features (fixed seed)
    X, y = ai_advisor.prepare_features(e_rating, h_size)
    
    if X is not None:
        # validate_model_performance is now deterministic
        accuracy, r2 = ai_advisor.validate_model_performance(X, y)
        ml_predicted_yield = ai_advisor.final_prediction(X)
    else:
        print("❌ ML Feature preparation failed.")
        return

    # --- 8. Financial Digital Twin Calculation ---
    print("\n[STEP 6] ⚙️ Calculating Financial Digital Twin...")
    analysis = calculate_architect_analysis(
        ml_annual_yield=ml_predicted_yield, 
        num_panels=num_panels, 
        monthly_bill=bill, 
        energy_rating=e_rating, 
        historical_df=historical_df,
        ai_accuracy_val=accuracy
    )
    
    # Adding extra data for the dashboard
    analysis['roof_area'] = area_sqm
    analysis['shadow_area'] = shadow_sqm
    
    # --- 9. Terminal Audit Summary (Executive Overview) ---
    print("\n" + "█"*60)
    r2_val = r2 if r2 is not None else 0.0
    print(f" 🛡️  AI RISK & PERFORMANCE AUDIT (R2: {r2_val:.4f})")
    print("█"*60)
    print(f" > AI Model Accuracy         : {accuracy:.2f}%")
    print(f" > Applied Grid Price        : {config.AVG_GRID_PRICE} €/kWh")
    print(f" > Total System Capacity     : {analysis['capacity_kwp']:.2f} kWp")
    print(f" > Optimized Panel Count     : {num_panels} Units") # Critical to check after rotation fix
    print(f" > Est. Annual Savings       : {analysis['financials']['annual_savings']:,.2f} €")
    print(f" > 20-Year Net Profit        : {analysis['financials']['twenty_year_profit']:,.2f} €")
    print("-" * 60)
    
    # --- 10. Launching the Strategy Dashboard ---
    print("[STEP 7] 📊 Launching Interactive Strategy Dashboard...")
    print(f"👉 LIVE URL: http://127.0.0.1:{config.DASH_PORT}")
    
    app_instance = create_professional_dashboard(analysis)
    app_instance.run(debug=False, port=config.DASH_PORT)

if __name__ == "__main__":
    main()