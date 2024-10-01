import boto3  # import aws sdk and supporting libraries
from botocore.config import Config
import json

def query(prompt):
    queryString = f"""Human: Briefly summarise the requirements given in <REQUIREMENTS> tag into a paragraph so that I may use the output as prompt to re-generate the full requirements later using a LLM. Key requirements and specifications must be included, however there is no need to be too deatiled.

    <requirements>
    {prompt}
    </requirements>

    Assistant:"""

    return queryString

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


prompt = """
Visa 	
Vendor must provide the right visa and quote for an all-inclusive visa application fee for student of the following nationalities to travel to the programme country during the entire overseas period.  Vendor shall indicate "NA" in the Price Schedule if VISA is not required for the corresponding nationalities.  Where there is a failure to indicate the VISA fee in the Price Schedule, it shall be deemed that the vendor will provide VISA at no additional cost for the corresponding nationalities. 	
- Singapore	
- Malaysia	
- Myanmar	
- Indonesia	
- China	
- Philippines	
- India	
- Thailand	
- Other nationalities

For trips where visas are required, vendors must : 
Apply visa for all students.	
"Apply Internship/study/training visa for all students going for this (study and training) internship programme at institution/company.

Vendor may use the below links for reference:
https://www.travelchinaguide.com/embassy/visa/student.htm
https://www.saporedicina.com/english/chinese-visa-application/"	
Obtain necessary documents required by embassy for application for the internship/study/training visa.	
Provide sufficient manpower to support the entire visa application process.	
Obtain detailed information and updates about visa regulations and information for countries to be visited.	
Provide supporting documents checklist for student participants of different nationalities via email/other modes of communication.	
Assist to type students' details into the application forms for Embassies that do not accept written applications. 	
"Arrange/conduct face-to-face visa application sessions with students/trip participants to assist/guide students with application
forms and collection of all required supporting documents. (within SP premises)"	
Check and ensure all fields required and signatories in the application form are duly completed and signed.	
Vendor must provide the right visa and quote for an all-inclusive visa application fee for the accompanying staff(s) for the specified travelling period.  Vendor shall indicate "NA" in the Price Schedule if VISA is not required.  Where there is a failure to indicate the VISA fee in the Price Schedule, it shall be deemed that the vendor will provide VISA at no additional cost for the accompanying staff.		
"""
string = query(prompt)
output = get_non_stream_llm_outline(string)