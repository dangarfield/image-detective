import cv2

import app_services
import aws_utils


def lambda_handler_kinesis_old(event, context):

    files = aws_utils.get_all_files_in_index_bucket()

    for file in files:
        print "Indexing: "
        print file
        aws_utils.execute_lambda_indexing_function(file)

    file = files[0]
    aws_utils.add_record_to_kenesis_stream(file)

    print "Triggered index for " + str(len(files)) + " images"
    return "Triggered index for " + str(len(files)) + " images"

def lambda_handler_kinesis_batch(event, context):
    return aws_utils.get_paginated_files_and_add_to_kenesis()

def lambda_handler_sns(event, context):
    return aws_utils.get_paginated_files_and_add_to_sns()


def lambda_handler(event, context):
    return lambda_handler_sns(event, context)

### Test locally with:
# python-lambda-local -f lambda_handler DET\lambda_query.py lambda-test-data\query.json