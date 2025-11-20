"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import date, time

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in CHF")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# La Nonna – App-specific schemas

class Reservation(BaseModel):
    """Reservation requests made from the website"""
    name: str = Field(..., min_length=2)
    email: EmailStr
    phone: str = Field(..., min_length=6, max_length=30)
    date: date
    time: time
    guests: int = Field(..., ge=1, le=20)
    notes: Optional[str] = Field(None, max_length=500)

class EventRequest(BaseModel):
    """Banquet / seminar booking inquiries"""
    name: str = Field(..., min_length=2)
    company: Optional[str] = Field(None, max_length=120)
    email: EmailStr
    phone: str = Field(..., min_length=6, max_length=30)
    event_date: date
    event_type: str = Field(..., description="e.g., Repas d’entreprise, Séminaire, Cocktail dînatoire")
    guests: int = Field(..., ge=10, le=200)
    budget_chf: Optional[float] = Field(None, ge=0)
    message: Optional[str] = Field(None, max_length=2000)

class ContactMessage(BaseModel):
    """General contact messages"""
    name: str = Field(..., min_length=2)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    subject: str = Field(..., max_length=120)
    message: str = Field(..., max_length=2000)

class Testimonial(BaseModel):
    """Optional testimonials storage"""
    author: str = Field(..., min_length=2)
    rating: int = Field(..., ge=1, le=5)
    content: str = Field(..., max_length=600)
    source: Optional[str] = Field(None, description="TripAdvisor, Google, etc.")

# Simple menu item schema (if we later want to persist menu items)
class MenuItem(BaseModel):
    title: str
    description: Optional[str] = None
    price_chf: float = Field(..., ge=0)
    category: str = Field(..., description="Category like Antipasti, Pizze, Paste, Risotti, Carni, Dolci")

# Validators
class _WithPhone:
    phone: Optional[str]

    @field_validator('phone')
    @classmethod
    def clean_phone(cls, v: Optional[str]):
        if v is None:
            return v
        cleaned = ''.join(ch for ch in v if ch.isdigit() or ch in ['+', ' '])
        return cleaned.strip()
