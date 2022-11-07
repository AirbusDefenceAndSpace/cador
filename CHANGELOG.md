# Change Log

All notable changes and fixes to this project will be document in this file.

## Version
 * 0.7.3 : fix output image format png, remove indirection to storage in output messages, better messages output, status in microseconds, POSIX storage
 * 0.7.2 : uniform storage message output between GCS and S3
 * 0.7.1 : bug fix with kafka handling
 * 0.7.0 : health check update, alluxio support, switch from libcloud to boto3, sanic update to 0.8.3
 * 0.6.2 : fix processing endpoint
 * 0.6.1 : fix CPU 100% after first processing
 * 0.6.0 : convert geometry to tags
 * 0.5.0 : Subdirectories in storage buckets
 * 0.4.0 : Asynchronous mode
 * 0.2.0 : Migration to Open Source GeoProcessing API, libcloud integration

### Recent changes
 * GeoProcessing API has evolved to converge with Airbus DS Geo API, the new API is Open Source
 * Apache libcloud integration, full support of S3
 * Google Cloud Storage management is now mapped on libcloud

### Upcoming changes
 * To Be Defined

### Known issues
 * Limited support of TagEntry format
