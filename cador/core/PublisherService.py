import json
import socket
import time

import cador.config as cador_config
from cador.config import log
from cador.core.HelperService import output_with_image, is_stateless, CadorMode
from cador.core.StorageService import StorageService


def _format_status(job_id: str, status: str, error_message: str = None, kafka_messages: [str] = None) -> str:
    if status not in [JobStatus.FAILED, JobStatus.CANCELLED] or error_message is None:
        error_message = ""

    json_status = {
        'taskId': job_id,
        'status': status,
        'errMsg': str(error_message),
        'node': {
            'containerId': socket.gethostname()
        },
        'stats': {
            'duration': 0  # TODO
        },
        'modifiedAt': int(round(time.time() * 1000))
    }

    if kafka_messages:
        json_status['producedKafkaMessages'] = kafka_messages

    return json.dumps(json_status)


class JobStatus:
    UNKNOWN = 'UNKNOWN'
    ACCEPTED = 'ACCEPTED'
    RUNNING = 'RUNNING'
    FAILED = 'FAILED'
    SUCCEEDED = 'SUCCEEDED'
    CANCELLED = 'CANCELLED'
    PAUSED = 'PAUSED'


def _is_storage_needed(mode: CadorMode):
    kafka_condition = (mode is CadorMode.KAFKA) and output_with_image()
    rest_condition = (mode is CadorMode.REST) and not is_stateless() and output_with_image()
    return kafka_condition or rest_condition


class PublisherService:

    def __init__(self, mode: CadorMode, technical_metadata=None, user_metadata=None) -> None:
        log.info('init PublishService ... (mode={})'.format(mode))

        if technical_metadata is None:
            technical_metadata = {}
        if user_metadata is None:
            user_metadata = {}

        self.producer_output = cador_config.CADOR_QUEUES['output']
        self.tag_output = cador_config.CADOR_QUEUES['tags']

        self.technical_metadata = technical_metadata
        self.user_metadata = user_metadata
        self.storage = None

        storage_config = technical_metadata.get('outputStorage')
        if storage_config is not None and storage_config != {}:
            log.info('object storage initialisation ...')
            storage_config = self.technical_metadata['outputStorage']
            self.storage = StorageService.create(storage_config)
            self.storage.init()

    async def publish_image(self, job_id: str, result_key, image_content):
        has_storage = self.storage is not None
        log.info('publish image with storage={}'.format(has_storage))
        if has_storage:
            return await self.publish_object(job_id, result_key, image_content)
        else:
            raise ValueError('Could not publish image : No storage was defined')
            # return await self.publish_output(image_content)

    async def publish_object(self, job_id: str, object_id: str, response_content):
        message = self.storage.store('{}_{}'.format(job_id, object_id), response_content)
        return message
        # msg = str.encode(json.dumps(message))
        # return await self.publish_output(msg)

    async def publish_output(self, raw):
        return await self.producer_output.publish(raw)

    async def publish_output_with_metadata(self, data: dict):
        msg = dict(data)
        msg['technicalMetadata'] = self.technical_metadata
        msg['userMetadata'] = self.user_metadata
        msg = str.encode(json.dumps(msg))
        return await self.publish_output(msg)

    @staticmethod
    async def publish_status(job_id, status, error_message=None, messages=None):
        msg = str.encode(_format_status(job_id, status, error_message, messages))
        return await cador_config.CADOR_QUEUES['status'].publish(msg)

    async def publish_tags(self, tags: []):
        messages = []
        for tag in tags:
            msg = await self.publish_tag(tag)
            messages.append(msg)
        return messages

    async def publish_tag(self, final_tag: dict):
        msg = str.encode(json.dumps(final_tag))
        return await self.tag_output.publish(msg)
