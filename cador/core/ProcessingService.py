import json

from cador.config import log
from cador.core.HelperService import HelperService, CadorMode, is_stateless, response_entry_is_image, \
    response_is_image
from cador.core.PublisherService import PublisherService, JobStatus
from cador.core.RequestService import RequestService
from cador.core.TagService import TagService


class ProcessingService:

    def __init__(self, request: dict) -> None:
        log.info('init processing ...')
        self.request = request
        self.technical_metadata = request.pop('technicalMetadata') if 'technicalMetadata' in request else {}
        self.user_metadata = request.pop('userMetadata') if 'userMetadata' in request else {}
        self.job_id = self.technical_metadata.get('taskId')
        self.publisher = None
        self.tag_postprocessing = self.technical_metadata.get('postProcessing', {}).get('tags', False)
        log.info('running in stateless mode : {}'.format(is_stateless()))

    async def init_publisher(self, mode: CadorMode):
        try:
            self.publisher = PublisherService(mode, self.technical_metadata, self.user_metadata)
            return 'OK'
        except Exception as e:
            message = 'Error while loading publisher service ! {}'.format(e)
            log.error(str(message))
            return e

    async def handle_request(self):
        try:
            publisher_status = await self.init_publisher(mode=CadorMode.KAFKA)
            if publisher_status == 'OK':
                await PublisherService.publish_status(job_id=self.job_id, status=JobStatus.RUNNING)
            else:
                return await PublisherService.publish_status(job_id=self.job_id, status=JobStatus.FAILED,
                                                             error_message=publisher_status)

            log.info('Start processing ...')
            response = await RequestService.async_processing(self.request)

            if response.status != 200:
                log.error('Error while calling processing web service !')
                return await PublisherService.publish_status(job_id=self.job_id, status=JobStatus.FAILED,
                                                             error_message=response.body)

            self.request['technicalMetadata'] = self.technical_metadata
            self.request['userMetadata'] = self.user_metadata

            if is_stateless():
                messages = await self.stateless_response_handler(response)
            else:
                messages = await self.asynchronous_response_handler(response)
            return await PublisherService.publish_status(job_id=self.job_id, status=JobStatus.SUCCEEDED,
                                                         messages=messages)
        except Exception as e:
            log.error('error while processing : {}'.format(e))
            log.exception(e)
            return await PublisherService.publish_status(job_id=self.job_id, status=JobStatus.FAILED, error_message=e)

    async def stateless_response_handler(self, response):
        if response_is_image(response):
            published_message = await self.publisher.publish_image(self.job_id, 'output', response.body)
            log.info('published image message : {}'.format(str(published_message)))
            messages = [published_message]
        else:
            stateless_response = json.loads(response.body.decode('utf-8'))
            stateless_response, tag_messages = await self.postprocessing_tags(stateless_response)
            published_message = await self.publisher.publish_output_with_metadata(stateless_response)
            messages = tag_messages + [published_message]
        return messages

    async def asynchronous_response_handler(self, response):
        async_response = json.loads(response.body.decode('utf-8'))

        stateless_response = await HelperService.convert_async_to_stateless(async_response)
        storage_messages = await self.image_to_storage(stateless_response)
        stateless_response, tag_messages = await self.postprocessing_tags(stateless_response)
        published_message = await self.publisher.publish_output_with_metadata(stateless_response)
        messages = storage_messages + tag_messages + [published_message]
        return messages

    async def image_to_storage(self, response_stateless):
        messages = list()
        for result_key in response_stateless:
            data = response_stateless[result_key]
            if response_entry_is_image(data):
                response_stateless[result_key] = await self.publisher.publish_image(self.job_id, result_key, data)
                messages.append(response_stateless[result_key])
        return messages

    async def postprocessing_tags(self, stateless_response: dict, output_kafka_messages: bool = False):
        if stateless_response.get('features') is not None:
            stateless_response = {'___patch___': stateless_response}

        messages = list()
        tag_service = TagService()
        inputs = self._build_inputs()
        referential = self.technical_metadata.get('referential')
        timestamp = self.technical_metadata.get('inputTimestamp')
        log.info('referential: {}'.format(referential))
        for result_key in stateless_response:
            tags = tag_service.extract_tags(inputs, referential, timestamp, stateless_response, result_key)
            # stateless_response[result_key] = tags

            if len(tags) > 0 and self.tag_postprocessing:
                log.info('tags: {} (#tags={})'.format(result_key, len(tags)))
                key_messages = await self.publisher.publish_tags(tags)
                messages.extend(key_messages)
                # if output_kafka_messages:
                #     stateless_response[result_key] = key_messages

        if stateless_response.get('___patch___') is not None:
            stateless_response = stateless_response.get('___patch___')

        return stateless_response, messages

    def _build_inputs(self):
        inputs = []
        for entry in self.request:
            if request_is_image(entry):
                inputs.append({'uri': self.request[entry]})
        return inputs


def request_is_image(entry):
    try:
        service_info = RequestService.get_service_info()
        return 'Image' in service_info['input']['properties'][entry]['$ref']
    except:
        return False
