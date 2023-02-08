## How to configure a [PESTO](https://github.com/AirbusDefenceAndSpace/pesto) service to expose an HTTPS interface

* In the PESTO environment, set the following variable:

      PESTO_USE_SSL="true"

* In the CADOR environment, update the `PROCESSING_SERVER` variable to use `https://` instead of `http://`:

      PROCESSING_SERVER="https://..."

## How to configure CADOR to expose an HTTPS interface

* In the CADOR environment, set the following variable:

      CADOR_USE_SSL="true"

## How to connect to an S3 storage through HTTPS

* In the PESTO environment, set the following variable:

      GDAL_HTTP_UNSAFESSL="YES"
