# frontend/app.py

import streamlit as st
import requests
import subprocess
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# --------------------------------------------------
# Session state
# --------------------------------------------------
if "dataset_context" not in st.session_state:
    st.session_state.dataset_context = None

if "df" not in st.session_state:
    st.session_state.df = None

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="LLM Powered Data Analyst",
    page_icon="📊",
    layout="centered"
)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.title("📊 LLM Powered Data Analyst")
st.write(
    "Upload a CSV or Excel file to get automated analysis, charts, "
    "and AI-powered explanations. Fully offline."
)

BACKEND_URL = "http://127.0.0.1:8000"

# --------------------------------------------------
# Ollama helper
# --------------------------------------------------
def ask_ollama_local(prompt: str) -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", "gemma:2b"],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=120
        )

        if result.returncode != 0:
            return f"Ollama error: {result.stderr}"

        return result.stdout.strip()

    except Exception as e:
        return f"Error: {str(e)}"

# --------------------------------------------------
# PDF Generator
# --------------------------------------------------
def generate_pdf_report(summary_text: str):
    buffer = BytesIO()
    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(buffer)
    elements = []

    elements.append(Paragraph("LLM Powered Data Analysis Report", styles["Title"]))
    elements.append(Paragraph("<br/>", styles["BodyText"]))

    for line in summary_text.split("\n"):
        if line.strip():
            elements.append(Paragraph(line.replace("**", ""), styles["BodyText"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# --------------------------------------------------
# File uploader
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx", "xls"]
)

# --------------------------------------------------
# Analyze section
# --------------------------------------------------
if uploaded_file:
    st.success(f"File selected: {uploaded_file.name}")

    # Load dataframe locally
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.session_state.df = df

    if st.button("🚀 Analyze with AI"):
        with st.spinner("Analyzing your data..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            eda_response = requests.post(f"{BACKEND_URL}/analyze", files=files)
            llm_response = requests.post(f"{BACKEND_URL}/analyze-with-llm", files=files)

        if eda_response.status_code == 200:
            eda = eda_response.json()

            st.subheader("📌 Dataset Overview")
            st.write(f"**Rows:** {eda['shape']['rows']}")
            st.write(f"**Columns:** {eda['shape']['columns']}")

            st.subheader("🧩 Missing Values")
            st.json(eda["missing_values"])

            st.subheader("🧾 Data Types")
            st.json(eda["data_types"])

        if llm_response.status_code == 200:
            llm_data = llm_response.json()
            st.session_state.dataset_context = llm_data["llm_explanation"]

            st.subheader("🤖 AI Explanation")
            st.write(llm_data["llm_explanation"])

            pdf = generate_pdf_report(llm_data["llm_explanation"])
            st.download_button(
                "📄 Download PDF Report",
                data=pdf,
                file_name="data_analysis_report.pdf",
                mime="application/pdf"
            )

# --------------------------------------------------
# Visualizations
# --------------------------------------------------
if st.session_state.df is not None:
    st.divider()
    st.subheader("📊 Visualizations")

    df = st.session_state.df
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

    if numeric_cols:
        selected_col = st.selectbox("Select a numeric column", numeric_cols)

        # Bar Chart
        st.markdown("### 📊 Bar Chart")
        st.bar_chart(df[selected_col])

        # Line Chart
        st.markdown("### 📈 Line Chart")
        st.line_chart(df[selected_col])

        # Pie Chart
        st.markdown("### 🥧 Pie Chart")
        pie_data = df[selected_col].value_counts().head(5)
        st.pyplot(
            pie_data.plot.pie(
                autopct="%1.1f%%",
                ylabel="",
                title=f"Distribution of {selected_col}"
            ).figure
        )

        # --------------------------------------------------
        # CORRELATION HEATMAP (NEW)
        # --------------------------------------------------
        if len(numeric_cols) > 1:
            st.markdown("### 🔥 Correlation Heatmap")
            corr = df[numeric_cols].corr()
            st.dataframe(corr.style.background_gradient(cmap="coolwarm"))

    else:
        st.info("No numeric columns found.")

# --------------------------------------------------
# Question-aware charts + AI answers
# --------------------------------------------------
st.divider()
st.subheader("💬 Ask a Question About Your Data")

question = st.text_input(
    "Ask anything (e.g., 'Show trends', 'Compare prices', 'Distribution of quantity')"
)

if question and st.session_state.df is not None:
    q = question.lower()
    df = st.session_state.df
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

    # Chart intelligence
    if "trend" in q or "over time" in q:
        st.markdown("### 📈 Trend Analysis")
        st.line_chart(df[numeric_cols])

    elif "distribution" in q:
        st.markdown("### 🥧 Distribution")
        col = numeric_cols[0]
        pie_data = df[col].value_counts()
        st.pyplot(pie_data.plot.pie(autopct="%1.1f%%").figure)

    elif "compare" in q:
        st.markdown("### 📊 Comparison")
        st.bar_chart(df[numeric_cols])

    # AI explanation
    with st.spinner("Thinking..."):
        prompt = f"""
You are a data analyst.

Dataset context:
{st.session_state.dataset_context}

User question:
{question}

Explain clearly in simple English.
Focus on insights, not raw numbers.
"""
        answer = ask_ollama_local(prompt)

    st.success("Answer generated successfully")
    st.write(answer)

elif question:
    st.warning("Please analyze a dataset first.")

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
st.caption(
    "Built with FastAPI, Pandas, Streamlit, and a local LLM (Ollama). "
    "Fully offline. No paid APIs."
)
