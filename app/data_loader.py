# app/data_loader.py

import pandas as pd
import os
from typing import Tuple

# Define the path to the data directory (relative to project root)
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# Explicit column definitions for robustness against manual/Excel formatting issues
INTERACTIONS_COLUMNS = ['interaction_id', 'user_id', 'product_id', 'type', 'timestamp']
PRODUCTS_COLUMNS = ['product_id', 'name', 'category', 'price', 'description']
USERS_COLUMNS = ['user_id', 'name', 'created_at']

def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Loads all mock data into Pandas DataFrames.
    
    Uses robust methods (header=None, sep=',') to handle common CSV formatting errors
    and includes debugging prints to identify which file is failing.
    """
    try:
        # --- 1. Load Products Data ---
        print("DEBUG: Attempting to load products.csv...") 
        products = pd.read_csv(os.path.join(DATA_DIR, 'products.csv'), header=None, sep=',')
        products.columns = PRODUCTS_COLUMNS
        products.columns = products.columns.str.strip() 

        # --- 2. Load Users Data ---
        print("DEBUG: Attempting to load users.csv...") 
        users = pd.read_csv(os.path.join(DATA_DIR, 'users.csv'), header=None, sep=',')
        users.columns = USERS_COLUMNS
        users.columns = users.columns.str.strip()
        
        # --- 3. Load Interactions Data ---
        print("DEBUG: Attempting to load interactions.csv...") 
        interactions = pd.read_csv(
            os.path.join(DATA_DIR, 'interactions.csv'), 
            header=None,
            sep=',' 
        )
        interactions.columns = INTERACTIONS_COLUMNS
        interactions.columns = interactions.columns.str.strip()

        # --- 4. Post-Processing ---
        # Convert 'timestamp' column to datetime objects
        interactions['timestamp'] = pd.to_datetime(interactions['timestamp'], errors='coerce')
        interactions = interactions.dropna(subset=['timestamp'])

        # Sort interactions by time (most recent first)
        interactions = interactions.sort_values(by='timestamp', ascending=False)
        
        print("DEBUG: Data loaded successfully.")
        return products, users, interactions

    except FileNotFoundError as e:
        print(f"Error loading data: {e}. Check your 'data' folder and file names.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        # This will now clearly tell us where the 'No columns to parse' error happened.
        print(f"An unexpected error occurred during data loading: {e}. Check the last DEBUG print to identify the failing file.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
