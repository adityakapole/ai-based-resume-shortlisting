import streamlit as st
import subprocess
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Run the Streamlit app
if __name__ == "__main__":
    subprocess.run(["streamlit", "run", "app.py"])
