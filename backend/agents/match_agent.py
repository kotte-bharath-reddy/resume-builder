import json
from langchain.prompts import ChatPromptTemplate
from backend.llm import get_huggingface_chat
from backend.prompt import MATCH_PROMPT


def get_job_match_and_resume(resume_json: dict, job_json: dict):
    """Compares resume JSON with job JSON, returns match details + optimized resume."""
    llm = get_huggingface_chat()

    prompt = ChatPromptTemplate.from_template(MATCH_PROMPT)
    chain = prompt | llm

    response = chain.invoke({
        "resume_json": json.dumps(resume_json, indent=2),
        "job_json": json.dumps(job_json, indent=2)
    })

    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON returned", "raw_response": response.content}
