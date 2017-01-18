import os
import boto3
import mimetypes
import json

# Set environments variables or config in your user directory for access key and secret

INDEX_BUCKET_NAME = 'content-hackathon-dg-test-index'
QUERY_BUCKET_NAME = 'content-hackathon-dg-test-query'
S3 = boto3.resource('s3')

def get_all_files_in_bucket(bucket_name):
    files = []
    for key in S3.Bucket(bucket_name).objects.all():
        if not key.key.endswith("/"):
            #print key.key + " - " + str(key.size)
            files.append(key.key)
    print str(len(files)) + " files in bucket: " + bucket_name
    return files
def get_all_files_in_index_bucket():
    return get_all_files_in_bucket(INDEX_BUCKET_NAME)
def get_all_files_in_query_bucket():
    return get_all_files_in_bucket(QUERY_BUCKET_NAME)



def download_file(bucket_name, directory, key):
    print "Downloading - " + key + " from bucket: " + bucket_name + " - START"
    s3object = S3.Object(bucket_name,key)
    fileDesination = directory+key
    if not os.path.exists(os.path.dirname(fileDesination)):
        os.makedirs(os.path.dirname(fileDesination))
    s3object.download_file(directory+key)
    print "Downloading - " + key + " from bucket: " + bucket_name + " - COMPLETE"
def download_index_file(directory, key):
    download_file(INDEX_BUCKET_NAME, directory, key)
def download_query_file(directory, key):
    download_file(QUERY_BUCKET_NAME, directory, key)

# def upload_files_to_s3(bucket_name, local_folder, files, s3path=''):
#     print "Attempting to upload " + str(len(files)) + " to bucket: " + bucket_name

#     print "Deleting all"
#     bucket = S3.Bucket(bucket_name)
#     for key in bucket.objects.all():
#         S3.Object(bucket_name,key.key).delete()
    
#     for file in files:
#         key = s3path + file
#         print "Uploading " + local_folder + file + " to " + key
#         bucket.upload_file(local_folder + file,key, ExtraArgs={'ContentType': mimetypes.guess_type(file)[0], 'ACL': "public-read"})
        
#     print "Uploaded complete"

# def upload_index_files_to_s3(local_folder, files):
#     upload_files_to_s3(INDEX_BUCKET_NAME, local_folder, files, s3path='test-folder/')
# def upload_query_files_to_s3(local_folder, files):
#     upload_files_to_s3(QUERY_BUCKET_NAME, local_folder, files)

def upload_file_to_s3(bucket_name, local_folder, s3path, file):
    bucket = S3.Bucket(bucket_name)
    key = s3path + file
    bucket.upload_file(local_folder + s3path + file,key, ExtraArgs={'ContentType': mimetypes.guess_type(file)[0], 'ACL': "public-read"})

def delete_s3_bucket_contents(bucket_name):
    # bucket = S3.Bucket(bucket_name)
    # for key in bucket.objects.all():
    #     S3.Object(bucket_name,key.key).delete()

    bucket = S3.Bucket(bucket_name)

    keys = []
    paginator = boto3.client('s3').get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(
        Bucket=bucket_name,
        PaginationConfig={
            'PageSize': 350,
            'StartingToken': None})


    for page in response_iterator:
        if 'Contents' in page:
            c = page['Contents']
            for contents in c:
                key = contents['Key']
                keys.append(key)

    for i, key in enumerate(keys):
        print "Deleting " + str(i+1) + " of " + str(len(keys)) + " - " + key
        S3.Object(bucket_name,key).delete()

def execute_lambda_indexing_function(key):
    payload = json.dumps({"key" : key})

    client = boto3.client('lambda')
    client.invoke(
        FunctionName='aws-lambda-python-opencv-index',
        InvocationType='Event',
        LogType='None',
        ClientContext='string',
        Payload=payload
    )

def add_record_to_kenesis_stream(key, partition_key="partition_key_1"):

    client = boto3.client('kinesis')
    client.put_record(
        StreamName='aws-lambda-python-opencv',
        Data=key,
        PartitionKey=partition_key
    )


def get_paginated_files_and_add_to_kenesis():
    print "start"
    count = 0
    paginator = boto3.client('s3').get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(
        Bucket=INDEX_BUCKET_NAME,
        PaginationConfig={
            'PageSize': 350,
            'StartingToken': None})

    kinesis = boto3.client('kinesis')

    for page in response_iterator:
        print("Next Page : {} ".format(page['IsTruncated']))
        c = page['Contents']
        records = []
        for contents in c:
            key = contents['Key']
            count = count + 1
            record = {'Data': key, 'PartitionKey': 'k1'}
            #print record
            records.append(record)
        print len(records)
        result = kinesis.put_records(
            Records=records,
            StreamName='aws-lambda-python-opencv'
        )
        print result
    print count
    
def get_paginated_files_and_add_to_sns():
    print "start"
    count = 0
    paginator = boto3.client('s3').get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(
        Bucket=INDEX_BUCKET_NAME,
        PaginationConfig={
            'PageSize': 350,
            'StartingToken': None})

    sns = boto3.client('sns')

    for page in response_iterator:
        print("Next Page : {} ".format(page['IsTruncated']))
        c = page['Contents']
        for contents in c:
            key = contents['Key']
            count = count + 1
            
            # Need to validate file extensions
            
            # result = sns.publish(
            #     TopicArn='arn:aws:sns:eu-central-1:841881772957:aws-lambda-python-opencv-index',
            #     Message=key
            # )

            # print result
            print count
    print count
    return "Indexing triggered for " + str(count) + " images"