# backend/main.py

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import pandas as pd
import subprocess
import json

app = FastAPI(title="LLM-Powered Data Analyst (Backend)")

# --------------------------------------------------
# Temporary in-memory storage for last analysis
# --------------------------------------------------
LAST_ANALYSIS = {}

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

    analysis = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_values": df.isnull().sum().to_dict(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "numeric_summary": df.describe().round(2).to_dict()
    }

    return {
        "file_name": filename,
        "shape": {
            "rows": df.shape[0],
            "columns": df.shape[1]
        },
        **analysis
    }


# --------------------------------------------------
# 4) Call Ollama via CLI (Windows-safe)
# --------------------------------------------------
def ask_ollama(prompt: str) -> str:
    """
    Calls Ollama using CLI.
    Works on Windows without --prompt flag.
    """

    try:
        result = subprocess.run(
            ["ollama", "run", "gemma:2b"],
            input=prompt,              # 👈 prompt sent via stdin
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            return f"Ollama error: {result.stderr}"

        return result.stdout.strip()

    except FileNotFoundError:
        return "Ollama is not installed or not available in PATH."

    except subprocess.TimeoutExpired:
        return "Ollama took too long to respond. Try again."

    except Exception as e:
        return f"Unexpected error: {str(e)}"


# --------------------------------------------------
# 5) Analyze data + explain with LLM
# --------------------------------------------------
@app.post("/analyze-with-llm")
def analyze_with_llm(file: UploadFile = File(...)):
    global LAST_ANALYSIS

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
        "numeric_summary": df.describe().round(2).to_dict()
    }

    # Store for question answering
    LAST_ANALYSIS = analysis

    prompt = f"""
Explain this dataset in very simple English.
Avoid technical words.
Mention any data quality issues and patterns.

Rows: {analysis['rows']}
Columns: {analysis['columns']}
Column names: {analysis['column_names']}
Missing values: {analysis['missing_values']}
"""

    explanation = ask_ollama(prompt)

    return {
        "file_name": filename,
        "llm_explanation": explanation
    }


# --------------------------------------------------
# 6) Ask questions about the data
# --------------------------------------------------
class QuestionRequest(BaseModel):
    question: str


@app.post("/ask-question")
def ask_question(request: QuestionRequest):
    if not LAST_ANALYSIS:
        return {
            "answer": "No dataset has been analyzed yet. Please upload and analyze a file first."
        }

    prompt = f"""
You are a junior data analyst explaining data to a non-technical manager.

Rules:
- Do NOT show tables
- Do NOT repeat raw data
- Explain in plain English
- Use bullet points for clarity
- Mention what the data is about
- Mention any patterns or insights
- Highlight data quality issues
- Keep it concise (4–6 bullet points max)

Explain:
1. What this dataset is about
2. Answer the question: {request.question}
3. Key patterns or trends
4. Any data quality issues
5. One practical takeaway

Dataset information:
{json.dumps(LAST_ANALYSIS, indent=2)}

Now write the summary:
"""

    answer = ask_ollama(prompt)

    return {
        "llm_explanation": answer
    }
