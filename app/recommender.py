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
    if PRODUCTS_DF.empty or INTERACTIONS_DF.empty:
        return [] 

    # --- 1. CORE RECOMMENDATION LOGIC ---
    user_purchases = INTERACTIONS_DF[
        (INTERACTIONS_DF['user_id'] == user_id) & 
        (INTERACTIONS_DF['type'] == 'purchase')
    ]

    # Decide which product set to recommend
    if user_purchases.empty:
        # Fallback: Recommend the top 3 overall products if the user has no purchase history
        print(f"DEBUG: User {user_id} has no purchase history. Recommending popular items.")
        recommended_products_df = PRODUCTS_DF.head(top_n)
        target_category = "General Popularity"
        
    else:
        # 1. Sort purchases to find the most recent one
        user_purchases = user_purchases.sort_values(by='timestamp', ascending=False)
        # 2. Find the most recently purchased product's category
        recent_product_id = user_purchases['product_id'].iloc[0]
        recent_product_row = PRODUCTS_DF[PRODUCTS_DF['product_id'] == recent_product_id]
        #target_category = recent_product_row['category']
        
        # Check if the product from the interactions exists in the product dataframe
        if recent_product_row.empty:
            print(f"WARN: Product {recent_product_id} from interactions not found in products. Reverting to fallback.")
            recommended_products_df = PRODUCTS_DF.head(top_n)
        else:
            target_category = recent_product_row['category'].iloc[0]
            print(f"DEBUG: User {user_id}'s last purchase category: {target_category}")

            # 3. Find other products in the same category that the user has not purchased
            purchased_ids = user_purchases['product_id'].unique()
            recommended_products_df = PRODUCTS_DF[
                (PRODUCTS_DF['category'] == target_category) &
                (~PRODUCTS_DF['product_id'].isin(purchased_ids))
            ]

            # 4. Take the top N from the filtered list
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

def generate_social_proof(product_id: str, interactions_df: pd.DataFrame) -> str:
    """
    Generate social proof string based on purchase data for a product.
    """
    if interactions_df is None or interactions_df.empty:
        return None
    
    # Filter for purchases of this specific product
    product_purchases = interactions_df[
        (interactions_df['product_id'] == product_id) &
        (interactions_df['type'] == 'purchase')
    ]

    purchase_count = len(product_purchases)

    if purchase_count > 2:
        return f"Popular! {purchase_count} users have purchased this product."
    
    return None # Return nothing if not popular enough
