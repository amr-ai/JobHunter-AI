# 🎯 JobHunter AI

<div align="center">

**AI-Powered Job Search Platform with Smart CV Matching**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.1.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.17-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://www.langchain.com/)
[![Status](https://img.shields.io/badge/Status-Under_Development-orange?style=for-the-badge)](#)

</div>

---

## 🚧 Project Status

> [!WARNING]
> **This project is currently under active development.**  
> Some features may be incomplete or experimental.

---

## 📖 Overview

**JobHunter AI** is a web application that leverages artificial intelligence to help you find your perfect job. It combines web scraping with RAG (Retrieval Augmented Generation) technology to deliver an intelligent job search experience.

**Key Features:**
- 🔍 Smart job search with web scraping
- 📄 Automatic CV analysis (PDF/DOCX)
- 🎯 Intelligent skill matching
- 💬 AI career advisor chatbot
- 👤 User authentication & profiles
- 💾 Save and track job applications

---

## 🛠️ Technology Stack

### **Core Backend**
- **Flask 3.1.0** - Web framework
- **Python 3.8+** - Programming language
- **Flask-Session 0.8.0** - Session management

### **AI & NLP**
- **LangChain 0.3.17** - LLM orchestration framework
- **LangChain-Ollama 0.2.0** - Local LLM integration
- **LangChain-Community 0.3.15** - Community integrations
- **Ollama** - Local language model runtime
- **FAISS (CPU)** - Vector similarity search
- **RAG Architecture** - Retrieval Augmented Generation for personalized responses

### **Web Scraping**
- **Selenium 4.27.1** - Browser automation for dynamic content
- **BeautifulSoup4 4.12.3** - HTML/XML parsing
- **Requests 2.32.3** - HTTP requests
- **aiohttp 3.11.11** - Async HTTP client
- **webdriver-manager 4.0.2** - Automatic driver management

### **Document Processing**
- **PyPDF2 3.0.1** - PDF parsing and text extraction
- **python-docx 1.1.2** - Word document processing

### **Data & Storage**
- **JSON** - User data persistence
- **File-based sessions** - Server-side session storage
- **In-memory caching** - Job listings cache

---

## 📁 Project Structure

```
jobhunter/
├── app.py                    # Main Flask application
├── run.py                    # Entry point
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
│
├── core/                     # Core modules
│   ├── auth.py              # Authentication
│   ├── cv_parser.py         # CV text extraction
│   ├── matcher.py           # Skill matching engine
│   ├── rag_chat.py          # RAG chatbot
│   ├── scrapers.py          # Web scraping
│   └── user.py              # User management
│
├── models/                   # Data models
│   └── job.py               # Job model
│
├── services/                 # Services
│   ├── chart_service.py     # Analytics
│   └── session_manager.py   # Session handling
│
├── templates/                # HTML templates
│   ├── landing.html
│   ├── results.html
│   ├── chat.html
│   └── ...
│
└── static/                   # CSS, JS, images
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip
- Ollama (optional - for AI chatbot)

### Setup

1. **Clone & Navigate**
   ```bash
   git clone https://github.com/amr-ai/JobHunter-AI.git
   cd jobhunter
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Ollama (Optional)**
   ```bash
   # Download from https://ollama.ai
   ollama pull llama2
   ```

5. **Run Application**
   ```bash
   python run.py
   ```

6. **Open Browser**
   ```
   http://127.0.0.1:5000
   ```

---

## 📚 Usage

1. **Sign up** and create an account
2. **Upload your CV** (PDF or DOCX)
3. **Search for jobs** by role and location
4. **View match scores** and missing skills
5. **Chat with AI** for career advice
6. **Save jobs** you're interested in

---

## 🗺️ Roadmap

### ✅ Completed
- [x] Job search & scraping
- [x] CV parsing
- [x] Match scoring
- [x] User authentication
- [x] Job bookmarking

### 🚧 In Progress
- [ ] RAG chatbot optimization
- [ ] Multi-source scraping
- [ ] Analytics dashboard

### 📋 Planned
- [ ] LinkedIn integration
- [ ] Email notifications
- [ ] Application tracking
- [ ] Mobile responsive design

---

## 🐛 Known Issues

- Some job sites may block scraping
- Ollama required for AI chatbot
- Unicode issues on Windows (rare)

---

📷Screanshots
<img width="1920" height="887" alt="home" src="https://github.com/user-attachments/assets/d71a5cfa-c2a8-40f7-badd-0be34c027195" />
<img width="1917" height="888" alt="profile" src="https://github.com/user-attachments/assets/141ddf18-1860-447a-a725-555bb35d06db" />
<img width="1913" height="887" alt="chat" src="https://github.com/user-attachments/assets/a214b9b4-70c4-4881-8b4c-56b31a12903c" />
<img width="1920" height="890" alt="search" src="https://github.com/user-attachments/assets/543163eb-377d-422b-9bfd-539b3e95533c" />
<img width="1721" height="817" alt="cv_builder" src="https://github.com/user-attachments/assets/37084397-93b5-41ab-b1e4-cd61be545d8d" />


⭐ **Star this repo if you find it helpful!**

</div>
"# JobHunter-AI" 
