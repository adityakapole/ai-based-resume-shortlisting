from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from .models import Base, JobDescription, Candidate, CandidateEvaluation

class Database:
    def __init__(self, db_path='sqlite:///recruitment.db'):
        """Initialize database connection"""
        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
    def get_session(self):
        """Get a new session"""
        return self.Session()
    
    def add_job_description(self, title, description, summary=None, questions=None):
        """Add a new job description to the database"""
        session = self.get_session()
        try:
            jd = JobDescription(title=title, description=description, summary=summary)
            if questions:
                jd.set_questions(questions)
            session.add(jd)
            session.commit()
            return jd.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_candidate(self, cv_filename, name=None, email=None, phone=None, extracted_data=None):
        """Add a new candidate to the database"""
        session = self.get_session()
        try:
            candidate = Candidate(cv_filename=cv_filename, name=name, email=email, phone=phone)
            if extracted_data:
                candidate.set_extracted_data(extracted_data)
            session.add(candidate)
            session.commit()
            return candidate.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_evaluation(self, candidate_id, job_id, similarity_score=None):
        """Add a new candidate evaluation"""
        session = self.get_session()
        try:
            eval = CandidateEvaluation(
                candidate_id=candidate_id,
                job_id=job_id,
                similarity_score=similarity_score
            )
            session.add(eval)
            session.commit()
            return eval.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update_evaluation(self, eval_id, **kwargs):
        """Update an existing evaluation"""
        session = self.get_session()
        try:
            eval = session.query(CandidateEvaluation).filter_by(id=eval_id).first()
            if not eval:
                raise ValueError(f"Evaluation with ID {eval_id} not found")
            
            for key, value in kwargs.items():
                if hasattr(eval, key):
                    setattr(eval, key, value)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_job_description(self, job_id):
        """Get job description by ID"""
        session = self.get_session()
        try:
            return session.query(JobDescription).filter_by(id=job_id).first()
        finally:
            session.close()
    
    def get_candidate(self, candidate_id):
        """Get candidate by ID"""
        session = self.get_session()
        try:
            return session.query(Candidate).filter_by(id=candidate_id).first()
        finally:
            session.close()
    
    def get_evaluation(self, eval_id):
        """Get evaluation by ID"""
        session = self.get_session()
        try:
            return session.query(CandidateEvaluation).filter_by(id=eval_id).first()
        finally:
            session.close()
    
    def get_all_job_descriptions(self):
        """Get all job descriptions"""
        session = self.get_session()
        try:
            return session.query(JobDescription).all()
        finally:
            session.close()
    
    def get_all_candidates(self):
        """Get all candidates"""
        session = self.get_session()
        try:
            return session.query(Candidate).all()
        finally:
            session.close()
    
    def get_candidates_for_job(self, job_id):
        """Get all candidates evaluated for a specific job"""
        session = self.get_session()
        try:
            return session.query(Candidate).join(CandidateEvaluation).filter(
                CandidateEvaluation.job_id == job_id
            ).all()
        finally:
            session.close()
    
    def get_shortlisted_candidates(self, job_id):
        """Get all shortlisted candidates for a specific job"""
        session = self.get_session()
        try:
            return session.query(Candidate).join(CandidateEvaluation).filter(
                CandidateEvaluation.job_id == job_id,
                CandidateEvaluation.shortlisted == True
            ).all()
        finally:
            session.close()
