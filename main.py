import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime

from database import create_document, get_documents, db
from schemas import Reservation, EventRequest, ContactMessage, Testimonial

app = FastAPI(title="La Nonna – API", description="Backend for restaurant website: reservations, events, contacts, testimonials")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "La Nonna API running", "time": datetime.utcnow().isoformat()}

@app.get("/api/hello")
def hello():
    return {"message": "Buongiorno dalla cucina!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response: Dict[str, Any] = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, 'name', '✅ Connected')
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# -------- Business Endpoints --------

@app.post("/api/reservations")
def create_reservation(payload: Reservation):
    try:
        inserted_id = create_document("reservation", payload)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/events")
def create_event_request(payload: EventRequest):
    try:
        inserted_id = create_document("eventrequest", payload)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contact")
def create_contact_message(payload: ContactMessage):
    try:
        inserted_id = create_document("contactmessage", payload)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/testimonials")
def list_testimonials(limit: int = 6):
    try:
        docs: List[Dict[str, Any]] = get_documents("testimonial", {}, limit)
        # Normalize _id to string
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return {"items": docs}
    except Exception:
        # Return a friendly fallback if DB not available
        fallback = [
            {"author": "Cliente heureux", "rating": 5, "content": "Pizzas savoureuses et accueil chaleureux – un vrai coin d'Italie à Martigny.", "source": "Avis client"},
            {"author": "Famille B.", "rating": 5, "content": "Salle parfaite pour notre fête familiale, service impeccable.", "source": "Avis client"},
        ]
        return {"items": fallback}

# Optional schema descriptor for admin tools
class SchemaInfo(BaseModel):
    name: str
    fields: List[str]

@app.get("/schema")
def schema_info() -> List[SchemaInfo]:
    return [
        SchemaInfo(name="reservation", fields=list(Reservation.model_fields.keys())),
        SchemaInfo(name="eventrequest", fields=list(EventRequest.model_fields.keys())),
        SchemaInfo(name="contactmessage", fields=list(ContactMessage.model_fields.keys())),
        SchemaInfo(name="testimonial", fields=list(Testimonial.model_fields.keys())),
    ]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
