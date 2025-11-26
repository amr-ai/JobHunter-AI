
class MatchScoreEngine:
    def __init__(self):
        self.weights = {
            "skills": 0.50,
            "keywords": 0.15,
            "experience": 0.20,
            "education": 0.10,
            "formatting": 0.05
        }
        
        self.critical_skills = {
            "python", "javascript", "react", "node.js", "django", "flask", "fastapi",
            "aws", "docker", "kubernetes", "sql", "postgresql", "mongodb",
            "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
            "pandas", "git", "linux", "ci/cd", "terraform", "typescript"
        }

    def calculate_score(self, job, cv_data):
        if not cv_data or not cv_data.get('parsed'):
            return 0, []

        user_skills = set(s.lower() for s in cv_data.get('skills', []))
        
        job_skills = set(s.lower() for s in job.get('skills_extracted', []))
        if not job_skills:
            title_words = set(job['title'].lower().split())
            job_skills = {w for w in title_words if len(w) > 3}

        skills_score = self._calculate_skills_score(user_skills, job_skills)
        
        keywords_score = skills_score 
        
        experience_score = 100
        if "senior" in job['title'].lower() and cv_data.get('experience_years', 0) < 3:
            experience_score = 40
            
        education_score = 100
        
        formatting_score = 100

        final_score = (
            skills_score * self.weights['skills'] +
            keywords_score * self.weights['keywords'] +
            experience_score * self.weights['experience'] +
            education_score * self.weights['education'] +
            formatting_score * self.weights['formatting']
        )
        
        final_score = min(int(final_score), 98)
        
        missing = [s.title() for s in (job_skills - user_skills) if s in self.critical_skills]
        
        return final_score, missing[:6]

    def _calculate_skills_score(self, user_skills, job_skills):
        if not job_skills:
            return 0
            
        matched = 0
        total_weight = 0
        
        for skill in job_skills:
            weight = 3 if skill in self.critical_skills else 1
            total_weight += weight
            if skill in user_skills:
                matched += weight
                
        if total_weight == 0:
            return 0
            
        return (matched / total_weight) * 100
