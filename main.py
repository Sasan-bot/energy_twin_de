import config
from data_fetcher import fetch_historical_weather, fetch_smard_prices, fetch_satellite_image
from roof_analyser import select_roof_manually
from ml_engine import SasanSolarAI
from solar_engine import calculate_architect_analysis
from optimizer import generate_architect_report
from dashboard import show_professional_dashboard
import os

def main():
    print("\n" + "="*60)
    print("🌍 ENERGY-TWIN: SASAN'S AI SOLAR STRATEGY PLATFORM (v2.0)")
    print("="*60)
    
    # 1. Location & Token Acquisition
    lat, lon = 50.720966, 7.114855 # Bonn, Germany
    mapbox_token = os.getenv('MAPBOX_TOKEN')
    
    if not mapbox_token or "your_" in mapbox_token:
        mapbox_token = getattr(config, 'MAPBOX_TOKEN', None)
    
    if not mapbox_token or "your_" in mapbox_token:
        print("❌ Error: Valid Mapbox Token not found in Environment or config.py")
        return

    # 2. Satellite Image Acquisition
    img_path = fetch_satellite_image(lat, lon, mapbox_token)
    if not img_path: 
        print("❌ Error: Could not fetch satellite imagery.")
        return

    # 3. Visual Roof Mapping & AI Panel Placement
    print("\n[STEP 1] 🖱️ ACTION REQUIRED: A window will open. Please click to define roof boundaries.")
    area_sqm, shadow_sqm, num_panels = select_roof_manually(img_path)
    
    if num_panels == 0:
        print("⚠️ No panels were placed. Analysis cancelled.")
        return

    # 4. Customer Profile & Personalization
    print("\n[STEP 2] --- PROJECT PERSONALIZATION ---")
    try:
        h_size = int(input("  > Number of residents (default 4): ") or 4)
        e_rating = input("  > Building Energy Rating (A-G, default D): ").upper() or "D"
        bill = float(input("  > Avg. monthly electricity bill in € (default 200): ") or 200.0)
    except ValueError:
        print("  ! Invalid input detected. Using default values.")
        h_size, e_rating, bill = 4, "D", 200.0
    
    # 5. Data Layer - Historical Weather Fetching
    print(f"\n[STEP 3] ⏳ Fetching {config.HISTORY_YEARS} years of high-res weather data for Bonn...")
    historical_df = fetch_historical_weather(lat, lon, years=config.HISTORY_YEARS)
    
    if historical_df is None: 
        print("❌ Error: Could not retrieve historical weather data.")
        return
    
    # 6. ML Brain - XGBoost Training & Prediction
    print("\n[STEP 4] 🧠 AI ENGINE: Analyzing Cloud Cover, Radiation, and Seasonality...")
    ai_advisor = SasanSolarAI(config.HISTORICAL_DATA_FILE)
    X, y = ai_advisor.prepare_features(e_rating, h_size)
    
    # Backtesting for transparency
    accuracy, r2 = ai_advisor.validate_model_performance(X, y)
    ml_predicted_yield = ai_advisor.final_prediction(X)

    # 7. Strategic Optimization & Financial Sync
    # ml_predicted_yield is kWh per sqm, we pass it to engine for total system analysis
    analysis = calculate_architect_analysis(ml_predicted_yield, num_panels, bill, e_rating)
    
    # --- CRITICAL: Syncing savings for the Dashboard Acquisition Roadmap ---
    # We estimate 0.40 EUR/kWh benefit (Grid saving + Feed-in tariff)
    if 'savings' not in analysis['no_battery'] or analysis['no_battery']['savings'] == 0:
        analysis['no_battery']['savings'] = analysis['yield'] * 0.40
    
    if 'savings' not in analysis['with_battery'] or analysis['with_battery']['savings'] == 0:
        # Battery systems usually save more per kWh due to higher self-consumption
        analysis['with_battery']['savings'] = analysis['yield'] * 0.44

    report_data = analysis['no_battery'] 
    strategic_advice = generate_architect_report(analysis, accuracy, e_rating)
    
    # 8. Terminal Report Display (Technical & Risk)
    print("\n" + "█"*60)
    print(f" 🛡️  AI RISK & PERFORMANCE AUDIT (Bonn, Germany) ")
    print("█"*60)
    print(f" [AI VALIDATION METRICS] ")
    print(f" > Model Backtesting Accuracy : {accuracy}%")
    print(f" > Reliability Score (R2)     : {r2}")
    print("-" * 60)
    print(f" [TECHNICAL CORE SPECS] ")
    print(f" > Annual Predicted Yield     : {analysis['yield']:,.0f} kWh")
    print(f" > System Nameplate Capacity  : {analysis['capacity_kwp']:.2f} kWp")
    print(f" > Optimized Panel Count      : {num_panels} Units (430W N-Type)")
    print("-" * 60)
    print(f" [FINANCIAL PREVIEW - STANDARD] ")
    print(f" > Total Capital Investment   : {report_data.get('invest', 0):,.0f} €")
    print(f" > Est. Annual Net Savings    : {report_data.get('savings', 0):,.0f} €")
    print(f" > Payback Period (ROI)       : {report_data.get('payback', 0):.1f} Years")
    
    sc_val = report_data.get('sc_rate', report_data.get('self_consumption_rate', 0))
    print(f" > Self-Consumption Rate      : {sc_val:.1f}%") 
    
    print("-" * 60)
    print(f" [AI STRATEGIC ADVICE] ")
    for i, tip in enumerate(strategic_advice, 1):
        print(f" {i}. 💡 {tip}")
    print("="*60)
    print(f"🍀 ECO IMPACT: Offsetting {analysis['co2_saved']:.2f} tons of CO2 per year.")
    print("="*60 + "\n")

    # 9. Launch High-End Visual Dashboard
    print("[STEP 5] 📊 Generating Visual Strategy Report...")
    show_professional_dashboard(analysis)

if __name__ == "__main__":
    main()