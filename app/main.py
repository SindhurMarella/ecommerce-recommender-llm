# app/main.py
import json
import redis
from fastapi import FastAPI, HTTPException
from typing import List
import os
import sys

# Add parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import RecommendedProduct
from app.data_loader import load_data
# We only need explanation and social proof generators now
#from app.recommender import get_content_based_recommendations
from app.recommender import generate_explanation, generate_social_proof
#from app.advanced_recommender import train_collaborative_model, get_collaborative_filtering_recommendations

from fastapi.middleware.cors import CORSMiddleware

# --- App Initialization ---
app = FastAPI(
    title="E-commerce Recommender API",
    description="An API that provides personalized product recommendations using a hybrid model.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global DataFrames & Model ---
# These are defined globally as None first. The startup event will populate them.
# These are still needed for fast lookups of product details
PRODUCTS_DF, USERS_DF, INTERACTIONS_DF = None, None, None
redis_client = None

@app.on_event("startup")
def startup_event():
    """
    On startup, load data into memory and connect to Redis.
    The model training is no longer done here.
    """
    global PRODUCTS_DF, USERS_DF, INTERACTIONS_DF, redis_client
    print("INFO: Application startup: Loading data and and connecting to cache...")
    
    # Load data into the global DataFrames
    PRODUCTS_DF, USERS_DF, INTERACTIONS_DF = load_data()
    
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        redis_client.ping()
        print("INFO: Successfully connected to Redis cache.")
    except redis.exceptions.ConnectionError as e:
        print(f"WARN: Could not connect to Redis. Caching is disabled. {e}")
        redis_client = None

# --- API Endpoints ---
@app.get("/", tags=["Health Check"])
async def root():
    """Simple health check to ensure the server is running."""
    return {"message": "Recommender API is running! Access /docs for documentation."}

@app.get(
    "/recommendations/{user_id}", 
    response_model=List[RecommendedProduct], 
    tags=["Recommendations"]
)

async def get_hybrid_recommendations_for_user(user_id: str, top_n: int = 5):
    """
    Retrieves pre-computed recommendations from the Redis cache for a user.
    This endpoint is now extremely fast.
    """

    if redis_client is None:
        raise HTTPException(status_code=503, detail="Caching service is unavailable.")
    
    if user_id not in USERS_DF['user_id'].values:
        raise HTTPException(status_code=404, detail=f"User ID '{user_id}' not found.")
    
    # 1. Fetch pre-computed product IDs from the Redis cache.
    redis_key = f"user:{user_id}:recommendations"
    cached_ids_json = redis_client.get(redis_key)

    if not cached_ids_json:
        # A "cache miss" means no recommendations were pre-computed for this user.
        return[]
    
    recommended_ids = json.loads(cached_ids_json)

    # 2. Fetch full product details from our in-memory DataFrame
    results_df = PRODUCTS_DF[PRODUCTS_DF['product_id'].isin(recommended_ids)]

    # Preserve the ranked order from Redis
    results_df = results_df.set_index('product_id').loc[recommended_ids].reset_index()

    # 3. Generate explanations and social proofs(fast enough to do on-the-fly)
    final_recommendations = []
    for _, product_row in results_df.iterrows():
        product_dict = product_row.to_dict()

        explanation = generate_explanation(product_dict, user_id, PRODUCTS_DF, INTERACTIONS_DF)
        social_proof = generate_social_proof(product_dict['product_id'], INTERACTIONS_DF)

        rec_product = RecommendedProduct(
            **product_dict,
            explanation=explanation,
            social_proof=social_proof
        )
        final_recommendations.append(rec_product)

    return final_recommendations 
   