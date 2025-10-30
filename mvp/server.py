#!/usr/bin/env python3
"""
Bit Buddy FastAPI Server - REST API for your digital companion
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

from bit_buddy import BitBuddy

app = FastAPI(title="Bit Buddy API", description="Your personal digital companion")
buddy = BitBuddy()

class QueryRequest(BaseModel):
    query: str

class NarrateRequest(BaseModel):
    type: str
    note: str

class PersonalityPatch(BaseModel):
    temperature: Optional[float] = None
    humor: Optional[int] = None
    curiosity: Optional[int] = None
    formality: Optional[int] = None

@app.get("/hello")
def hello():
    """Say hello to your bit buddy"""
    return buddy.hello()

@app.post("/ask")
def ask(request: QueryRequest):
    """Ask your bit buddy something"""
    return buddy.ask(request.query)

@app.get("/personality")
def get_personality():
    """Get current personality traits"""
    return buddy.get_personality()

@app.post("/personality")
def patch_personality(patch: PersonalityPatch):
    """Adjust personality traits"""
    current = buddy.get_personality()
    
    # Apply patches
    if patch.temperature is not None:
        buddy.personality.temperature = max(0.0, min(1.5, patch.temperature))
    if patch.humor is not None:
        buddy.personality.humor = max(0, min(10, patch.humor))
    if patch.curiosity is not None:
        buddy.personality.curiosity = max(0, min(10, patch.curiosity))
    if patch.formality is not None:
        buddy.personality.formality = max(0, min(10, patch.formality))
    
    buddy._save_personality(buddy.personality)
    return {
        "message": "Personality updated!",
        "new_personality": buddy.get_personality()
    }

@app.post("/personality/randomize")
def randomize_personality():
    """Generate a completely new personality"""
    return buddy.randomize_personality()

@app.post("/narrate")
def narrate(request: NarrateRequest):
    """Add a story beat to your buddy's journal"""
    return buddy.narrate(request.type, request.note)

@app.get("/drive")
def get_drive_summary():
    """See what your buddy knows about your drive"""
    return buddy.get_drive_summary()

@app.post("/rescan")
def rescan_drive():
    """Ask buddy to rescan your drive"""
    buddy._scan_environment()
    return {
        "message": f"I've taken another look around your drive!",
        "summary": buddy.get_drive_summary()
    }

@app.get("/")
def root():
    """Root endpoint with buddy greeting"""
    response = buddy.hello()
    return {
        "welcome": "Welcome to your Bit Buddy!",
        "buddy_says": response['message'],
        "buddy_aside": response['aside'],
        "endpoints": {
            "hello": "GET /hello - Greet your buddy",
            "ask": "POST /ask - Ask questions",
            "personality": "GET /personality - View traits",
            "patch": "POST /personality - Adjust traits",  
            "randomize": "POST /personality/randomize - New personality",
            "narrate": "POST /narrate - Add story beats"
        }
    }

if __name__ == "__main__":
    print("🤖 Starting Bit Buddy server...")
    print("Your digital companion is waking up!")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")