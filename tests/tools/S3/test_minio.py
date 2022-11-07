from minio import Minio

minioClient = Minio('localhost:9000',
                    access_key='',
                    secret_key='',
                    secure=False)


#minioClient.make_bucket('test')


buckets = minioClient.list_buckets()
for bucket in buckets:
    print(bucket.name, bucket.creation_date)
