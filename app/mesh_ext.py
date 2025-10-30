# app/mesh_ext.py — monkey-patches persona into mesh if present
from fastapi import APIRouter

from .persona import load_persona, narrate, patch_persona, randomize_persona

router = APIRouter()


@router.get("/persona")
def get_persona():
    return load_persona()


@router.post("/persona")
def set_persona(body: dict):
    return patch_persona(body or {})


@router.post("/persona/randomize")
def reroll(body: dict | None = None):
    bounds = body or {}
    return randomize_persona(bounds)


@router.post("/narrate")
def add_beat(body: dict):
    t = (body or {}).get("type", "event")
    note = (body or {}).get("note", "")
    return {"aside": narrate(t, note)}
