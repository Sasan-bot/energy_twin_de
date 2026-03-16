from datetime import datetime

class Config:
    START_MS = int(datetime(2024, 1, 1).timestamp() * 1000)
    END_MS = int(datetime(2025, 12, 31, 23, 59, 59).timestamp() * 1000)
    
    RESOLUTION = "hour"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    # Now using lists so the API client can try multiple combinations
    MODULES = {
        "Wholesale_Prices":       {"ids": [8004169, 4169], "regions": ["DE-LU", "DE"]}, 
        "Electricity_Load":       {"ids": [410],           "regions": ["DE"]},
        "Generation_Solar":       {"ids": [4068],          "regions": ["DE"]},
        "Generation_Wind_Onshore":{"ids": [4067],          "regions": ["DE"]},
        "Generation_Wind_Offshore":{"ids": [1225],         "regions": ["DE"]}
    }