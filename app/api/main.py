import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from data.load_data import get_incidents_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voicerag")

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    if not os.environ.get("RUNNING_IN_PRODUCTION"):
        logger.info("Running in development mode, loading from .env file")
        load_dotenv()

@app.get("/health")
async def read_root():
    return 'hello with customer service Orange'

@app.get("/api/incidents")
async def get_incidents(id: Optional[int] = None, name: Optional[str] = None):
    incidents = get_incidents_data()
    if id:
        incidents = [b for b in incidents if b["id"] == id]
    if name:
        incidents = [b for b in incidents if b["name"].lower() == name.lower()]
    return {"incidents": incidents}

@app.get("/api/incidents/{incident_id}")
async def get_incident(incident_id: int):
    incidents = get_incidents_data()
    incident = next((b for b in incidents if b["id"] == incident_id), None)
    if not incident:
        raise HTTPException(status_code=404, detail="incident not found")
    return {"incident": incident}


if __name__ == "__main__":
    import uvicorn
    host = "0.0.0.0"
    port = int(os.getenv("PORT", 8765))  # Changed default port to 8765
    uvicorn.run(app, host=host, port=port)