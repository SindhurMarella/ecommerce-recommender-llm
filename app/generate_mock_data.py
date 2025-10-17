import pandas as pd
from datetime import datetime
import os
import numpy as np

# --- Configuration ---
NUM_USERS = 5
NUM_PRODUCTS = 12
NUM_INTERACTIONS = 50
DATA_DIR = 'data'

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# 1. Generate PRODUCTS Data
def generate_products(num):
    """Generates mock product data with rich descriptions."""
    
    categories = ['Book', 'Electronics', 'Homeware', 'Apparel', 'Tool', 'Health']
    
    products = []
    descriptions = [
        "A comprehensive guide to modern data science techniques.",
        "Wireless noise-cancelling headphones with superior sound quality.",
        "Ergonomic coffee mug, perfect for long working sessions.",
        "Lightweight, breathable running shirt made from recycled materials.",
        "Multi-function power drill with a long-lasting lithium battery.",
        "Advanced fitness tracker watch with heart rate and sleep monitoring.",
        "Best-selling fantasy novel, first book in the 'Ember Saga'.",
        "Fast-charging power bank for mobile devices.",
        "Set of artisanal scented candles for a relaxing atmosphere.",
        "Stylish quick-dry hiking shorts for summer adventures.",
        "High-precision laser level for construction and DIY projects.",
        "Protein powder blend optimized for recovery."
    ]

    for i in range(num):
        product_id = f"P{i+1:03d}"
        name = descriptions[i % len(descriptions)].split(',')[0].strip() 
        category = categories[i % len(categories)]
        price = round(np.random.uniform(10, 300), 2)
        description = descriptions[i % len(descriptions)]
        
        products.append({
            'product_id': product_id, 
            'name': name, 
            'category': category, 
            'price': price, 
            'description': description
        })
        
    return pd.DataFrame(products)

# 2. Generate USERS Data
def generate_users(num):
    """Generates mock user data."""
    users = []
    start_date = datetime(2024, 1, 1)
    
    for i in range(num):
        user_id = f"U{i+1:03d}"
        name = f"User{i+1}"
        created_at = start_date + pd.Timedelta(days=np.random.randint(1, 100))
        users.append({'user_id': user_id, 'name': name, 'created_at': created_at.strftime('%Y-%m-%d')})
        
    return pd.DataFrame(users)

# 3. Generate INTERACTIONS Data
def generate_interactions(users_df, products_df, num):
    """Generates mock interaction data, focusing on creating clear user patterns."""
    
    user_ids = users_df['user_id'].tolist()
    product_ids = products_df['product_id'].tolist()
    
    interactions = []
    interaction_types = ['view'] * 4 + ['purchase'] * 1 + ['add_to_cart'] * 1 # Weighted types
    start_time = datetime(2025, 10, 1)

    for i in range(1, num + 1):
        user_id = np.random.choice(user_ids)
        product_id = np.random.choice(product_ids)
        interaction_type = np.random.choice(interaction_types)
        timestamp = start_time + pd.Timedelta(hours=i * 2 + np.random.randint(0, 12))
        
        interactions.append({
            'interaction_id': i,
            'user_id': user_id,
            'product_id': product_id,
            'type': interaction_type,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })

    # --- Inject Specific Test Patterns for Alice (U001) ---
    # Alice (U001) likes Books (P001, P007) and Homeware (P003, P009)
    interactions.append({'interaction_id': num + 1, 'user_id': 'U001', 'product_id': 'P001', 'type': 'purchase', 'timestamp': (start_time + pd.Timedelta(hours=100)).strftime('%Y-%m-%d %H:%M:%S')}) # Book
    interactions.append({'interaction_id': num + 2, 'user_id': 'U001', 'product_id': 'P003', 'type': 'purchase', 'timestamp': (start_time + pd.Timedelta(hours=101)).strftime('%Y-%m-%d %H:%M:%S')}) # Homeware

    # Bob (U002) likes Electronics (P002, P006) and Tools (P005, P011)
    interactions.append({'interaction_id': num + 3, 'user_id': 'U002', 'product_id': 'P002', 'type': 'purchase', 'timestamp': (start_time + pd.Timedelta(hours=102)).strftime('%Y-%m-%d %H:%M:%S')}) # Electronics
    interactions.append({'interaction_id': num + 4, 'user_id': 'U002', 'product_id': 'P005', 'type': 'view', 'timestamp': (start_time + pd.Timedelta(hours=103)).strftime('%Y-%m-%d %H:%M:%S')}) # Tool


    return pd.DataFrame(interactions).sort_values(by='timestamp', ascending=False)


if __name__ == "__main__":
    
    print("Generating mock data...")
    
    products_df = generate_products(NUM_PRODUCTS)
    users_df = generate_users(NUM_USERS)
    interactions_df = generate_interactions(users_df, products_df, NUM_INTERACTIONS)

    # Save to CSV using the to_csv method, which guarantees correct formatting
    products_df.to_csv(os.path.join(DATA_DIR, 'products.csv'), index=False)
    users_df.to_csv(os.path.join(DATA_DIR, 'users.csv'), index=False)
    interactions_df.to_csv(os.path.join(DATA_DIR, 'interactions.csv'), index=False)
    
    print(f"Successfully generated {NUM_PRODUCTS} products, {NUM_USERS} users, and {len(interactions_df)} interactions.")
    print(f"Files saved in the '{DATA_DIR}' directory.")
    print("You can now run 'uvicorn app.main:app --reload' to test the API.")
