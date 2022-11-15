import json
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3
import requests
import urllib.parse
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
    
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

headers = { "Content-Type": "application/json" }
region = 'us-east-1'
lex = boto3.client('lex-runtime', region_name=region)

def lambda_handler(event, context):

    print ('event : ', event)

    q1 = event["queryStringParameters"]['q']
        
    print("q1:", q1 )
    labels = get_labels(q1)
    print("labels", labels)
    if len(labels) != 0:
        img_paths = get_photo_path(labels)

    if not img_paths:
        return{
            'statusCode':200,
            "headers": {"Access-Control-Allow-Origin":"*"},
            'body': json.dumps('No Results found')
        }
    else:    
        return{
            'statusCode': 200,
            'headers': {"Access-Control-Allow-Origin":"*"},
            'body': {
                'imagePaths':img_paths,
                'userQuery':q1,
                'labels': labels,
            },
            'isBase64Encoded': False
        }
    
def get_labels(query):
    response = lex.post_text(
        botName='SearchBot',                 
        botAlias='$LATEST',
        userId="string",           
        inputText=query
    )
    print("lex-response", response)
    
    labels = []
    if 'slots' not in response:
        print("No photo collection for query {}".format(query))
    else:
        print ("slot: ",response['slots'])
        slot_val = response['slots']
        for key,value in slot_val.items():
            if value!=None:
                labels.append(value)
    return labels

    
def get_photo_path(keys):
    
    host = 'vpc-photos-ryu2uf43z2m5tbnfpuizbuc3ua.us-east-1.es.amazonaws.com'
    es = Elasticsearch(
    hosts=[{'host': host,'port':443}],
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    http_auth=('admin', 'Admin@12345')
    )
    
    resp = []
    for key in keys:
        if (key is not None) and key != '':
            searchData = es.search({"query": {"match": {"labels": key}}})
            resp.append(searchData)
    print(resp)
    output = []
    for r in resp:
        if 'hits' in r:
             for val in r['hits']['hits']:
                key = val['_source']['objectKey']
                if key not in output:
                    output.append('YOUR-BUCKET-LINK/'+key)
    print (output)
    return output  