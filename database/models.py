from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import json
import os

Base = declarative_base()

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    summary = Column(Text)
    questions = Column(Text)  # JSON string of questions
    
    candidates = relationship("CandidateEvaluation", back_populates="job")
    
    def set_questions(self, questions_list):
        self.questions = json.dumps(questions_list)
        
    def get_questions(self):
        if self.questions:
            return json.loads(self.questions)
        return []

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True)
    cv_filename = Column(String)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    extracted_data = Column(Text)  # JSON string of extracted data
    
    evaluations = relationship("CandidateEvaluation", back_populates="candidate")
    
    def set_extracted_data(self, data_dict):
        self.extracted_data = json.dumps(data_dict)
        
    def get_extracted_data(self):
        if self.extracted_data:
            return json.loads(self.extracted_data)
        return {}

class CandidateEvaluation(Base):
    __tablename__ = "candidate_evaluations"
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    job_id = Column(Integer, ForeignKey("job_descriptions.id"))
    similarity_score = Column(Float)
    recruiting_score = Column(Float)
    final_score = Column(Float)
    shortlisted = Column(Boolean, default=False)
    interview_scheduled = Column(Boolean, default=False)
    interview_details = Column(Text)  # JSON string of interview details
    rejection_reason = Column(Text)
    
    candidate = relationship("Candidate", back_populates="evaluations")
    job = relationship("JobDescription", back_populates="candidates")
    
    def set_interview_details(self, details_dict):
        self.interview_details = json.dumps(details_dict)
        
    def get_interview_details(self):
        if self.interview_details:
            return json.loads(self.interview_details)
        return {}
