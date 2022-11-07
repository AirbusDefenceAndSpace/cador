import argparse
import asyncio
import os

from sanic import Sanic
from sanic_openapi import swagger_blueprint, openapi_blueprint

import cador.config as cador_config
from cador.apis.v1 import v1
from cador.config import log as log
# Declare Sanic application
from cador.core.KafkaService import KafkaService
from cador.core.KafkaTopic import KafkaTopic

cador_app = Sanic(__name__)

# API Configuration
cador_app.blueprint(openapi_blueprint)
cador_app.blueprint(swagger_blueprint)
cador_app.blueprint(v1)
cador_app.config.API_VERSION = '1.0.0'
cador_app.config.API_TITLE = 'GeoProcessing SDK API'
cador_app.config.API_DESCRIPTION = 'GeoProcessing SDK API'
cador_app.config.API_TERMS_OF_SERVICE = 'Apache 2.0'
cador_app.config.API_PRODUCES_CONTENT_TYPES = ['application/json', 'mimetypes/jpeg', 'mimetypes/tiff']
cador_app.config.API_CONTACT_EMAIL = 'tesui@airbus.com'


# TODO : API SPEC URL?

######################################################################################################################################
###                                 Server Management                                                                               ##
######################################################################################################################################

# Initialize queue, semaphore & other stuffs before starting app
@cador_app.listener('before_server_start')
async def init(sanic, loop):
    cador_config.cador_processing_semaphore = asyncio.Semaphore(1, loop=loop)
    cador_config.cador_queue_semaphore = asyncio.Semaphore(1, loop=loop)

    consumer = cador_config.CADOR_QUEUES['input']
    producer = cador_config.CADOR_QUEUES['output']
    tags = cador_config.CADOR_QUEUES['tags']
    status = cador_config.CADOR_QUEUES['status']

    if consumer.server:
        await KafkaService.check_alive(consumer)
        await asyncio.gather(asyncio.ensure_future(status.init_producer()),
                             asyncio.ensure_future(producer.init_producer()),
                             asyncio.ensure_future(tags.init_producer())
                             )


# When server is online, we start consuming the queue
@cador_app.listener('after_server_start')
async def queue_consumer(sanic, loop):
    consumer = cador_config.CADOR_QUEUES['input']
    if consumer.server:
        await KafkaService.consume(consumer)


@cador_app.listener('after_server_stop')
async def close_queues(sanic, loop):
    for key in cador_config.CADOR_QUEUES.keys():
        if cador_config.CADOR_QUEUES[key] is not None:
            cador_config.CADOR_QUEUES[key].stop()


# Start function, to call inside a interpreter or directly with python3 command
def start():
    # environment variables
    try:
        cador_port = os.environ['CADOR_PORT']
        algo_server = os.environ['PROCESSING_SERVER']

        input_brokers = os.environ.get('KAFKA_BROKERS_REQUEST')
        input_topic = os.environ.get('EOPAAS_JOB_REQUEST_TOPIC')
        kafka_consumer_group = os.environ.get('KAFKA_CONSUMER_GROUP')

        output_brokers = os.environ.get('KAFKA_BROKERS_OUTPUT')
        output_topic = os.environ.get('EOPAAS_JOB_OUTPUT_TOPIC')

        status_brokers = os.environ.get('KAFKA_BROKERS_STATUS')
        status_topic = os.environ.get('EOPAAS_STATUS_UPDATE_TOPIC')

        tags_brokers = os.environ.get('KAFKA_BROKERS_TAGS', output_brokers)
        tags_topic = os.environ.get('EOPAAS_JOB_TAGS_TOPIC', output_topic)

        cador_config.CADOR_TIMEOUT_SECONDS = int(os.environ.get('CADOR_TIMEOUT_SECONDS', cador_config.CADOR_TIMEOUT_SECONDS))

    except Exception as e:
        log.error('Bad configuration of kafka brokers and topics : {}'.format(e))
        raise e

    cador_config.CADOR_ALGO_SRV = algo_server
    cador_config.CADOR_KAFKA_CONSUMER_GROUP = kafka_consumer_group

    cador_config.CADOR_QUEUES['input'] = KafkaTopic('input', input_brokers, input_topic)
    cador_config.CADOR_QUEUES['output'] = KafkaTopic('output', output_brokers, output_topic)
    cador_config.CADOR_QUEUES['status'] = KafkaTopic('status', status_brokers, status_topic)
    cador_config.CADOR_QUEUES['tags'] = KafkaTopic('tags', tags_brokers, tags_topic)

    log_app_conf()
    cador_app.run(host='0.0.0.0', port=int(cador_port))


def log_app_conf():
    """
    Load current app configuration
    """
    log.info('[CONF][ALGO_SRV] : {0}'.format(cador_config.CADOR_ALGO_SRV))
    log.info('[CONF][KAFKA_CONSUMER_GROUP] : {0}'.format(cador_config.CADOR_KAFKA_CONSUMER_GROUP))

    for key in cador_config.CADOR_QUEUES.keys():
        log.info('[CONF][{}] : {}'.format(key, cador_config.CADOR_QUEUES[key].server))
        log.info('[CONF][{}] : {}'.format(key, cador_config.CADOR_QUEUES[key].topic))


if __name__ == '__main__':
    arguments = argparse.ArgumentParser(description='Cradle For Algorithms Dockers')
    args = arguments.parse_args()
    start()
