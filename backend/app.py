from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import os

app = Flask(__name__)
# Enable CORS so your Flutter app can make requests to this API safely
CORS(app)

print("🧠 Waking up the EnergyTwin AI...")

# 1. Load the XGBoost Model
# Update this path if you saved your model in a different folder!
MODEL_PATH = "../models//xgboost_price_predictor_v1.joblib" 

try:
    # We use absolute pathing to avoid directory confusion
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_model_path = os.path.join(base_dir, MODEL_PATH)
    
    model = joblib.load(full_model_path)
    print("✅ XGBoost Model loaded successfully!")
except FileNotFoundError:
    print(f"⚠️ Warning: Model not found at {full_model_path}.")
    print("The server will start, but predictions will return mock data until the path is fixed.")
    model = None

# 2. Health Check Endpoint
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online",
        "message": "EnergyTwin DE Flask Backend is running!"
    }), 200

# 3. The AI Prediction Endpoint
@app.route('/predict_price', methods=['POST'])
def predict_price():
    try:
        # Get raw data from the mobile app (or our curl test)
        data = request.get_json()
        
        # If the model didn't load, return an error
        if model is None:
            return jsonify({"error": "Model not loaded on server."}), 500

        # 1. Extract base values (with sensible fallbacks just in case)
        load = data.get('Electricity_Load', 60000)
        solar = data.get('Generation_Solar', 15000)
        wind_on = data.get('Generation_Wind_Onshore', 20000)
        wind_off = data.get('Generation_Wind_Offshore', 5000)
        
        hour = data.get('hour', 12)
        day_of_week = data.get('day_of_week', 2)
        month = data.get('month', 6)
        is_weekend = data.get('is_weekend', 0)

        # 2. Re-create your awesome Engineered Features!
        total_renewable = solar + wind_on + wind_off
        renewable_ratio = total_renewable / load if load > 0 else 0

        # 3. Build the exact DataFrame XGBoost expects
        input_dict = {
            'Electricity_Load': [load],
            'Generation_Solar': [solar],
            'Generation_Wind_Onshore': [wind_on],
            'Generation_Wind_Offshore': [wind_off],
            'Total_Renewable': [total_renewable],
            'Renewable_Ratio': [renewable_ratio],
            'hour': [hour],
            'day_of_week': [day_of_week],
            'month': [month],
            'is_weekend': [is_weekend]
        }
        df_input = pd.DataFrame(input_dict)
        
        # Ensure the column order matches the training data perfectly
        expected_cols = [
            'Electricity_Load', 'Generation_Solar', 'Generation_Wind_Onshore', 
            'Generation_Wind_Offshore', 'Total_Renewable', 'Renewable_Ratio', 
            'hour', 'day_of_week', 'month', 'is_weekend'
        ]
        df_input = df_input[expected_cols]

        # 4. Make the real prediction!
        prediction = model.predict(df_input)[0]

        return jsonify({
            "predicted_price_mwh": float(prediction),
            "status": "success"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
# 4. The Investment Advisor Endpoint (Phase 2 Digital Twin)
@app.route('/simulate_investment', methods=['POST'])
def simulate_investment():
    """
    Expects a JSON payload from the Flutter app like:
    {
        "monthly_gas_bill_eur": 150,
        "house_size_sqm": 120
    }
    """
    try:
        data = request.get_json()
        
        # 1. The User's Current Reality
        monthly_gas = data.get('monthly_gas_bill_eur', 150)
        yearly_gas_cost = monthly_gas * 12
        
        # 2. The Digital Twin Baseline (From our simulate_house.py!)
        # Our physics engine proved a standard house needs 5,938 kWh of electricity for heating.
        heatpump_kwh_needed = 5938 
        
        # 3. The "Dumb" Heat Pump Scenario
        # If they don't use your AI, they pay the standard German flat rate (~30 cents/kWh)
        standard_elec_price = 0.30 
        dumb_hp_cost = heatpump_kwh_needed * standard_elec_price
        
        # 4. The "EnergyTwin AI" Scenario
        # Because your XGBoost model shifts the heating to cheap hours (e.g., sunny/windy days),
        # the average price drops significantly (e.g., ~18 cents/kWh).
        smart_elec_price = 0.18
        smart_hp_cost = heatpump_kwh_needed * smart_elec_price
        
        # 5. The ROI Math
        # How much money does your app save them compared to their old gas heater?
        annual_savings = yearly_gas_cost - smart_hp_cost
        
        # Assume an average Heat Pump installation costs €15,000 (after German BAFA subsidies)
        installation_cost = 15000 
        
        # Calculate years to break even
        roi_years = installation_cost / annual_savings if annual_savings > 0 else 99
        
        return jsonify({
            "current_yearly_gas_cost_eur": round(yearly_gas_cost, 2),
            "dumb_heatpump_cost_eur": round(dumb_hp_cost, 2),
            "smart_heatpump_cost_eur": round(smart_hp_cost, 2),
            "ai_annual_savings_eur": round(annual_savings, 2),
            "estimated_roi_years": round(roi_years, 1),
            "status": "success"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
if __name__ == '__main__':
    # Run the server on port 5000
    app.run(debug=True, host='0.0.0.0', port=5001)