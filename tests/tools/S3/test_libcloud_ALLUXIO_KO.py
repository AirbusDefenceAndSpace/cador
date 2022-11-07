import io

import libcloud
from libcloud.storage.base import Container
from libcloud.storage.providers import get_driver
from libcloud.storage.types import Provider

s3 = get_driver(Provider.S3)

driver = s3(
    key='',
    secret='',
    api_version='/api/v1/s3',
    host='127.0.0.1',
    port='39999',
    secure=False
)
container = driver.create_container('tttt')


try:
    container = driver.get_container(container_name='/test')
except libcloud.storage.types.ContainerDoesNotExistError:
    container = driver.create_container('test')

message = driver.upload_object_via_stream(io.BytesIO('bbbbbb'.encode('utf-8')), driver.get_container('test'), 'id_432')

driver.get_object_cdn_url(message)
