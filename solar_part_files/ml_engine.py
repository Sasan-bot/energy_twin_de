import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import config  
import os

# --- GLOBAL DETERMINISTIC SEED ---
# Ensures that any stochastic operations in NumPy produce identical results every run
np.random.seed(42)

class SasanSolarAI:
    """
    AI Yield Engine: Utilizing XGBoost to forecast solar energy production.
    Updated for strict reproducibility to ensure consistent client reports.
    """
    def __init__(self, csv_path=None):
        self.csv_path = csv_path or config.HISTORICAL_DATA_FILE
        
        # Fixed hyperparameters with random_state and n_jobs=1 for absolute consistency
        self.model = xgb.XGBRegressor(
            n_estimators=500,
            learning_rate=0.03,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='reg:squarederror',
            random_state=42,
            n_jobs=1  # Single-threaded execution prevents tiny floating-point variances
        )

    def prepare_features(self, energy_rating, household_size):
        """
        Transforms raw weather logs into ML-ready features.
        Locked time-logic to prevent month-shifting between runs.
        """
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Historical data missing at {self.csv_path}.")

        df = pd.read_csv(self.csv_path)
        
        # Mapping Building Rating A-G to numerical values
        rating_map = {chr(65+i): i+1 for i in range(7)} 
        rating_val = rating_map.get(energy_rating.upper(), 4)

        features = ['shortwave_radiation', 'temperature_2m', 'cloud_cover']
        X = df[features].copy()
        
        # Strict Month Calculation: Ensures the cycle is always anchored to 24h/365d
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])
            X['month'] = df['time'].dt.month
        else:
            # Deterministic backup: Mapping rows to a fixed 12-month calendar cycle
            X['month'] = ((np.arange(len(df)) % (24 * 365)) // (24 * 30)) + 1
        
        X.loc[:, 'energy_rating'] = rating_val
        X.loc[:, 'household_size'] = household_size
        
        # --- PHYSICAL YIELD SIMULATION TARGET ---
        # Based on 21% Photovoltaic efficiency and temperature degradation
        efficiency_factor = 0.21 
        y = (X['shortwave_radiation'] * 0.001 * efficiency_factor) * \
            (1 - (X['temperature_2m'] - 25).clip(0) * abs(config.TEMP_COEFFICIENT))
        
        # Atmospheric loss adjustment (15% reduction for heavy cloud cover)
        y = y * (1 - (X['cloud_cover'] / 100) * 0.15)
        
        return X, y

    def validate_model_performance(self, X, y):
        """
        Trains the model and returns deterministic Accuracy and R2 metrics.
        """
        # Fixed split ensures the train/test sets are always identical for the same data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        
        predictions = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        # Accuracy calculation normalized by mean of test labels
        accuracy = (1 - (mae / (y_test.mean() + 1e-6))) * 100
        return round(max(0, accuracy), 2), round(r2, 4)

    def final_prediction(self, X):
        """
        Predicts total yield and averages it across the config.HISTORY_YEARS timeframe.
        """
        predictions = self.model.predict(X)
        # Sum is converted to float to avoid numpy-specific type inconsistencies
        total_yield = float(np.sum(predictions))
        annual_avg_yield = total_yield / config.HISTORY_YEARS
        return annual_avg_yield