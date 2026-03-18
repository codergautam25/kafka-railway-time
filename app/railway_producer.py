import os
import time
import json
import random
from confluent_kafka import Producer

KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
p = Producer({'bootstrap.servers': KAFKA_SERVERS})

TRAINS = [
    {"train_no": "12864", "name": "HWH SMVB EXP", "source": "Howrah", "destination": "Bangalore"},
    {"train_no": "12863", "name": "SMVB HWH EXP", "source": "Bangalore", "destination": "Howrah"},
    {"train_no": "12245", "name": "DURONTO EXPRESS", "source": "Howrah", "destination": "Bangalore"},
    {"train_no": "11301", "name": "UDYAN EXPRESS", "source": "Mumbai", "destination": "Bangalore"},
    {"train_no": "12133", "name": "MANGALURU EXP", "source": "Mumbai", "destination": "Bangalore"},
    {"train_no": "12951", "name": "MUMBAI RAJDHANI", "source": "Mumbai", "destination": "New Delhi"},
    {"train_no": "12435", "name": "RAJDHANI EXPRESS", "source": "Bangalore", "destination": "New Delhi"}
]

STATIONS = ["Bangalore City", "Howrah Jn", "Mumbai Central", "New Delhi", "Chennai", "Pune", "Nagpur"]

def generate_update():
    train = random.choice(TRAINS)
    return {
        "train_no": train["train_no"],
        "train_name": train["name"],
        "source": train["source"],
        "destination": train["destination"],
        "station": random.choice(STATIONS),
        "delay_mins": random.randint(0, 120),
        "status": "In Transit",
        "timestamp": str(time.time())
    }

if __name__ == "__main__":
    print("Railway Producer started...")
    while True:
        data = generate_update()
        print(f"Pushing update: {data}")
        p.produce("railway-updates", value=json.dumps(data))
        p.flush()
        time.sleep(5)  # Update every 5 seconds
