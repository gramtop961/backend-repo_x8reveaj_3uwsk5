"""
Database Schemas for Rent-a-Car & Excursions

Each Pydantic model maps to a MongoDB collection (lowercased class name).
"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class Car(BaseModel):
    brand: str = Field(..., description="Brand name (e.g., Toyota)")
    model: str = Field(..., description="Model (e.g., Corolla)")
    transmission: str = Field(..., description="Manual or Automatic")
    seats: int = Field(..., ge=1, le=9, description="Number of seats")
    fuel: str = Field(..., description="Fuel type (Petrol/Diesel/Hybrid/EV)")
    price_per_day: float = Field(..., ge=0, description="Price per day in TND")
    image: Optional[str] = Field(None, description="Image URL")
    features: List[str] = Field(default_factory=list, description="Feature tags")

class Excursion(BaseModel):
    title: str
    region: str = Field(..., description="Region or city (e.g., Tunis, Tozeur)")
    duration_hours: int = Field(..., ge=1, le=72)
    price_per_person: float = Field(..., ge=0)
    description: str
    image: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)

class Booking(BaseModel):
    type: str = Field(..., description="'car' | 'excursion' | 'combo'")
    pickup_location: str
    dropoff_location: Optional[str] = None
    pickup_date: str
    dropoff_date: Optional[str] = None
    car_id: Optional[str] = None
    excursion_id: Optional[str] = None
    full_name: str
    phone: str
    email: EmailStr
    passengers: Optional[int] = Field(1, ge=1, le=50)
    notes: Optional[str] = None
