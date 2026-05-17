import re

SKILLS = ["python", "java", "javascript", "react", "angular", "node", "django", "flask", "sql", "aws", "docker", "tensorflow", "pytorch", "machine learning", "ai", "excel", "tableau", "git"]

def analyze_job_description(description: str):
    desc_lower = description.lower()
    found = [s for s in SKILLS if s in desc_lower]
    
    exp_years = 0
    match = re.search(r'(\d+)\+?\s*years?', description, re.IGNORECASE)
    if match:
        exp_years = int(match.group(1))
    
    return {
        "required_skills": found[:10],
        "min_experience_years": exp_years,
        "word_count": len(description.split())
    }
