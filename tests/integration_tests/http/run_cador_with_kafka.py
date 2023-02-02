from typing import Any, Dict
import json
import asyncio
import argparse  # type: ignore
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import boto3
import rasterio
import warnings

warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)

# Stateful mode (with result indirection)
async def call_cador_through_kafka(url: str, topic: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    producer = AIOKafkaProducer(bootstrap_servers=url)
    try:
        print("[Producer] starting...")
        await producer.start()
        print("[Producer] sending task request...")
        await producer.send_and_wait(topic, str.encode(json.dumps(payload)))
    finally:
        print("[Producer] stopping...")
        await producer.stop()

async def get_result(url):
    # Listen for one task result message on kafka
    consumer = AIOKafkaConsumer("task_results", bootstrap_servers=url)
    try:
        print("[Consumer] starting...")
        await consumer.start()
        print("[Consumer] awaiting task result...")
        message_bytes = await consumer.getone()
    finally:
        print("[Consumer] stopping...")
        await consumer.stop()

    message = json.loads(message_bytes.value.decode())
    # Download & return the image mentioned in the task result message
    storage_conf = message["technicalMetadata"]["outputStorage"]["S3"]
    mask_conf = message["cloud_mask"]
    resource = boto3.resource("s3",
                              use_ssl=storage_conf["ssl"],
                              endpoint_url=storage_conf["url"],
                              aws_access_key_id=storage_conf["key"],
                              aws_secret_access_key=storage_conf["secret"])
    print("Downloading the image...")
    obj = resource.Object(mask_conf["containerPath"], mask_conf["objectId"]).get()
    image_bytes = obj["Body"].read()
    with rasterio.MemoryFile(image_bytes) as memfile:
        with memfile.open() as ds:
            return ds.read()


async def call_cador_and_get_result(url, topic, payload):
    return await asyncio.gather(call_cador_through_kafka(url, topic, payload), get_result(url))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("in_image", type=str)
    parser.add_argument("--url", type=str, default="127.0.0.1:9093")
    parser.add_argument("--topic", type=str, default="pesto_task_requests")
    args = parser.parse_args()
    payload = {
        "image": args.in_image,
        "technicalMetadata" : {
            "taskId": "test_task",
            "outputStorage" : {
                "S3": {
                    "url": "http://minio:9000",
                    "containerPath": "testbucket",

                    "ssl": False,
                    "key": "minioadmin",
                    "secret": "minioadmin"
                }
            },
        }
    }
    _, image = asyncio.run(call_cador_and_get_result(args.url, args.topic, payload))
    print(f"Successfully downloaded an image : shape={image.shape}, dtype={image.dtype}")
