# prompt.py
SEGREGATE_PROMPT = """
You are an expert resume parser. I will give you the raw text of a resume. The raw text may contain the paragraphs repeated. 
Your job is to put them in the suitable sections.
Your task is to structure it into the following JSON fields:

- name
- profile
- email
- phone
- skills (list)
- education
- experience
- certifications (if any)


Also add if there are any other sections and their conent in the resume. There might also be linkedin/github links. get them too
Only return valid JSON.
Resume text:
{resume_text}
"""

JOB_EXTRACT_PROMPT = """
You are an expert job description parser. 
Your task is to extract the following fields from the given job description text:

- job_title (string)
- company_name (string)
- location (string)
- responsibilities (list of strings)
- required_skills (list of strings)
- preferred_skills (list of strings)
- qualifications (string)
- experience_required (string)
- employment_type (string)
- salary (string)
- other_benefits (list of strings)
- job_url (string)

Example output:

{{
  "job_title": "AI Engineer",
  "company_name": "MightyBot",
  "location": "Hyderabad, India",
  "responsibilities": ["Develop AI models", "Deploy machine learning solutions"],
  "required_skills": ["Python", "SQL", "Machine Learning"],
  "preferred_skills": ["Deep Learning", "NLP"],
  "qualifications": "BTech in CS",
  "experience_required": "2+ years",
  "employment_type": "Full-time",
  "salary": "Not specified",
  "other_benefits": ["Health insurance", "Flexible hours"],
  "job_url": "https://linkedin.com/jobs/view/..."
}}

**Only return valid JSON**. Do not include extra characters or explanations.

Job description text:
{job_text}
"""

MATCH_PROMPT = """
You are an AI job matcher and resume optimizer.

Task:
1. Compare the candidate's resume with the job description.
2. Provide a structured JSON output with match analysis.
3. Generate an optimized resume text (for PDF generation) that:
   - Uses the candidate's existing headings and structure.
   - Keeps their tech stack intact (no adding new tools not present).
   - Uses alternate terms / synonyms from the job description where possible.
   - Improves ATS (Applicant Tracking System) compatibility by aligning phrasing with the job description.

Input Data:

**Candidate Resume JSON:**
{resume_json}

**Job Description JSON:**
{job_json}

Return a valid JSON with the following structure:

{{
  "match_score": "integer (0-100)",
  "summary": "short paragraph summarizing the match",
  "strengths": ["list of strong matches between resume and job"],
  "gaps": ["list of missing or weak skills/requirements"],
  "optimized_resume": {{
      "name": "...",
      "profile": "...",
      "email": "...",
      "phone": "...",
      "skills": ["..."],
      "education": "...",
      "experience": [
          {{"role": "...", "company": "...", "description": "..."}}
      ],
      "certifications": ["..."],
      "other_sections": {{"linkedin": "...", "github": "..."}}
  }}
}}

Rules:
- Only return JSON.
- Do not hallucinate new tools, tech stacks, or companies.
- Use alternate terms from the job description only if they mean the same thing as the original.
"""
