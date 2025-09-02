SEGREGATE_PROMPT = """
You are an expert resume parser. I will give you the raw text of a resume. 
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

