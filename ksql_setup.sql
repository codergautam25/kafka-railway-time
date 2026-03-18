-- Create stream from user-events topic
CREATE STREAM USER_EVENTS (
    id VARCHAR,
    user_id VARCHAR,
    amount DOUBLE,
    location VARCHAR,
    timestamp VARCHAR
) WITH (
    KAFKA_TOPIC='user-events',
    VALUE_FORMAT='JSON',
    PARTITIONS=1
);

-- Detect fraud: transactions > 1000 are alerts
CREATE STREAM FRAUD_ALERTS AS
SELECT
    id,
    user_id,
    amount,
    'HIGH_VALUE' as reason
FROM USER_EVENTS
WHERE amount > 1000
EMIT CHANGES;

-- Railway Status Stream
CREATE STREAM RAILWAY_STATUS (
    train_no VARCHAR,
    train_name VARCHAR,
    source VARCHAR,
    destination VARCHAR,
    station VARCHAR,
    delay_mins INT,
    status VARCHAR,
    timestamp VARCHAR
) WITH (
    KAFKA_TOPIC='railway-updates',
    VALUE_FORMAT='JSON',
    PARTITIONS=1
);

-- Detect Significant Delays (> 30 mins)
CREATE STREAM DELAYED_ALERTS AS
SELECT
    train_no,
    train_name,
    source,
    destination,
    station,
    delay_mins,
    'SIGNIFICANT_DELAY' as alert_type
FROM RAILWAY_STATUS
WHERE delay_mins > 30
EMIT CHANGES;
