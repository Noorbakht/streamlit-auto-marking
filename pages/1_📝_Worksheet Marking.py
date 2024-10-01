import streamlit as st
import boto3
import json
import PyPDF2
from io import BytesIO
import base64
import docx

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
# model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
# model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    print(text)
    return text

def read_word_doc(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    print(text)
    return text

def app():
    st.title("Student Worksheet Marking")

    # Upload answer scheme
    answer_scheme_file = st.file_uploader("Upload Answer Scheme", type=['pdf'])
    
    # Upload student worksheet
    student_worksheet_file = st.file_uploader("Upload Student Worksheet", type=['png', 'pdf'])

    if st.button("Mark Worksheet"):
        if answer_scheme_file is not None and student_worksheet_file is not None:
            print(student_worksheet_file.type)
            if student_worksheet_file.type == "image/png":
                model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
                # model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
                # Read the contents of both files
                answer_scheme_text = read_pdf(answer_scheme_file)
                # student_worksheet_text = read_pdf(student_worksheet_file)
                base64_image = base64.b64encode(student_worksheet_file.read()).decode('utf-8')

                # Prepare the query string
                query_string = f"""
                Answer Scheme:
                {answer_scheme_text}

                Please mark the student's worksheet attached in the image based on the answer scheme provided. Follow the answer scheme strictly, checking strictly if the student left the answer in fraction or decimal points as this will affect the score. For example, if the student has left an answer to y^4 = 2x^2 - 31/16x^2 while the answer scheme explicitly states that the answer should be in decimal places then the student will not be awarded a point as the answer is represented in fraction (C = -31/16) and not its equivalent decimal figure (1.9375). If the student wrote C = -31/16, do not award it a point.
                """

                # Call the Bedrock API to mark the student worksheet
                response = bedrock.invoke_model(
                    modelId=model_id,
                    body=json.dumps(
                    {
                        "anthropic_version": "bedrock-2023-05-31",
                        "temperature": 0,
                        "max_tokens": 4096,
                        "system": "You are a teacher marking a student's worksheet based on the answer scheme provided in the text. Tell me the score the student will receive for his worksheet attached as an image.",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": query_string
                                    },
                                    {
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": "image/png",
                                            "data": base64_image
                                        }
                                    }
                                ],
                            }
                        ],
                    }
                ))

                # Parse the response
                response_body = json.loads(response['body'].read())
                marked_worksheet = response_body['content'][0]['text']

                # Display the marked worksheet
                st.subheader("Marked Worksheet")
                st.write(marked_worksheet)
            else:
                answer_scheme_text = read_pdf(answer_scheme_file)
                student_response = read_pdf(student_worksheet_file)
                model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

                # Prepare the query string
                query_string = f"""
                Answer Scheme:
                {answer_scheme_text}

                Please mark the student's worksheet attached in the pdf based on the answer scheme provided.
                """

                # Call the Bedrock API to mark the student worksheet
                response = bedrock.invoke_model(
                    modelId=model_id,
                    body=json.dumps(
                    {
                        "anthropic_version": "bedrock-2023-05-31",
                        "temperature": 0,
                        "max_tokens": 4096,
                        "system": "You are a teacher marking a student's worksheet based on the answer scheme provided in the text. Follow the answer scheme strictly but do note you can give the student 2 marks if stuent states surface roughness as this corresponds to viscous damping on the venturi due to the surface not being completely smooth, when marking the response. Give the student 0 marks if student's response does not directly match any of the possible answers listed in the answer scheme",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": query_string
                                    },
                                    {
                                        "type": "text",
                                        "text": student_response
                                    }
                                ],
                            }
                        ],
                    }
                ))

                # Parse the response
                response_body = json.loads(response['body'].read())
                marked_worksheet = response_body['content'][0]['text']

                # Display the marked worksheet
                st.subheader("Marked Worksheet")
                st.write(marked_worksheet)

if __name__ == "__main__":
    app()


# import streamlit as st
# import boto3
# import markdown as markdown
# from botocore.config import Config
# import json

# bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
# s3 = boto3.client('s3')
# bucket_name = 'tp-auto-marking-demo'
# model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0" 

# def app():
#     st.title("Student Worksheet Marking")

#     # Upload answer scheme
#     answer_scheme_file = st.file_uploader("Upload Answer Scheme", type=['pdf'])
#     if answer_scheme_file is not None:
#     # Upload the answer scheme to S3
#         try:
#             response = s3.put_object(answer_scheme_file, 'tp-auto-marking-demo', 'answer_scheme.pdf')
#             print(response)
#             print(f"File uploaded successfully!")

#         except s3.exceptions.ClientError as e:
#             print(f"Error uploading file: {e}")

#     # Upload student worksheet
#     student_worksheet_file = st.file_uploader("Upload Student Worksheet", type=['pdf'])
#     if student_worksheet_file is not None:
#         # Upload the student worksheet to S3
#         try:
#             response = s3.put_object(student_worksheet_file, 'tp-auto-marking-demo', 'student_worksheet.pdf')
#             print(response)
#             print(f"File uploaded successfully!")

#         except s3.exceptions.ClientError as e:
#             print(f"Error uploading file: {e}")

#     if st.button("Mark Worksheet"):

#         # Call the Bedrock API to mark the student worksheet
#         response = bedrock.invoke_model(
#             modelId=model_id,
#             body=json.dumps(
#             {
#                 "anthropic_version": "bedrock-2023-05-31",
#                 "temperature": 0,
#                 "max_tokens": 4096,
#                 "system": "You are a teacher marking a student's worksheet based on the answer scheme provided. Do not include an introduction in your response.",
#                 "messages": [
#                     {
#                         "role": "user",
#                         "content": [{"type": "text", "text": queryString}],
#                     }
#                 ],
#             }
#         ),
#     )

# if __name__ == "__main__":
#     app()