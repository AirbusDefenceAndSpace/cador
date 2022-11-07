#!/usr/bin/env bash

export KAFKA_BROKERS_REQUEST=kafka:9092
export KAFKA_BROKERS_OUTPUT=kafka:9092
export KAFKA_BROKERS_STATUS=kafka:9092

export EOPAAS_JOB_REQUEST_TOPIC=ipcloud_requests
export EOPAAS_JOB_OUTPUT_TOPIC=ipcloud_out
export EOPAAS_STATUS_UPDATE_TOPIC=ipcloud_status

