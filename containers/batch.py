import json
from botocore.config import Config
import boto3
import argparse
import pandas as pd
import boto3
import io
import datetime
import markdown
from fpdf import FPDF
import random
from pdf2docx import Converter
from io import BytesIO
import os

demo = 'sp'

def read_txt_s3(path):
    # Create an S3 client
    s3 = boto3.client('s3')
    bucket_name = 'customer-batchinf-755215164008'
    # Read the object from S3
    try:
        response = s3.get_object(Bucket=bucket_name, Key=path)
        content = response['Body'].read().decode('utf-8')
        return content

    except s3.exceptions.NoSuchKey:
        print(f"The object {path} does not exist in the bucket {bucket_name}.")\

def read_csv_s3(path):
    # Create an S3 client
    s3 = boto3.client('s3')
    bucket_name = 'customer-batchinf-755215164008'
    # Read the object from S3
    try:
        response = s3.get_object(Bucket=bucket_name, Key=path)
        content = response['Body'].read()
        csv = pd.read_csv(io.BytesIO(content))
        return csv 

    except s3.exceptions.NoSuchKey:
        print(f"The object {path} does not exist in the bucket {bucket_name}.")

def store_s3(file_data):
    # Create an S3 client
    s3 = boto3.client('s3')

    # Specify the bucket name and object key
    bucket_name = 'customer-batchinf-755215164008'

    # specify object_key with current date and time
    now = datetime.datetime.now()
    object_raw_key = f'outputs/raw/output-{now.date()}-{now.time()}.txt'
    object_pdf_key = f'outputs/pdf/output-{now.date()}-{now.time()}.pdf'
    object_docx_key = f'outputs/docx/output-{now.date()}-{now.time()}.docx'
    
    data_raw_bytes = file_data.encode('utf-8')

    # Upload the raw file to S3
    try:
        response = s3.put_object(
            Body=data_raw_bytes,
            Bucket=bucket_name,
            Key=object_raw_key
        )
        print(response)
        print(f"File uploaded successfully to {bucket_name}/{object_raw_key}")

    except s3.exceptions.ClientError as e:
        print(f"Error uploading file: {e}")
        # Upload the raw file to S3

    html_text = markdown.markdown(file_data)
    generated_pdf, generated_docx = gen_pdf(html_text)


    try:
        response = s3.put_object(
            Body=generated_pdf,
            Bucket=bucket_name,
            Key=object_pdf_key
        )
        print(response)
        print(f"PDF file uploaded successfully to s3://{bucket_name}/{object_pdf_key}")
        pdf_s3url = f'https://d7ula8f6ljqje.cloudfront.net/{object_pdf_key}'
        
        response = s3.put_object(
            Body=generated_docx,
            Bucket=bucket_name,
            Key=object_docx_key
        )
        print(response)
        print(f"PDF file uploaded successfully to s3://{bucket_name}/{object_docx_key}")
        docx_s3url = f'https://d7ula8f6ljqje.cloudfront.net/{object_docx_key}'
        
        return pdf_s3url, docx_s3url

    except s3.exceptions.ClientError as e:
        print(f"Error uploading file: {e}")


def submit_tender_cloud_job(uploaded_file_string_path, tender_outline_df_path, tender_type, email):
    # TODO
    # 1. Send job to step function
    # 2. Step function trigger AWS Batch 
    # 3. AWS Batch performs generation mod-by-mod and save file to S3 , proxied by Cloudfront and sends back task token to SF
    # 4. Step function use SES to send completion email (including cloudfront pdf link)

    uploaded_file_string = read_txt_s3(uploaded_file_string_path)
    tender_outline_df = read_csv_s3(tender_outline_df_path)

    tender_module_specs_markdown = ""
    final_markdown_output = ""
    counter=1
    for index, row in tender_outline_df.iterrows():
        mod, sub_mod, purpose = row
        purpose = purpose.replace("\n", " ")
        tender_module_specs_markdown = generate_tender_module(uploaded_file_string + "\n" + final_markdown_output,counter,mod,sub_mod,purpose,tender_type)
        final_markdown_output = final_markdown_output + "\n\n" + tender_module_specs_markdown
        tender_module_specs_markdown = f"""## M{counter}: {mod}\n### Sub-Modules: {sub_mod}\n**Definition/Purpose**: {purpose}\n""" + tender_module_specs_markdown
        counter+=1
    print("job submitted")
    return final_markdown_output

def send_email(email, pdf, docx):
    my_config = Config(
        region_name='ap-southeast-1',
    )

    client = boto3.client('ses', config=my_config)
    
    email_body = (
        f"Your Tender Spec Document has been successfully generated. Access the documents here:\n"
        f"- PDF: {pdf}\n"
        f"- DOCX: {docx}\n"
    )

    response = client.send_email(
        Source='aws-lol@amazon.com',
        Destination={
            'ToAddresses': [
                email,
            ]
        },
        Message={
            'Subject': {
                'Data': 'Tender Spec Builder - Your Document is Ready'
            },
            'Body': {
                'Text': {
                    'Data': email_body
                }
            }
        }
    )
    print(response)

def get_non_stream_llm_outline(queryString):
    # increase the standard time out limits in boto3, because Bedrock may take a while to respond to large requests.
    my_config = Config(
        connect_timeout=500,  # seconds
        read_timeout=500,  # seconds
    )

    bedrock = boto3.client(
        service_name="bedrock-runtime", region_name="us-east-1", config=my_config
    )

    model_id = "anthropic.claude-3-sonnet-20240229-v1:0" 

    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "temperature": 0,
                "max_tokens": 4096,
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

def read(file_path):

    # Read the content of the text file
    with open(file_path, 'r') as file:
        content = file.read()

    # Print the content
    print(content)
    return content

def generate_tender_module(prompt_content,counter,module,sub_mod,purpose,tender_type):

    if tender_type == "Curriculum services":
        queryString = generate_curriculum_tender_module(prompt_content,counter,module,sub_mod,purpose)
    elif tender_type == "Equipment":
        queryString = generate_equipment_tender_module(prompt_content,counter,module,sub_mod,purpose)

    print_helper("Tender Generation Prompt", queryString)

    response = get_non_stream_llm_outline(queryString)

    return response

random_id = f'Tender No. : TO{str(random.randint(2000000, 9999999))}'

class FPDF(FPDF):
    def header(self):
        # Logo
        self.image('sit_logo.png', 5, 5, 40)
        # Arial bold 15
        self.set_font('Arial', 'I', 10)
        # Move to the right
        self.cell(160)
        # Title
        self.cell(30, 10, random_id, 0, 0, 'C')
        # Line break
        self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

def gen_pdf(html_text):

    print(html_text)

    TABLE_DATA = [
    ]

    # Data preparation for PDF output
    rows = html_text.split("\n")
    
    for row in rows[0:-1]:
        cells = row.split("|")
        number = cells[1].strip()
        spec = cells[2].strip()
        TABLE_DATA.append((number, spec))
    
    print(TABLE_DATA)

    # Create the PDF and config format
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 7)
    line_height = 5

    for d in range(len(TABLE_DATA)):
        row = TABLE_DATA[d]
        
        # Check if row is section title
        if '.' not in row[0]:
            pdf.ln(line_height)  # Add space above the section title
            pdf.set_font('Arial', 'B', 10)
            for i in range(len(row)):
                if i == len(row)-1:
                    pdf.multi_cell(0, line_height, f'{row[i]}', 0)
                else:
                    pdf.cell(1, line_height, '', 0)

        # Check if row is divider
        elif row[0] == '------------------':
            pdf.set_draw_color(0, 0, 0)  # black line
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(line_height)

        else:
            pdf.set_font('Arial', '', 7)
            for i in range(len(row)):
                if i == len(row)-1:
                    pdf.multi_cell(0, line_height, f'{row[i]}', 0)
                else:
                    pdf.cell(10, line_height, f'{row[i]}', 0)
                    
    
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    
    file_path = os.path.join(os.getcwd(), 'temp_pdf.pdf')
    with open(file_path, 'wb') as file:
        file.write(pdf_bytes)
    print(f"PDF bytes saved locally to '{file_path}'.")
    
    # Convert PDF to DOCX
    # pdf_stream = BytesIO(pdf_bytes)
    cv = Converter(file_path)

    # Create a BytesIO object to hold the converted docx data
    docx_stream = BytesIO()
    
    # Convert to docx and write to the BytesIO object
    cv.convert(docx_stream, start=0, end=None)
    
    # Close the converter
    cv.close()
    
    # Reset the stream position to the beginning for reading
    docx_stream.seek(0)

    return pdf_bytes, docx_stream

def generate_curriculum_tender_module(prompt_content,counter,module,sub_mod,purpose):
    queryString = f"""Human: You are a helpful tender specifications manager specialist from a university. Given the tender specs in <DOCUMENT> tag, you are required to create the specifications for only one specific tender module with at least 2500 words. Your response should strictly follow the content in <FORMAT> tag. Your response should not include <p>Here are the specifications for the {module} Module with at least 2500 words:</p>.
   
<document>
{prompt_content}
</document>

<format>
| {counter}         | {module}   |
| ------------------ | -------------- |
| {counter}.1 | Specifications 1 |
| {counter}.2 | Specifications 2 |
| {counter}.3 | Specifications 3 |
| {counter}.4 | Specifications 4 |
| {counter}.5 | Specifications 5 |
| {counter}.6 | Specifications 6 |
| {counter}.7 | Specifications 7 |
| {counter}.8 | Specifications 8 |
| {counter}.X | Specifications X |
</format>

Each specification should have at least 60 words. Depending on requirements, there can be between 10 to 20 specifications.

Assistant:
## M{counter}: {module}
### Sub-Modules: {sub_mod}
#### Definition/Purpose: {purpose}
"""

    return queryString

def generate_equipment_tender_module(prompt_content,counter,module,sub_mod,purpose):
    queryString = f"""Human: You are a helpful machinery and equipment tender specifications manager specialist from a university. Given the tender specs in <DOCUMENT> tag, you are required to create the specifications for only one specific tender module with at least 2500 words. Your response should strictly follow the content in <FORMAT> tag. Your response should not include <p>Here are the specifications for the {module} Module with at least 2500 words:</p>.
   
<document>
{prompt_content}
</document>

<format>
| {counter}         | {module}   |
| ------------------ | -------------- |
| {counter}.1 | Specifications 1 |
| {counter}.2 | Specifications 2 |
| {counter}.3 | Specifications 3 |
| {counter}.4 | Specifications 4 |
| {counter}.5 | Specifications 5 |
| {counter}.6 | Specifications 6 |
| {counter}.7 | Specifications 7 |
| {counter}.8 | Specifications 8 |
| {counter}.X | Specifications X |
</format>

Each specification should have at least 50 words. Depending on requirements, please return 1-50 requirements.

Assistant:
## M{counter}: {module}
### Sub-Modules: {sub_mod}
#### Definition/Purpose: {purpose}
"""

    return queryString

def print_helper(title, data):
    print("*" * 100)
    print(title)
    print("*" * 100)
    print(data)
    print()
    print()

def main():
    parser = argparse.ArgumentParser(description='Process some parameters.')
    parser.add_argument('uploaded_file_string', type=str, help='prompt')
    parser.add_argument('tender_outline_df', type=str, help='The tender outline df parameter')
    parser.add_argument('tender_type', type=str, help='The tender type parameter')
    parser.add_argument('email', type=str, help='The email parameter')

    args = parser.parse_args()

    print(args.uploaded_file_string)
    print(args.tender_outline_df)
    print(args.tender_type)
    print(args.email)

    results = submit_tender_cloud_job(args.uploaded_file_string, args.tender_outline_df, args.tender_type, args.email)
    print(f"Results: {results}")

    pdf, docx = store_s3(results)

    send_email(args.email, pdf, docx)

if __name__ == "__main__":
    main()