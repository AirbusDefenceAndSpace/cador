import json

import kafka

KAFKA_SERVER_URL = 'localhost:9092'
TOPIC = 'ipcloud_requests'


def main():
    producer = kafka.KafkaProducer(bootstrap_servers=KAFKA_SERVER_URL,
                                   value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    producer.send(TOPIC, {"dataObjectID": "test33"}).get(timeout=5)


if __name__ == "__main__":
    main()
