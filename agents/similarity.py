from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, Any, List, Tuple
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class SimilarityScoreCalculator:
    """Calculate similarity between job descriptions and resumes using TF-IDF"""
    
    def __init__(self, model_name=None):
        """Initialize the Similarity Score Calculator with TF-IDF"""
        # Use TF-IDF vectorizer instead of sentence-transformers
        self.vectorizer = TfidfVectorizer(stop_words='english')
    
    def _preprocess_jd(self, jd_data: Dict[str, Any]) -> str:
        """Preprocess job description data for embedding"""
        components = []
        
        if "job_title" in jd_data:
            components.append(f"Job Title: {jd_data['job_title']}")
        
        if "summary" in jd_data:
            components.append(f"Summary: {jd_data['summary']}")
        
        if "key_requirements" in jd_data and jd_data["key_requirements"]:
            requirements = " ".join(jd_data["key_requirements"])
            components.append(f"Requirements: {requirements}")
        
        return " ".join(components)
    
    def _preprocess_resume(self, resume_data: Dict[str, Any]) -> str:
        """Preprocess resume data for embedding"""
        components = []
        
        # Add skills
        if "skills" in resume_data and resume_data["skills"]:
            if isinstance(resume_data["skills"], list):
                skills = " ".join(resume_data["skills"])
            else:
                skills = resume_data["skills"]
            components.append(f"Skills: {skills}")
        
        # Add experience
        if "experience" in resume_data and resume_data["experience"]:
            if isinstance(resume_data["experience"], list):
                experience_texts = []
                for exp in resume_data["experience"]:
                    if isinstance(exp, dict):
                        exp_text = f"{exp.get('title', '')} at {exp.get('company', '')} {exp.get('description', '')}"
                        experience_texts.append(exp_text)
                    else:
                        experience_texts.append(str(exp))
                experience = " ".join(experience_texts)
            else:
                experience = resume_data["experience"]
            components.append(f"Experience: {experience}")
        
        # Add education
        if "education" in resume_data and resume_data["education"]:
            if isinstance(resume_data["education"], list):
                education_texts = []
                for edu in resume_data["education"]:
                    if isinstance(edu, dict):
                        edu_text = f"{edu.get('degree', '')} from {edu.get('institution', '')}"
                        education_texts.append(edu_text)
                    else:
                        education_texts.append(str(edu))
                education = " ".join(education_texts)
            else:
                education = resume_data["education"]
            components.append(f"Education: {education}")
        
        # Add qualifications
        if "qualifications" in resume_data and resume_data["qualifications"]:
            if isinstance(resume_data["qualifications"], list):
                qualifications = " ".join(resume_data["qualifications"])
            else:
                qualifications = resume_data["qualifications"]
            components.append(f"Qualifications: {qualifications}")
        
        # Add certifications
        if "certifications" in resume_data and resume_data["certifications"]:
            if isinstance(resume_data["certifications"], list):
                certifications = " ".join(resume_data["certifications"])
            else:
                certifications = resume_data["certifications"]
            components.append(f"Certifications: {certifications}")
        
        return " ".join(components)
    
    def calculate_similarity(self, jd_data: Dict[str, Any], resume_data: Dict[str, Any]) -> float:
        """Calculate similarity score between job description and resume using TF-IDF"""
        try:
            # Preprocess data
            jd_text = self._preprocess_jd(jd_data)
            resume_text = self._preprocess_resume(resume_data)
            
            # Generate TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform([jd_text, resume_text])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Scale to 0-10 range
            score = float(similarity * 10)
            
            # Ensure score is within bounds
            return max(0, min(10, score))
            
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def calculate_requirement_matches(self, jd_data: Dict[str, Any], resume_data: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Calculate similarity for each key requirement using TF-IDF"""
        requirement_scores = []
        
        try:
            if "key_requirements" not in jd_data or not jd_data["key_requirements"]:
                return []
            
            resume_text = self._preprocess_resume(resume_data)
            
            for req in jd_data["key_requirements"]:
                # Generate TF-IDF vectors for this requirement and the resume
                tfidf_matrix = self.vectorizer.fit_transform([req, resume_text])
                
                # Calculate cosine similarity
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                
                score = float(similarity * 10)
                requirement_scores.append((req, max(0, min(10, score))))
            
            return requirement_scores
            
        except Exception as e:
            print(f"Error calculating requirement matches: {e}")
            return []
