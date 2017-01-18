import base64
import json

import app_services
import aws_utils

def download_and_index(key):
    aws_utils.download_index_file(app_services.INDEX, key)
    indexed_images = app_services.hash_and_index_full_and_features(app_services.INDEX, app_services.INDEX_FEATURES, key, index_name=aws_utils.INDEX_BUCKET_NAME)
    print "Indexed " + key + " and " + str(len(indexed_images)-1) + " feature images"
    return indexed_images


def lambda_handler(event, context):

    all_indexed_images = []

    print "event"
    print event
    if 'key' in event:
        key = event['key']
        print "Standard key : "
        all_indexed_images.append(download_and_index(key))
    else:
        for record in event["Records"]:
            print record
            if 'kinesis' in record:
                print "Kenesis driven key :"
                key = base64.b64decode(record['kinesis']['data'])
            else:
                print "Sns driven key :"
                key = record['Sns']['Message']

            print "Key for index: " + key
            all_indexed_images.append(download_and_index(key))
            
    return all_indexed_images

### Test locally with:
# python-lambda-local -f lambda_handler DET\lambda_query.py lambda-test-data\query.json