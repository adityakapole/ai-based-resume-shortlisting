from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
import os
import json
from typing import Dict, Any, List

class RecruitingAgent:
    """Agent for evaluating candidates based on job requirements"""
    
    def __init__(self, api_key=None, model_name="llama3-8b-8192"):
        """Initialize the Recruiting Agent"""
        self.api_key = api_key or os.getenv("CHATGROQ_API_KEY")
        self.model_name = model_name
        self.llm = ChatGroq(
            groq_api_key=self.api_key,
            model_name=self.model_name,
            temperature=0.2
        )
    
    def evaluate_candidate(self, jd_data: Dict[str, Any], resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a candidate based on job requirements and resume data"""
        
        # Extract job title and questions
        job_title = jd_data.get("job_title", "Unknown Position")
        questions = jd_data.get("evaluation_questions", [])
        
        if not questions:
            return {
                "score": 0.0,
                "feedback": "No evaluation questions available",
                "question_scores": []
            }
        
        # Format resume data for the prompt
        resume_sections = []
        
        if "name" in resume_data:
            resume_sections.append(f"Name: {resume_data['name']}")
        
        if "skills" in resume_data and resume_data["skills"]:
            if isinstance(resume_data["skills"], list):
                skills = ", ".join(resume_data["skills"])
            else:
                skills = resume_data["skills"]
            resume_sections.append(f"Skills: {skills}")
        
        if "experience" in resume_data and resume_data["experience"]:
            resume_sections.append("Experience:")
            if isinstance(resume_data["experience"], list):
                for exp in resume_data["experience"]:
                    if isinstance(exp, dict):
                        exp_text = f"- {exp.get('title', '')} at {exp.get('company', '')}, {exp.get('duration', '')}: {exp.get('description', '')}"
                        resume_sections.append(exp_text)
                    else:
                        resume_sections.append(f"- {exp}")
            else:
                resume_sections.append(f"- {resume_data['experience']}")
        
        if "education" in resume_data and resume_data["education"]:
            resume_sections.append("Education:")
            if isinstance(resume_data["education"], list):
                for edu in resume_data["education"]:
                    if isinstance(edu, dict):
                        edu_text = f"- {edu.get('degree', '')} from {edu.get('institution', '')}, {edu.get('year', '')}"
                        resume_sections.append(edu_text)
                    else:
                        resume_sections.append(f"- {edu}")
            else:
                resume_sections.append(f"- {resume_data['education']}")
        
        if "qualifications" in resume_data and resume_data["qualifications"]:
            if isinstance(resume_data["qualifications"], list):
                qualifications = ", ".join(resume_data["qualifications"])
            else:
                qualifications = resume_data["qualifications"]
            resume_sections.append(f"Qualifications: {qualifications}")
        
        if "certifications" in resume_data and resume_data["certifications"]:
            if isinstance(resume_data["certifications"], list):
                certifications = ", ".join(resume_data["certifications"])
            else:
                certifications = resume_data["certifications"]
            resume_sections.append(f"Certifications: {certifications}")
        
        resume_text = "\n".join(resume_sections)
        
        # Format questions for the prompt
        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
        
        prompt = f"""You are an expert recruiter evaluating candidates for a {job_title} position.
        Your task is to evaluate how well a candidate's resume matches the job requirements by answering specific questions.
        For each question, provide a score from 0-10 (where 10 is perfect match) and brief feedback.
        Be objective and fair in your assessment, focusing only on the information provided in the resume.

        Please evaluate the following candidate for the {job_title} position:

        RESUME:
        {resume_text}
        
        EVALUATION QUESTIONS:
        {questions_text}
        
        For each question, provide:
        1. A score from 0-10 (where 10 is perfect match)
        2. Brief feedback explaining your score
        
        Then provide an overall score (average of all question scores) and general feedback.
        
        Format your response as a JSON with the following structure:
        {{
            "question_scores": [
                {{"question": "question text", "score": score, "feedback": "feedback"}}
            ],
            "overall_score": average_score,
            "general_feedback": "general feedback"
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
                    "question_scores": [],
                    "overall_score": 0.0,
                    "general_feedback": "Failed to parse evaluation results"
                }
            
            # Ensure overall_score is a float
            if "overall_score" in result:
                try:
                    result["overall_score"] = float(result["overall_score"])
                except (ValueError, TypeError):
                    result["overall_score"] = 0.0
            
            return result
            
        except Exception as e:
            print(f"Error in evaluating candidate: {e}")
            return {
                "question_scores": [],
                "overall_score": 0.0,
                "general_feedback": f"Error evaluating candidate: {str(e)}"
            }
