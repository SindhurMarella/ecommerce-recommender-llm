# app/data_loader.py

import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
MDB_URI = os.getenv("MDB_URI")
DB_NAME = "ecommerce_recommender"

def load_data():
    """
    Connects to the MongoDB database and loads the products, users, and 
    interactions collections into pandas DataFrames.
    """
    if not MDB_URI:
        print("FATAL ERROR: MDB_URI not found. Please set it in your .env file.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    client = None  # Initialize client to None
    try:
        print("INFO: Connecting to MongoDB...")
        client = MongoClient(MDB_URI)
        db = client[DB_NAME]
        
        # Load collections into pandas DataFrames
        print("INFO: Loading 'products' collection...")
        products_df = pd.DataFrame(list(db.products.find()))
        
        print("INFO: Loading 'users' collection...")
        users_df = pd.DataFrame(list(db.users.find()))
        
        print("INFO: Loading 'interactions' collection...")
        interactions_df = pd.DataFrame(list(db.interactions.find()))

        # --- Data Cleaning & Preparation ---
        # Drop the default MongoDB '_id' column as it's not needed
        if '_id' in products_df.columns:
            products_df.drop('_id', axis=1, inplace=True)
        if '_id' in users_df.columns:
            users_df.drop('_id', axis=1, inplace=True)
        if '_id' in interactions_df.columns:
            interactions_df.drop('_id', axis=1, inplace=True)

        # Convert timestamp to datetime objects for proper sorting
        if not interactions_df.empty:
            interactions_df['timestamp'] = pd.to_datetime(interactions_df['timestamp'])

        print("INFO: Data loaded and prepared successfully.")
        
        return products_df, users_df, interactions_df

    except Exception as e:
        print(f"FATAL ERROR: Could not load data from MongoDB: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    finally:
        if client:
            client.close()
            print("INFO: MongoDB connection closed.")