import boto3
import json

from api.personas import Persona
from api.rubrics import Rubric
from api.submissions import Submission

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def _construct_prompt(persona: Persona, rubric: Rubric, submission: Submission):
    rubric_dimensions = [
        f"{dimension['name']}|{dimension['description']}|{dimension['weight']}"
        for dimension in rubric.dimensions
    ]

    # add the table headers the prompt is expecting to the front of the dimensions list
    rubric_dimensions[:0] = ["dimension_name|dimension_description|dimension_weight"]
    rubric_string = "\n".join(rubric_dimensions)
    print(rubric_string)

    with open("prompt/prompt_template.txt", "r") as prompt:
        prompt = prompt.read()
        print(prompt)
        return prompt.format(
            PROPOSAL=submission.content,
            PERSONA=persona.description,
            RUBRIC=rubric_string,
        )


def get_assessment(submission: Submission, persona: Persona, rubric: Rubric):
    prompt = _construct_prompt(persona, rubric, submission)

    body = json.dumps(
        {
            "anthropic_version": "",
            "max_tokens": 2000,
            "temperature": 0.5,
            "top_p": 1,
            "messages": [{"role": "user", "content": prompt}],
        }
    )
    response = bedrock.invoke_model(
        body=body, modelId="anthropic.claude-3-haiku-20240307-v1:0"
    )
    response_body = json.loads(response.get("body").read())
    return response_body.get("content")[0].get("text")
