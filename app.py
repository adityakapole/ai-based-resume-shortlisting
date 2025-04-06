import streamlit as st
import os
import pandas as pd
import json
from pathlib import Path
import tempfile
import time
from typing import Dict, Any, List

# Import agents
from agents.jd_summarizer import JDSummarizerAgent
from agents.resume_extractor import ResumeExtractorAgent
from agents.similarity import SimilarityScoreCalculator
from agents.recruiting import RecruitingAgent
from agents.shortlisting import ShortlistingAgent
from agents.scheduler import InterviewSchedulerAgent

# Import database
from database.db import Database
from database.models import JobDescription, Candidate, CandidateEvaluation

# Set page configuration
st.set_page_config(
    page_title="AI Recruitment Assistant",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "job_data" not in st.session_state:
    st.session_state.job_data = None
if "candidates" not in st.session_state:
    st.session_state.candidates = []
if "processed_candidates" not in st.session_state:
    st.session_state.processed_candidates = {"shortlisted": [], "rejected": []}
if "db" not in st.session_state:
    st.session_state.db = Database()

# Helper functions
def load_job_descriptions():
    """Load job descriptions from CSV file"""
    try:
        jd_path = os.path.join("Dataset", "job_description.csv")
        return pd.read_csv(jd_path, encoding='latin1')  # Try latin1 encoding first
    except Exception as e:
        st.error(f"Error loading job descriptions: {e}")
        return pd.DataFrame(columns=["Job Title", "Job Description"])

def load_resumes():
    """Get list of resume files"""
    try:
        cv_path = os.path.join("Dataset", "CVs1")
        return [f for f in os.listdir(cv_path) if f.endswith(".pdf")]
    except Exception as e:
        st.error(f"Error loading resumes: {e}")
        return []

# Main app
def main():
    st.title("AI Recruitment Assistant")
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        
        # API Key input
        api_key = st.text_input("Enter Chatgroq API Key:", type="password", value=st.session_state.api_key)
        if api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
        
        # Navigation
        st.header("Navigation")
        menu = ["Upload JD", "Process CVs", "View Results", "Shortlist Candidates", "Generate Emails"]
        choice = st.radio("Go to", menu)
    
    # Main content
    if choice == "Upload JD":
        upload_jd_page()
    elif choice == "Process CVs":
        process_cvs_page()
    elif choice == "View Results":
        view_results_page()
    elif choice == "Shortlist Candidates":
        shortlist_candidates_page()
    elif choice == "Generate Emails":
        generate_emails_page()

def upload_jd_page():
    st.header("Upload Job Description")
    
    # Option to use existing JD from dataset
    st.subheader("Use Existing Job Description")
    try:
        jd_df = load_job_descriptions()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        try:
            jd_path = os.path.join("Dataset", "job_description.csv")
            jd_df = pd.read_csv(jd_path, encoding='latin1')
        except Exception as e:
            st.error(f"Error loading job descriptions with alternative encoding: {e}")
            jd_df = pd.DataFrame(columns=["Job Title", "Job Description"])
    
    
    if not jd_df.empty:
        job_titles = jd_df["Job Title"].tolist()
        selected_job = st.selectbox("Select Job Title", job_titles)
        
        if selected_job:
            job_description = jd_df[jd_df["Job Title"] == selected_job]["Job Description"].values[0]
            st.text_area("Job Description", job_description, height=200, disabled=True)
            
            if st.button("Process Selected Job Description"):
                with st.spinner("Processing job description..."):
                    # Initialize JD Summarizer Agent
                    jd_agent = JDSummarizerAgent(api_key=st.session_state.api_key)
                    
                    # Process job description
                    result = jd_agent.summarize_jd(selected_job, job_description)
                    result["job_title"] = selected_job
                    result["original_description"] = job_description
                    
                    # Store in session state
                    st.session_state.job_data = result
                    
                    # Store in database
                    db = st.session_state.db
                    job_id = db.add_job_description(
                        title=selected_job,
                        description=job_description,
                        summary=result.get("summary"),
                        questions=result.get("evaluation_questions")
                    )
                    
                    st.success(f"Job description processed successfully! Job ID: {job_id}")
                    
                    # Display results
                    st.subheader("Job Summary")
                    st.write(result.get("summary", "No summary generated"))
                    
                    st.subheader("Key Requirements")
                    for req in result.get("key_requirements", []):
                        st.write(f"- {req}")
                    
                    st.subheader("Evaluation Questions")
                    for q in result.get("evaluation_questions", []):
                        st.write(f"- {q}")
    
    # Option to upload custom JD
    st.subheader("Or Upload Custom Job Description")
    
    job_title = st.text_input("Job Title")
    job_description = st.text_area("Job Description", height=200)
    
    if st.button("Process Custom Job Description") and job_title and job_description:
        with st.spinner("Processing job description..."):
            # Initialize JD Summarizer Agent
            jd_agent = JDSummarizerAgent(api_key=st.session_state.api_key)
            
            # Process job description
            result = jd_agent.summarize_jd(job_title, job_description)
            result["job_title"] = job_title
            result["original_description"] = job_description
            
            # Store in session state
            st.session_state.job_data = result
            
            # Store in database
            db = st.session_state.db
            job_id = db.add_job_description(
                title=job_title,
                description=job_description,
                summary=result.get("summary"),
                questions=result.get("evaluation_questions")
            )
            
            st.success(f"Job description processed successfully! Job ID: {job_id}")
            
            # Display results
            st.subheader("Job Summary")
            st.write(result.get("summary", "No summary generated"))
            
            st.subheader("Key Requirements")
            for req in result.get("key_requirements", []):
                st.write(f"- {req}")
            
            st.subheader("Evaluation Questions")
            for q in result.get("evaluation_questions", []):
                st.write(f"- {q}")

def process_cvs_page():
    st.header("Process Resumes")
    
    # Check if job description is processed
    if not st.session_state.job_data:
        st.warning("Please process a job description first!")
        return
    
    st.info(f"Current Job: {st.session_state.job_data.get('job_title', 'Unknown')}")
    
    # Option to use existing CVs from dataset
    st.subheader("Use Existing Resumes")
    resume_files = load_resumes()
    
    if resume_files:
        num_resumes = len(resume_files)
        st.write(f"Found {num_resumes} resumes in the dataset")
        
        # Allow selecting number of resumes to process
        num_to_process = st.slider("Number of resumes to process", 1, min(num_resumes, 20), 5)
        selected_resumes = resume_files[:num_to_process]
        
        st.write(f"Selected resumes: {', '.join(selected_resumes)}")
        
        if st.button("Process Selected Resumes"):
            process_resumes(selected_resumes)
    
    # Option to upload custom resumes
    st.subheader("Or Upload Custom Resumes")
    uploaded_files = st.file_uploader("Upload Resumes (PDF)", type="pdf", accept_multiple_files=True)
    
    if uploaded_files and st.button("Process Uploaded Resumes"):
        # Save uploaded files to temp directory
        temp_dir = tempfile.mkdtemp()
        temp_files = []
        
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            temp_files.append(file_path)
        
        process_resumes(temp_files, is_temp=True)

def process_resumes(resume_files, is_temp=False):
    """Process resumes and calculate similarity scores"""
    if not resume_files:
        st.warning("No resumes selected!")
        return
    
    job_data = st.session_state.job_data
    
    # Initialize agents
    resume_agent = ResumeExtractorAgent(api_key=st.session_state.api_key)
    similarity_calculator = SimilarityScoreCalculator()
    recruiting_agent = RecruitingAgent(api_key=st.session_state.api_key)
    
    # Process each resume
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    candidates = []
    
    for i, resume_file in enumerate(resume_files):
        status_text.text(f"Processing resume {i+1}/{len(resume_files)}: {resume_file}")
        
        try:
            # Construct full path if not using temp files
            if not is_temp:
                resume_path = os.path.join("Dataset", "CVs1", resume_file)
            else:
                resume_path = resume_file
            
            # Extract resume information
            resume_data = resume_agent.process_resume_file(resume_path)
            
            if "error" in resume_data:
                st.error(f"Error processing {resume_file}: {resume_data['error']}")
                continue
            
            # Calculate similarity score
            similarity_score = similarity_calculator.calculate_similarity(job_data, resume_data)
            
            # Store candidate in database
            db = st.session_state.db
            candidate_id = db.add_candidate(
                cv_filename=os.path.basename(resume_path),
                name=resume_data.get("name"),
                email=resume_data.get("email"),
                phone=resume_data.get("phone"),
                extracted_data=resume_data
            )
            
            # Only proceed with recruiting evaluation if similarity score is high enough
            recruiting_score = None
            if similarity_score >= 8.0:
                # Evaluate candidate with recruiting agent
                recruiting_score = recruiting_agent.evaluate_candidate(job_data, resume_data)
            
            # Store evaluation in database
            eval_id = db.add_evaluation(
                candidate_id=candidate_id,
                job_id=1,  # Assuming job ID 1 for simplicity
                similarity_score=similarity_score
            )
            
            if recruiting_score:
                db.update_evaluation(
                    eval_id=eval_id,
                    recruiting_score=recruiting_score.get("overall_score"),
                    final_score=(similarity_score + recruiting_score.get("overall_score", 0)) / 2
                )
            
            # Add to candidates list
            candidate = {
                "id": candidate_id,
                "eval_id": eval_id,
                "filename": os.path.basename(resume_path),
                "data": resume_data,
                "similarity_score": similarity_score,
                "recruiting_score": recruiting_score
            }
            candidates.append(candidate)
            
        except Exception as e:
            st.error(f"Error processing {resume_file}: {str(e)}")
        
        # Update progress
        progress_bar.progress((i + 1) / len(resume_files))
    
    # Store candidates in session state
    st.session_state.candidates = candidates
    
    status_text.text(f"Processed {len(candidates)} resumes successfully!")
    st.success("Resume processing complete!")

def view_results_page():
    st.header("View Results")
    
    # Check if candidates are processed
    if not st.session_state.candidates:
        st.warning("No candidates processed yet!")
        return
    
    # Display job information
    job_data = st.session_state.job_data
    st.subheader(f"Job: {job_data.get('job_title', 'Unknown')}")
    
    # Display candidates
    st.subheader("Candidates")
    
    # Create tabs for different views
    tabs = st.tabs(["All Candidates", "Similarity Scores", "Recruiting Scores"])
    
    with tabs[0]:
        for i, candidate in enumerate(st.session_state.candidates):
            with st.expander(f"{i+1}. {candidate['data'].get('name', 'Unknown')} - {candidate['filename']}"):
                st.write(f"**Similarity Score:** {candidate['similarity_score']:.2f}/10")
                
                if candidate['recruiting_score']:
                    st.write(f"**Recruiting Score:** {candidate['recruiting_score'].get('overall_score', 0):.2f}/10")
                    st.write(f"**Final Score:** {(candidate['similarity_score'] + candidate['recruiting_score'].get('overall_score', 0)) / 2:.2f}/10")
                else:
                    st.write("**Recruiting Score:** Not evaluated (similarity score below threshold)")
                
                # Display candidate data
                st.write("**Candidate Information:**")
                st.json(candidate['data'])
    
    with tabs[1]:
        # Create bar chart of similarity scores
        candidates_df = pd.DataFrame([
            {
                "Candidate": c['data'].get('name', f"Candidate {i+1}"),
                "Similarity Score": c['similarity_score']
            } for i, c in enumerate(st.session_state.candidates)
        ])
        
        st.bar_chart(candidates_df.set_index("Candidate"))
    
    with tabs[2]:
        # Create bar chart of recruiting scores
        recruiting_df = pd.DataFrame([
            {
                "Candidate": c['data'].get('name', f"Candidate {i+1}"),
                "Recruiting Score": c['recruiting_score'].get('overall_score', 0) if c['recruiting_score'] else 0
            } for i, c in enumerate(st.session_state.candidates)
        ])
        
        st.bar_chart(recruiting_df.set_index("Candidate"))

def shortlist_candidates_page():
    st.header("Shortlist Candidates")
    
    # Check if candidates are processed
    if not st.session_state.candidates:
        st.warning("No candidates processed yet!")
        return
    
    # Display job information
    job_data = st.session_state.job_data
    st.subheader(f"Job: {job_data.get('job_title', 'Unknown')}")
    
    # Initialize shortlisting agent
    shortlisting_agent = ShortlistingAgent()
    
    # Shortlist candidates
    if st.button("Shortlist Candidates"):
        with st.spinner("Shortlisting candidates..."):
            result = shortlisting_agent.shortlist_candidates(st.session_state.candidates, job_data)
            st.session_state.processed_candidates = result
            
            # Update database
            db = st.session_state.db
            for candidate in result["shortlisted"]:
                db.update_evaluation(
                    eval_id=candidate["eval_id"],
                    shortlisted=True
                )
            
            for candidate in result["rejected"]:
                db.update_evaluation(
                    eval_id=candidate["eval_id"],
                    shortlisted=False,
                    rejection_reason=candidate.get("shortlisting_reason", "")
                )
            
            st.success(f"Shortlisted {len(result['shortlisted'])} candidates, rejected {len(result['rejected'])} candidates")
    
    # Display shortlisted candidates
    if st.session_state.processed_candidates["shortlisted"]:
        st.subheader("Shortlisted Candidates")
        
        for i, candidate in enumerate(st.session_state.processed_candidates["shortlisted"]):
            with st.expander(f"{i+1}. {candidate['data'].get('name', 'Unknown')} - {candidate['filename']}"):
                st.write(f"**Similarity Score:** {candidate['similarity_score']:.2f}/10")
                
                if candidate['recruiting_score']:
                    st.write(f"**Recruiting Score:** {candidate['recruiting_score'].get('overall_score', 0):.2f}/10")
                    st.write(f"**Final Score:** {(candidate['similarity_score'] + candidate['recruiting_score'].get('overall_score', 0)) / 2:.2f}/10")
                
                st.write(f"**Shortlisting Reason:** {candidate.get('shortlisting_reason', '')}")
    
    # Display rejected candidates
    if st.session_state.processed_candidates["rejected"]:
        st.subheader("Rejected Candidates")
        
        for i, candidate in enumerate(st.session_state.processed_candidates["rejected"]):
            with st.expander(f"{i+1}. {candidate['data'].get('name', 'Unknown')} - {candidate['filename']}"):
                st.write(f"**Similarity Score:** {candidate['similarity_score']:.2f}/10")
                
                if candidate['recruiting_score']:
                    st.write(f"**Recruiting Score:** {candidate['recruiting_score'].get('overall_score', 0):.2f}/10")
                    st.write(f"**Final Score:** {(candidate['similarity_score'] + candidate['recruiting_score'].get('overall_score', 0)) / 2:.2f}/10")
                
                st.write(f"**Rejection Reason:** {candidate.get('shortlisting_reason', '')}")

def generate_emails_page():
    st.header("Generate Emails")
    
    # Check if candidates are shortlisted
    if not st.session_state.processed_candidates["shortlisted"] and not st.session_state.processed_candidates["rejected"]:
        st.warning("No candidates have been shortlisted or rejected yet!")
        return
    
    # Display job information
    job_data = st.session_state.job_data
    st.subheader(f"Job: {job_data.get('job_title', 'Unknown')}")
    
    # Initialize interview scheduler agent
    scheduler_agent = InterviewSchedulerAgent(api_key=st.session_state.api_key)
    
    # Generate emails
    if st.button("Generate Emails"):
        with st.spinner("Generating emails..."):
            result = scheduler_agent.process_candidates(job_data, st.session_state.processed_candidates)
            
            # Update database
            db = st.session_state.db
            for candidate in result["shortlisted"]:
                db.update_evaluation(
                    eval_id=candidate["eval_id"],
                    interview_scheduled=True,
                    interview_details=candidate.get("invitation", {})
                )
            
            st.success(f"Generated emails for {len(result['shortlisted'])} shortlisted candidates and {len(result['rejected'])} rejected candidates")
            
            # Store results back in session state
            st.session_state.processed_candidates = result
    
    # Display interview invitations
    if st.session_state.processed_candidates["shortlisted"]:
        st.subheader("Interview Invitations")
        
        for i, candidate in enumerate(st.session_state.processed_candidates["shortlisted"]):
            if "invitation" in candidate:
                with st.expander(f"{i+1}. {candidate['data'].get('name', 'Unknown')} - {candidate['filename']}"):
                    invitation = candidate["invitation"]
                    
                    st.write(f"**To:** {candidate['data'].get('email', 'candidate@example.com')}")
                    st.write(f"**Subject:** {invitation['email']['subject']}")
                    st.write("**Body:**")
                    st.text_area(f"Email body {i+1}", invitation['email']['body'], height=200, key=f"invite_{i}")
                    
                    st.write(f"**Interview Format:** {invitation.get('interview_format', 'Video Interview')}")
                    st.write(f"**Proposed Dates:** {', '.join(invitation.get('proposed_dates', []))}")
                    st.write(f"**Proposed Times:** {', '.join(invitation.get('proposed_times', []))}")
    
    # Display rejection emails
    if st.session_state.processed_candidates["rejected"]:
        st.subheader("Rejection Emails")
        
        for i, candidate in enumerate(st.session_state.processed_candidates["rejected"]):
            if "rejection" in candidate:
                with st.expander(f"{i+1}. {candidate['data'].get('name', 'Unknown')} - {candidate['filename']}"):
                    rejection = candidate["rejection"]
                    
                    st.write(f"**To:** {candidate['data'].get('email', 'candidate@example.com')}")
                    st.write(f"**Subject:** {rejection['email']['subject']}")
                    st.write("**Body:**")
                    st.text_area(f"Email body {i+1}", rejection['email']['body'], height=200, key=f"reject_{i}")

if __name__ == "__main__":
    main()
