import os
import time
from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

# Simple cache for news (5 min TTL)
_news_cache = {"items": [], "ts": 0}

class NewsItem(BaseModel):
    id: int
    title: str
    severity: str
    time: str
    summary: str

class NewsResponse(BaseModel):
    items: List[NewsItem]

@app.get("/api/cyber/news", response_model=NewsResponse)
def cyber_news():
    now = int(time.time())
    if _news_cache["items"] and now - _news_cache["ts"] < 300:
        return {"items": _news_cache["items"]}

    # In a real app, fetch from CMS or database. Here, serve deterministic mock items for SEO + demo.
    items = [
        {"id": 1, "title": "New CVE-2025-10421 detected affecting popular HTTP library", "severity": "high", "time": "2m ago", "summary": "Remote code execution possible under specific header parsing conditions."},
        {"id": 2, "title": "Patch available for X package (2.4.1) – upgrade recommended", "severity": "medium", "time": "12m ago", "summary": "Fixes input validation bypass leading to privilege escalation."},
        {"id": 3, "title": "Supply-chain alert: package yanked from registry after compromise", "severity": "critical", "time": "28m ago", "summary": "Malicious versions detected. Pin hashes and audit lockfiles."},
    ]

    _news_cache["items"] = items
    _news_cache["ts"] = now
    return {"items": items}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
