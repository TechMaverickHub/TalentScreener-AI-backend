import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def extract_relevant_sections_with_llm(text: str) -> str:
    """
    Uses Groq LLM to extract relevant sections like Responsibilities, Requirements, Skills, and Summary.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""
    You are an AI assistant that extracts only the most relevant and technical parts of a job description or resume.
    From the following text, return a clean summary of these sections:
    - Responsibilities
    - Requirements or Qualifications
    - Skills or Technologies
    - Summary or Role Overview
    
    Return only those parts in bullet or paragraph form. Ignore company background, perks, or filler text.
    
    TEXT:
    {text}
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message.content.strip()

    return content


def extract_job_keywords_from_resume(resume_text: str) -> list[str]:
    """
    Uses an LLM to extract job-related keywords or titles from resume text
    (e.g., 'frontend developer', 'data engineer', etc.) for filtering search results.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""
    From the following resume, extract a concise list of job titles or roles the candidate is suited for.
    Return them as a comma-separated list (e.g., frontend developer, backend engineer, data analyst).
    Avoid general traits and focus on actual job functions.

    Resume:
    {resume_text}
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message.content.strip()

    # Parse comma-separated string into clean list
    roles = [role.strip().lower() for role in content.split(",") if role.strip()]
    return roles


def parse_resume_with_llm(text):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""
    Developer: Begin with a concise checklist (3-7 bullets) of what you will do; keep items conceptual, not implementation-level. Extract the following fields from the provided resume text:


- years_of_experience
- skills
- technical_experience
- summary

If the resume text is missing or empty, return a JSON object with all fields set to null.
For any field that cannot be extracted because it is missing from the resume, set its value to null in the output JSON.
Return the result as a JSON object following this structure:

{{

 "years_of_experience": integer or null,
  "skills": array of strings or null,
  "technical_experience": string or null,
  "summary": string or null
}}
Strictly adhere to this output format. Do not output content other than the single JSON object. The order of keys in the JSON does not matter.

Example output:

{{
    "years_of_experience": 5,
  "skills": ["Python", "SQL", "Machine Learning"],
  "technical_experience": "Experience with AWS and Docker in large-scale applications.",
  "summary": "Engineering leader with a focus on cloud technologies."
}}

    TEXT:
    {text}
    """
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def parse_job_description_with_llm(text):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""
    You are an expert information extractor.

Given the resume text below, extract the following fields:
- years_of_experience (integer)
- skills (array of strings)
- technical_experience (string)
- summary (string)

Return a valid JSON object with these exact keys. 
If any field is missing or unavailable, set its value to null.

**Return ONLY the JSON object**. Do not include explanations or surrounding text.

Expected format:
{{
  "years_of_experience": 5,
  "skills": ["Python", "SQL", "Machine Learning"],
  "technical_experience": "Experience with AWS and Docker in large-scale applications.",
  "summary": "Engineering leader with a focus on cloud technologies."
}}

Now extract from the following resume text:

    {text}
    """
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def flatten_resume_dict(resume_data: dict) -> str:
    """
    Converts structured resume fields into a flat text string for embedding.
    """
    parts = []
    if resume_data.get("summary"):
        parts.append(f"Summary: {resume_data['summary']}")
    if resume_data.get("technical_experience"):
        parts.append(f"Experience: {resume_data['technical_experience']}")
    if resume_data.get("skills"):
        skills = ", ".join(resume_data["skills"])
        parts.append(f"Skills: {skills}")
    if resume_data.get("years_of_experience") is not None:
        parts.append(f"Years of experience: {resume_data['years_of_experience']}")
    return " ".join(parts)
