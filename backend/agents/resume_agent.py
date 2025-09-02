# backend/agents.py
import fitz
from ..llm import get_huggingface_chat
from ..prompt import SEGREGATE_PROMPT
from langchain.prompts import ChatPromptTemplate


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    with fitz.open(pdf_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

def segregate_resume_with_llm(raw_text: str) -> str:
    llm = get_huggingface_chat()
    prompt = ChatPromptTemplate.from_template(SEGREGATE_PROMPT)
    chain = prompt | llm
    response = chain.invoke({"resume_text": raw_text})
    return response.content 


