from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
from langchain.document_loaders import PyPDFLoader
import os
import json
from typing import Dict, Any, Optional
import re
import sys
sys.path.append('/Users/adityakapole/Downloads/Accenture')
from utils.helpers import mask_pii

class ResumeExtractorAgent:
    """Agent for extracting structured information from resumes"""
    
    def __init__(self, api_key=None, model_name="llama3-8b-8192"):
        """Initialize the Resume Extractor Agent"""
        self.api_key = api_key or os.getenv("CHATGROQ_API_KEY")
        self.model_name = model_name
        self.llm = ChatGroq(
            groq_api_key=self.api_key,
            model_name=self.model_name,
            temperature=0.1
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from a PDF file"""
        try:
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            text = " ".join([page.page_content for page in pages])
            return text
        except Exception as e:
            print(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""
    
    def extract_resume_info(self, resume_text: str) -> Dict[str, Any]:
        """Extract structured information from resume text"""
        
        # Mask PII in the resume text before sending to the LLM
        masked_text = mask_pii(resume_text)
        
        prompt = f"""You are an expert resume parser. Your task is to extract key information from resumes into a structured format.
        Extract only the information that is explicitly mentioned in the resume. Do not make assumptions or add information that is not present.
        If a field is not found in the resume, leave it empty or null.

        Please extract the following information from this resume:

        {masked_text[:4000]}  # Limit text length to avoid token limits
        
        Format your response as a JSON with the following structure:
        {{
            "name": "candidate name",
            "email": "email address",
            "phone": "phone number",
            "education": [
                {{"degree": "degree name", "institution": "institution name", "year": "graduation year"}}
            ],
            "skills": ["skill1", "skill2", ...],
            "experience": [
                {{"title": "job title", "company": "company name", "duration": "duration", "description": "brief description"}}
            ],
            "qualifications": ["qualification1", "qualification2", ...],
            "certifications": ["certification1", "certification2", ...]
        }}
        
        Ensure the output is valid JSON format.
        """
        
        try:
            response = self.llm.invoke(prompt)
            
            # Handle potential formatting issues in the response
            try:
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'({.*})', response.replace('\n', ''), re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                else:
                    # Try to parse the entire response as JSON
                    result = json.loads(response)
            except json.JSONDecodeError:
                # Fallback to manual parsing if JSON extraction fails
                result = {
                        "name": self._extract_name(resume_text),
                        "email": self._extract_email(resume_text),
                        "phone": self._extract_phone(resume_text),
                        "education": [],
                        "skills": [],
                        "experience": [],
                        "qualifications": [],
                        "certifications": []
                    }
            
            return result
            
        except Exception as e:
            print(f"Error in extracting resume information: {e}")
            # Fallback to basic extraction
            return {
                "name": self._extract_name(resume_text),
                "email": self._extract_email(resume_text),
                "phone": self._extract_phone(resume_text),
                "education": [],
                "skills": [],
                "experience": [],
                "qualifications": [],
                "certifications": []
            }
    
    def process_resume_file(self, pdf_path: str) -> Dict[str, Any]:
        """Process a PDF resume file and extract information"""
        try:
            resume_text = self.extract_text_from_pdf(pdf_path)
            if not resume_text:
                return {"error": f"Failed to extract text from {pdf_path}"}
            
            resume_info = self.extract_resume_info(resume_text)
            resume_info["source_file"] = os.path.basename(pdf_path)
            
            return resume_info
            
        except Exception as e:
            print(f"Error processing resume file {pdf_path}: {e}")
            return {"error": str(e), "source_file": os.path.basename(pdf_path)}
    
    # Fallback extraction methods using regex
    def _extract_name(self, text: str) -> str:
        """Extract name from resume text (fallback method)"""
        # This is a simplified approach and may not work for all resumes
        lines = text.split('\n')
        # Assume name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) > 3 and len(line.split()) <= 4:
                return line
        return "Unknown"
    
    def _extract_email(self, text: str) -> str:
        """Extract email from resume text (fallback method)"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number from resume text (fallback method)"""
        phone_pattern = r'(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else ""
