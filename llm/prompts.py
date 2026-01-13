SYSTEM_DEFAULT = """
You are a precise, structured AI assistant.
You reason step by step internally, but respond concisely and clearly.
"""

RESUME_ANALYSIS_PROMPT = """
Analyze the following resume and extract:
- Skills
- Years of experience
- Roles
- Tools
- A concise professional summary

Resume:
{resume_text}
"""

JOB_MATCHING_PROMPT = """
Compare the resume data with the job description.
Return:
- Fit score (0–100)
- Missing skills
- Reasoning

Resume:
{resume}

Job Description:
{job_description}
"""
