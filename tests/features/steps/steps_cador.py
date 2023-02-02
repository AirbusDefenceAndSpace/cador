import json
import os
import uuid

import requests
from behave import *
from kafka import KafkaProducer

kafka_URL = 'localhost:9092'
KAFKA_REQUEST_TOPIC = 'ipcloud_requests'
KAFKA_OUTPUT_TOPIC = 'ipcloud_out'

URL = 'http://localhost:4000'


@given(u'The web-service is running')
def step_impl(context):
    context.URL = URL


@when(u'The test folder is defined')
def step_impl(context):
    context.root_path = '{}/resources/cador'.format(os.getcwd())


@then(u'Check each test is passing')
def step_impl(context):
    for folder in os.listdir(context.root_path):
        for i in range(20):
            if os.path.isdir(os.path.join(context.root_path, folder)):
                validate_folder('{}/{}'.format(context.root_path, folder))


def validate_folder(path):
    input_path = '{}/input'.format(path)
    payload = _generate_payload(input_path)

    producer = KafkaProducer(bootstrap_servers=kafka_URL,
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    producer.send(KAFKA_REQUEST_TOPIC, payload).get(timeout=10)


def _generate_payload(path, image_prefix='file://'):
    payload = {
        'technicalMetadata': {
            'postProcessing': {
                'tags': True
            },
            'referential': {
                'upperLeft': {
                    'lat': 41.2,
                    'lon': 2.07
                },
                'latStep': 1.07E-5,
                'lonStep': 1.072E-5
            },
            'outputStorage': {
                'S3': {
                    'key': '',
                    'secret': '',
                    'host': 'object-storage',
                    'port': '9000',
                    'ssl': False,
                    'container': 'test',
                    'container_folder': 'my/specific/folder'
                }
            },
            'taskId': str(uuid.uuid4())
        }
    }

    for file in os.listdir(path):
        name, ext = os.path.splitext(file)
        if ext == '.string':
            with open('{}/{}'.format(path, file)) as f:
                value = f.read()
        elif ext == '.float':
            with open('{}/{}'.format(path, file)) as f:
                value = float(f.read())
        elif ext == '.int':
            with open('{}/{}'.format(path, file)) as f:
                value = int(f.read())
        elif ext == '.json':
            with open('{}/{}'.format(path, file)) as f:
                value = json.load(f)
        else:
            value = '{}{}/{}'.format(image_prefix, path, file)
        payload[name] = value
    return payload


def download_result(URL, link):
    response = requests.get('{}{}'.format(URL, link), verify=False)
    tmp_path = '/tmp/{}'.format(str(uuid.uuid4()))
    with open(tmp_path, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=128):
            fd.write(chunk)
    return tmp_path
