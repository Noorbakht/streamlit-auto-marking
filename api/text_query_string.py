def generate_curriculum_tender_module(prompt_content):
    print(prompt_content)
    queryString = f"""Human: Given the answer scheme in <DOCUMENT> tag, you are required to mark the student's worksheet. Do not include any prompt framing or prelude text in your response. A non-exhausit list of example prelude text that should not be included in your response is given in <EXCLUDE> tag.

<DOCUMENT>
{prompt_content}
</DOCUMENT>

Assistant:
""" 

    return queryString