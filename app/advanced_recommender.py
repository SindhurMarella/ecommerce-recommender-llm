# app/advanced_recommender.py

import pandas as pd
from surprise import Dataset, Reader, SVD

# This global variable will hold our trained model in memory
COLLAB_MODEL = None

def train_collaborative_model(interactions_df: pd.DataFrame):
    """
    Trains an SVD collaborative filtering model on the user-item interaction data.
    """
    global COLLAB_MODEL
    print("INFO: Starting Collaborative filtering model training...")

    # We need to create "ratings" from interactions. Let's assign weights.
    interaction_strength = {
        'view': 1.0,
        'add_to_cart': 2.0,
        'purchase': 3.0, # <-- BUG FIX: Changed 'purchased' to 'purchase' to match data
    }

    # Create a 'rating' column based on interaction type
    interactions_df['rating'] = interactions_df['type'].map(interaction_strength)
    
    # Drop any interactions that didn't map to a rating (if any)
    rated_interactions = interactions_df.dropna(subset=['rating'])

    # The 'surprise' library needs data in a specific format
    reader = Reader(rating_scale=(1, 3))
    data = Dataset.load_from_df(rated_interactions[['user_id', 'product_id', 'rating']], reader)

    # Build a training set from the entire dataset
    trainset = data.build_full_trainset()

    # Use the SVD Algorithm
    algo = SVD()
    algo.fit(trainset)

    COLLAB_MODEL = algo
    print("INFO: Collaborative model trained successfully.")
    return COLLAB_MODEL

def get_collaborative_filtering_recommendations(user_id: str, products_df: pd.DataFrame, interactions_df: pd.DataFrame, top_n: int = 10) -> list:
    """
    Generates product recommendations for a user using the trained collaborative model. 
    """
    if COLLAB_MODEL is None:
        print("WARN: Collaborative model not trained yet. Skipping.")
        return []
    
    # Get a list of all the product IDs the user has already interacted with
    interacted_product_ids = interactions_df[interactions_df['user_id'] == user_id]['product_id'].unique()

    # Get a list of all the product IDs they have NOT interacted with
    all_product_ids = products_df['product_id'].unique()
    unseen_product_ids = [pid for pid in all_product_ids if pid not in interacted_product_ids]

    # Predict a "rating" for all unseen products
    predictions = [COLLAB_MODEL.predict(uid=user_id, iid=pid) for pid in unseen_product_ids]

    # Sort the predictions by estimated rating in descending order
    predictions.sort(key=lambda x: x.est, reverse=True)

    # Get the top N product IDs
    recommended_product_ids = [pred.iid for pred in predictions[:top_n]]

    print(f"DEBUG: Collaborative filtering recommends: {recommended_product_ids}")
    return recommended_product_ids