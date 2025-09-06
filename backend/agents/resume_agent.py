# resume_agent.py
import fitz
from ..llm import get_huggingface_chat
from ..prompt import SEGREGATE_PROMPT
from langchain.prompts import ChatPromptTemplate


def extract_text_from_pdf(pdf_path: str) -> str:
    """Hybrid extractor: try unstructured, fallback to pdfplumber."""
    try:
        from unstructured.partition.pdf import partition_pdf
        elements = partition_pdf(filename=pdf_path)
        if elements:
            structured_text = []
            for el in elements:
                if el.category == "Title":
                    structured_text.append(f"\n## {el.text}\n")
                elif el.category == "ListItem":
                    structured_text.append(f"- {el.text}")
                else:
                    structured_text.append(el.text)
            return "\n".join(structured_text)
    except Exception as e:
        print(f"[WARN] unstructured failed: {e}")

    # fallback
    import pdfplumber
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
    return response.content 


