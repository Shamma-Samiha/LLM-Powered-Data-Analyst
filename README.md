# LLM Powered Data Analyst

An AI-powered backend application that allows users to upload datasets (CSV/Excel),
automatically analyzes the data, and generates human-readable insights using a local LLM.

## Features
- Upload CSV or Excel files
- Automatic EDA (missing values, data types, statistics)
- LLM-generated explanations using Ollama
- FastAPI backend
- Fully free & runs locally

## Website View

![Website View 1](assets/website_view_1.png)
![Website View 2.0](assets/website_view_2.0.png)
![Website View 2](assets/website_view_2.png)
![Website View 2.1](assets/website_view_2.1.png)
![Website View 2.2](assets/website_view_2.2.png)
![Website View 3](assets/website_view_3.png)
![Website View 4](assets/website_view_4.png)
![Website View 4.1](assets/website_view_4.1.png)
![Website View 5.1](assets/website_view_5.1.png)
![Website View 5.2](assets/website_view_5.2.png)
![Website View 5.3](assets/website_view_5.3.png)

## Tech Stack
- Python
- FastAPI
- Pandas
- Ollama (Gemma 2B)
- Uvicorn

## How to Run
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
