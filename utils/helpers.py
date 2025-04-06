import os
import re
import pandas as pd
from datetime import datetime, timedelta
import random

def sanitize_filename(filename):
    """Sanitize a filename by removing invalid characters"""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def generate_interview_dates(num_dates=3, start_days=3):
    """Generate potential interview dates starting from start_days from now"""
    dates = []
    start_date = datetime.now() + timedelta(days=start_days)
    
    # Generate weekday dates (Monday to Friday)
    current_date = start_date
    while len(dates) < num_dates:
        if current_date.weekday() < 5:  # Monday to Friday
            dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    return dates

def generate_interview_times(num_times=3):
    """Generate potential interview time slots"""
    times = ["10:00 AM", "11:30 AM", "2:00 PM", "3:30 PM", "5:00 PM"]
    return random.sample(times, min(num_times, len(times)))

def generate_rejection_email(candidate_name):
    """Generate a rejection email template"""
    subject = "Application Status Update"
    
    body = f"""Dear {candidate_name},

Thank you for your interest in our company and for taking the time to apply for the position.

After careful consideration of your application, we regret to inform you that we have decided not to move forward with your candidacy at this time. We received many qualified applications, and the selection process was highly competitive.

We appreciate your interest in our organization and encourage you to apply for future positions that match your qualifications and experience.

We wish you the best in your job search and future professional endeavors.

Best regards,
Recruitment Team
"""
    return {"subject": subject, "body": body}

def generate_interview_email(candidate_name, job_title, dates, times, interview_format="video"):
    """Generate an interview invitation email template"""
    date_options = ", ".join(dates)
    time_options = ", ".join(times)
    
    subject = f"Interview Invitation: {job_title} Position"
    
    body = f"""Dear {candidate_name},

We are pleased to inform you that your application for the {job_title} position has been shortlisted. We would like to invite you for an interview to further discuss your qualifications and experience.

Interview Details:
- Format: {interview_format.capitalize()} Interview
- Potential Dates: {date_options}
- Potential Times: {time_options}

Please reply to this email with your preferred date and time from the options above, and we will confirm the details.

If you have any questions or need to reschedule, please don't hesitate to contact us.

We look forward to speaking with you!

Best regards,
Recruitment Team
"""
    return {"subject": subject, "body": body}

def mask_pii(text):
    """Mask personally identifiable information in text"""
    # Mask email addresses
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL REDACTED]', text)
    
    # Mask phone numbers (various formats)
    text = re.sub(r'\b(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', '[PHONE REDACTED]', text)
    
    # Mask addresses (simplified)
    text = re.sub(r'\b\d+\s+[A-Za-z\s,]+(?:Avenue|Lane|Road|Boulevard|Drive|Street|Ave|Dr|Rd|Blvd|Ln|St)\.?\b', 
                 '[ADDRESS REDACTED]', text)
    
    return text

def calculate_similarity_threshold(job_title):
    """Calculate similarity threshold based on job title/category"""
    # Default threshold
    threshold = 8.0
    
    # Adjust threshold based on job category
    job_title_lower = job_title.lower()
    
    if any(tech in job_title_lower for tech in ['software', 'developer', 'engineer', 'programmer']):
        threshold = 7.5  # Technical roles might have more variance in descriptions
    elif any(exec_role in job_title_lower for exec_role in ['manager', 'director', 'executive', 'lead']):
        threshold = 8.5  # Management roles might need higher precision
    
    return threshold
