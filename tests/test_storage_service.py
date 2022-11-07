from cador.core.StorageService import StorageService

config_alluxio = {
    "S3": {
        "url": "http://alluxio-storage:39999/api/v1/s3",
        "container_path": "test",

        "ssl": False,
        "key": "",
        "secret": ""
    }
}

config_minio = {
    "S3": {
        "url": "http://object-storage:9000",
        "container_path": "xxxxxxxx",

        "ssl": False,
        "key": "",
        "secret": ""
    }
}

config = config_alluxio

storage = StorageService.create(config)

storage.init()
response = storage.store('xxx', 'test content')

print(response)
