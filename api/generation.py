import os
from langchain.llms.bedrock import Bedrock
import boto3  # import aws sdk and supporting libraries
from botocore.config import Config
from langchain.chains import ConversationChain
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import BedrockChat
import json
from api.text_query_string import *
import pandas as pd
import datetime

########################
# Outline helpers
########################

def submit_tender_cloud_job(uploaded_file_string, tender_outline_df, tender_type, email, reference, demo):
    # 1. Send job to step function
    # 2. Step function trigger AWS Batch 
    # 3. AWS Batch performs generation mod-by-mod and save file to S3 , proxied by Cloudfront and sends back task token to SF
    # 4. Step function use SES to send completion email (including cloudfront pdf link)

    # OPTION 1:
    filestring_path, df_path, reference_path = store_s3(uploaded_file_string, tender_outline_df, reference)

    input_data =  {
        "uploaded_file_string": filestring_path,
        "tender_outline_df": df_path,
        "tender_type": tender_type,
        "email": email,
        "reference": reference_path,
        "demo": demo
    }

    json_string = json.dumps(input_data)
    print(json_string)

    my_config = Config(
        region_name='ap-southeast-2',

    )

    client = boto3.client('stepfunctions', config=my_config)

    response = client.start_execution(
        stateMachineArn='arn:aws:states:ap-southeast-2:755215164008:stateMachine:BatchJobWithLambdaStateMachine-paVgWcnqwoKX',
        input=json_string,
    )

    return response

def store_s3(string, df, reference):
    # Create an S3 client
    s3 = boto3.client('s3')

    # Specify the bucket name and object key
    bucket_name = 'customer-batchinf-755215164008'

    # specify object_key with current date and time
    now = datetime.datetime.now()
    object_key_string = f'prompts/string/file-string-{now.date()}-{now.time()}.txt'
    object_key_df = f'prompts/df/tender-df-{now.date()}-{now.time()}.csv'
    object_key_reference = f'prompts/reference/reference-{now.date()}-{now.time()}.txt'

    csv_data = df.to_csv(index=False)

    # Upload the file to S3
    try:
        response = s3.put_object(
            Body=string.encode('utf-8'),
            Bucket=bucket_name,
            Key=object_key_string
        )
        print(response)
        print(f"File uploaded successfully to {bucket_name}/{object_key_string}")

        response = s3.put_object(
            Body=csv_data.encode('utf-8'),
            Bucket=bucket_name,
            Key=object_key_df
        )
        print(response)
        print(f"CSV file uploaded successfully to {bucket_name}/{object_key_df}")

        response = s3.put_object(
            Body=reference.encode('utf-8'),
            Bucket=bucket_name,
            Key=object_key_reference
        )
        print(response)
        print(f"Reference file uploaded successfully to {bucket_name}/{object_key_reference}")

        return object_key_string, object_key_df, object_key_reference

    except s3.exceptions.ClientError as e:
        print(f"Error uploading file: {e}")

def get_non_stream_llm_outline(queryString):
    # increase the standard time out limits in boto3, because Bedrock may take a while to respond to large requests.
    my_config = Config(
        connect_timeout=500,  # seconds
        read_timeout=500,  # seconds
    )

    bedrock = boto3.client(
        service_name="bedrock-runtime", region_name="us-east-1", config=my_config
    )

    model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0" 

    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "temperature": 0,
                "max_tokens": 4096,
                "system": "You are a tender specifications document generator. You are required to generate tender specifications document to be sent to vendors. Do not include an introduction in your response.",
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": queryString}],
                    }
                ],
            }
        ),
    )

    # Process and print the response
    result = json.loads(response.get("body").read())
    input_tokens = result["usage"]["input_tokens"]
    output_tokens = result["usage"]["output_tokens"]
    output_list = result.get("content", [])

    print("Invocation details:")
    print(f"- The input length is {input_tokens} tokens.")
    print(f"- The output length is {output_tokens} tokens.")

    print(f"- The model returned {len(output_list)} response(s):")
    for output in output_list:
        print(output["text"])

    llm = output_list[0]["text"]

    return llm #choose llm for BR and llm2 for Anthropic

def generate_tender_module(prompt_content,counter,module,sub_mod,purpose,tender_type,reference):

    if tender_type == "Curriculum services":
        queryString = generate_curriculum_tender_module(prompt_content,counter,module,sub_mod,purpose)
    
    print_helper("Tender Generation Prompt", queryString)

    response = get_non_stream_llm_outline(queryString)

    return response

def convert_to_jsonl(query):
    with open("output.jsonl", "w") as f:
        for text in query:
            json_data = {
                "modelInput": {
                    "inputText": text
                }
            }
            json_line = json.dumps(json_data)
            f.write(json_line + "\n")  # Add a newline character after each line

def print_helper(title, data):
    print("*" * 100)
    print(title)
    print("*" * 100)
    print(data)
    print()
    print()
