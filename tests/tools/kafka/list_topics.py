import json

import kafka

KAFKA_SERVER_URL = 'localhost:9092'


def main():
    consumer = kafka.KafkaConsumer(bootstrap_servers=KAFKA_SERVER_URL,
                                   auto_offset_reset='earliest',
                                   value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    print(consumer.topics())


if __name__ == "__main__":
    main()
