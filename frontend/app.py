# frontend/app.py

import streamlit as st
import requests
import subprocess
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

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
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# --------------------------------------------------
# Custom CSS for dark theme (ash, gray, green)
# --------------------------------------------------
st.markdown("""
    <style>
    /* Main background - dark theme with ash, gray, green */
    .stApp {
        background: linear-gradient(135deg, #2d3436 0%, #3d4a52 25%, #4a5d6b 50%, #2d4a2d 75%, #3d5a3d 100%);
        background-attachment: fixed;
    }
    
    /* Main content container - full width with minimal padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Remove sidebars completely */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Make main content area full width */
    .main {
        width: 100% !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    
    /* Remove any default margins that create empty spaces */
    .stApp > div {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    
    /* All text should be visible - white/light colors */
    .main {
        color: #e0e0e0;
    }
    
    p, div, span, label {
        color: #e0e0e0 !important;
    }
    
    /* Top bar for title and description - looks like empty box */
    .top-bar {
        background: rgba(45, 52, 54, 0.95) !important;
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 2rem 2.5rem !important;
        margin: 0 auto 2rem auto !important;
        max-width: 95% !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(76, 175, 80, 0.2);
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 120px;
    }
    
    /* Ensure title is visible inside top bar */
    .top-bar h1 {
        margin: 0 0 1rem 0 !important;
        padding: 0 !important;
    }
    
    /* Ensure description text is properly styled */
    .top-bar p {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Header container for description - no bar, just text */
    .header-container {
        background: transparent;
        padding: 1rem 0;
        margin: 0 auto 2rem auto;
        max-width: 95%;
    }
    
    /* Card containers - dark theme */
    .card {
        background: rgba(45, 52, 54, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem 1.5rem 1rem 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(76, 175, 80, 0.2);
    }
    
    /* Card with reduced padding for question section */
    .card-question {
        background: rgba(45, 52, 54, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem 1.25rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(76, 175, 80, 0.2);
    }
    
    /* Button styling - green accent */
    .stButton > button {
        background: linear-gradient(135deg, #4a7c59 0%, #2d5a3d 100%);
        color: #ffffff !important;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a8c69 0%, #3d6a4d 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.6);
        color: #ffffff !important;
    }
    
    /* File uploader styling */
    .uploadedFile {
        background: rgba(61, 74, 82, 0.8);
        border-radius: 10px;
        padding: 1rem;
        color: #e0e0e0;
    }
    
    /* File uploader area */
    [data-testid="stFileUploader"] {
        background: rgba(45, 52, 54, 0.8);
        border: 2px dashed rgba(76, 175, 80, 0.5);
        border-radius: 10px;
    }
    
    /* Success message */
    .stSuccess {
        background: rgba(76, 175, 80, 0.2);
        border-left: 4px solid #4CAF50;
        border-radius: 5px;
        color: #e0e0e0 !important;
    }
    
    /* Info boxes */
    .stInfo {
        background: rgba(76, 175, 80, 0.15);
        border-left: 4px solid #4CAF50;
        border-radius: 5px;
        color: #e0e0e0 !important;
    }
    
    /* Warning boxes */
    .stWarning {
        background: rgba(255, 193, 7, 0.15);
        border-left: 4px solid #ffc107;
        border-radius: 5px;
        color: #e0e0e0 !important;
    }
    
    /* Subheader styling - light colors for visibility */
    h1, h2, h3, h4, h5, h6 {
        color: #e0e0e0 !important;
        font-weight: 700;
    }
    
    /* Text input - dark theme */
    .stTextInput > div > div > input {
        background: rgba(61, 74, 82, 0.8) !important;
        color: #e0e0e0 !important;
        border-radius: 8px;
        border: 1px solid rgba(76, 175, 80, 0.3);
    }
    
    .stTextInput > div > div > input:focus {
        border: 1px solid rgba(76, 175, 80, 0.6);
    }
    
    /* Selectbox - dark theme */
    .stSelectbox > div > div > select {
        background: rgba(61, 74, 82, 0.8) !important;
        color: #e0e0e0 !important;
        border-radius: 8px;
        border: 1px solid rgba(76, 175, 80, 0.3);
    }
    
    /* Metrics - dark theme */
    [data-testid="stMetricValue"] {
        color: #4CAF50 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #b0b0b0 !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        background: rgba(45, 52, 54, 0.9) !important;
        color: #e0e0e0 !important;
    }
    
    /* JSON display */
    .stJson {
        background: rgba(45, 52, 54, 0.9) !important;
        color: #e0e0e0 !important;
    }
    
    /* Tabs - dark theme */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(45, 52, 54, 0.8);
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #b0b0b0 !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #4CAF50 !important;
        background: rgba(76, 175, 80, 0.2);
    }
    
    /* Charts background */
    [data-testid="stChart"] {
        background: rgba(45, 52, 54, 0.9);
    }
    
    /* Divider */
    hr {
        border-color: rgba(76, 175, 80, 0.3);
    }
    
    /* Caption */
    .stCaption {
        color: #b0b0b0 !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #4a7c59 0%, #2d5a3d 100%);
        color: #ffffff !important;
        border: none;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #5a8c69 0%, #3d6a4d 100%);
        color: #ffffff !important;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove empty sidebars and ensure full width */
    .stApp > div:first-child {
        width: 100% !important;
    }
    
    /* Remove any default padding that creates empty spaces */
    .element-container {
        max-width: 100% !important;
    }
    
    /* Ensure cards use available width */
    .card {
        max-width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# Header Section - Title and Description in Top Bar
# --------------------------------------------------
# Top bar with title and description - everything in one div
st.markdown("""
<div class="top-bar">
    <div style="width: 100%; text-align: center;">
        <h1 style="color: #e0e0e0; font-size: 2.5rem; 
                    background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-weight: 800; margin: 0 0 1rem 0; text-align: center; width: 100%;">
            LLM Powered Data Analyst
        </h1>
        <p style="color: #b0b0b0; font-size: 1.1rem; text-align: center; line-height: 1.6; margin: 0;">
            Upload a CSV or Excel file to get automated analysis, charts, 
            and AI-powered explanations. Fully offline.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

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
# File Upload Section
# --------------------------------------------------
st.markdown("""
<div class="card">
    <h2 style="color: #e0e0e0; font-size: 1.8rem; font-weight: 700; margin: 0 0 1rem 0; padding: 0;">
        📁 Upload Your Data File
    </h2>
    <p style="color: #b0b0b0; font-size: 1rem; margin: 0 0 1.5rem 0;">
        Select a CSV or Excel file to begin your analysis. 
        Maximum file size: 200MB
    </p>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx", "xls"],
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# Analyze section
# --------------------------------------------------
if uploaded_file:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.success(f"✅ File selected: **{uploaded_file.name}**")
    
    # File info columns
    col1, col2, col3 = st.columns(3)
    
    # Load dataframe locally
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.session_state.df = df
    
    with col1:
        st.metric("📊 Rows", f"{len(df):,}")
    with col2:
        st.metric("📋 Columns", len(df.columns))
    with col3:
        file_size = len(uploaded_file.getvalue()) / 1024
        st.metric("💾 Size", f"{file_size:.1f} KB")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_btn = st.button("🚀 Analyze with AI", use_container_width=True, type="primary")
    
    if analyze_btn:
        with st.spinner("🔍 Analyzing your data with AI... This may take a moment."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            eda_response = requests.post(f"{BACKEND_URL}/analyze", files=files)
            llm_response = requests.post(f"{BACKEND_URL}/analyze-with-llm", files=files)

        if eda_response.status_code == 200:
            eda = eda_response.json()
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📌 Dataset Overview")
            
            overview_col1, overview_col2 = st.columns(2)
            with overview_col1:
                st.metric("Total Rows", f"{eda['shape']['rows']:,}")
            with overview_col2:
                st.metric("Total Columns", eda['shape']['columns'])
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Missing values and data types in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("🧩 Missing Values")
                missing_df = pd.DataFrame(list(eda["missing_values"].items()), 
                                         columns=["Column", "Missing Count"])
                st.dataframe(missing_df, use_container_width=True, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("🧾 Data Types")
                types_df = pd.DataFrame(list(eda["data_types"].items()), 
                                       columns=["Column", "Data Type"])
                st.dataframe(types_df, use_container_width=True, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)

        if llm_response.status_code == 200:
            llm_data = llm_response.json()
            st.session_state.dataset_context = llm_data["llm_explanation"]

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("🤖 AI-Powered Explanation")
            st.markdown(f"""
            <div style="background: rgba(76, 175, 80, 0.15); padding: 1.5rem; 
                        border-radius: 10px; border-left: 4px solid #4CAF50;">
                <p style="color: #e0e0e0; line-height: 1.8; font-size: 1.05rem;">
                    {llm_data["llm_explanation"].replace(chr(10), '<br>')}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            pdf = generate_pdf_report(llm_data["llm_explanation"])
            st.download_button(
                "📄 Download PDF Report",
                data=pdf,
                file_name="data_analysis_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# Visualizations
# --------------------------------------------------
if st.session_state.df is not None:
    st.markdown("---")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Data Visualizations")
    st.markdown("""
    <p style="color: #b0b0b0; margin-bottom: 1rem;">
        Explore your data through interactive charts and visualizations
    </p>
    """, unsafe_allow_html=True)

    df = st.session_state.df
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

    if numeric_cols:
        selected_col = st.selectbox("📈 Select a numeric column to visualize", numeric_cols)
        
        # Charts in tabs for better organization
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Bar Chart", "📈 Line Chart", "🥧 Pie Chart", "🔥 Correlation"])

        with tab1:
            st.markdown("### Bar Chart Visualization")
            st.bar_chart(df[selected_col], height=400)

        with tab2:
            st.markdown("### Line Chart Visualization")
            st.line_chart(df[selected_col], height=400)

        with tab3:
            st.markdown("### Distribution Pie Chart")
            pie_data = df[selected_col].value_counts().head(10)
            fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2d3436')
            ax.set_facecolor('#2d3436')
            pie_data.plot.pie(
                autopct="%1.1f%%",
                ylabel="",
                title=f"Distribution of {selected_col}",
                ax=ax,
                colors=plt.cm.Set3.colors,
                textprops={'color': '#e0e0e0'}
            )
            ax.title.set_color('#e0e0e0')
            st.pyplot(fig)

        with tab4:
            if len(numeric_cols) > 1:
                st.markdown("### Correlation Heatmap")
                corr = df[numeric_cols].corr()
                st.dataframe(corr.style.background_gradient(cmap="coolwarm", axis=None), 
                           use_container_width=True)
            else:
                st.info("Need at least 2 numeric columns for correlation analysis.")
    else:
        st.info("ℹ️ No numeric columns found in the dataset.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# Question-aware charts + AI answers
# --------------------------------------------------
st.markdown("---")
st.markdown("""
<div class="card-question">
    <h2 style="color: #e0e0e0; font-size: 1.5rem; font-weight: 700; margin: 0 0 0.75rem 0; padding: 0;">
        💬 Ask a Question About Your Data
    </h2>
    <p style="color: #b0b0b0; margin: 0 0 1rem 0; font-size: 0.95rem;">
        Get AI-powered insights by asking questions about your dataset
    </p>
""", unsafe_allow_html=True)

question = st.text_input(
    "💭 Ask anything (e.g., 'Show trends', 'Compare prices', 'Distribution of quantity')",
    placeholder="Type your question here...",
    label_visibility="collapsed"
)

if question and st.session_state.df is not None:
    q = question.lower()
    df = st.session_state.df
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

    # Chart intelligence
    if numeric_cols:
        if "trend" in q or "over time" in q:
            st.markdown("### 📈 Trend Analysis")
            st.line_chart(df[numeric_cols], height=400)

        elif "distribution" in q:
            st.markdown("### 🥧 Distribution Analysis")
            col = numeric_cols[0]
            pie_data = df[col].value_counts().head(10)
            fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2d3436')
            ax.set_facecolor('#2d3436')
            pie_data.plot.pie(autopct="%1.1f%%", ax=ax, colors=plt.cm.Set3.colors, 
                            textprops={'color': '#e0e0e0'})
            ax.title.set_color('#e0e0e0')
            st.pyplot(fig)

        elif "compare" in q:
            st.markdown("### 📊 Comparison Analysis")
            st.bar_chart(df[numeric_cols], height=400)

    # AI explanation
    with st.spinner("🤔 AI is thinking about your question..."):
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

    st.markdown("---")
    st.markdown("### ✨ AI Answer")
    st.markdown(f"""
    <div style="background: rgba(76, 175, 80, 0.15); padding: 1.5rem; 
                border-radius: 10px; border-left: 4px solid #4CAF50;">
        <p style="color: #e0e0e0; line-height: 1.8; font-size: 1.05rem;">
            {answer.replace(chr(10), '<br>')}
        </p>
    </div>
    """, unsafe_allow_html=True)

elif question:
    st.warning("⚠️ Please upload and analyze a dataset first.")

st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #b0b0b0;">
    <p style="font-size: 0.9rem; margin: 0;">
        Built with ❤️ using FastAPI, Pandas, Streamlit, and a local LLM (Ollama). 
        Fully offline. No paid APIs.
    </p>
</div>
""", unsafe_allow_html=True)
