# Cradle For Algorithm Docker

CADOR is a wrapper for [GeoProcessingAPI](https://github.com/AirbusDefenceAndSpace/geoprocessing-api/tree/master/1.0)-compliant services. CADOR listens to a kafka topic, runs a process upon receiving a message, and can optionally write output images in an object storage.

# Get started

## Install & build

To build wheel package & docker image :
```bash
$ cd docker && make build
```

To install:
```bash
$ make install
```

# How to use

## API REST

CADoR exposes the same REST API as the GeoProcessing SDK : 

 * http://server:port/describe : GET request, returning the service information in JSON format,
 * http://server:port/jobs : POST request, run the processing and deal with the results locally on the server
 * http://server:port/health : GET request to test if service is alive
 * http://server:port/swagger : GET request giving access to swagger API description

It deals with these requests and manage the docker algorithm.

## KAFKA

Image can be read in input queue if it has been configured. In this case, results are push to a queue or an object store given the configuration.

## Accepted payload

CADoR behaviour can be tunned by adding a 'technicalMetadata' field to the algorithm payload :
- outputStorage : configure S3, GCS ou POSIX storage to store output images
- referential : if present, convert all output geojson coordinates
- postProcessing.tags : automatic transformation of geojson output into tags

```json
 {
     ... // algorithm payload
     
     "technicalMetadata" : {
         "outputStorage" : {
             ... // S3, GCS ou POSIX configuration (cf. Storage configurations)
         },
         "postProcessing": {
            "tags": true
         },         
         "referential": {
            "upperLeft": {
              "lat": 41.2,
              "lon": 2.07
            },
            "latStep": 1.07E-5,
            "lonStep": 1.072E-5
         }         
     }
 }
```

S3 storage :
```
  "outputStorage": {
    "S3": {
      "url": "http://object-storage:9000/api/v1/s3",
      "containerPath": "folder0/folder1/folder2/test",
      
      "ssl": false,
      "key": "xxxxx",
      "secret": "xxxxx"
    }
  },
```

GCS storage :
```
  "outputStorage": {
    "GCS": {
      "containerPath": "folder0/folder1/folder2/test",
      
      "key": "xxxxx",
      "secret": "xxxxx"
    }
  },
```
POSIX storage :
```
  "outputStorage": {
    "POSIX": {
      "folder": "/path/to/Storage"
    }
  },
```

[Example payload](https://github.com/AirbusDefenceAndSpace/cador/blob/master/tests/integration_tests/http/run_cador_with_kafka.py#L62) storing the result in a S3 storage.

## Configuration
You can configure the server with the following environement variables : 

 * CADOR_PORT : port where the server run
 * CADOR_USE_SSL : whether to use SSL or not (call the service with `https` scheme if set to `"true"`)
 * PROCESSING_SERVER : address of the algorithm docker to bin with
 * KAFKA_BROKERS_REQUEST : queue_in to read request orders (only kafka is available for now). Not mandatory, if not provided only REST API is available
 * EOPAAS_JOB_REQUEST_TOPIC : queue_in topic, mandatory if queue_in specified
 * KAFKA_CONSUMER_GROUP : group used by all Kafka consumers, all instances of cador for one algorithm needs to have the same
 * KAFKA_BROKERS_OUTPUT : queue_out to push results
 * EOPAAS_JOB_OUTPUT_TOPIC : topic for queue out
 * KAFKA_BROKERS_STATUS : queue to push status, not mandatory
 * EOPAAS_STATUS_UPDATE_TOPIC : topic to push status
 * KAFKA_BROKERS_TAGS : queue to push tags, not mandatory
 * EOPAAS_JOB_TAGS_TOPIC : topic to push tags

[Example configuration](https://github.com/AirbusDefenceAndSpace/cador/blob/master/tests/integration_tests/http/docker-compose.yaml#L40)
