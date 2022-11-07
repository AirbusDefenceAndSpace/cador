import json
import logging

from sanic import Blueprint, response
from sanic_openapi import doc

import cador.config as cador_config
from cador.core.HelperService import HelperService, CadorMode, is_stateless
from cador.core.KafkaService import KafkaService
from cador.core.ProcessingService import ProcessingService
from cador.core.RequestService import RequestService

log = logging.getLogger(__name__)
v1 = Blueprint('v1', url_prefix='/api/v1')


######################################################################################################################################
###                                 Route defintion for direct access                                                               ##
######################################################################################################################################

@v1.route('/jobs', methods=['POST'])
@doc.summary('Run a processing')
@doc.consumes('JSON request order')
@doc.produces('JSON or raw output if stateless')
async def jobs(request):
    """
    Async processing management, receive the request and create a task to be run async
    """
    log.info('POST predict request received from {0}:{1}, sending to {2}...'.format(request.ip, request.port,
                                                                                    cador_config.CADOR_ALGO_SRV))

    request_json = request.json
    processing_service = ProcessingService(request_json)
    publisher_status = await processing_service.init_publisher(mode=CadorMode.REST)
    if publisher_status != 'OK':
        raise ValueError(publisher_status)

    process_response = await RequestService.async_processing(request_json)
    log.debug('raw response (first 256 characters) : {}'.format(str(process_response.body)[:256]))

    try:
        raw_response = json.loads(process_response.body.decode('utf-8'))
        if is_stateless():
            stateless_response = raw_response
        else:
            stateless_response = await HelperService.convert_async_to_stateless(raw_response)

        _, tag_messages = await processing_service.postprocessing_tags(stateless_response)
        process_response.body = json.dumps(stateless_response).encode('utf-8')
        log.info(str(tag_messages))
        return process_response
    except:
        log.info('response is not a json .. handling bytes as an image')
        return process_response


@v1.route('/describe', methods=['GET'])
@doc.summary('Get the service description')
@doc.produces('JSON')
async def describe(request):
    """
    Async describe request manangement
    """
    log.info('GET about request received from {0}:{1}, sending to {2}...'.format(request.ip, request.port,
                                                                                 cador_config.CADOR_ALGO_SRV))
    # return await make_get_json(cador_config.CADOR_ALGO_SRV + '/describe')
    service_info = RequestService.get_service_info()
    text = json.dumps(service_info)
    text = text.replace(cador_config.CADOR_ALGO_SRV, request.url.replace('/describe', ''))
    service_info = json.loads(text)
    return response.json(service_info)


@v1.route('/health', methods=['GET'])
@doc.summary('Check if service is OK')
async def health(request):
    messages = []

    consumer = cador_config.CADOR_QUEUES['input']
    if not KafkaService.is_alive(consumer):
        messages.append('KO : kafka is dead')

    log.info('GET health request received from {0}:{1}, sending to {2}...'.format(request.ip, request.port,
                                                                                  cador_config.CADOR_ALGO_SRV))
    process_response = await RequestService.async_get_text(cador_config.CADOR_ALGO_SRV + '/health')
    if process_response.status != 200:
        messages.append('KO : process response http code is {}'.format(process_response.status))

    if len(messages) == 0:
        messages = 'OK'

    return response.text(messages)


@v1.route('/version', methods=['GET'])
@doc.summary('Get service version')
@doc.produces('JSON')
async def version(request):
    log.info('GET version request received fron {0}:{1}, sending to {2}...'.format(request.ip, request.port,
                                                                                   cador_config.CADOR_ALGO_SRV))
    return await RequestService.async_get_json(cador_config.CADOR_ALGO_SRV + '/version')


@v1.route('/openapi', methods=['GET'])
@doc.summary('Get YAML OpenAPI specification')
async def openapi(request):
    log.info('GET openapi request received fron {0}:{1}, sending to {2}...'.format(request.ip, request.port,
                                                                                   cador_config.CADOR_ALGO_SRV))
    return await RequestService.async_get_file(cador_config.CADOR_ALGO_SRV + '/openapi')


@v1.route('/config', methods=['GET', 'PUT'])
@doc.summary('Get or update config')
async def config(request):
    if request.method == 'GET':
        return await RequestService.async_get_json(cador_config.CADOR_ALGO_SRV + '/config')
    else:
        return RequestService.async_put(cador_config.CADOR_ALGO_SRV + '/config', request.json)

# @v1.route('/result/<id>', methods=['GET', 'DELETE'])
# @doc.summary('Get or Delete a result')
# async def result(request, id):
#     log.info('GET result request received from {0}:{1}, sending to {2}...'.format(request.ip, request.port, app.config.ALGO_SRV))
#     if request.method == 'GET':
#         return await make_get_file_request(cador_config.config.ALGO_SRV + '/result/' + id)
#     elif request.method == 'DELETE':
#         return await async_delete_with_json_return(app.config.ALGO_SRV + '/result/' + id)

# @v1.route('/results', methods=['DELETE'])
# @doc.summary('Delete all local stored outputs')
# async def results(request):
#     log.info('DELETE results request received from {0}:{1}, sending to {2}...'.format(request.ip, request.port, app.config.ALGO_SRV))
#     return await async_delete_with_json_return(cador_config.config.ALGO_SRV + '/results')
