from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_match_score(resume_text: str, job_description: str, job_skills: list):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    resume_lower = resume_text.lower()
    matched = sum(1 for skill in job_skills if skill.lower() in resume_lower)
    skill_rate = (matched / len(job_skills)) * 100 if job_skills else 0
    
    final_score = (similarity * 0.6) + (skill_rate * 0.4)
    
    return {
        "similarity_score": round(similarity * 100, 2),
        "skill_match_rate": round(skill_rate, 2),
        "final_score": round(final_score, 2),
        "matched_skills": matched,
        "total_skills": len(job_skills)
    }
