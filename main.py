import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from database import db, create_document, get_documents

app = FastAPI(title="Hammamet Rent-a-Car & Excursions API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Backend running", "service": "rentacar-excursions"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Data models for request validation
class BookingRequest(BaseModel):
    type: str  # car | excursion | combo
    pickup_location: str
    dropoff_location: Optional[str] = None
    pickup_date: str
    dropoff_date: Optional[str] = None
    car_id: Optional[str] = None
    excursion_id: Optional[str] = None
    full_name: str
    phone: str
    email: EmailStr
    passengers: Optional[int] = 1
    notes: Optional[str] = None


# Seed helpers
SAMPLE_CARS = [
    {
        "brand": "Toyota",
        "model": "Corolla",
        "transmission": "Automatic",
        "seats": 5,
        "fuel": "Petrol",
        "price_per_day": 120.0,
        "image": "https://images.unsplash.com/photo-1619767886558-efdc259cde1a?q=80&w=1200&auto=format&fit=crop",
        "features": ["A/C", "Bluetooth", "USB", "ABS"],
    },
    {
        "brand": "Volkswagen",
        "model": "Golf",
        "transmission": "Manual",
        "seats": 5,
        "fuel": "Diesel",
        "price_per_day": 140.0,
        "image": "https://images.unsplash.com/photo-1555215695-3004980ad54e?q=80&w=1200&auto=format&fit=crop",
        "features": ["A/C", "CarPlay", "Cruise", "Sensors"],
    },
    {
        "brand": "Hyundai",
        "model": "i10",
        "transmission": "Automatic",
        "seats": 4,
        "fuel": "Petrol",
        "price_per_day": 90.0,
        "image": "https://images.unsplash.com/photo-1549921296-3cce18d7c7c7?q=80&w=1200&auto=format&fit=crop",
        "features": ["A/C", "Bluetooth", "Eco"],
    },
]

SAMPLE_EXCURSIONS = [
    {
        "title": "Medina of Tunis & Sidi Bou Said",
        "region": "Tunis",
        "duration_hours": 8,
        "price_per_person": 180.0,
        "description": "Discover the UNESCO-listed medina and the blue-white village by the sea.",
        "image": "https://images.unsplash.com/photo-1597248881519-ef9a5b1f407f?q=80&w=1200&auto=format&fit=crop",
        "highlights": ["Zitouna Mosque", "Souks", "Cafés of Sidi Bou Said"],
    },
    {
        "title": "Sahara Adventure: Douz & Ksar Ghilane",
        "region": "Kebili",
        "duration_hours": 14,
        "price_per_person": 350.0,
        "description": "Full-day desert tour with dunes, oasis, and optional camel ride.",
        "image": "https://images.unsplash.com/photo-1516426122078-c23e76319801?q=80&w=1200&auto=format&fit=crop",
        "highlights": ["Grand Erg", "Hot Spring Oasis", "Camel ride"],
    },
    {
        "title": "El Jem Amphitheatre & Monastir",
        "region": "Mahdia",
        "duration_hours": 9,
        "price_per_person": 220.0,
        "description": "Explore the Roman Colosseum of Africa and coastal Monastir.",
        "image": "https://images.unsplash.com/photo-1602854375907-6d8ab9b3138c?q=80&w=1200&auto=format&fit=crop",
        "highlights": ["El Jem", "Ribat Monastir", "Marina"],
    },
]


def ensure_seeded():
    if db is None:
        return
    try:
        if db["car"].count_documents({}) == 0:
            db["car"].insert_many(SAMPLE_CARS)
        if db["excursion"].count_documents({}) == 0:
            db["excursion"].insert_many(SAMPLE_EXCURSIONS)
    except Exception:
        pass


@app.get("/api/cars")
def list_cars():
    ensure_seeded()
    try:
        cars = get_documents("car")
        for c in cars:
            c["_id"] = str(c.get("_id"))
        return cars
    except Exception as e:
        # Fallback to samples if DB not available
        return SAMPLE_CARS


@app.get("/api/excursions")
def list_excursions():
    ensure_seeded()
    try:
        ex = get_documents("excursion")
        for d in ex:
            d["_id"] = str(d.get("_id"))
        return ex
    except Exception:
        return SAMPLE_EXCURSIONS


@app.post("/api/bookings")
def create_booking(payload: BookingRequest):
    data = payload.model_dump()
    try:
        booking_id = create_document("booking", data)
        return {"status": "ok", "booking_id": booking_id}
    except Exception as e:
        # Accept booking even if DB down, but mark as not persisted
        return {"status": "accepted", "persisted": False, "message": str(e)[:120]}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "Unknown"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
