# batch_recommender.py

import os
import json
import redis
import sys
from dotenv import load_dotenv

# Add the 'app' directory to the Python path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.data_loader import load_data
from app.recommender import get_content_based_recommendations
from app.advanced_recommender import train_collaborative_model, get_collaborative_filtering_recommendations

# --- Configuration & Connections ---
load_dotenv()
TOP_N_RECOMMENDATIONS = 10 # Number of recommendations to pre-compute for each user

# Connect to Redis
try:
    # `decode_responses=True` ensures Redis returns strings, not bytes
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping() # Check the connection
    print("✅ INFO: Successfully connected to Redis.")
except redis.exceptions.ConnectionError as e:
    print(f"❌ FATAL ERROR: Could not connect to Redis. Is the Docker container running? {e}")
    exit()

def run_batch_recommendation_job():
    """
    The main batch processing job. It loads data, trains models,
    generates recommendations for all users, and caches them in Redis.
    """
    print("\n--- Starting Batch Recommendation Job ---")

    # 1. Load all data from MongoDB into pandas DataFrames
    products_df, users_df, interactions_df = load_data()
    if users_df.empty or products_df.empty or interactions_df.empty:
        print("❌ ERROR: Data loading failed or one of the collections is empty. Aborting job.")
        return

    # 2. Train the Collaborative Filtering Model on the full dataset
    train_collaborative_model(interactions_df)
    
    all_user_ids = users_df['user_id'].unique()
    print(f"INFO: Found {len(all_user_ids)} users to process.")

    # 3. Generate and Cache Recommendations for Each User
    recommendations_cached = 0
    for user_id in all_user_ids:
        # --- Run the hybrid logic by calling our refactored functions ---
        
        # Get content-based recommendations (returns a DataFrame)
        content_recs_df = get_content_based_recommendations(
            user_id, products_df, interactions_df, top_n=TOP_N_RECOMMENDATIONS
        )
        content_rec_ids = list(content_recs_df['product_id'])
        
        # Get collaborative filtering recommendations (returns a list of IDs)
        collab_rec_ids = get_collaborative_filtering_recommendations(
            user_id=user_id,
            products_df=products_df,
            interactions_df=interactions_df,
            top_n=TOP_N_RECOMMENDATIONS
        )

        # --- Combine and de-duplicate the IDs ---
        # Start with content-based, as it's a reliable fallback
        final_rec_ids = content_rec_ids
        for pid in collab_rec_ids:
            if pid not in final_rec_ids:
                final_rec_ids.append(pid)
        
        # Ensure we only store the top N recommendations
        final_rec_ids = final_rec_ids[:TOP_N_RECOMMENDATIONS]

        if final_rec_ids:
            # The key is "user:{user_id}:recommendations"
            redis_key = f"user:{user_id}:recommendations"
            # The value is a JSON string representation of the list of product IDs
            redis_client.set(redis_key, json.dumps(final_rec_ids))
            recommendations_cached += 1
    
    print(f"\n--- ✅ Batch Job Complete ---")
    print(f"Successfully pre-computed and cached recommendations for {recommendations_cached} users in Redis.")

# --- Main Execution Block ---
if __name__ == "__main__":
    run_batch_recommendation_job()