import os
import time
from confluent_kafka import Consumer
import redis, json

KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

r = redis.Redis(host=REDIS_HOST, port=6379)

c = Consumer({
    'bootstrap.servers': KAFKA_SERVERS,
    'group.id': 'enterprise-group',
    'auto.offset.reset': 'earliest'
})

c.subscribe(["FRAUD_ALERTS", "DELAYED_ALERTS", "railway-updates"])

while True:
    msg = c.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print(f"Consumer error: {msg.error()}")
        continue

    try:
        topic = msg.topic()
        data = json.loads(msg.value().decode())
        data["_topic"] = topic
        
        # 1. Update Latest Status Index (from all updates)
        if topic == "railway-updates":
            train_no = data.get('train_no', 'unknown')
            r.set(f"train:LATEST:{train_no}", json.dumps(data))
            print(f"Updated Search Index for Train {train_no}")
            continue # Don't add raw updates to the alert history

        # 2. Update Alert History (from Alerts topics)
        if topic == "FRAUD_ALERTS":
            key = f"fraud:{data.get('ID', data.get('id', '1'))}:{time.time()}"
            r.set(key, json.dumps(data), ex=600)
        elif topic == "DELAYED_ALERTS":
            key = f"railway:{data.get('TRAIN_NO', 'unknown')}:{time.time()}"
            r.set(key, json.dumps(data), ex=600)
            
        print(f"Processed Alert {topic}: {data}")
    except Exception as e:
        print(f"Error processing message: {e}")
