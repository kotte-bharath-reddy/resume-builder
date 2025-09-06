# job_agent.py
import json
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from langchain.prompts import ChatPromptTemplate
from ..llm import get_huggingface_chat
from ..prompt import JOB_EXTRACT_PROMPT


# -----------------------------
# Step 1: Page fetchers
# -----------------------------
def fetch_html_requests(url: str) -> str:
    """Try fetching page HTML using requests (fast path)."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.text
    except Exception as e:
        print(f"[WARN] Requests fetch failed: {e}")
    return ""


def scroll_page(driver, scroll_pause=1, max_scroll=5):
    """Scrolls the page to trigger lazy loading."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_scroll):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def fetch_html_selenium(url: str) -> str:
    """Fetch page HTML with Selenium (handles JS-heavy pages)."""
    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Wait for <body> to load
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except Exception as e:
        print(f"[WARN] Timeout waiting for body: {e}")

    # Scroll to load lazy content
    scroll_page(driver, scroll_pause=1, max_scroll=6)

    html = driver.page_source
    driver.quit()
    return html


# -----------------------------
# Step 2: Extract job description
# -----------------------------
def extract_text_from_url(url: str) -> str:
    """Robust scraper for job descriptions (requests → fallback Selenium)."""
    html = fetch_html_requests(url)
    if not html or len(html) < 500:  # fallback if page incomplete
        html = fetch_html_selenium(url)

    soup = BeautifulSoup(html, "html.parser")

    # Prefer known containers if available
    job_container = (
        soup.find("div", class_="job-description")
        or soup.find("section", class_="description")
        or soup.find("div", {"id": "jobDescriptionText"})
    )
    if job_container:
        return job_container.get_text(separator=" ", strip=True)

    # Fallback: collect all meaningful text blocks
    texts = []
    for tag in soup.find_all(["p", "li", "div", "h1", "h2", "h3", "span"]):
        t = tag.get_text(strip=True)
        if len(t.split()) > 3:  # keep useful lines only
            texts.append(t)

    # Deduplicate
    unique_texts = []
    for t in texts:
        if t not in unique_texts:
            unique_texts.append(t)

    return "\n".join(unique_texts)


# -----------------------------
# Step 3: Chunk text
# -----------------------------
def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    """Split text into chunks of approx chunk_size words."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks


# -----------------------------
# Step 4: Merge JSON outputs
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
        "job_url": "",
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
# Step 5: LLM parsing
# -----------------------------
def parse_job_with_llm(
    job_text: str,
    temperature: float = 0.4,
    max_new_tokens: int = 2048
) -> dict:
    """
    Parse job description into structured JSON using LLM.
    Handles long texts by chunking and merges outputs.
    """
    llm = get_huggingface_chat(
        temperature=temperature,
        max_new_tokens=max_new_tokens
    )
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
