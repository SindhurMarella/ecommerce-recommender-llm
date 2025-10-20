# app/recommender.py

import pandas as pd
import os
from typing import List
from google import genai
from dotenv import load_dotenv
import sys

# Add parent directory to path to allow imports from app/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    GENAI_CLIENT = genai.Client()
    print("DEBUG: Gemini Client initialized successfully.")
except Exception as e:
    print(f"ERROR: Could not initialize Gemini Client. Check GEMINI_API_KEY in .env: {e}")
    GENAI_CLIENT = None

def generate_explanation(recommended_product: dict, user_id: str, products_df: pd.DataFrame, interactions_df: pd.DataFrame) -> str:
    """
    Uses Gemini to generate a personalized explanation for the recommendation.
    Now accepts products_df and interactions_df as arguments.
    """
    if GENAI_CLIENT is None:
        return "The AI Explanation service is temporarily unavailable. Check your API key."
    
    # 1. Get User Purchase/Interaction History Summary
    user_interactions = interactions_df[interactions_df['user_id'] == user_id]
    if user_interactions.empty:
        user_context = "This product is popular overall and we thought you might like it."
    else:
        # Summarize user behaviour: list top categories purchased/viewed
        top_categories_list = user_interactions['product_id'].map(
            lambda pid: products_df[products_df['product_id'] == pid]['category'].iloc[0]
        ).value_counts().head(3).index.to_list()
        user_context = f"User has previously interacted with items in categories such as : {', '.join(top_categories_list)}. The recommendation is based on category similarity."

    # 2. Define the product details
    product_details = f"Product Name: {recommended_product['name']}. Category: {recommended_product['category']}. Description: {recommended_product['description']}"

    # 3. Create the prompt (Prompt Engineering)
    prompt = f"""
        You are an expert e-commerce recommendation system. Your goal is to write a short, personalized, and persuasive explanation for the recommended product below.
        Context:
        - {user_context}
        - Recommended Product: {product_details}

        Instructions:
        1. Write a single paragraph (Max 3 sentences).
        2. Focus on connecting the product's category and description directly to the user's past interactions.
        3. Be friendly and confident. Do not mention "Gemini", "AI", or "algorithm".
        4. Start the explanation directly, e.g., "Since you recently..." or "Because you love..."
    """

    # 4. Call the Gemini API
    try:
        response = GENAI_CLIENT.generate_content(
            model="models/gemini-pro", # Using a standard model name
            prompt=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"ERROR: Gemini API call failed for user {user_id}. {e}")
        return "The AI recommendation explanation service is temporarily unavailable."

def get_content_based_recommendations(user_id: str, products_df: pd.DataFrame, interactions_df: pd.DataFrame, top_n: int = 3) -> pd.DataFrame:
    """
    Recommends products based on the user's most recent purchase category.
    Accepts DataFrames as arguments and returns a DataFrame of recommended products.
    """
    # Check if data is valid
    if products_df.empty or interactions_df.empty:
        return pd.DataFrame() 

    # --- 1. CORE RECOMMENDATION LOGIC ---
    user_purchases = interactions_df[
        (interactions_df['user_id'] == user_id) & 
        (interactions_df['type'] == 'purchase')
    ]

    if user_purchases.empty:
        # Fallback: Recommend the top N overall products if the user has no purchase history
        recommended_products_df = products_df.head(top_n)
    else:
        # Find the most recently purchased product's category
        user_purchases = user_purchases.sort_values(by='timestamp', ascending=False)
        recent_product_id = user_purchases['product_id'].iloc[0]
        recent_product_row = products_df[products_df['product_id'] == recent_product_id]
        
        if recent_product_row.empty:
            recommended_products_df = products_df.head(top_n) # Fallback if product not found
        else:
            target_category = recent_product_row['category'].iloc[0]
            purchased_ids = user_purchases['product_id'].unique()
            
            # Find other products in the same category the user hasn't purchased
            recommended_products_df = products_df[
                (products_df['category'] == target_category) & 
                (~products_df['product_id'].isin(purchased_ids))
            ]
            recommended_products_df = recommended_products_df.head(top_n)
            
    return recommended_products_df

def generate_social_proof(product_id: str, interactions_df: pd.DataFrame) -> str:
    """
    Generates a social proof string based on purchase data for a product.
    """
    if interactions_df is None or interactions_df.empty:
        return None
    
    product_purchases = interactions_df[
        (interactions_df['product_id'] == product_id) &
        (interactions_df['type'] == 'purchase')
    ]
    purchase_count = len(product_purchases)

    if purchase_count > 2:
        return f"Popular! {purchase_count} users have purchased this product."
    
    return None