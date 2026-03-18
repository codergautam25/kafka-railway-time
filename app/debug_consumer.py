import os
import time
from confluent_kafka import Consumer
import redis, json

KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

print(f"Connecting to Kafka: {KAFKA_SERVERS}")
print(f"Connecting to Redis: {REDIS_HOST}")

r = redis.Redis(host=REDIS_HOST, port=6379)
c = Consumer({
    'bootstrap.servers': KAFKA_SERVERS,
    'group.id': 'debug-group',
    'auto.offset.reset': 'earliest'
})

c.subscribe(["FRAUD_ALERTS", "DELAYED_ALERTS"])

print("Polling...")
for _ in range(10):
    msg = c.poll(2.0)
    if msg is None:
        print("No message...")
        continue
    if msg.error():
        print(f"Error: {msg.error()}")
        continue
    
    data = json.loads(msg.value().decode())
    print(f"Got message from {msg.topic()}: {data}")
    r.set(f"debug:{msg.topic()}", json.dumps(data))
    print("Saved to Redis.")

c.close()
