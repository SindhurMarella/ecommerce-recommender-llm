# app/main.py

from fastapi import FastAPI, HTTPException
from typing import List
import os
import sys

# Add parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import RecommendedProduct
from app.data_loader import load_data
from app.recommender import get_content_based_recommendations, generate_explanation, generate_social_proof
from app.advanced_recommender import train_collaborative_model, get_collaborative_filtering_recommendations

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
PRODUCTS_DF, USERS_DF, INTERACTIONS_DF = None, None, None

@app.on_event("startup")
def startup_event():
    """
    This function is executed ONLY when the application starts.
    It loads data from MongoDB into the global variables and trains the model.
    """
    global PRODUCTS_DF, USERS_DF, INTERACTIONS_DF
    print("INFO: Application startup: Loading data and training models...")
    
    # Load data into the global DataFrames
    PRODUCTS_DF, USERS_DF, INTERACTIONS_DF = load_data()
    
    if INTERACTIONS_DF.empty or INTERACTIONS_DF is None:
        print("WARN: Interactions data is empty. Cannot train collaborative model.")
    else:
        # Train the model using the loaded data
        train_collaborative_model(INTERACTIONS_DF)

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
    Retrieves hybrid recommendations for a user by combining content-based
    and collaborative filtering models.
    """
    # 1. Validate User and Data
    # The endpoint now correctly reads from the global USERS_DF variable
    if USERS_DF is None or USERS_DF.empty:
        raise HTTPException(status_code=500, detail="Data not loaded or unavailable. Check server logs.")
        
    if user_id not in USERS_DF['user_id'].values:
        raise HTTPException(status_code=404, detail=f"User ID '{user_id}' not found.")
        
    # 2. Get Content-Based Recommendations
    content_recs = get_content_based_recommendations(user_id, top_n=top_n)
    
    # 3. Get Collaborative Filtering Recommendations
    collab_rec_ids = get_collaborative_filtering_recommendations(
        user_id=user_id,
        products_df=PRODUCTS_DF,
        interactions_df=INTERACTIONS_DF,
        top_n=top_n
    )

    # 4. Combine and De-duplicate Results
    final_recommendations_map = {rec.product_id: rec for rec in content_recs}
    
    for product_id in collab_rec_ids:
        if len(final_recommendations_map) >= top_n:
            break # Stop once we have enough recommendations
        if product_id not in final_recommendations_map:
            product_row = PRODUCTS_DF[PRODUCTS_DF['product_id'] == product_id].iloc[0]
            product_dict = product_row.to_dict()
            explanation = generate_explanation(product_dict, user_id)
            rec_product = RecommendedProduct(**product_dict, explanation=explanation)
            final_recommendations_map[product_id] = rec_product

    final_list_without_social_proof = list(final_recommendations_map.values())[:top_n]
    
    # --- Add social proof to each recommendation ---
    final_list_with_social_proof = []
    for rec in final_list_without_social_proof:
        # Call the social proof function for each product recommended.
        social_proof_text = generate_social_proof(rec.product_id, INTERACTIONS_DF)
        # Update the Pydantic model with the social proof text
        rec.social_proof = social_proof_text
        final_list_with_social_proof.append(rec)

    # 5. Return the top N combined recommendations
    return final_list_with_social_proof