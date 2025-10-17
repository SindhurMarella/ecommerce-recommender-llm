# # app/test_recommender.py

import sys
import os
# CRITICAL FIX: Add the project root to the path so 'app' imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.recommender import get_content_based_recommendations
from app.models import RecommendedProduct # We use the model for type hinting

print('--- Starting Recommendation Logic Test ---')

# Test Case 1: Alice (U001) - Should recommend items in her recent purchase category (Homeware, Book)
USER_ALICE = "U001"
print(f"\n--- Recommendations for {USER_ALICE} (Alice) ---")
alice_recs: list[RecommendedProduct] = get_content_based_recommendations(USER_ALICE)

if alice_recs:
    for product in alice_recs:
        print(f"- {product.name} (Category: {product.category})")
        # Print the LLM explanation if available (may be generic if API key is not set)
        print(f"  > Explanation: {product.explanation[:50]}...")
else:
    print(f"No recommendations found for {USER_ALICE}. (Check data patterns)")

# Test Case 2: Bob (U002) - Should recommend items in his recent purchase category (Electronics, Tool)
USER_BOB = "U002"
print(f"\n--- Recommendations for {USER_BOB} (Bob) ---")
bob_recs: list[RecommendedProduct] = get_content_based_recommendations(USER_BOB)

if bob_recs:
    for product in bob_recs:
        print(f"- {product.name} (Category: {product.category})")
        print(f"  > Explanation: {product.explanation[:50]}...")
else:
    print(f"No recommendations found for {USER_BOB}. (Check data patterns)")
    
print('\n--- Test Complete ---')


# import pandas as pd
# import os
# from typing import Tuple
# print('Testing recommendation')

# # Define the path to the data directory (relative to project root)
# # os.path.dirname(__file__) is the 'app' directory
# # '..' goes up one level to the project root
# DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# # Explicit column definitions for robustness against Excel formatting issues
# INTERACTIONS_COLUMNS = ['interaction_id', 'user_id', 'product_id', 'type', 'timestamp']
# PRODUCTS_COLUMNS = ['product_id', 'name', 'category', 'price', 'description']
# USERS_COLUMNS = ['user_id', 'name', 'created_at']

# def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
#     """
#     Loads all mock data into Pandas DataFrames.
    
#     Includes robust handling for column naming and ensures data types are correct
#     for the recommendation logic.
#     """
#     try:
#         # --- 1. Load Products Data ---
#         products = pd.read_csv(os.path.join(DATA_DIR, 'products.csv'), header=None, sep=',')
#         products.columns = PRODUCTS_COLUMNS
#         products.columns = products.columns.str.strip() # Safety strip

#         # --- 2. Load Users Data ---
#         users = pd.read_csv(os.path.join(DATA_DIR, 'users.csv'), header=None, sep=',')
#         users.columns = USERS_COLUMNS
#         users.columns = users.columns.str.strip()
        
#         # --- 3. Load Interactions Data (CRITICAL FIX) ---
#         # Read the CSV without a header (header=None) and specify the separator (sep=',')
#         interactions = pd.read_csv(
#             os.path.join(DATA_DIR, 'interactions.csv'), 
#             header=None,
#             sep=',' 
#         )
#         # Assign the correct column names manually
#         interactions.columns = INTERACTIONS_COLUMNS
#         interactions.columns = interactions.columns.str.strip()

#         # --- 4. Post-Processing ---
#         # Convert 'timestamp' column to datetime objects (needed for sorting)
#         # errors='coerce' turns unparseable dates into NaT (Not a Time)
#         interactions['timestamp'] = pd.to_datetime(interactions['timestamp'], errors='coerce')
        
#         # Drop any rows where the timestamp couldn't be parsed
#         interactions = interactions.dropna(subset=['timestamp'])

#         # Sort interactions by time (most recent first)
#         interactions = interactions.sort_values(by='timestamp', ascending=False)
#         return products, users, interactions

#     except FileNotFoundError as e:
#         print(f"Error loading data: {e}. Check your 'data' folder and file names.")
#         # Return empty dataframes for graceful failure
#         return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
#     except Exception as e:
#         print(f"An unexpected error occurred during data loading: {e}")
#         return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()