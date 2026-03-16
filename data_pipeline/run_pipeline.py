import pandas as pd
from config import Config
from api_client import SmardApiClient
from data_processor import DataProcessor

def main():
    print("🚀 Starting SMARD Data Pipeline (2024-2025) with Fallbacks...")
    
    collected_dfs = {} 
    
    for name, config_data in Config.MODULES.items():
        mod_ids = config_data["ids"]
        regions = config_data["regions"]
        print(f"\n➡️ Processing {name} (Trying IDs: {mod_ids})...")
        
        # Step 1: Get Timestamps using the Fallback loop
        valid_id, valid_region, all_timestamps = SmardApiClient.get_timestamps(mod_ids, regions)
        
        if not all_timestamps:
            print(f"   ⚠️ Skipping {name}. API blocked or data unavailable.")
            continue
            
        print(f"   ✅ Found endpoint! Using ID {valid_id} and Region {valid_region}")
            
        # Step 2: Filter to 2024-2025
        target_timestamps = DataProcessor.filter_timestamps_for_period(all_timestamps)
        
        # Step 3: Fetch Data
        all_rows = []
        print(f"   ⬇️ Downloading {len(target_timestamps)} chunks...", end="", flush=True)
        
        for ts in target_timestamps:
            chunk_data = SmardApiClient.fetch_chunk(valid_id, valid_region, ts)
            all_rows.extend(chunk_data)
            
        print(" Done.")
        
        # Step 4: Process into DataFrame
        df = DataProcessor.process_raw_data(all_rows, name)
        if df is not None and not df.empty:
            collected_dfs[name] = df
        else:
            print(f"   ⚠️ No data found in the 2024-2025 range for {name}.")

    # Step 5: Merge & Save
    if not collected_dfs:
        print("\n❌ Pipeline failed. No data collected.")
        return

    print("\n🔄 Merging datasets...")
    df_master = DataProcessor.merge_datasets(collected_dfs)
    
    filename = "../data/energy_data_2024_2025.csv"
    df_master.to_csv(filename)
    
    print("------------------------------------------------")
    print(f"✅ SUCCESS! Data saved to: {filename}")
    print(f"📊 Total Rows: {len(df_master)}")
    print("------------------------------------------------")

if __name__ == "__main__":
    main()