from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.auth import verify_token
from app.producer import send_event
import os

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
    keys = r.keys("*")
    alerts = []
    for key in keys:
        try:
            val = r.get(key)
            if val:
                alerts.append(json.loads(val))
        except:
            pass
    return alerts

@app.post("/event")
def publish(data: dict, token=Depends(verify_token)):
    send_event(data)
    return {"msg":"sent"}
