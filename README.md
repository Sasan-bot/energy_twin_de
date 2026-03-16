# EnergyTwin DE ⚡🇩🇪

An AI-powered digital twin and energy optimization assistant for German households. 

## Phase 1: Operational AI & Market Data
This module automatically fetches European Spot Market electricity data (EPEX SPOT) via the SMARD API and uses an XGBoost Machine Learning model to predict day-ahead electricity prices.

### Core Features:
* **Automated Data Pipeline:** Fault-tolerant API client fetching Generation, Load, and Price data.
* **Exploratory Data Analysis:** Jupyter notebooks demonstrating the "Merit Order Effect" and negative pricing on the German grid.
* **Predictive AI:** XGBoost Regressor predicting prices with a €17.56/MWh Mean Absolute Error.

### Setup Instructions
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Fetch the latest data: `python data_pipeline/run_pipeline.py`