# app/main.py

from fastapi import FastAPI, HTTPException
from app.recommender import get_content_based_recommendations, USERS_DF
from app.models import RecommendedProduct
from typing import List

from fastapi.middleware.cors import CORSMiddleware



# Initialize the FastAPI application
# Include a title and description for the auto-generated documentation (/docs)
app = FastAPI(
    title="E-commerce Recommender API",
    description="Provides product recommendations and LLM-generated explanations (Placeholder currently active).",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health Check"])
async def root():
    """Simple health check to ensure the server is running."""
    return {"message": "Recommender API is running! Access /docs for documentation."}

# --- Recommendation Endpoint ---
@app.get(
    "/recommendations/{user_id}", 
    # Use the RecommendedProduct model for guaranteed output structure
    response_model=List[RecommendedProduct], 
    tags=["Recommendations"]
)
async def get_recommendations_for_user(user_id: str):
    """
    Retrieves recommended products for a specific user based on the content-based logic.
    """
    # 1. Check if the user exists in the DataFrame before attempting logic
    if USERS_DF.empty:
        raise HTTPException(status_code=500, detail="Data loading failed on server startup.")
        
    if user_id not in USERS_DF['user_id'].values:
        raise HTTPException(status_code=404, detail=f"User ID '{user_id}' not found.")
        
    # 2. Call the core recommendation logic
    recommendations = get_content_based_recommendations(user_id, top_n=3)
    
    if not recommendations:
        # If the recommendation engine returns an empty list, return an empty list gracefully
        return []
        
    return recommendations
