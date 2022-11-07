import asyncio
import json
import time

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

import cador.config as cador_config
from cador.config import log as log
from cador.core.KafkaTopic import KafkaTopic
from cador.core.ProcessingService import ProcessingService


class KafkaService:
    @staticmethod
    async def consume(consumer: KafkaTopic):
        log.info('CADoR starts consuming')
        await consumer.init_consumer(cador_config.CADOR_KAFKA_CONSUMER_GROUP)
        try:
            async for msg in consumer.queue:
                try:
                    log.info('Loading message from Kafka ...')
                    json_content = json.loads(msg.value.decode('ascii'))
                    log.info('Processing message ...')
                    processing = ProcessingService(json_content)
                    await processing.handle_request()

                    log.info('Processing done !')
                except Exception as e:
                    message = 'Error while processing : {}'.format(e)
                    log.error(message)
        finally:
            await consumer.stop()

    @staticmethod
    async def check_alive(consumer: KafkaTopic):
        start_time = time.time()
        while not KafkaService.is_alive(consumer):
            elapsed_time = time.time() - start_time
            if elapsed_time > cador_config.CADOR_TIMEOUT_SECONDS:
                raise RuntimeError('Kafka connection timeout : could not connect to kafka !')
            await asyncio.sleep(1)

    @staticmethod
    def is_alive(consumer: KafkaTopic):
        try:
            # FIXME : use AIOKafkaConsumer ?? Stop it after usage ?
            test_consumer = KafkaConsumer(consumer.topic,
                                          group_id=cador_config.CADOR_KAFKA_CONSUMER_GROUP,
                                          auto_offset_reset='earliest',
                                          bootstrap_servers=consumer.server)
            return True
        except NoBrokersAvailable as err:
            log.error("Unable to find a broker : {0}".format(err))
            return False
        except Exception as err:
            log.error("Exception : {0}".format(err))
            return False
