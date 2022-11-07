import asyncio

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from kafka.errors import NoBrokersAvailable

from cador.config import log as log


class KafkaTopic:
    def __init__(self, id: str, server: str, topic: str) -> None:
        if server is None or topic is None:
            error_message = 'KafkaTopic : bad parameters : id={}, server={}, topic={}'.format(id, server, topic)
            log.warning(error_message)

        self.id = id
        self.server = server
        self.topic = topic
        self.queue = None

    def stop(self):
        if self.queue is not None:
            self.queue.stop()
            self.queue = None

    async def init_producer(self):
        if self.queue is not None:
            raise RuntimeError('The queue is already initialized !')

        status = None
        while status is None:
            try:
                self.queue = AIOKafkaProducer(bootstrap_servers=self.server, loop=asyncio.get_event_loop())
                status = 'Started'
                await self.queue.start()
            except (NoBrokersAvailable, ConnectionError) as err:
                log.error("Unable to find a broker : {0}".format(err))
                await asyncio.sleep(1)

    async def init_consumer(self, consumer_group):
        if self.queue is not None:
            raise RuntimeError('The queue is already initialized !')

        kafka_server = self.server
        kafka_topic = self.topic
        self.queue = AIOKafkaConsumer(kafka_topic,
                                      group_id=consumer_group,
                                      auto_offset_reset='latest',
                                      bootstrap_servers=kafka_server,
                                      retry_backoff_ms=10000, loop=asyncio.get_event_loop())
        await self.queue.start()

    async def publish(self, message):
        try:
            record_metadata = await self.queue.send_and_wait(self.topic, message)
            return {
                'topic': record_metadata.topic,
                'partition': record_metadata.partition,
                'offset': record_metadata.offset
            }
        except Exception as e:
            log.exception(e)
            error_message = 'Cannot publish on {} : {}'.format(self.topic, str(e))
            raise ValueError(error_message)
