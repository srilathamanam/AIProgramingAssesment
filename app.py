import streamlit as st
import requests
import subprocess
import json
import time

# --- Judge0 Config ---
JUDGE0_API_URL = "https://judge0-ce.p.rapidapi.com/submissions"
RAPID_API_KEY = "e4cfe2c982msh0c0641fd6f48054p19a36ajsn8f073aa0610e"  # Replace with your own key if needed

HEADERS = {
    "x-rapidapi-host": "judge0-ce.p.rapidapi.com",
    "x-rapidapi-key": RAPID_API_KEY,
    "content-type": "application/json"
}

LANGUAGE_ID = {
    "python": 71,
    "cpp": 54,
    "java": 62
}

# --- Streamlit UI ---
st.title("AI Code Evaluator with Judge0 + Ollama")

problem_statement = st.text_area("Enter Your Problem Statement", height=150)
language = st.selectbox("Choose Language", ["python", "cpp", "java"])
user_code = st.text_area(" Paste Your Code Here", height=250)

# Test cases (can be extended or modified)
test_cases = [
    ("500", "100"),
    ("800", "160"),
    ("1200", "264")
]

# --- Judge0 Submission ---
def run_judge0(code, lang, input_data):
    payload = {
        "language_id": LANGUAGE_ID[lang],
        "source_code": code,
        "stdin": input_data,
        "redirect_stderr_to_stdout": True
    }

    response = requests.post(
        JUDGE0_API_URL + "?base64_encoded=false&wait=true",
        headers=HEADERS,
        json=payload
    )
    return response.json()

# --- Ollama AI Feedback ---
def get_ai_feedback(problem, code):
    prompt = f"""
### Problem Statement:
{problem}

### User's Code:
{code}

### Feedback:
Give suggestions for improving logic, readability, and best practices.
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "codellama"],
            input=prompt,
            text=True,
            capture_output=True,
            encoding="utf-8",  # Fix for UnicodeDecodeError
            timeout=360
        )
        return result.stdout
    except Exception as e:
        return f"Error from Ollama: {e}"

# --- Submission Action ---
if st.button(" Submit & Evaluate"):
    if not problem_statement.strip() or not user_code.strip():
        st.warning("Please fill in both problem statement and code.")
    else:
        st.info("Running test cases...")

        passed = 0
        total = len(test_cases)

        for i, (input_data, expected_output) in enumerate(test_cases):
            result = run_judge0(user_code, language, input_data)
            output = result.get("stdout", "").strip()

            if output == expected_output:
                st.success(f"Test Case {i+1}: Passed")
                passed += 1
            else:
                st.error(f"Test Case {i+1}: Failed\nInput: {input_data}\nExpected: {expected_output}, Got: {output}")

        st.subheader(f"Final Score: {passed}/{total}")

        st.info("Generating AI Feedback...")
        feedback = get_ai_feedback(problem_statement, user_code)
        st.text_area("AI Feedback", value=feedback.strip(), height=300)
