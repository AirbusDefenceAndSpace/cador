# How to test http & https

* In the `docker-compose.yaml` file, edit the `pesto.image` & `cador.image` fields to use available docker images:

      vim docker-compose.yaml

* Run the docker instances:

      docker-compose -f docker-compose.yaml --project-name ipcloud up

* Find the IP of your `minio` docker:

      docker exec -it minio ip a | grep "inet.*eth0"

* Register your `minio` container as a known host:

      sudo vim /etc/hosts
      # Append this line (replacing x.x.x.x with your minio IP): x.x.x.x minio

* Create a `minio` bucket, upload an image and create a shareable link:

      firefox http://minio:9000
      # Create a bucket named "testbucket"
      # Upload an image in the bucket test_image.tif
      # Create an authentified URL of the stored image : http://minio:9000/testbucket/test_image.tif?...

* Send a processing request through Kafka and try to open the processing result. Expected output is `"Successfully downloaded an image..."`.

      python run_cador_with_kafka.py "http://minio:9000/testbucket/test_image.tif?..."

* Remove the test containers:

      docker-compose -f docker-compose.yaml --project-name ipcloud down -v

## How to test https

Run the same steps as http with the following changes:
* Use `docker-compose-https.yaml` instead of `docker-compose.yaml`
* Connect to the minio web portal through `https://minio:9000` instead of `http://minio:9000`
* Use `run_cador_with_kafka_https.py` instead of `run_cador_with_kafka.py`
