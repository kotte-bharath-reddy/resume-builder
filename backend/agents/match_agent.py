# match_agent.py
import json
from langchain.prompts import ChatPromptTemplate
from ..llm import get_huggingface_chat
from .resume_agent import extract_text_from_pdf, segregate_resume_with_llm
from .job_agent import extract_text_from_url, parse_job_with_llm


def calculate_ats_score_from_files(resume_pdf_path: str, job_url: str, temperature=0.4, max_new_tokens=2048) -> dict:
    """Calculate ATS score using summaries from resume and job description."""
    
    print("Extracting text from resume PDF...")
    resume_text = extract_text_from_pdf(resume_pdf_path)
    resume_json = segregate_resume_with_llm(resume_text)


    print("Extracting text from job URL...")
    job_text = extract_text_from_url(job_url)
    job_json = parse_job_with_llm(job_text)


    # Create smaller summaries for LLM
    resume_summary = {
        "skills": resume_json.get("skills", []),
        "experience": [exp.get("title") for exp in resume_json.get("experience", [])],
        "education": [edu.get("degree") for edu in resume_json.get("education", [])]
    }

    job_summary = {
        "required_skills": job_json.get("required_skills", []),
        "preferred_skills": job_json.get("preferred_skills", []),
        "responsibilities": job_json.get("responsibilities", [])
    }

    ATS_PROMPT = """
You are an ATS (Applicant Tracking System) scoring AI.

Compare the candidate's resume with the job description.
You MUST return **only JSON**, no explanations or markdown.

Return JSON exactly as:
{{
  "match_score": integer (0-100),
  "summary": "one sentence summary of fit",
  "strengths": ["matched skills/requirements"],
  "gaps": ["missing or weak skills/requirements"]
}}

Resume Summary:
{resume_summary}

Job Summary:
{job_summary}
"""

    llm = get_huggingface_chat(temperature=temperature, max_new_tokens=max_new_tokens)
    prompt = ChatPromptTemplate.from_template(ATS_PROMPT)
    chain = prompt | llm

    print("Calculating ATS score with LLM...")
    response = chain.invoke({
        "resume_summary": json.dumps(resume_summary),
        "job_summary": json.dumps(job_summary)
    })

    # Remove any markdown fences if accidentally included
    content = response.content.strip().replace("```json", "").replace("```", "")

    try:
        ats_result = json.loads(content)
    except Exception:
        ats_result = {"match_score": 0, "summary": "LLM failed to parse", "strengths": [], "gaps": []}

    return ats_result
