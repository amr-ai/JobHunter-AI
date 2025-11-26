try:
    from langchain_ollama import ChatOllama, OllamaEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    OLLAMA_AVAILABLE = True
except ImportError as e:
    OLLAMA_AVAILABLE = False
    print(f"Warning: Ollama dependencies not installed. Error: {e}")
    print("Using fallback mode.")

class RAGChatBot:
    
    def __init__(self, cv_data=None):
        self.cv_data = cv_data or {}
        self.has_cv = bool(cv_data and cv_data.get('parsed'))
        self.ollama_ready = False
        
        if OLLAMA_AVAILABLE:
            try:
                print("[INFO] Initializing Ollama RAG system...")
                self._init_ollama()
                self.ollama_ready = True
                print("[SUCCESS] Ollama RAG system initialized successfully.")
            except Exception as e:
                print(f"[ERROR] Ollama initialization failed: {e}")
                self.ollama_ready = False
        else:
            print("[WARNING] Ollama dependencies not available. RAG disabled.")
    
    def _init_ollama(self):
        self.embeddings = OllamaEmbeddings(
            model="all-minilm",
            base_url="http://localhost:11434"
        )
        
        self.llm = ChatOllama(
            model="llama3.2",
            base_url="http://localhost:11434",
            temperature=0.7,
        )
        
        if self.has_cv:
            self.vector_store = self._create_vector_store()
        else:
            self.vector_store = None
    
    def _create_vector_store(self):
        try:
            cv_text = self.cv_data.get('raw_text', '')
            if not cv_text:
                return None
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            chunks = text_splitter.split_text(cv_text)
            
            skills = self.cv_data.get('skills', [])
            experience = self.cv_data.get('experience_years', 0)
            metadata_text = f"User Skills: {', '.join(skills)}. Experience: {experience} years."
            chunks.insert(0, metadata_text)
            
            vector_store = FAISS.from_texts(
                texts=chunks,
                embedding=self.embeddings
            )
            return vector_store
        except Exception as e:
            print(f"Vector store error: {e}")
            return None
    
    def generate_response(self, message, chat_history=None):
        
        chat_history = chat_history or []
        
        if self.ollama_ready and self.has_cv and self.vector_store:
            try:
                print(f"[INFO] Generating RAG response for: {message[:50]}...")
                retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
                docs = retriever.get_relevant_documents(message)
                context = "\n".join([doc.page_content for doc in docs])
                print(f"[INFO] Retrieved {len(docs)} context chunks.")
                
                history_str = ""
                for exchange in chat_history[-3:]:
                    history_str += f"User: {exchange['user']}\nAssistant: {exchange['assistant']}\n\n"
                
                prompt = f"""You are an expert career advisor. Use the CV context to give personalized advice.

CV Context:
{context}

Chat History:
{history_str}

Current Question: {message}

Provide specific, actionable career advice based on the user's CV. Be encouraging and professional. Keep responses concise (2-3 paragraphs max).

Answer:"""
                
                response = self.llm.invoke(prompt)
                print("[SUCCESS] RAG response generated.")
                return response.content
            except Exception as e:
                print(f"[ERROR] RAG generation error: {e}")
                return self._simple_ollama_generation(message, chat_history)
        
        elif self.ollama_ready:
            return self._simple_ollama_generation(message, chat_history)
        
        else:
            return self._fallback_response(message)
    
    def _simple_ollama_generation(self, message, chat_history):
        try:
            context = ""
            for exchange in chat_history[-3:]:
                context += f"User: {exchange['user']}\nAssistant: {exchange['assistant']}\n\n"
            
            prompt = f"""You are a helpful career advisor. 

Previous conversation:
{context}

Current question: {message}

Provide brief, helpful career advice (2-3 paragraphs max). Be specific and actionable."""
            
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"Ollama generation error: {e}")
            return self._fallback_response(message)
    
    def _fallback_response(self, message):
        message_lower = message.lower()
        
        if not self.has_cv:
            return "Please upload your CV to get personalized career advice! I can help much better once I analyze your background."
        
        if 'advice' in message_lower or 'career' in message_lower:
            return "Focus on building your skills, networking, and applying to roles that match your experience. Would you like specific tips on any of these areas?"
        
        if 'skill' in message_lower:
            return "Consider learning in-demand skills like cloud computing, AI/ML, or modern frameworks. What's your current tech stack?"
        
        if 'interview' in message_lower:
            return "Prepare by researching the company, practicing STAR method answers, and reviewing your projects. Need help with specific interview questions?"
        
        return "I'm here to help with career advice! Ask me about skills, job search, interviews, or CV improvement."
