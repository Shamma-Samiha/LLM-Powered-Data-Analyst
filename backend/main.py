# backend/main.py

from fastapi import FastAPI, UploadFile, File
import pandas as pd
import subprocess
import json
import tempfile
import os

app = FastAPI(title="LLM-Powered Data Analyst (Backend)")

# --------------------------------------------------
# 1) Health check
# --------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}


# --------------------------------------------------
# 2) Upload file and basic info
# --------------------------------------------------
@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    filename = file.filename

    if filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(file.file)
    else:
        return {"error": "Only CSV or Excel files are allowed"}

    return {
        "file_name": filename,
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns)
    }


# --------------------------------------------------
# 3) Automatic data analysis (EDA)
# --------------------------------------------------
@app.post("/analyze")
def analyze_file(file: UploadFile = File(...)):
    filename = file.filename

    if filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(file.file)
    else:
        return {"error": "Only CSV or Excel files are allowed"}

    return {
        "file_name": filename,
        "shape": {
            "rows": df.shape[0],
            "columns": df.shape[1]
        },
        "missing_values": df.isnull().sum().to_dict(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "numeric_summary": df.describe().to_dict()
    }


# --------------------------------------------------
# 4) Call Ollama via CLI (WINDOWS SAFE)
# --------------------------------------------------
def ask_ollama(prompt: str) -> str:
    """
    Calls Ollama using CLI instead of HTTP.
    This works reliably on Windows.
    """

    try:
        result = subprocess.run(
            ["ollama", "run", "gemma:2b"],
            input=prompt,
            capture_output=True,
            text=True,
        
            timeout=120
        )

        if result.returncode != 0:
            return f"Ollama error: {result.stderr}"

        return result.stdout.strip()

    except FileNotFoundError:
        return "Ollama is not installed or not in PATH."

    except subprocess.TimeoutExpired:
        return "Ollama took too long to respond."

    except Exception as e:
        return f"Unexpected error: {str(e)}"


# ----------------------------------uvicorn backend.main:app --reload----------------
# 5) Analyze data + explain with LLM
# --------------------------------------------------
@app.post("/analyze-with-llm")
def analyze_with_llm(file: UploadFile = File(...)):
    filename = file.filename

    if filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(file.file)
    else:
        return {"error": "Only CSV or Excel files are allowed"}

    analysis = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "numeric_summary": df.describe().to_dict()
    }

    prompt = f"""
You are a data analyst.
Explain this dataset in simple English.
Avoid technical words.
Mention problems and patterns.

Dataset analysis:
{json.dumps(analysis, indent=2)}
"""

    explanation = ask_ollama(prompt)

    return {
        "file_name": filename,
        "llm_explanation": explanation
    }
