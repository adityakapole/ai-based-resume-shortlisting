from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
import os
import json
import pandas as pd
from typing import List, Dict, Any

class JDSummarizerAgent:
    """Agent for summarizing job descriptions and generating relevant questions"""
    
    def __init__(self, api_key=None, model_name="llama3-8b-8192"):
        """Initialize the JD Summarizer Agent"""
        self.api_key = api_key or os.getenv("CHATGROQ_API_KEY")
        self.model_name = model_name
        self.llm = ChatGroq(
            groq_api_key=self.api_key,
            model_name=self.model_name,
            temperature=0.2
        )
        
    def summarize_jd(self, job_title: str, job_description: str) -> Dict[str, Any]:
        """Summarize a job description and generate relevant questions"""
        
        prompt = f"""You are an expert HR professional specializing in job analysis. 
        Your task is to analyze job descriptions and extract key requirements and qualifications.
        Based on these requirements, generate specific questions that can be used to evaluate candidates.
        Focus on technical skills, experience, education, and other important qualifications mentioned in the job description.

        Please analyze the following job description for the position of {job_title}:

        {job_description}
        
        Provide:
        1. A concise summary of the job (max 150 words)
        2. A list of 5-8 key requirements extracted from the job description
        3. A list of specific questions (5-10) that can be used to evaluate if a candidate meets these requirements
        
        Format your response as a JSON with the following structure:
        {{
            "summary": "concise summary here",
            "key_requirements": ["requirement 1", "requirement 2", ...],
            "evaluation_questions": ["question 1", "question 2", ...]
        }}
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
                    "summary": response[:150] if len(response) > 150 else response,
                    "key_requirements": [],
                    "evaluation_questions": []
                }
            
            return result
            
        except Exception as e:
            print(f"Error in summarizing job description: {e}")
            return {
                "summary": f"Error processing job description: {str(e)}",
                "key_requirements": [],
                "evaluation_questions": []
            }
    
    def process_jd_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a CSV file containing job descriptions"""
        try:
            df = pd.read_csv(file_path)
            results = []
            
            for _, row in df.iterrows():
                job_title = row.get('Job Title', 'Unknown Position')
                job_description = row.get('Job Description', '')
                
                if job_description:
                    result = self.summarize_jd(job_title, job_description)
                    result['job_title'] = job_title
                    result['original_description'] = job_description
                    results.append(result)
            
            return results
        
        except Exception as e:
            print(f"Error processing JD file: {e}")
            return []
