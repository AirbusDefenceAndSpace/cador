import io
import os

import boto3
import libcloud
from libcloud.storage.providers import get_driver
from libcloud.storage.types import Provider

"""
Example configuration :
  "S3": {
        "url": "http://localhost:39999/api/v1/s3",
        "container_path": "cccc/aaa/tt/bb",
        "ssl": False,
        "key": "",
        "secret": ""
    }

Example usage :
storage = StorageService.create(config)
data = bytes('abcd')
storage.store('item', data)

"""


class StorageService:
    @staticmethod
    def create(storage_config: dict):
        if "S3" in storage_config.keys():
            return S3Service(storage_config['S3'])
        elif "GCS" in storage_config.keys():
            return GCSService(storage_config['GCS'])
        elif "POSIX" in storage_config.keys():
            return POSIXService(storage_config['POSIX'])
        else:
            raise ValueError('Unsupported object store type')

    def store(self, object_id: str, raw) -> dict:
        raise NotImplementedError()

    def init(self):
        raise NotImplementedError()


class S3Service(StorageService):

    def __init__(self, config: dict):
        parts = config['containerPath'].split('/')
        self.container_path = config['containerPath']
        self.container = parts[0]
        self.container_folder = os.path.join(*parts[1:]) if len(parts) > 1 else ''

        self.s3 = boto3.resource('s3',
                                 use_ssl=config.get('ssl') or False,
                                 endpoint_url=(config['url']),
                                 aws_access_key_id=(config['key']),
                                 aws_secret_access_key=(config['secret']),
                                 verify=False)

    def init(self):
        try:
            self.s3.create_bucket(Bucket=self.container)
        except Exception as e:
            print(e)
            pass

    def store(self, object_id: str, raw) -> dict:
        object_path = os.path.join(self.container_folder, object_id)
        storage_object = self.s3.Object(self.container, object_path)
        response = storage_object.put(Body=raw)
        response = {
            'containerPath': self.container_path,
            'objectId': object_id
        }
        return response


class GCSService(StorageService):

    def __init__(self, config: dict):
        self.driver = get_driver(Provider.GOOGLE_STORAGE)(key=config['key'], secret=config['secret'])
        self.container_path = config['containerPath']

    def init(self):
        try:
            self.driver.get_container(self.container_path)
        except libcloud.storage.types.ContainerDoesNotExistError:
            self.driver.create_container(self.container_path)

    def store(self, object_id: str, raw) -> dict:
        container = self.driver.get_container(self.container_path)
        blob = self.driver.upload_object_via_stream(io.BytesIO(raw), container, object_id)

        response = {
            'containerPath': self.container_path,
            'objectId': object_id
        }
        return response


class POSIXService(StorageService):

    def __init__(self, config: dict):
        self.folder = config['folder']

    def init(self):
        os.makedirs(self.folder, exist_ok=True)

    def store(self, object_id: str, raw) -> dict:
        object_path = os.path.join(self.folder, object_id)

        with open(object_path, 'wb') as _:
            _.write(raw)

        response = {
            'folder': self.folder,
            'objectId': object_id
        }
        return response
