import fitz
import re
from .llm import get_huggingface_client
from .prompt import SEGREGATE_PROMPT

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    with fitz.open(pdf_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text() 
    return text


def segregate_resume_with_llm(raw_text: str) -> str:
    client = get_huggingface_client()
    prompt = SEGREGATE_PROMPT.format(resume_text=raw_text)

    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        messages=[
            {"role": "system", "content": "You are an expert resume parser."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=2048,
        temperature=0.3,
    )

    return response.choices[0].message["content"]
