import cv2

import app_services
import aws_utils


def lambda_handler(event, context):

    print "OpenCV installed version:", cv2.__version__

    key = event['key']
    hash_type = 'dhash'
    print "Key for query: " + key

    aws_utils.download_query_file(app_services.QUERY, key)
    results = app_services.query(key, hash_type, True, True, index_name=aws_utils.INDEX_BUCKET_NAME)

    print results
    
    return results

### Test locally with:
# python-lambda-local -f lambda_handler DET\lambda_query.py lambda-test-data\query.json