import logging

# Set log format
logging_format = "[%(asctime)s] %(process)d-%(levelname)s "
logging_format += "%(module)s::%(funcName)s():l%(lineno)d: "
logging_format += "%(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO)
log = logging.getLogger()

logging.getLogger('aiokafka').setLevel(logging.INFO)
logging.getLogger('boto').setLevel(logging.CRITICAL)

# CADoR Global Variables for Queues and processing semaphore
cador_processing_semaphore = None
cador_queue_semaphore = None
cador_kafka_available = None

# CADoR Cache
cador_cache_service_description = None

# CADoR Application Configuration
CADOR_ALGO_SRV = None
CADOR_KAFKA_CONSUMER_GROUP = None

CADOR_QUEUES = {
    # input, output, tags, status
}

CADOR_TIMEOUT_SECONDS = 10
