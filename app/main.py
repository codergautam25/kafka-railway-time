from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.auth import verify_token
from app.producer import send_event
import os
import time

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def home():
    return FileResponse("app/static/dashboard.html")

@app.get("/health")
def health():
    return {"status": "ok"}

import redis
import json

r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)

@app.get("/alerts")
def get_alerts():
    # Only return historical alert records (prefixed with fraud: or railway:)
    keys = r.keys("fraud:*") + r.keys("railway:*")
    alerts = []
    for key in keys:
        try:
            val = r.get(key)
            if val:
                alerts.append(json.loads(val))
        except:
            pass
    return alerts

@app.get("/search/train/{train_no}")
def search_train(train_no: str):
    data = r.get(f"train:LATEST:{train_no}")
    if data:
        result = json.loads(data)
        result["is_simulated"] = False
        return result
    
    # Fallback simulation for any 5-digit train number
    if train_no.isdigit() and len(train_no) == 5:
        import hashlib
        h = int(hashlib.md5(train_no.encode()).hexdigest(), 16)
        
        train_names = ["KANCHANJANGA EXP", "COROMANDEL EXP", "TAMIL NADU EXP", "GARIB RATH", "SUPERFAST EXP"]
        stations = ["Howrah Jn", "New Delhi", "Chennai Central", "Mumbai Central", "Bangalore City"]
        
        return {
            "train_no": train_no,
            "train_name": train_names[h % len(train_names)],
            "source": stations[h % len(stations)],
            "destination": stations[(h+1) % len(stations)],
            "station": stations[(h+2) % len(stations)],
            "delay_mins": (h % 120),
            "status": "In Transit",
            "timestamp": str(time.time()),
            "is_simulated": True
        }
        
    return {"error": "Train data not found. Please try a 5-digit train number like 12133 or 11301."}

@app.get("/search/pnr/{pnr}")
def search_pnr(pnr: str):
    # Deterministic simulation based on PNR number
    import hashlib
    h = int(hashlib.md5(pnr.encode()).hexdigest(), 16)
    
    statuses = ["CONFIRMED", "RAC", "WL", "CANCELLED"]
    coaches = ["A1", "B1", "B2", "S1", "S2"]
    
    status = statuses[h % len(statuses)]
    coach = coaches[h % len(coaches)] if status == "CONFIRMED" else "N/A"
    berth = (h % 72) + 1 if status == "CONFIRMED" else "N/A"
    
    return {
        "pnr": pnr,
        "status": status,
        "coach": coach,
        "berth": berth,
        "train_no": ["12864", "12133", "12951"][h % 3],
        "passenger_count": (h % 4) + 1,
        "chart_status": "Prepared" if (h % 2 == 0) else "Not Prepared"
    }

@app.post("/event")
def publish(data: dict, token=Depends(verify_token)):
    send_event(data)
    return {"msg":"sent"}

@app.post("/submit-alert")
def submit_alert(data: dict):
    # Public endpoint for demo simulation
    send_event(data)
    return {"status": "event_published"}
