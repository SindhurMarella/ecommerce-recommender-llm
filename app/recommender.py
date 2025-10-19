# app/recommender.py

import pandas as pd
import os
from typing import List
from google import genai
from dotenv import load_dotenv
import sys
# Add parent directory to path to allow imports from app/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Import the necessary Pydantic models and data loader
from app.data_loader import load_data
from app.models import RecommendedProduct



load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    GENAI_CLIENT = genai.Client()
    print("DEBUG: Gemini Client initialized successfully.")
except Exception as e:
    print(f"ERROR: Could not initialize Gemini Client. Check GEMINI_API_KEY in .env: {e}")
    GENAI_CLIENT = None

# Load data once at the start. This ensures the data is ready for API requests.
PRODUCTS_DF, USERS_DF, INTERACTIONS_DF = load_data()

def generate_explanation(recommended_product: dict, user_id: str) -> str:
    """
        Uses Gemini to generate a pesonalized explanation for the recommendation.
    """
    if GENAI_CLIENT is None:
        return "The AI Explanation service is temporarily unavailable. Check your API key."
    
    # 1. Get User Purchase/Interaction History Summary
    user_interactions = INTERACTIONS_DF[INTERACTIONS_DF['user_id'] == user_id]
    # Summarize user behaviour: list top categories purchased/viewed
    top_categories_list = user_interactions['product_id'].map(
        lambda pid: PRODUCTS_DF[PRODUCTS_DF['product_id'] == pid]['category'].iloc[0]
    ).value_counts().head(3).index.to_list()

    user_context = f"User has previously interacted with items in categories such as : {', '.join(top_categories_list)}. The recommendation is based on category similarity."

    # 2. Define the product details
    product_details = f"Product Name: {recommended_product['name']}. Category: {recommended_product['category']}. Description: {recommended_product['description']}"

    # 3. Create the prompt (Prompt Engineering)
    prompt = f"""
        You are an expert e-commerce recommendation system. Your goal is to write a short, personalized , and persuasive explanation for the recommended product below.
        Context:
        -{user_context}
        - Recommended Product: {product_details}

        Instructions:
        1. Write a single paragraph (Max 3 sentences).
        2. Focus on connecting the product's category and description dorectly to the user's past interactions.
        3. Be friendly and confident. Do not mention "Gemini", "AI", or "algorithm".
        4. Start the explanation directly, e.g. , "Since you recently..." or "Because you love..."
    """

    #4. Call the Gemini API
    try:
        response  = GENAI_CLIENT.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"temperature": 0.5} # Allows for creative, less predictable responses
        )
        return response.text.strip()
    except Exception as e:
        print(f"ERROR: Gemini API call failed for user {user_id}. {e}")
        return "The AI recommendation explanation service is temporarily unavailable."

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

    
    # --- 2. LLM Explanation Generation and Final Formatting ---
    final_recommendations = []
    
    for _, product_row in recommended_products_df.iterrows():
        product_dict = product_row.to_dict()

        # *** INTEGRATION POINT: Call the LLM to generate the explanation ***
        explanation_text = generate_explanation(product_dict, user_id)

        # Combine product data with the real explanation
        recommended_product_data = {
            **product_dict,
            "explanation": explanation_text
        }
        
        # Validate and create the final Pydantic model
        final_recommendations.append(RecommendedProduct(**recommended_product_data))
        
    return final_recommendations
