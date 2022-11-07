import io

import libcloud
from libcloud.storage.providers import get_driver
from libcloud.storage.types import Provider

s3 = get_driver(Provider.S3)

driver = s3(key='',
            secret='',
            host='object-storage',
            port='9000',
            secure=False
            )

# driver.upload_object_via_stream(io.BytesIO('bbbbbb'.encode('utf-8')), driver.get_container('test'), 'id_432')

# l = driver.list_containers()

try:
    container = driver.get_container(container_name='test')
    print(str(container))
except libcloud.storage.types.ContainerDoesNotExistError:
    container = driver.create_container('test')
    print(str(container))

message = driver.upload_object_via_stream(io.BytesIO('bbbbbb'.encode('utf-8')), driver.get_container('test'), 'id_432')

driver.get_object_cdn_url(message)

