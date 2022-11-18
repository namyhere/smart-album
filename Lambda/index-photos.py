import json
import boto3
import time
import requests

# CloudFormation Demo for Index Photos lambda function

def lambda_handler(event, context):
    print(event)
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        photokey = record['s3']['object']['key']
        print(bucket, photokey)
        labels = []
        labels = get_photo_labels(bucket, photokey)
        new_doc = {
            "objectKey": photokey,
            "bucket": bucket,
            "createdTimestamp": time.strftime("%Y%m%d-%H%M%S"),
            "labels": labels
        }
        index_into_es('all-photos','photo',json.dumps(new_doc))
    print('Done')
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
def get_photo_labels(bucket, photokey):
    rekClient = boto3.client('rekognition')
    print('Detecting Labels...')
    response = rekClient.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photokey}}, MaxLabels=10, MinConfidence=90)
    print('Done')
    print(response)
    print(response['Labels'])
    labels = [label['Name'] for label in response['Labels']]
    print(labels)
    return labels

def index_into_es(index, type_doc, new_doc):
    endpoint = 'https://search-all-photos-kegyxncx6jlwnvwwuj22hn4pli.us-east-1.es.amazonaws.com/{}/{}'.format(index, type_doc)
    headers = {'Content-Type':'application/json'}
    res = requests.post(endpoint, data=new_doc, headers=headers, auth=('admin', 'Admin@12345'))
    print(res.content)