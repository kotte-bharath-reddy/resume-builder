from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from langchain.prompts import ChatPromptTemplate
from ..llm import get_huggingface_chat
from ..prompt import JOB_EXTRACT_PROMPT
import json
import time

# -----------------------------
# Step 1: Scrape + clean job description using Selenium
# -----------------------------
def extract_text_from_url(url: str) -> str:
    """Scrape and clean job description text from a URL using Selenium."""
    options = Options()
    options.headless = True  # run in background
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Wait for job description to load
    time.sleep(5)  # adjust for slow pages

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # Extract meaningful text
    texts = []
    for tag in soup.find_all(["p", "li", "h2", "h3", "span"]):
        t = tag.get_text(strip=True)
        if len(t) > 20:  # filter out short/noise text
            texts.append(t)

    return " ".join(texts)

# -----------------------------
# Step 2: Chunk text
# -----------------------------
def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    """Split text into chunks of approx chunk_size words."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks

# -----------------------------
# Step 3: Merge JSON outputs
# -----------------------------
def merge_job_json(chunk_outputs: list[str]) -> dict:
    """Merge multiple chunk outputs into a single JSON."""
    merged = {
        "job_title": "",
        "company_name": "",
        "location": "",
        "responsibilities": [],
        "required_skills": [],
        "preferred_skills": [],
        "qualifications": "",
        "experience_required": "",
        "employment_type": "",
        "salary": "",
        "other_benefits": [],
        "job_url": ""
    }

    for chunk in chunk_outputs:
        try:
            data = json.loads(chunk)
        except json.JSONDecodeError:
            continue  # skip malformed chunk

        for key in merged:
            if key not in data or data[key] in [None, "", []]:
                continue
            if isinstance(merged[key], list):
                merged[key].extend(data[key])
            elif merged[key] == "":
                merged[key] = data[key]

    # Deduplicate lists
    for key, value in merged.items():
        if isinstance(value, list):
            merged[key] = list(set(value))

    return merged

# -----------------------------
# Step 4: LLM parsing
# -----------------------------
def parse_job_with_llm(job_text: str) -> dict:
    """
    Parse job description into structured JSON using LLM.
    Handles long texts by chunking and merges outputs.
    """
    llm = get_huggingface_chat()
    prompt = ChatPromptTemplate.from_template(JOB_EXTRACT_PROMPT)
    chain = prompt | llm

    chunks = chunk_text(job_text, chunk_size=500)
    chunk_outputs = []

    for i, chunk in enumerate(chunks):
        print(f"Parsing chunk {i+1}/{len(chunks)}...")
        response = chain.invoke({"job_text": chunk})
        chunk_outputs.append(response.content.strip())

    merged_json = merge_job_json(chunk_outputs)
    return merged_json
