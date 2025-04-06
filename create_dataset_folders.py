import os

# Create Dataset directory structure
os.makedirs("Dataset/CVs1", exist_ok=True)

# Create a sample job description CSV
with open("Dataset/job_description.csv", "w", encoding="utf-8") as f:
    f.write("Job Title,Job Description\n")
    f.write("Software Engineer,\"We are looking for a Software Engineer to join our team. Requirements include: 3+ years of experience in Python, knowledge of web frameworks like Django or Flask, and database experience.\"\n")
    f.write("Data Scientist,\"Seeking a Data Scientist with strong analytical skills. Must have experience with Python, R, machine learning algorithms, and data visualization tools.\"\n")

print("Dataset directory structure created successfully!")
