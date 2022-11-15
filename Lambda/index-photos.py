import json
import os
import time
import logging
import boto3
from datetime import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

region = 'us-east-1'
service = 'es'
host = 'vpc-photos-ryu2uf43z2m5tbnfpuizbuc3ua.us-east-1.es.amazonaws.com/'
rekognition = boto3.client('rekognition')

es = Elasticsearch(
    hosts=[{'host': host,'port':443}],
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    http_auth=('admin', 'Admin@12345')
    )

def handler(event, context):

    os.environ['TZ'] = 'America/New_York'
    time.tzset()

    records = event['Records']
    #print(records)

    for record in records:

        s3object = record['s3']
        bucket = s3object['bucket']['name']
        objectKey = s3object['object']['key']

        image = {
            'S3Object' : {
                'Bucket' : bucket,
                'Name' : objectKey
            }
        }

        response = rekognition.detect_labels(Image = image)
        labels = list(map(lambda x : x['Name'], response['Labels']))
        timestamp = datetime.now().strftime('%Y-%d-%mT%H:%M:%S')

        esObject = json.dumps({
            'objectKey' : objectKey,
            'bucket' : bucket,
            'createdTimesatamp' : timestamp,
            'labels' : labels
        })

        es.index(index = "photos", doc_type = "Photo", id = objectKey, body = esObject, refresh = True)


    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
