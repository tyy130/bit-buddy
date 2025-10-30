# Wire-up note

In your existing `app/mesh.py`, add:

```python
# at top, after FastAPI creation
from .persona import ensure_persona, load_persona
from .mesh_ext import router as persona_router

# right after app = FastAPI(...)
ensure_persona()
app.include_router(persona_router)

# then, in /hello and /ask responses, you can include persona 'asides' e.g.:
#   from .persona import load_persona
#   p = load_persona()
#   aside = p.get("quirks",{}).get("favorite_phrase","")
#   return {..., "aside": aside[:p.get("voice",{}).get("max_aside_len",120)]}
```
