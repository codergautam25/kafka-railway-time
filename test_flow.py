
import requests
import jwt
import time
import redis
import json

SECRET = "enterprise_secret"
API_URL = "http://localhost:8000"

def generate_token():
    return jwt.encode({"user": "test_user"}, SECRET, algorithm="HS256")

def test_flow():
    token = generate_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    event = {
        "id": "evt_123",
        "user_id": "user_456",
        "amount": 1500.0,
        "location": "NY",
        "timestamp": str(time.time())
    }
    
    print(f"Sending event: {event}")
    resp = requests.post(f"{API_URL}/event", json=event, headers=headers)
    print(f"API Response: {resp.status_code} - {resp.json()}")
    
    if resp.status_code == 200:
        print("Waiting for processing...")
        time.sleep(10)  # Wait for Kafka -> ksqlDB -> Consumer -> Redis
        
        r = redis.Redis(host='localhost', port=6379, db=0)
        alert = r.get("evt_123")
        
        if alert:
            print(f"SUCCESS: Found alert in Redis: {json.loads(alert)}")
        else:
            print("FAILURE: Alert not found in Redis. Check ksqlDB and Consumer logs.")

if __name__ == "__main__":
    test_flow()
