import os
from confluent_kafka import Producer
import json

KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
p = Producer({'bootstrap.servers': KAFKA_SERVERS})

def send_event(data):
    p.produce("user-events", value=json.dumps(data))
    p.flush()
