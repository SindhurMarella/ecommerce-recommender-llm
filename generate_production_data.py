import os
from dotenv import load_dotenv
from pymongo import MongoClient
from faker import Faker
import random
from datetime import datetime, timedelta

# --- Configuration ---
NUM_USERS = 50
NUM_PRODUCTS = 100
NUM_INTERACTIONS = 500
DB_NAME = "ecommerce_recommender"

# Load environment variables
load_dotenv()
MDB_URI = os.getenv("MDB_URI")

if not MDB_URI:
    print("FATAL ERROR: MDB_URI not found. Please set it in your .env file.")
    exit()

# Initialize Faker
fake = Faker()

# --- MongoDB Connection ---
try:
    client = MongoClient(MDB_URI)
    db = client[DB_NAME]
    
    # Define collection names (to clear them before generation)
    users_col = db["users"]
    products_col = db["products"]
    interactions_col = db["interactions"]

    # Clear old data
    users_col.drop()
    products_col.drop()
    interactions_col.drop()
    print(f"DEBUG: Cleared old collections in database: {DB_NAME}")

except Exception as e:
    print(f"FATAL ERROR: Could not connect to MongoDB or drop collections: {e}")
    exit()

# --- Helper Lists ---
CATEGORIES = ['Electronics', 'Book', 'Apparel', 'Homeware', 'Tool', 'Health', 'Toy', 'Software']
PRODUCT_ADJECTIVES = ['Premium', 'Ergonomic', 'Wireless', 'Smart', 'Vintage', 'High-Speed', 'Organic']

# --- 1. Generate PRODUCTS ---
# --- Helper Lists & Dictionaries ---
CATEGORIES = ['Electronics', 'Book', 'Apparel', 'Homeware', 'Tool', 'Health', 'Toy']
PRODUCT_ADJECTIVES = ['Premium', 'Ergonomic', 'Wireless', 'Smart', 'Vintage', 'Heavy-Duty', 'Organic', 'Compact']

# A dictionary of realistic product names for each category
REALISTIC_PRODUCTS = {
    'Electronics': ['Digital Camera', 'Bluetooth Speaker', 'Gaming Mouse', 'Smart Watch', 'Noise-Cancelling Headphones', 'Portable Charger'],
    'Book': ['Sci-Fi Novel', 'Cookbook', 'Mystery Thriller', 'History of Ancient Rome', 'Python Programming Guide'],
    'Apparel': ['Cotton T-Shirt', 'Denim Jeans', 'Leather Jacket', 'Running Shoes', 'Winter Scarf'],
    'Homeware': ['Coffee Mug Set', 'Scented Candle', 'Plush Bath Towel', 'Non-stick Frying Pan', 'Bookshelf'],
    'Tool': ['Cordless Drill', 'Hammer', 'Wrench Set', 'Screwdriver Kit', 'Measuring Tape'],
    'Health': ['Yoga Mat', 'Vitamin D Supplements', 'Electric Toothbrush', 'Digital Scale', 'Foam Roller'],
    'Toy': ['LEGO Starship Set', 'Jigsaw Puzzle', 'Remote Control Car', 'Stuffed Animal', 'Board Game']
}

# --- 1. Generate PRODUCTS (REVISED FUNCTION) ---
def generate_products():
    products = []
    product_id_counter = 1
    
    # Loop until we have enough products
    while len(products) < NUM_PRODUCTS:
        for category, names in REALISTIC_PRODUCTS.items():
            if len(products) >= NUM_PRODUCTS:
                break # Stop if we've hit our target number
            
            base_name = random.choice(names)
            adjective = random.choice(PRODUCT_ADJECTIVES)
            
            # Create a more realistic product name
            product_name = f"{adjective} {base_name}"
            
            # Create a contextually relevant description
            description = f"A high-quality, {adjective.lower()} {base_name} from our {category} collection. Excellent for personal use or as a gift."

            products.append({
                "product_id": f"P{product_id_counter:04d}",
                "name": product_name,
                "category": category,
                "price": round(random.uniform(10.0, 500.0), 2),
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
def generate_interactions(user_ids, product_ids):
    interactions = []
    interaction_types = ['view', 'purchase', 'add_to_cart']
    start_date = datetime.now() - timedelta(days=90)

    for i in range(NUM_INTERACTIONS):
        interaction_type = random.choices(interaction_types, weights=[6, 3, 1], k=1)[0]
        user_id = random.choice(user_ids)
        
        # Bias interactions: 20% of the time, choose a product from a user's recent purchase category
        if random.random() < 0.2 and interaction_type == 'purchase':
             # Skip complicated bias logic for simplicity, just ensure a mix of IDs
             product_id = random.choice(product_ids)
        else:
             product_id = random.choice(product_ids)

        timestamp = start_date + timedelta(seconds=random.randint(0, int(timedelta(days=90).total_seconds())))

        interactions.append({
            "interaction_id": i + 1,
            "user_id": user_id,
            "product_id": product_id,
            "type": interaction_type,
            "timestamp": timestamp 
        })
        
    interactions_col.insert_many(interactions)
    print(f"INFO: Successfully inserted {len(interactions)} interactions.")

# --- Main Execution ---
if __name__ == "__main__":
    
    print("\n--- Starting Production Data Generation into MongoDB ---")
    
    # 1. Generate and Insert Products
    products_data = generate_products()
    
    # 2. Generate and Insert Users
    users_data = generate_users()
    
    # 3. Generate and Insert Interactions
    user_ids = [u['user_id'] for u in users_data]
    product_ids = [p['product_id'] for p in products_data]
    generate_interactions(user_ids, product_ids)
    
    print("\n--- MongoDB Data Generation Complete ---")
    client.close()