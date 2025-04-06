from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
import os
import json
from typing import Dict, Any, List
import sys
sys.path.append('/Users/adityakapole/Downloads/Accenture')
from utils.helpers import generate_interview_dates, generate_interview_times, generate_interview_email, generate_rejection_email

class InterviewSchedulerAgent:
    """Agent for generating personalized interview invitation emails"""
    
    def __init__(self, api_key=None, model_name="llama3-8b-8192"):
        """Initialize the Interview Scheduler Agent"""
        self.api_key = api_key or os.getenv("CHATGROQ_API_KEY")
        self.model_name = model_name
        self.llm = ChatGroq(
            groq_api_key=self.api_key,
            model_name=self.model_name,
            temperature=0.3
        )
    
    def generate_interview_format(self, jd_data: Dict[str, Any], candidate_data: Dict[str, Any]) -> str:
        """Determine the appropriate interview format based on job and candidate data"""
        job_title = jd_data.get("job_title", "Unknown Position")
        job_summary = jd_data.get("summary", "")
        
        prompt = f"""You are an expert HR professional responsible for determining the most appropriate interview format for candidates.
        Based on the job description and candidate profile, recommend the best interview format (e.g., technical, behavioral, case study, panel, etc.).

        Please recommend the most appropriate interview format for a {job_title} position with the following details:

        Job Summary: {job_summary}
        
        Candidate Profile:
        - Skills: {', '.join(candidate_data.get('skills', [])) if isinstance(candidate_data.get('skills', []), list) else candidate_data.get('skills', '')}
        - Experience: {len(candidate_data.get('experience', [])) if isinstance(candidate_data.get('experience', []), list) else 'Unknown'} positions
        
        Provide only the interview format as a single word or short phrase (e.g., "Technical Video Interview" or "Panel Discussion").
        """
        
        try:
            response = self.llm.invoke(prompt)
            interview_format = response.strip()
            return interview_format
        except Exception as e:
            print(f"Error generating interview format: {e}")
            return "Video Interview"  # Default format
    
    def generate_interview_invitation(self, jd_data: Dict[str, Any], candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a personalized interview invitation email"""
        try:
            # Get candidate name
            candidate_name = candidate_data.get("name", "Candidate")
            
            # Get job title
            job_title = jd_data.get("job_title", "the position")
            
            # Generate interview dates and times
            dates = generate_interview_dates(num_dates=3)
            times = generate_interview_times(num_times=3)
            
            # Determine interview format
            interview_format = self.generate_interview_format(jd_data, candidate_data)
            
            # Generate email
            email_data = generate_interview_email(candidate_name, job_title, dates, times, interview_format)
            
            # Add additional data
            result = {
                "email": email_data,
                "candidate_name": candidate_name,
                "job_title": job_title,
                "interview_format": interview_format,
                "proposed_dates": dates,
                "proposed_times": times
            }
            
            return result
            
        except Exception as e:
            print(f"Error generating interview invitation: {e}")
            return {
                "email": {
                    "subject": "Interview Invitation",
                    "body": f"Error generating interview invitation: {str(e)}"
                }
            }
    
    def generate_rejection_email_for_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a rejection email for a candidate"""
        try:
            # Get candidate name
            candidate_name = candidate_data.get("name", "Candidate")
            
            # Generate email
            email_data = generate_rejection_email(candidate_name)
            
            return {
                "email": email_data,
                "candidate_name": candidate_name
            }
            
        except Exception as e:
            print(f"Error generating rejection email: {e}")
            return {
                "email": {
                    "subject": "Application Status Update",
                    "body": f"Error generating rejection email: {str(e)}"
                }
            }
    
    def process_candidates(self, jd_data: Dict[str, Any], candidates: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Process all candidates and generate appropriate emails"""
        results = {
            "shortlisted": [],
            "rejected": []
        }
        
        # Process shortlisted candidates
        for candidate in candidates.get("shortlisted", []):
            invitation = self.generate_interview_invitation(jd_data, candidate)
            candidate_result = {**candidate, "invitation": invitation}
            results["shortlisted"].append(candidate_result)
        
        # Process rejected candidates
        for candidate in candidates.get("rejected", []):
            rejection = self.generate_rejection_email_for_candidate(candidate)
            candidate_result = {**candidate, "rejection": rejection}
            results["rejected"].append(candidate_result)
        
        return results
