import boto3
import pandas as pd
import json

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
sns_arn = 'arn:aws:sns:ap-south-1:975050266922:SNS-testing'


def lambda_handler(event,context):
    print("Event data :", event)
    print("context data :", context)

    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_object_key = event['Records'][0]['s3']['object']['key']

    response = s3_client.get_object(Bucket=s3_bucket, Key=s3_object_key)
    print(response)
    print(response['Body'])

    #s3_bucket_url = "'s3://{}/{}'".format(s3_bucket,s3_object_key)
    #print(s3_bucket_url)

    df = pd.read_json(response['Body'], orient='JsonSeriesOrient')
    #print(df)
    print(df[df['status'] == 'delivered'])

    df = df[df['status'] == 'delivered']

    s3_write_bucket = 'doordash-processing-bucket-module-assignment-1'
    s3_write_object_key_delivered = '2024-03-00-processed_output_delivered.json'
    s3_write_path = f's3://{s3_write_bucket}/{s3_write_object_key_delivered}'

    json_str = df.to_json(orient='table')
    print(json_str)

    write_response = s3_client.put_object(
        Body = json_str,
        Bucket = 'doordash-processing-bucket-module-assignment-1',
        Key = '2024-03-02-processed_output_delivered.json'
    )
    #print(write_response)

    status = write_response["ResponseMetadata"]["HTTPStatusCode"]

    #print(status)
    
    if status == 200:
        msg = f"{s3_write_object_key_delivered} successfully uploaded to s3://{s3_write_bucket}"
        print(msg)

        sns_client.publish(Subject ='SUCCESS - Daily Data Processing', \
                           TargetArn = sns_arn, \
                           Message = msg, \
                           MessageStructure = 'text'
        )
    else:
        msg = f"{s3_write_object_key_delivered} successfully uploaded to s3://{s3_write_bucket}"
        print(msg)

        sns_client.publish(Subject ='FAILED - Daily Data Processing', \
                           TargetArn = sns_arn, \
                           Message = msg, \
                           MessageStructure = 'text'
        )