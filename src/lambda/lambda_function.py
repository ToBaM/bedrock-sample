import boto3
import json
import os

s3_client = boto3.client('s3')
bedrock_client = boto3.client('bedrock-runtime', region_name='ap-northeast-1')

def lambda_handler(event, context):
    # S3イベントからバケット名とファイル名を取得
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    
    # S3から会話ログファイルを取得
    s3_response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    text_data = s3_response['Body'].read().decode('utf-8')
    prompt = '以下のテキストを、「問題：～、対処：～」のような形式で要約してください。'
    
    # Bedrockにテキストを送信して要約を生成
    bedrock_response = bedrock_client.invoke_model(
        modelId='amazon.titan-text-express-v1',
        body=json.dumps({
            'inputText':  prompt + text_data,
            'textGenerationConfig': {
                'maxTokenCount': 500
            }
        })
    )
    
    # Bedrockのレスポンスから要約結果を取得
    response_body = json.loads(bedrock_response.get('body').read())
    output_text = response_body['results'][0]['outputText']
    
    # 要約結果をS3に保存
    output_bucket = 'bedrock-sample-output'
    output_key = f"summaries/{file_key.split('/')[-1].replace('.txt', '_summary.txt')}"
    s3_client.put_object(Bucket=output_bucket, Key=output_key, Body=output_text)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Summary successfully generated and stored.')
    }