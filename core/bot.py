import random

class JobBot:
    def __init__(self):
        self.responses = {
            "greeting": [
                "Hello! How can I help you with your job search today?",
                "Hi there! I'm your AI career assistant. What do you need?",
                "Welcome! Ready to land your dream job?"
            ],
            "improve": [
                "To improve your CV for this role, consider adding more details about your experience with {missing_skills}.",
                "I noticed you're missing {missing_skills}. If you have these skills, add them! If not, consider a quick project to demonstrate them.",
                "Your CV is strong, but highlighting {missing_skills} would make it a perfect match."
            ],
            "cover_letter": [
                "Here's a draft cover letter for {company}:\n\nDear Hiring Manager,\n\nI am writing to express my strong interest in the {title} position at {company}...",
                "I've generated a cover letter tailored to {company}. It emphasizes your skills in {skills}."
            ],
            "interview": [
                "For a {title} role, expect questions about {skills}. Be ready to discuss your experience with them.",
                "Prepare for behavioral questions. Use the STAR method to explain your past challenges and successes.",
                "Since this is at {company}, research their recent news and values. They often ask 'Why us?'"
            ],
            "gap": [
                "You have a {score}% match. The main gap is in {missing_skills}. Focus on bridging this gap.",
                "Skill Gap Analysis:\n- Missing: {missing_skills}\n- Recommendation: Take a crash course or build a small project."
            ]
        }

    def generate_response(self, action, context=None):
        context = context or {}
        
        if action == "improve":
            missing = ", ".join(context.get('missing_skills', ['specific technical skills']))
            return random.choice(self.responses['improve']).format(missing_skills=missing)
            
        elif action == "cover_letter":
            return random.choice(self.responses['cover_letter']).format(
                company=context.get('company', 'the company'),
                title=context.get('title', 'this role'),
                skills=", ".join(context.get('skills', [])[:3])
            )
            
        elif action == "interview":
            return random.choice(self.responses['interview']).format(
                title=context.get('title', 'this role'),
                company=context.get('company', 'the company'),
                skills=", ".join(context.get('skills', [])[:3])
            )
            
        elif action == "gap":
            missing = ", ".join(context.get('missing_skills', ['specific skills']))
            return random.choice(self.responses['gap']).format(
                score=context.get('match_score', 0),
                missing_skills=missing
            )
            
        return random.choice(self.responses['greeting'])
