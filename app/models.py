#app/models.py

from pydantic import BaseModel
from typing import Literal
from datetime import datetime

#--- Product Model ---

class Product(BaseModel):
    product_id: str
    name: str
    category: str
    price: float
    description: str  #Vital for LLM context

#--- User Model ---
class User(BaseModel):
    user_id: str
    name: str
    created_at: datetime = None

#--- User Interaction Model ---
class Interaction(BaseModel):
    interaction_id: str
    user_id: str
    product_id: str
    type: Literal['view', 'purchase', 'addd_to_cart']
    timestamp: datetime


    
