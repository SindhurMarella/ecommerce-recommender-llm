# app/recommender.py

import pandas as pd
from typing import List

# Import the necessary Pydantic models and data loader
from app.data_loader import load_data
from app.models import RecommendedProduct 

# Load data once at the start. This ensures the data is ready for API requests.
PRODUCTS_DF, USERS_DF, INTERACTIONS_DF = load_data()

def get_content_based_recommendations(user_id: str, top_n: int = 3) -> List[RecommendedProduct]:
    """
    Recommends products based on the category of the user's most recent purchase 
    (Content-Based Filtering MVP).
    
    This function returns a list of RecommendedProduct models, including a 
    placeholder explanation that will be replaced by the LLM in Day 4.
    """
    global PRODUCTS_DF, USERS_DF, INTERACTIONS_DF
    
    # Check if data loading was successful
    if PRODUCTS_DF.empty:
        return [] 

    # --- 1. CORE RECOMMENDATION LOGIC ---
    user_purchases = INTERACTIONS_DF[
        (INTERACTIONS_DF['user_id'] == user_id) & 
        (INTERACTIONS_DF['type'] == 'purchase')
    ]

    # Decide which product set to recommend
    if user_purchases.empty:
        # Fallback: Recommend the top 3 overall products if the user has no purchase history
        recommended_products_df = PRODUCTS_DF.head(top_n)
        target_category = "General Popularity"
        
    else:
        # 1. Find the most recently purchased product's category
        recent_product_id = user_purchases['product_id'].iloc[0]
        recent_product_row = PRODUCTS_DF[PRODUCTS_DF['product_id'] == recent_product_id].iloc[0]
        target_category = recent_product_row['category']
        
        # 2. Find products in the same category the user hasn't purchased
        recommended_products_df = PRODUCTS_DF[
            (PRODUCTS_DF['category'] == target_category) & 
            (~PRODUCTS_DF['product_id'].isin(user_purchases['product_id']))
        ]
        
        # 3. Take the top N 
        recommended_products_df = recommended_products_df.head(top_n)

    
    # --- 2. CONVERSION TO API MODEL (with placeholder explanation) ---
    final_recommendations = []
    
    for _, product_row in recommended_products_df.iterrows():
        product_dict = product_row.to_dict()
        
        # Convert to RecommendedProduct and inject a placeholder explanation
        recommended_product_data = {
            **product_dict,
            "explanation": f"Recommendation placeholder: This product is in the {target_category} category, which aligns with your most recent purchase behavior."
        }
        
        # Validate and create the final Pydantic model
        final_recommendations.append(RecommendedProduct(**recommended_product_data))
        
    return final_recommendations
