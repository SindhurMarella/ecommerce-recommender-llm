import os
import random
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from faker import Faker
from datetime import datetime, timedelta

# --- Configuration ---
NUM_USERS = 200
NUM_PRODUCTS = 150
NUM_INTERACTIONS = 5000  # More interactions for a denser dataset
DB_NAME = "ecommerce_recommender"

# Load environment variables from .env file
load_dotenv()
MDB_URI = os.getenv("MDB_URI")

if not MDB_URI:
    print("FATAL ERROR: MDB_URI not found in .env file.")
    exit()

# Initialize Faker for user names
fake = Faker()

# --- MongoDB Connection ---
try:
    client = MongoClient(MDB_URI)
    db = client[DB_NAME]
    
    # Define collections
    users_col = db["users"]
    products_col = db["products"]
    interactions_col = db["interactions"]

    # Clear old data for a fresh start
    users_col.drop()
    products_col.drop()
    interactions_col.drop()
    print(f"INFO: Cleared old collections in database: {DB_NAME}")

except Exception as e:
    print(f"FATAL ERROR: Could not connect to MongoDB or drop collections: {e}")
    exit()

# --- Realistic Product Generation Data ---
REALISTIC_PRODUCTS = {
    'Electronics': {
        'base_names': ['Digital Camera', 'Bluetooth Speaker', 'Gaming Mouse', 'Smart Watch', 'Noise-Cancelling Headphones', 'Portable Charger', '4K Monitor'],
        'adjectives': ['Wireless', 'Smart', 'High-Speed', 'Compact', 'Ultra-HD', 'Ergonomic']
    },
    'Book': {
        'base_names': ['Sci-Fi Novel', 'Cookbook', 'Mystery Thriller', 'History of Ancient Rome', 'Python Programming Guide'],
        'adjectives': ['Hardcover', 'First Edition', 'Illustrated', 'Abridged', 'Bestselling']
    },
    'Apparel': {
        'base_names': ['Cotton T-Shirt', 'Denim Jeans', 'Leather Jacket', 'Running Shoes', 'Winter Scarf'],
        'adjectives': ['Vintage', 'Organic', 'Slim-Fit', 'Designer', 'Weatherproof']
    },
    'Homeware': {
        'base_names': ['Coffee Mug Set', 'Scented Candle', 'Plush Bath Towel', 'Non-stick Frying Pan', 'Bookshelf'],
        'adjectives': ['Artisan', 'Ergonomic', 'Minimalist', 'Rustic', 'Modern']
    }
}

# --- 1. Generate PRODUCTS ---
def generate_products():
    products = []
    product_id_counter = 1
    
    while len(products) < NUM_PRODUCTS:
        for category, details in REALISTIC_PRODUCTS.items():
            if len(products) >= NUM_PRODUCTS:
                break
            
            base_name = random.choice(details['base_names'])
            adjective = random.choice(details['adjectives'])
            
            product_name = f"{adjective} {base_name}"
            description = f"A high-quality, {adjective.lower()} {base_name.lower()} from our exclusive {category} collection."

            products.append({
                "product_id": f"P{product_id_counter:04d}",
                "name": product_name,
                "category": category,
                "price": round(random.uniform(15.0, 450.0), 2),
                "description": description,
                "created_at": fake.date_time_this_year()
            })
            product_id_counter += 1
            
    products_col.insert_many(products)
    print(f"INFO: Successfully inserted {len(products)} realistic products.")
    return products

# --- 2. Generate USERS ---
def generate_users():
    users = []
    for i in range(NUM_USERS):
        users.append({
            "user_id": f"U{i+1:03d}",
            "name": fake.name(),
            "created_at": fake.date_time_this_year()
        })
    users_col.insert_many(users)
    print(f"INFO: Successfully inserted {len(users)} users.")
    return users

# --- 3. Generate INTERACTIONS ---
def generate_interactions(users_data, products_data):
    interactions = []
    interaction_types = ['view', 'purchase', 'add_to_cart']
    user_ids = [u['user_id'] for u in users_data]
    product_ids = [p['product_id'] for p in products_data]

    # Simulate Bestsellers: 10% of products get 40% of interactions
    num_popular_products = int(len(product_ids) * 0.1)
    popular_product_ids = random.sample(product_ids, num_popular_products)
    
    # Simulate User Affinity: Each user has a "favorite" category
    user_profiles = {uid: {'favorite_category': random.choice(list(REALISTIC_PRODUCTS.keys()))} for uid in user_ids}
    products_df = pd.DataFrame(products_data)

    for i in range(NUM_INTERACTIONS):
        interaction_type = random.choices(interaction_types, weights=[5, 2, 3], k=1)[0]
        user_id = random.choice(user_ids)
        
        # Simulate realistic choices
        if random.random() < 0.4:  # 40% chance to interact with a popular item
            product_id = random.choice(popular_product_ids)
        elif random.random() < 0.7: # 30% chance to pick from user's favorite category
            fav_category = user_profiles[user_id]['favorite_category']
            possible_pids = products_df[products_df['category'] == fav_category]['product_id'].tolist()
            product_id = random.choice(possible_pids) if possible_pids else random.choice(product_ids)
        else: # Otherwise, choose randomly
            product_id = random.choice(product_ids)

        interactions.append({
            "interaction_id": i + 1,
            "user_id": user_id,
            "product_id": product_id,
            "type": interaction_type,
            "timestamp": datetime.now() - timedelta(days=random.randint(0, 90))
        })
        
    interactions_col.insert_many(interactions)
    print(f"INFO: Successfully inserted {len(interactions)} realistic interactions.")

# --- Main Execution ---
if __name__ == "__main__":
    print("\n--- Starting Realistic Data Generation into MongoDB ---")
    
    products = generate_products()
    users = generate_users()
    generate_interactions(users, products)
    
    print("\n--- MongoDB Data Generation Complete ---")
    client.close()
    print("You can now run 'uvicorn app.main:app --reload' to test the API.")