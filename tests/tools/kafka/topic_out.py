import json

import kafka

KAFKA_SERVER_URL = 'localhost:9092'
TOPIC = 'ipcloud_out'


def deserializer(x):
    try:
        return json.loads(x.decode('utf-8'))
    except:
        return str(x)


def main(topic=TOPIC):
    consumer = kafka.KafkaConsumer(bootstrap_servers=KAFKA_SERVER_URL,
                                   auto_offset_reset='earliest',
                                   value_deserializer=deserializer)
    consumer.subscribe([topic])

    for msg in consumer:
        print(msg)


if __name__ == "__main__":
    main()
