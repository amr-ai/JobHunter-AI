import pdfplumber
from docx import Document
import re
from pathlib import Path
from rapidfuzz import fuzz
import logging

SKILLS_DB = {
    "Python": ["python", "py", "python3", "python 3", "pandas", "numpy"],
    "JavaScript": ["javascript", "js", "ecmascript", "node.js", "nodejs"],
    "React": ["react", "react.js", "reactjs", "react native", "redux"],
    "Node.js": ["node.js", "nodejs", "node"],
    "Django": ["django", "django-rest", "drf"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi", "fast api"],
    "TypeScript": ["typescript", "ts", "type script"],
    "Vue.js": ["vue", "vue.js", "vuejs", "vuetify"],
    "Angular": ["angular", "angularjs"],

    "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda", "cloudformation", "ecs", "eks"],
    "Docker": ["docker", "containers", "docker-compose"],
    "Kubernetes": ["kubernetes", "k8s", "k8", "gke", "eks", "helm"],
    "Terraform": ["terraform", "iac"],
    "CI/CD": ["ci/cd", "ci cd", "jenkins", "gitlab ci", "github actions", "circleci"],

    "Machine Learning": ["machine learning", "ml", "ai", "artificial intelligence"],
    "Deep Learning": ["deep learning", "neural networks", "cnn", "rnn"],
    "NLP": ["nlp", "natural language processing", "text mining", "bert", "gpt", "llm", "transformers", "hugging face"],
    "Computer Vision": ["computer vision", "opencv", "yolo", "image processing"],
    "TensorFlow": ["tensorflow", "tf", "keras"],
    "PyTorch": ["pytorch", "torch"],
    "Pandas": ["pandas", "pd"],
    "NumPy": ["numpy", "np"],
    "SQL": ["sql", "mysql", "postgresql", "postgres", "sqlite", "oracle", "mssql", "redshift"],

    "Git": ["git", "github", "gitlab", "bitbucket"],
    "Linux": ["linux", "ubuntu", "bash", "shell scripting"],
    "Figma": ["figma", "ui/ux", "adobe xd"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Excel": ["excel", "vba", "pivot tables"],
    "Agile": ["agile", "scrum", "kanban", "jira", "trello"],
}

FLATTENED_SKILLS = {}
for standard, variants in SKILLS_DB.items():
    for v in variants:
        FLATTENED_SKILLS[v.lower()] = standard

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        logging.error(f"PDF error: {e}")
    return text

def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except:
        return ""

def extract_text(file_path):
    file_path = Path(file_path)
    if file_path.suffix.lower() == ".pdf":
        return extract_text_from_pdf(file_path)
    elif file_path.suffix.lower() in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    return ""

def segment_sections(text):
    text = text.lower()
    sections = {
        "experience": "",
        "education": "",
        "skills": "",
        "projects": ""
    }
    
    markers = {
        "experience": ["experience", "work history", "employment", "career history"],
        "education": ["education", "academic", "qualifications", "degrees"],
        "skills": ["skills", "technologies", "technical skills", "competencies", "expertise"],
        "projects": ["projects", "portfolio"]
    }
    
    current_section = None
    lines = text.split('\n')
    
    for line in lines:
        clean_line = line.strip()
        found_new_section = False
        
        for section, keywords in markers.items():
            if any(k in clean_line for k in keywords) and len(clean_line) < 30:
                current_section = section
                found_new_section = True
                break
        
        if found_new_section:
            continue
            
        if current_section:
            sections[current_section] += line + "\n"
            
    return sections

def extract_skills_from_cv(text):
    if not text:
        return []
    text = text.lower()
    found = set()

    for variant, standard in FLATTENED_SKILLS.items():
        if re.search(r'\b' + re.escape(variant) + r'\b', text):
            found.add(standard)

    if not found:
        for skill in SKILLS_DB.keys():
            if fuzz.partial_ratio(skill.lower(), text) > 90:
                found.add(skill)

    return sorted(list(found))

def extract_experience_years(text):
    years = re.findall(r'(\d{4})\s*-\s*(\d{4}|present|current|now)', text.lower())
    total_years = 0
    if years:
        total_years = len(years) * 2
    return total_years

def parse_cv(file_path):
    text = extract_text(file_path)
    if not text.strip():
        return {"raw_text": "", "skills": [], "parsed": False}

    sections = segment_sections(text)
    
    skills = extract_skills_from_cv(text)
    
    experience_years = extract_experience_years(sections['experience'] or text)

    return {
        "raw_text": text,
        "sections": sections,
        "skills": skills,
        "experience_years": experience_years,
        "parsed": True
    }