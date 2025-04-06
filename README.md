# AI Recruitment Assistant

An agentic system using LangChain and its tools for enhancing job screening with AI and data science.

## Project Overview

This project implements a multi-agent AI system to automate the recruitment process by:
- Summarizing job descriptions
- Extracting information from resumes
- Matching candidates to job descriptions
- Shortlisting candidates
- Generating interview invitation emails

## Agent Architecture

1. **JD Summariser Agent**: Extracts key requirements from job descriptions and formulates relevant questions
2. **Resume Extractor Agent**: Parses PDFs to extract structured information in JSON format
3. **Similarity Score Calculator**: Computes match between resume and JD (score out of 10)
4. **Recruiting Agent**: Evaluates candidate relevance based on JD questions (score out of 10)
5. **Shortlisting Agent**: Calculates final score and shortlists candidates
6. **Interview Scheduler**: Generates personalized emails with interview details

## Technical Details

- **Frontend**: Streamlit
- **Similarity Search**: DistilBERT
- **LLM**: Gemma from Chatgroq
- **Database**: SQLite for long-term memory
- **PDF Processing**: PyPDF

## Setup Instructions

1. Clone the repository
2. Run the setup script to create a virtual environment and install dependencies:
   ```
   cd /Users/adityakapole/Downloads/Accenture
   chmod +x setup.sh
   ./setup.sh
   ```
3. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```
4. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## Usage

1. **Upload JD**: Upload or select a job description to process
2. **Process CVs**: Upload or select resumes to process
3. **View Results**: View candidate scores and details
4. **Shortlist Candidates**: Automatically shortlist candidates based on scores
5. **Generate Emails**: Generate interview invitation emails for shortlisted candidates and rejection emails for others

## Data Privacy

The system includes privacy protection features:
- PII masking in resume processing
- Secure database storage
- Early filtering to reduce unnecessary processing

## Requirements

- Python 3.7+
- Streamlit
- LangChain
- Transformers
- PyPDF
- SQLAlchemy
- Sentence-Transformers
