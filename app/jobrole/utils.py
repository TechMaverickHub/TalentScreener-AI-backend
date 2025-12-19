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