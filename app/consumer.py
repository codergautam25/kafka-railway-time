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

c.subscribe(["FRAUD_ALERTS", "DELAYED_ALERTS"])

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
        
        # Use unique key for Redis (history with 10min TTL)
        if topic == "FRAUD_ALERTS":
            key = f"fraud:{data.get('ID', data.get('id', '1'))}"
            r.set(key, json.dumps(data), ex=600)
        else:
            key = f"railway:{data.get('TRAIN_NO', 'unknown')}:{time.time()}"
            r.set(key, json.dumps(data), ex=600)
        print(f"Processed {topic}: {data}")
    except Exception as e:
        print(f"Error processing message: {e}")
