import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

from data.load_data import get_bookings_data, get_flights_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voicerag")

class BookingOptions(BaseModel):
    luggage: Optional[str] = None
    meals: Optional[str] = None
    delay: Optional[str] = None

class BookingUpdateRequest(BaseModel):
    phone: str
    options: BookingOptions

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    if not os.environ.get("RUNNING_IN_PRODUCTION"):
        logger.info("Running in development mode, loading from .env file")
        load_dotenv()

@app.get("/health")
async def read_root():
    return 'hello with Air France and KLM flights'

@app.get("/api/bookings")
async def get_bookings(flight: Optional[str] = None, name: Optional[str] = None):
    bookings = get_bookings_data()
    if flight:
        bookings = [b for b in bookings if b["flight"] == flight]
    if name:
        bookings = [b for b in bookings if b["name"].lower() == name.lower()]
    return {"bookings": bookings}

@app.get("/api/bookings/{booking_id}")
async def get_booking(booking_id: int):
    bookings = get_bookings_data()
    booking = next((b for b in bookings if b["id"] == booking_id), None)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"booking": booking}

@app.get("/api/flights")
async def get_flights(flight: Optional[str] = None):
    flights = get_flights_data()
    if flight:
        flights = [f for f in flights if f["id"] == flight]
    return {"flights": flights}

@app.get("/api/flights/{flight_id}")
async def get_flight_by_id(flight_id: str):
    """
    Retrieve a specific flight by its ID.
    
    - **flight_id**: The unique identifier of the flight.
    """
    flights = get_flights_data()
    flight = next((f for f in flights if f["id"] == flight_id), None)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return {"flight": flight}

if __name__ == "__main__":
    import uvicorn
    host = "0.0.0.0"
    port = int(os.getenv("PORT", 8765))  # Changed default port to 8765
    uvicorn.run(app, host=host, port=port)