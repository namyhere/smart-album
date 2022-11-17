import json
import boto3
import time
import requests

def lambda_handler(event, context):
    print(event)
    inputText = event['queryStringParameters']['q']
    keywords = get_keywords(inputText)
    image_array = get_image_locations(keywords)
    return {
        'statusCode': 200,
        'headers':{
            'Access-Control-Allow-Origin':'*',
            'Access-Control-Allow-Credentials':True
        },
        'body': json.dumps({"results":image_array})
    }

def get_keywords(inputText):
    lex = boto3.client('lex-runtime')
    response = lex.post_text(
        botName = 'SearchBot',
        botAlias = '$LATEST',
        userId = 'userId',
        inputText = inputText
    )
    print(response['slots'])
    keywords = []
    slots = response['slots']
    keywords = [v for _, v in slots.items() if v]
    print(keywords)
    return keywords
    
def get_image_locations(keywords):
    endpoint = 'https://search-all-photos-kegyxncx6jlwnvwwuj22hn4pli.us-east-1.es.amazonaws.com/all-photos/_search'
    headers = {'Content-Type': 'application/json'}
    prepared_q = []
    for k in keywords:
        prepared_q.append({"match": {"labels": k}})
    q = {"query": {"bool": {"should": prepared_q}}}
    r = requests.post(endpoint, headers=headers, data=json.dumps(q), auth=('admin', 'Admin@12345'))
    print(r.json())
    image_array = []
    for each in r.json()['hits']['hits']:
        objectKey = each['_source']['objectKey']
        bucket = each['_source']['bucket']
        image_url = "https://" + bucket + ".s3.amazonaws.com/" + objectKey
        image_array.append(image_url)
        print(each['_source']['labels'])
    print(image_array)
    return image_array