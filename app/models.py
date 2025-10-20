# app/models.py

from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

# --- Internal Data Models (Used by data_loader) ---
class Product(BaseModel):
    product_id: str
    name: str
    category: str # e.g., 'Books', 'Electronics', 'Apparel'
    price: float
    description: str

class User(BaseModel):
    user_id: str
    name: str
    created_at: datetime = None

class Interaction(BaseModel):
    interaction_id: int
    user_id: str
    product_id: str
    type: Literal['view', 'purchase', 'add_to_cart']
    timestamp: datetime

# --- API Response Model (Used by main.py and recommender.py) ---
class RecommendedProduct(Product):
    """Extends the Product model to include the LLM-generated explanation."""
    explanation: str
    social_proof: Optional[str] = None