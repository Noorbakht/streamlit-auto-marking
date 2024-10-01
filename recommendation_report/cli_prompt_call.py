import os
import boto3  # import aws sdk and supporting libraries
from botocore.config import Config
import json
import PyPDF2

def read_pdf(file_path):
    # Open the PDF file in read-binary mode
    with open(file_path, 'rb') as file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(file)

        # Initialize an empty string to store the text
        text = ''

        # Iterate over each page and extract the text
        for page_num in range(len(pdf_reader.pages)):
            # Get the page object
            page = pdf_reader.pages[page_num]

            # Extract the text from the page
            page_text = page.extract_text()

            # Append the page text to the overall text variable
            text += page_text

    return text

vendora = read_pdf("./vendora.pdf")
vendorb = read_pdf("./vendorb.pdf")
vendorc = read_pdf("./vendorc.pdf")


queryString = f"""Human: You are a helpful tender specifications evaluator specialist from a university. Given the submitted tender proposals in <SUBMISSION> tag, you are required to generate a comprehensive recommendation report detailing the recommended Vendor and the reasons using the evaluation criterias given in <RUBRICS> tag. Each reason should be detailed, using no less than 100 words, and include in line citations back to the source. Follow the format given in <FORMAT> tag.

<SUBMISSION>
Vendor A: {vendora}
Vendor B: {vendorb}
Vendor C: {vendorc}
</SUBMISSION>

<RUBRICS>
Evaluation Criteria	Description
1. Vendor Track Record	Assesses the vendor's past performance and relevant experience in delivering similar projects.
2. Cost	Evaluates the cost-effectiveness of the proposal in relation to the budget and scope.
3. Technical Specifications	Evaluates the technical aspects of the proposal, including system design, architecture, and scalability.
</RUBRICS>

<FORMAT>
Recommendation:
- Vendor: <vendor_name>

Reasons:
- <reason_1>
- <reason_2>
...
</FORMAT>

Assistant:"""

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

output = get_non_stream_llm_outline(queryString)

# ## Generate report
# from fpdf import FPDF

# class PDF(FPDF):
#     def header(self):
#         # Logo
#         self.image('sit_logo.png', 5, 5, 40)
#         # Arial bold 15
#         self.set_font('Arial', '', 10)
#         # Move to the right
#         self.cell(160)
#         # Line break
#         self.ln(20)

#     def chapter_title(self, title):
#         self.set_font("Arial", "B", 9)
#         self.cell(0, 9, title, 0, 1, "L")
#         self.ln(4)

#     def chapter_body(self, body):
#         self.set_font("Arial", "", 9)
#         self.multi_cell(0, 9, body)
#         self.ln()

#     def add_section(self, title, body):
#         self.chapter_title(title)
#         self.chapter_body(body)

#     # Page footer
#     def footer(self):
#         # Position at 1.5 cm from bottom
#         self.set_y(-15)
#         # Arial italic 8
#         self.set_font('Arial', '', 7)
#         # Page number
#         self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

# # Create instance of FPDF class
# pdf = PDF()

# # Add a page
# pdf.add_page()

# # Title section
# pdf.set_font("Arial", "B", 16)
# pdf.cell(0, 10, "Tender Proposal Recommendation Report", 0, 1, "C")
# pdf.ln(10)

# # Sections with placeholders
# sections = {
#     "Project Summary/Description": "The Integrated Student Management System (ISMS) is designed to provide educational institutions with a comprehensive platform for managing all aspects of student administration and academic processes. The system aims to streamline operations, improve data accuracy, enhance communication, and support decision-making by centralizing and automating the management of student information, academic records, financial transactions, and communications.",
#     "Project Objectives": """- To centralize student data management, including enrollment, academic records, and financials, into a single, user-friendly system.
# - To enhance the efficiency and accuracy of administrative processes by automating routine tasks such as course registration, grade entry, and fee processing.
# - To improve communication between students, faculty, and administration through a centralized communication hub.
# - To provide real-time reporting and analytics capabilities, enabling data-driven decision-making for administrators.
# - To ensure the system is scalable and secure, with the ability to integrate with existing institutional systems and adapt to future needs.
# """,
#     "Approved Budget": "499,000",
#     "Tenderers Submitted": "6",
#     "Tenderers Shortlisted": """- Vendor A
# - Vendor B
# - Vendor C
# """,
#     "Recommendation": output,
#     "Summary": "While Vendor B and Vendor C also presented strong proposals, Vendor A's combination of relevant experience, cost-effectiveness, reasonable timeline, and comprehensive technical approach makes them the recommended choice for SIT's Integrated Student Management System project."
# }

# # Adding sections to the PDF
# for title, body in sections.items():
#     pdf.add_section(title, body)

# # Output the PDF
# output_file = "Tender_Proposal_Recommendation_Report.pdf"
# pdf.output(output_file)

# print(f"PDF generated: {output_file}")