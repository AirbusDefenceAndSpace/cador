import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import requests
from sanic import response

import cador.config as cador_config
from cador.config import log


class RequestService:
    HEADERS = {'X-Serverd-By': 'CADoR'}

    @staticmethod
    def get_service_info():
        """
        Get service information from describe, call the async routine
        """
        if not cador_config.cador_cache_service_description:
            r = requests.get(cador_config.CADOR_ALGO_SRV + '/describe')
            if r.status_code != 200:
                message = 'Bad response : server algorithm send {0} with code {1}'.format(r.text, r.status_code)
                raise ValueError(message)
            cador_config.cador_cache_service_description = r.json()
        return cador_config.cador_cache_service_description

    @staticmethod
    async def async_processing(payload):
        """
        Make prediction
        :param payload: json content describing the request
        :return a Sanic response
        """

        semaphore = cador_config.cador_processing_semaphore
        await semaphore.acquire()
        try:
            processing_path = RequestService.get_service_info()['_links'].get('execution', {}).get('href', '/jobs')
            if processing_path.startswith('http'):
                url = processing_path
            else:
                url = cador_config.CADOR_ALGO_SRV.replace('/api/v1', processing_path)
            log.info('processing on : {}'.format(url))

            future = RequestService.async_post(url=url, payload=payload)
            r = await asyncio.wait_for(future, timeout=1000)

            return r
        except Exception as e:
            log.exception(e)
            return make_error_response('Error handling predict request : {}'.format(e))
        finally:
            semaphore.release()

    @staticmethod
    async def async_post(url, payload):
        r = await RequestService.async_exec(partial(requests.post, url, json=payload))
        return response.raw(r.content, status=r.status_code)

    @staticmethod
    async def async_get(url):
        return await RequestService.async_exec(partial(requests.get, url))

    @staticmethod
    async def async_get_text(url):
        try:
            r = await RequestService.async_get(url)
            return response.text(r.text, status=r.status_code)
        except Exception as e:
            log.exception(e)
            return make_error_response('Error handling get request on {0}'.format(url))

    @staticmethod
    async def async_get_json(url):
        """
        Make a get request on given url, with JSON return only
        :param url: service url
        :return a Sanic response
        """
        try:
            r = await RequestService.async_get(url)
            return response.json(r.json(), status=r.status_code)
        except Exception as e:
            log.exception(e)
            return make_error_response('Error handling get request on {0}'.format(url))

    @staticmethod
    async def async_get_file(url):
        """
        Make a GET request on given url to retrieve a file
        :param url: service url
        :return a Sanic response
        """
        try:
            r = await RequestService.async_get(url)
            return response.raw(r.content, status=r.status_code)
        except Exception as e:
            log.exception(e)
            return make_error_response('Error handling file request on {0}'.format(url))

    @staticmethod
    async def async_delete(url):
        return await RequestService.async_exec(partial(requests.delete, url))

    @staticmethod
    async def async_delete_json(url):
        """
        Make a delete request on given url, with JSON return only
        :param url: service url
        :return a Sanic response
        """
        try:
            r = await RequestService.async_exec(partial(requests.delete, url))
            return response.json(r.json(), headers=RequestService.HEADERS, status=r.status_code)
        except Exception as e:
            log.exception(e)
            return make_error_response('Error handling delete request on {0}'.format(url))

    @staticmethod
    async def async_put(url, payload):
        """
        Make a put request
        :param url: service url
        :param payload: json payload
        :return a Sanic response
        """
        try:
            r = await RequestService.async_exec(partial(requests.put, url=url, json=payload))
            return response.json(r.json(), status=r.status_code)
        except Exception as e:
            log.exception(e)
            return make_error_response('Error handling put request')

    @staticmethod
    async def async_exec(callback):
        with ThreadPoolExecutor() as executor:
            return await asyncio.get_event_loop().run_in_executor(executor, callback)


def make_error_response(message):
    return response.json({'message': message}, headers=RequestService.HEADERS, status=500)
