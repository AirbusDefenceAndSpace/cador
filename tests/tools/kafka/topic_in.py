import json

import kafka

KAFKA_SERVER_URL = 'localhost:9092'
TOPIC = 'ipcloud_requests'


def main(topic=TOPIC):
    consumer = kafka.KafkaConsumer(bootstrap_servers=KAFKA_SERVER_URL,
                                   auto_offset_reset='earliest',
                                   value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    consumer.subscribe([topic])

    for msg in consumer:
        print(msg)


if __name__ == "__main__":
    main()
