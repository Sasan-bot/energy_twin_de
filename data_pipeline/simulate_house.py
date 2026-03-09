import pandas as pd
import numpy as np
import os
import demandlib.bdew as bdew
import datetime

# Note: hplib has specific simulation functions. For this baseline, 
# we will calculate the physics (COP) based on standard hplib principles.
# COP (Coefficient of Performance) = Thermal Energy Output / Electrical Energy Input

def simulate_household_and_heatpump():
    print("🏠 Starting the Physics Engine: Simulating German Household...")

    # 1. Load the Weather Data (The physical environment)
    weather_path = "data/weather_data_2024_2025.csv"
    if not os.path.exists(weather_path):
        print(f"❌ Error: Cannot find {weather_path}. Run fetch_weather.py first.")
        return

    df = pd.read_csv(weather_path, parse_dates=['timestamp'], index_col='timestamp')
    
    # Ensure the index is timezone-aware or naive consistently (SMARD was UTC)
    if df.index.tz is None:
        df.index = df.index.tz_localize('UTC')

    # 2. Simulate Base Household Electricity (demandlib)
    print("   💡 Generating baseline electricity consumption (BDEW H0 Profile)...")
    # We use the standard German BDEW 'H0' profile for households
    # Assuming 4000 kWh annual consumption
    annual_elec_consumption_kwh = 4000 
    
    # demandlib needs the year to generate the profile

    elec_demand = []
    for year in [2024, 2025]:
        # Initialize the standard load profile
        slp = bdew.ElecSlp(year)
        
        # Use the NEW updated demandlib physics method
        profile = slp.get_scaled_power_profiles({'h0': annual_elec_consumption_kwh})
        
        # This new method returns power in kW. 
        # Taking the mean over exactly 1 hour ('h') mathematically converts it perfectly to kWh!
        hourly_profile = profile['h0'].resample('h').mean()
        
        elec_demand.append(hourly_profile)

    # Combine years and align with our weather dataframe
    df['household_elec_demand_kWh'] = pd.concat(elec_demand).values[:len(df)]

    # 3. Simulate Heat Pump Physics
    print("   🌡️ Calculating Heat Pump Efficiency (COP) & Power Draw...")
    
    # Constants for our house
    target_indoor_temp = 20.0 # °C
    heating_flow_temp = 35.0  # °C (Standard for underfloor heating. Radiators would be ~55°C)
    house_heat_loss_coefficient = 150 # W/K (How leaky the house is)
    
    # Calculate Heating Demand: How much thermal energy the house needs to stay at 20°C
    # If outside is warmer than 15°C, heating is off (0 demand).
    df['thermal_heating_demand_kWh'] = np.where(
        df['temperature_2m_C'] < 15.0,
        (target_indoor_temp - df['temperature_2m_C']) * house_heat_loss_coefficient / 1000, 
        0.0
    )

    # Calculate COP based on the Carnot efficiency principle (simplified hplib logic)
    # The colder it is outside, the lower the COP.
    # We add a cap of 5.5 (max efficiency) and floor of 1.0 (pure electric resistance heating)
    temp_difference = heating_flow_temp - df['temperature_2m_C']
    
    # Avoid division by zero or negative differences
    temp_difference = np.maximum(temp_difference, 1.0) 
    
    # Estimated COP curve: higher difference = lower COP
    df['heatpump_COP'] = np.clip(10.0 / np.sqrt(temp_difference), 1.0, 5.5)
    
    # Turn off Heat Pump if there is no heating demand
    df.loc[df['thermal_heating_demand_kWh'] == 0, 'heatpump_COP'] = 0

    # Calculate exactly how much electricity the Heat Pump pulls from the grid!
    # Electricity = Thermal Demand / COP
    df['heatpump_elec_demand_kWh'] = np.where(
        df['heatpump_COP'] > 0,
        df['thermal_heating_demand_kWh'] / df['heatpump_COP'],
        0.0
    )

    # 4. Total House Electricity
    df['total_home_elec_demand_kWh'] = df['household_elec_demand_kWh'] + df['heatpump_elec_demand_kWh']

    # 5. Save the output
    output_file = "data/household_simulation_2024_2025.csv"
    df.to_csv(output_file)
    
    print("\n✅ Simulation Complete!")
    print(f"💾 Saved to: {output_file}")
    print("-" * 50)
    print("📊 Quick Annual Summary (2024):")
    df_2024 = df.loc['2024-01-01':'2024-12-31']
    print(f"Total Household Base Electricity: {df_2024['household_elec_demand_kWh'].sum():.0f} kWh")
    print(f"Total Heat Pump Electricity:      {df_2024['heatpump_elec_demand_kWh'].sum():.0f} kWh")
    print(f"Average Winter COP:               {df_2024.loc[df_2024['temperature_2m_C'] < 5, 'heatpump_COP'].mean():.2f}")
    print("-" * 50)

if __name__ == "__main__":
    simulate_household_and_heatpump()