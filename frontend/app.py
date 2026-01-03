# frontend/app.py

import streamlit as st
import requests
import subprocess
import pandas as pd
import numpy as np
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

if "selected_chart_type" not in st.session_state:
    st.session_state.selected_chart_type = "📈 Line Chart"

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
    
    /* Luminous chart buttons */
    .chart-button {
        background: rgba(45, 52, 54, 0.8) !important;
        border: 2px solid rgba(76, 175, 80, 0.3) !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        color: #b0b0b0 !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
    }
    
    .chart-button:hover {
        background: rgba(76, 175, 80, 0.2) !important;
        border-color: rgba(76, 175, 80, 0.6) !important;
        color: #e0e0e0 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.5) !important;
    }
    
    .chart-button.active {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.3) 0%, rgba(76, 175, 80, 0.15) 100%) !important;
        border: 2px solid rgba(76, 175, 80, 0.8) !important;
        color: #4CAF50 !important;
        box-shadow: 0 0 20px rgba(76, 175, 80, 0.6), 0 4px 15px rgba(76, 175, 80, 0.4) !important;
        text-shadow: 0 0 10px rgba(76, 175, 80, 0.8) !important;
    }
    
    .chart-buttons-container {
        display: flex;
        gap: 0.75rem;
        flex-wrap: nowrap;
        margin: 1.5rem 0;
        padding: 1rem;
        background: rgba(45, 52, 54, 0.5);
        border-radius: 12px;
        border: 1px solid rgba(76, 175, 80, 0.2);
    }
    
    .chart-buttons-container [data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0 !important;
        width: 0 !important;
    }
    
    .chart-buttons-container [data-testid="column"] > div {
        width: 100% !important;
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
            
            st.markdown("""
            <div class="card">
                <h2 style="color: #e0e0e0; font-size: 1.8rem; font-weight: 700; margin: 0 0 1rem 0; padding: 0;">
                    📌 Dataset Overview
                </h2>
            """, unsafe_allow_html=True)
            
            overview_col1, overview_col2 = st.columns(2)
            with overview_col1:
                st.metric("Total Rows", f"{eda['shape']['rows']:,}")
            with overview_col2:
                st.metric("Total Columns", eda['shape']['columns'])
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Missing values and data types in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="card">
                    <h2 style="color: #e0e0e0; font-size: 1.8rem; font-weight: 700; margin: 0 0 1rem 0; padding: 0;">
                        🧩 Missing Values
                    </h2>
                """, unsafe_allow_html=True)
                missing_df = pd.DataFrame(list(eda["missing_values"].items()), 
                                         columns=["Column", "Missing Count"])
                st.dataframe(missing_df, use_container_width=True, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="card">
                    <h2 style="color: #e0e0e0; font-size: 1.8rem; font-weight: 700; margin: 0 0 1rem 0; padding: 0;">
                        🧾 Data Types
                    </h2>
                """, unsafe_allow_html=True)
                types_df = pd.DataFrame(list(eda["data_types"].items()), 
                                       columns=["Column", "Data Type"])
                st.dataframe(types_df, use_container_width=True, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)

        if llm_response.status_code == 200:
            llm_data = llm_response.json()
            st.session_state.dataset_context = llm_data["llm_explanation"]

            st.markdown(f"""
            <div class="card">
                <h2 style="color: #e0e0e0; font-size: 1.8rem; font-weight: 700; margin: 0 0 1rem 0; padding: 0;">
                    🤖 AI-Powered Explanation
                </h2>
            """, unsafe_allow_html=True)
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
    st.markdown("""
    <div class="card">
        <h2 style="color: #e0e0e0; font-size: 1.8rem; font-weight: 700; margin: 0 0 1rem 0; padding: 0;">
            📊 Data Visualizations
        </h2>
        <p style="color: #b0b0b0; font-size: 1rem; margin: 0 0 1.5rem 0;">
            Explore your data through interactive charts and visualizations
        </p>
    """, unsafe_allow_html=True)

    df = st.session_state.df
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    all_cols = df.columns.tolist()

    if numeric_cols:
        # Variable selection section
        st.markdown("""
        <div style="background: rgba(45, 52, 54, 0.5); padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem; border: 1px solid rgba(76, 175, 80, 0.2);">
            <h3 style="color: #e0e0e0; font-size: 1.1rem; margin: 0 0 1rem 0;">📊 Variable Selection</h3>
        """, unsafe_allow_html=True)
        
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            selected_col = st.selectbox("📈 Primary Variable (Y-axis)", numeric_cols, key="primary_var")
        
        # Initialize variables
        secondary_col = None
        selected_vars = [selected_col]
        multi_select = False
        
        with filter_col2:
            if st.session_state.selected_chart_type in ["🔍 Scatter Plot"]:
                if len(numeric_cols) > 1:
                    secondary_col = st.selectbox("📈 Secondary Variable (X-axis)", 
                                                 [col for col in numeric_cols if col != selected_col], 
                                                 key="secondary_var")
            elif st.session_state.selected_chart_type in ["📈 Line Chart", "📊 Area Chart"]:
                multi_select = st.checkbox("📊 Show Multiple Variables", key="multi_var")
                if multi_select and len(numeric_cols) > 1:
                    selected_vars = st.multiselect("Select Variables", 
                                                  numeric_cols,
                                                  default=[selected_col],
                                                  key="multi_vars")
                    if not selected_vars:  # Ensure at least one variable is selected
                        selected_vars = [selected_col]
                else:
                    selected_vars = [selected_col]
        
        # Grouping option for categorical data
        if categorical_cols and st.session_state.selected_chart_type in ["📈 Line Chart", "📊 Area Chart", "🥧 Pie Chart"]:
            group_by = st.selectbox("📂 Group By (Optional)", ["None"] + categorical_cols, key="group_by")
            if group_by == "None":
                group_by = None
        else:
            group_by = None
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Chart type selection with luminous buttons
        chart_types = [
            "📈 Line Chart", "📊 Area Chart", "🥧 Pie Chart",
            "📉 Histogram", "📊 Box Plot", "🔍 Scatter Plot", "🔥 Correlation"
        ]
        
        st.markdown("""
        <div class="chart-buttons-container">
        """, unsafe_allow_html=True)
        
        cols = st.columns(len(chart_types))
        for idx, chart_type in enumerate(chart_types):
            with cols[idx]:
                is_active = st.session_state.selected_chart_type == chart_type
                button_style = "active-chart-btn" if is_active else ""
                if st.button(chart_type, key=f"chart_btn_{idx}", use_container_width=True):
                    st.session_state.selected_chart_type = chart_type
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add custom CSS for luminous button effects
        active_chart = st.session_state.selected_chart_type
        active_idx = chart_types.index(active_chart) if active_chart in chart_types else 0
        st.markdown(f"""
        <style>
        /* Target Streamlit column structure for uniform button sizes */
        .chart-buttons-container [data-testid="column"] {{
            flex: 1 1 0% !important;
            min-width: 0 !important;
            width: 0 !important;
        }}
        
        .chart-buttons-container [data-testid="column"] > div {{
            width: 100% !important;
        }}
        
        /* Base styling for all chart buttons - uniform size */
        .chart-buttons-container .stButton {{
            width: 100% !important;
            min-width: 0 !important;
        }}
        
        .chart-buttons-container .stButton > button {{
            background: rgba(45, 52, 54, 0.8) !important;
            border: 2px solid rgba(76, 175, 80, 0.3) !important;
            border-radius: 10px !important;
            color: #b0b0b0 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
            font-weight: 600 !important;
            width: 100% !important;
            min-width: 0 !important;
            max-width: 100% !important;
            height: 50px !important;
            padding: 0.5rem 0.5rem !important;
            font-size: 0.85rem !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-sizing: border-box !important;
        }}
        
        .chart-buttons-container .stButton > button:hover {{
            background: rgba(76, 175, 80, 0.2) !important;
            border-color: rgba(76, 175, 80, 0.6) !important;
            color: #e0e0e0 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.5) !important;
        }}
        
        /* Active button - luminous effect using nth-of-type */
        .chart-buttons-container [data-testid="column"]:nth-of-type({active_idx + 1}) .stButton > button {{
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.3) 0%, rgba(76, 175, 80, 0.15) 100%) !important;
            border: 2px solid rgba(76, 175, 80, 0.8) !important;
            color: #4CAF50 !important;
            box-shadow: 0 0 20px rgba(76, 175, 80, 0.6), 0 4px 15px rgba(76, 175, 80, 0.4) !important;
            text-shadow: 0 0 10px rgba(76, 175, 80, 0.8) !important;
            animation: chartGlow 2s ease-in-out infinite alternate !important;
        }}
        
        @keyframes chartGlow {{
            from {{
                box-shadow: 0 0 20px rgba(76, 175, 80, 0.6), 0 4px 15px rgba(76, 175, 80, 0.4);
            }}
            to {{
                box-shadow: 0 0 30px rgba(76, 175, 80, 0.8), 0 4px 20px rgba(76, 175, 80, 0.6);
            }}
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # Display selected chart
        if st.session_state.selected_chart_type == "📈 Line Chart":
            st.markdown("### 📈 Line Chart Visualization")
            if multi_select and len(selected_vars) > 0:
                chart_data = df[selected_vars]
                if group_by:
                    chart_data = df.groupby(group_by)[selected_vars].mean()
                st.line_chart(chart_data, height=450)
                st.caption(f"📈 Showing {len(selected_vars)} variable(s)" + (f" grouped by {group_by}" if group_by else ""))
            else:
                chart_data = df[selected_col]
                if group_by:
                    chart_data = df.groupby(group_by)[selected_col].mean()
                st.line_chart(chart_data, height=450)
                st.caption(f"📈 {selected_col}" + (f" grouped by {group_by}" if group_by else ""))
        
        elif st.session_state.selected_chart_type == "📊 Area Chart":
            st.markdown("### 📊 Area Chart Visualization")
            if multi_select and len(selected_vars) > 0:
                chart_data = df[selected_vars]
                if group_by:
                    chart_data = df.groupby(group_by)[selected_vars].mean()
                st.area_chart(chart_data, height=450)
                st.caption(f"📊 Showing {len(selected_vars)} variable(s)" + (f" grouped by {group_by}" if group_by else ""))
            else:
                chart_data = df[selected_col]
                if group_by:
                    chart_data = df.groupby(group_by)[selected_col].mean()
                st.area_chart(chart_data, height=450)
                st.caption(f"📊 {selected_col}" + (f" grouped by {group_by}" if group_by else ""))
        
        elif st.session_state.selected_chart_type == "🥧 Pie Chart":
            st.markdown("### 🥧 Distribution Pie Chart")
            
            # Allow grouping by categorical column
            if group_by:
                pie_data = df.groupby(group_by)[selected_col].sum().head(10)
                title = f"Distribution of {selected_col} by {group_by}"
            else:
                pie_data = df[selected_col].value_counts().head(10)
                title = f"Distribution of {selected_col}"
            
            if len(pie_data) > 0:
                fig, ax = plt.subplots(figsize=(7, 5), facecolor='#2d3436')
                ax.set_facecolor('#2d3436')
                
                # Use a better color scheme
                colors = plt.cm.viridis(np.linspace(0, 1, len(pie_data)))
                
                wedges, texts, autotexts = ax.pie(
                    pie_data.values,
                    labels=pie_data.index,
                    autopct="%1.1f%%",
                    colors=colors,
                    startangle=90,
                    textprops={'color': '#e0e0e0', 'fontsize': 9, 'fontweight': 'bold'}
                )
                
                ax.set_title(title, color='#e0e0e0', fontsize=14, fontweight='bold', pad=20)
                
                # Add summary stats
                total = pie_data.sum()
                st.caption(f"📊 Total: {total:,.2f} | Categories: {len(pie_data)} | Top category: {pie_data.index[0]} ({pie_data.iloc[0]/total*100:.1f}%)")
                
                st.pyplot(fig)
            else:
                st.warning("⚠️ No data available for pie chart.")
        
        elif st.session_state.selected_chart_type == "📉 Histogram":
            st.markdown("### 📉 Histogram Distribution")
            
            # Allow grouping by categorical column
            if group_by:
                fig, ax = plt.subplots(figsize=(12, 6), facecolor='#2d3436')
                ax.set_facecolor('#2d3436')
                
                groups = df[group_by].unique()[:10]  # Limit to 10 groups
                colors = plt.cm.viridis(np.linspace(0, 1, len(groups)))
                
                for i, group in enumerate(groups):
                    group_data = df[df[group_by] == group][selected_col].dropna()
                    if len(group_data) > 0:
                        ax.hist(group_data, bins=30, alpha=0.6, label=str(group), 
                               color=colors[i], edgecolor='white', linewidth=0.5)
                
                ax.set_xlabel(selected_col, color='#e0e0e0', fontsize=12, fontweight='bold')
                ax.set_ylabel('Frequency', color='#e0e0e0', fontsize=12, fontweight='bold')
                ax.set_title(f'Histogram of {selected_col} by {group_by}', color='#e0e0e0', fontsize=14, fontweight='bold')
                ax.legend(title=group_by, title_fontsize=10, fontsize=9, facecolor='#2d3436', edgecolor='#4CAF50')
                ax.tick_params(colors='#e0e0e0')
                ax.grid(True, alpha=0.3, color='#4CAF50', linestyle='--')
            else:
                fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2d3436')
                ax.set_facecolor('#2d3436')
                
                data = df[selected_col].dropna()
                n, bins, patches = ax.hist(data, bins=30, color='#4CAF50', edgecolor='#66BB6A', alpha=0.7, linewidth=1.5)
                
                # Add statistics
                mean_val = data.mean()
                median_val = data.median()
                std_val = data.std()
                
                ax.axvline(mean_val, color='#FF6B6B', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
                ax.axvline(median_val, color='#4ECDC4', linestyle='--', linewidth=2, label=f'Median: {median_val:.2f}')
                
                ax.set_xlabel(selected_col, color='#e0e0e0', fontsize=12, fontweight='bold')
                ax.set_ylabel('Frequency', color='#e0e0e0', fontsize=12, fontweight='bold')
                ax.set_title(f'Histogram of {selected_col}', color='#e0e0e0', fontsize=14, fontweight='bold')
                ax.legend(facecolor='#2d3436', edgecolor='#4CAF50', fontsize=10)
                ax.tick_params(colors='#e0e0e0')
                ax.grid(True, alpha=0.3, color='#4CAF50', linestyle='--')
                
                # Display statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Mean", f"{mean_val:,.2f}")
                with col2:
                    st.metric("Median", f"{median_val:,.2f}")
                with col3:
                    st.metric("Std Dev", f"{std_val:,.2f}")
                with col4:
                    st.metric("Count", f"{len(data):,}")
            
            st.pyplot(fig)
        
        elif st.session_state.selected_chart_type == "📊 Box Plot":
            st.markdown("### 📊 Box Plot Analysis")
            
            # Allow grouping by categorical column or multiple variables
            if group_by:
                fig, ax = plt.subplots(figsize=(12, 6), facecolor='#2d3436')
                ax.set_facecolor('#2d3436')
                
                groups = df[group_by].dropna().unique()[:15]  # Limit to 15 groups
                data_to_plot = [df[df[group_by] == group][selected_col].dropna().values for group in groups]
                
                bp = ax.boxplot(data_to_plot, labels=[str(g) for g in groups], patch_artist=True,
                               boxprops=dict(facecolor='#4CAF50', alpha=0.7, linewidth=1.5),
                               medianprops=dict(color='#66BB6A', linewidth=2.5),
                               whiskerprops=dict(color='#e0e0e0', linewidth=1.5),
                               capprops=dict(color='#e0e0e0', linewidth=1.5),
                               flierprops=dict(marker='o', markerfacecolor='#FF6B6B', markersize=5, alpha=0.5))
                
                ax.set_xlabel(group_by, color='#e0e0e0', fontsize=12, fontweight='bold')
                ax.set_ylabel(selected_col, color='#e0e0e0', fontsize=12, fontweight='bold')
                ax.set_title(f'Box Plot of {selected_col} by {group_by}', color='#e0e0e0', fontsize=14, fontweight='bold')
                plt.xticks(rotation=45, ha='right')
            elif multi_select and len(selected_vars) > 1:
                fig, ax = plt.subplots(figsize=(12, 6), facecolor='#2d3436')
                ax.set_facecolor('#2d3436')
                
                data_to_plot = [df[var].dropna().values for var in selected_vars]
                
                bp = ax.boxplot(data_to_plot, labels=selected_vars, patch_artist=True,
                               boxprops=dict(facecolor='#4CAF50', alpha=0.7, linewidth=1.5),
                               medianprops=dict(color='#66BB6A', linewidth=2.5),
                               whiskerprops=dict(color='#e0e0e0', linewidth=1.5),
                               capprops=dict(color='#e0e0e0', linewidth=1.5),
                               flierprops=dict(marker='o', markerfacecolor='#FF6B6B', markersize=5, alpha=0.5))
                
                ax.set_ylabel('Value', color='#e0e0e0', fontsize=12, fontweight='bold')
                ax.set_title('Box Plot Comparison', color='#e0e0e0', fontsize=14, fontweight='bold')
                plt.xticks(rotation=45, ha='right')
            else:
                fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2d3436')
                ax.set_facecolor('#2d3436')
                
                data = df[selected_col].dropna()
                bp = ax.boxplot([data], labels=[selected_col], patch_artist=True,
                               boxprops=dict(facecolor='#4CAF50', alpha=0.7, linewidth=1.5),
                               medianprops=dict(color='#66BB6A', linewidth=2.5),
                               whiskerprops=dict(color='#e0e0e0', linewidth=1.5),
                               capprops=dict(color='#e0e0e0', linewidth=1.5),
                               flierprops=dict(marker='o', markerfacecolor='#FF6B6B', markersize=5, alpha=0.5))
                
                # Add statistics
                q1 = data.quantile(0.25)
                q3 = data.quantile(0.75)
                iqr = q3 - q1
                median_val = data.median()
                
                ax.set_ylabel(selected_col, color='#e0e0e0', fontsize=12, fontweight='bold')
                ax.set_title(f'Box Plot of {selected_col}', color='#e0e0e0', fontsize=14, fontweight='bold')
                
                # Display statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Q1 (25%)", f"{q1:,.2f}")
                with col2:
                    st.metric("Median", f"{median_val:,.2f}")
                with col3:
                    st.metric("Q3 (75%)", f"{q3:,.2f}")
                with col4:
                    st.metric("IQR", f"{iqr:,.2f}")
            
            ax.tick_params(colors='#e0e0e0')
            ax.grid(True, alpha=0.3, color='#4CAF50', linestyle='--', axis='y')
            st.pyplot(fig)
        
        elif st.session_state.selected_chart_type == "🔍 Scatter Plot":
            if len(numeric_cols) > 1 and secondary_col:
                st.markdown("### 🔍 Scatter Plot Analysis")
                
                # Allow grouping by categorical column
                if group_by:
                    fig, ax = plt.subplots(figsize=(11, 7), facecolor='#2d3436')
                    ax.set_facecolor('#2d3436')
                    
                    groups = df[group_by].dropna().unique()[:10]  # Limit to 10 groups
                    colors = plt.cm.viridis(np.linspace(0, 1, len(groups)))
                    
                    for i, group in enumerate(groups):
                        group_data = df[df[group_by] == group]
                        if len(group_data) > 0:
                            ax.scatter(group_data[selected_col], group_data[secondary_col], 
                                     alpha=0.6, s=60, label=str(group), color=colors[i], edgecolors='white', linewidth=0.5)
                    
                    ax.set_xlabel(selected_col, color='#e0e0e0', fontsize=12, fontweight='bold')
                    ax.set_ylabel(secondary_col, color='#e0e0e0', fontsize=12, fontweight='bold')
                    ax.set_title(f'Scatter Plot: {selected_col} vs {secondary_col} by {group_by}', 
                               color='#e0e0e0', fontsize=14, fontweight='bold')
                    ax.legend(title=group_by, title_fontsize=10, fontsize=9, facecolor='#2d3436', edgecolor='#4CAF50')
                else:
                    fig, ax = plt.subplots(figsize=(11, 7), facecolor='#2d3436')
                    ax.set_facecolor('#2d3436')
                    
                    # Calculate correlation
                    correlation = df[[selected_col, secondary_col]].corr().iloc[0, 1]
                    
                    ax.scatter(df[selected_col], df[secondary_col], alpha=0.6, color='#4CAF50', 
                             s=60, edgecolors='white', linewidth=0.5)
                    
                    # Add trend line
                    z = np.polyfit(df[selected_col].dropna(), df[secondary_col].dropna(), 1)
                    p = np.poly1d(z)
                    ax.plot(df[selected_col].dropna().sort_values(), 
                           p(df[selected_col].dropna().sort_values()), 
                           "r--", alpha=0.8, linewidth=2, label=f'Trend (r={correlation:.3f})')
                    
                    ax.set_xlabel(selected_col, color='#e0e0e0', fontsize=12, fontweight='bold')
                    ax.set_ylabel(secondary_col, color='#e0e0e0', fontsize=12, fontweight='bold')
                    ax.set_title(f'Scatter Plot: {selected_col} vs {secondary_col}', 
                               color='#e0e0e0', fontsize=14, fontweight='bold')
                    ax.legend(facecolor='#2d3436', edgecolor='#4CAF50', fontsize=10)
                    
                    # Display correlation
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Correlation Coefficient", f"{correlation:.4f}")
                    with col2:
                        strength = "Strong" if abs(correlation) > 0.7 else "Moderate" if abs(correlation) > 0.3 else "Weak"
                        st.metric("Relationship", strength)
                
                ax.tick_params(colors='#e0e0e0')
                ax.grid(True, alpha=0.3, color='#4CAF50', linestyle='--')
                st.pyplot(fig)
            else:
                st.info("ℹ️ Need at least 2 numeric columns for scatter plot. Please select a secondary variable.")
        
        elif st.session_state.selected_chart_type == "🔥 Correlation":
            if len(numeric_cols) > 1:
                st.markdown("### 🔥 Correlation Heatmap")
                
                # Allow selection of specific columns for correlation
                selected_corr_cols = st.multiselect(
                    "📊 Select variables for correlation analysis",
                    numeric_cols,
                    default=numeric_cols[:min(10, len(numeric_cols))],  # Default to first 10
                    key="corr_vars"
                )
                
                if len(selected_corr_cols) > 1:
                    corr = df[selected_corr_cols].corr()
                    
                    # Create a visual heatmap
                    fig, ax = plt.subplots(figsize=(max(10, len(selected_corr_cols)*0.8), 
                                                    max(8, len(selected_corr_cols)*0.8)), 
                                         facecolor='#2d3436')
                    ax.set_facecolor('#2d3436')
                    
                    im = ax.imshow(corr.values, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
                    
                    # Set ticks and labels
                    ax.set_xticks(np.arange(len(selected_corr_cols)))
                    ax.set_yticks(np.arange(len(selected_corr_cols)))
                    ax.set_xticklabels(selected_corr_cols, rotation=45, ha='right', color='#e0e0e0')
                    ax.set_yticklabels(selected_corr_cols, color='#e0e0e0')
                    
                    # Add text annotations
                    for i in range(len(selected_corr_cols)):
                        for j in range(len(selected_corr_cols)):
                            text = ax.text(j, i, f'{corr.iloc[i, j]:.2f}',
                                         ha="center", va="center", color="white" if abs(corr.iloc[i, j]) > 0.5 else "#b0b0b0",
                                         fontweight='bold' if abs(corr.iloc[i, j]) > 0.7 else 'normal')
                    
                    ax.set_title('Correlation Heatmap', color='#e0e0e0', fontsize=14, fontweight='bold', pad=20)
                    
                    # Add colorbar
                    cbar = plt.colorbar(im, ax=ax)
                    cbar.set_label('Correlation Coefficient', color='#e0e0e0', fontsize=11)
                    cbar.ax.tick_params(colors='#e0e0e0')
                    
                    st.pyplot(fig)
                    
                    # Display correlation matrix as dataframe
                    st.markdown("#### 📋 Correlation Matrix (Detailed)")
                    st.dataframe(corr.style.background_gradient(cmap="coolwarm", axis=None, vmin=-1, vmax=1)
                                .format("{:.3f}"), use_container_width=True)
                    
                    # Find strongest correlations
                    st.markdown("#### 🔍 Strongest Correlations")
                    corr_pairs = []
                    for i in range(len(selected_corr_cols)):
                        for j in range(i+1, len(selected_corr_cols)):
                            corr_pairs.append({
                                'Variable 1': selected_corr_cols[i],
                                'Variable 2': selected_corr_cols[j],
                                'Correlation': corr.iloc[i, j]
                            })
                    corr_df = pd.DataFrame(corr_pairs).sort_values('Correlation', key=abs, ascending=False)
                    st.dataframe(corr_df.head(10), use_container_width=True, hide_index=True)
                else:
                    st.warning("⚠️ Please select at least 2 variables for correlation analysis.")
            else:
                st.info("ℹ️ Need at least 2 numeric columns for correlation analysis.")
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
