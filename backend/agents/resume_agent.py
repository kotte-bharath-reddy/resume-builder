# resume_agent.py
from ..llm import get_huggingface_chat
from ..prompt import SEGREGATE_PROMPT
from langchain.prompts import ChatPromptTemplate
import pdfplumber
import json
import re
def extract_text_from_pdf(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def segregate_resume_with_llm(
    raw_text: str,
    temperature: float = 0.3,
    max_new_tokens: int = 2048
) -> str:
    """Use LLM to structure resume text into sections."""
    llm = get_huggingface_chat(
        temperature=temperature,
        max_new_tokens=max_new_tokens
    )
    prompt = ChatPromptTemplate.from_template(SEGREGATE_PROMPT)
    chain = prompt | llm
    response = chain.invoke({"resume_text": raw_text})

    if response.content.startswith("```"):
        response.content = re.sub(r"^```[a-zA-Z]*\n", "", response.content)   # remove opening fence
        response.content = re.sub(r"\n```$", "", response.content) 
    try:
        # Validate if the response is a valid JSON
        return json.loads(response.content)
    except Exception as e:
        print("LLM output is not valid JSON:", e)
        print("LLM output:", response.content.strip())
        raise ValueError("LLM output is not valid JSON.")


