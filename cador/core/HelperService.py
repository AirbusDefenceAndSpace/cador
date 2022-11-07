from enum import Enum
from typing import Any

from cador.config import log
from cador.core.RequestService import RequestService


class CadorMode(Enum):
    KAFKA = 'KAFKA'
    REST = 'REST'


class HelperService:
    @staticmethod
    async def convert_async_to_stateless(async_response: dict) -> dict:
        job_results_url = async_response['link'].replace('status', 'results')
        job_response = await RequestService.async_get(job_results_url)
        reponse_stateless = job_response.json()
        for result_key in reponse_stateless:
            log.info('asynchronous : handle {}'.format(result_key))
            partial_output_url = reponse_stateless[result_key]
            raw_response = await RequestService.async_get(partial_output_url)
            if response_is_image(raw_response):
                log.info('image: {}'.format(result_key))
                reponse_stateless[result_key] = raw_response.content
            else:
                log.info('json: {}'.format(result_key))
                reponse_stateless[result_key] = raw_response.json()
            # clean up processing results
            await RequestService.async_delete('{}/{}'.format(job_results_url, result_key))
        return reponse_stateless


def is_stateless() -> bool:
    service_info = RequestService.get_service_info()
    return not service_info['asynchronous']


def output_with_image():
    service_info = RequestService.get_service_info()

    content = service_info['output']['content']
    image_as_output = any([
        '#/definitions/Image' in content,
        'image' in content,
        any(['image' in _ for _ in content.values()])
    ])
    return image_as_output


def response_is_image(response):
    return response.headers.get('Content-Type', '').startswith('image')


def response_entry_is_image(data: Any) -> bool:
    return isinstance(data, bytes)
