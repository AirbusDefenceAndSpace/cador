import boto3

access_key = ''
secret_key = ''
endpoint_url = ''

s3 = boto3.resource('s3',
                    use_ssl=False,
                    endpoint_url=endpoint_url,
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key)


bucket_name = 'bucket-for-testing'
# s3.create_bucket(Bucket=bucket_name)

s3.Object(bucket_name, 'xx').put(Body='signed URL with ALLUXIO')


