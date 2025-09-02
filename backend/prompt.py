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
