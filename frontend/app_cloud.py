# frontend/app_cloud.py
# Cloud version (EDA-only) for Streamlit Community Cloud
# - No FastAPI backend
# - No Ollama (local LLM)
# - Keeps UI, EDA, charts, PDF export

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

# --------------------------------------------------
# Session state
# --------------------------------------------------
if "df" not in st.session_state:
    st.session_state.df = None

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "selected_chart_type" not in st.session_state:
    st.session_state.selected_chart_type = "📈 Line Chart"

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="LLM Powered Data Analyst (Cloud Demo)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# --------------------------------------------------
# Custom CSS for dark theme (ash, gray, green)
# (same CSS as your app.py)
# --------------------------------------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #2d3436 0%, #3d4a52 25%, #4a5d6b 50%, #2d4a2d 75%, #3d5a3d 100%);
        background-attachment: fixed;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    section[data-testid="stSidebar"] { display: none !important; }
    .main { width: 100% !important; padding-left: 0 !important; padding-right: 0 !important; }
    .stApp > div { padding-left: 0 !important; padding-right: 0 !important; }
    .main { color: #e0e0e0; }
    p, div, span, label { color: #e0e0e0 !important; }

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

    .card {
        background: rgba(45, 52, 54, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem 1.5rem 1rem 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(76, 175, 80, 0.2);
    }

    .card-question {
        background: rgba(45, 52, 54, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem 1.25rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(76, 175, 80, 0.2);
    }

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

    [data-testid="stFileUploader"] {
        background: rgba(45, 52, 54, 0.8);
        border: 2px dashed rgba(76, 175, 80, 0.5);
        border-radius: 10px;
    }

    .stTextInput > div > div > input {
        background: rgba(61, 74, 82, 0.8) !important;
        color: #e0e0e0 !important;
        border-radius: 8px;
        border: 1px solid rgba(76, 175, 80, 0.3);
    }

    h1, h2, h3, h4, h5, h6 { color: #e0e0e0 !important; font-weight: 700; }
    hr { border-color: rgba(76, 175, 80, 0.3); }
    .stCaption { color: #b0b0b0 !important; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown("""
<div class="top-bar">
    <div style="width: 100%; text-align: center;">
        <h1 style="color: #e0e0e0; font-size: 2.5rem;
                    background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-weight: 800; margin: 0 0 1rem 0; text-align: center; width: 100%;">
            LLM Powered Data Analyst (Cloud Demo)
        </h1>
        <p style="color: #b0b0b0; font-size: 1.05rem; text-align: center; line-height: 1.6; margin: 0;">
            This public demo runs EDA + charts + PDF export.
            <br/>
            🤖 AI/Ollama features are available in LOCAL mode only.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.info("✅ Cloud Demo Mode: EDA + Charts + PDF works here.  🤖 Local AI mode (Ollama) works when running the project on your PC.")

# --------------------------------------------------
# PDF Generator (still works on cloud)
# --------------------------------------------------
def generate_pdf_report(summary_text: str):
    buffer = BytesIO()
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(buffer)
    elements = []

    elements.append(Paragraph("Data Analysis Report (Cloud Demo)", styles["Title"]))
    elements.append(Paragraph("<br/>", styles["BodyText"]))

    for line in summary_text.split("\n"):
        if line.strip():
            elements.append(Paragraph(line, styles["BodyText"]))

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
        Select a CSV or Excel file to run analysis in cloud demo mode.
    </p>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx", "xls"],
    label_visibility="collapsed"
)
st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# Analyze section (Cloud EDA)
# --------------------------------------------------
if uploaded_file:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.success(f"✅ File selected: **{uploaded_file.name}**")

    # Load dataframe
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Could not read the file. Error: {e}")
        st.stop()

    st.session_state.df = df

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Rows", f"{len(df):,}")
    with col2:
        st.metric("📋 Columns", len(df.columns))
    with col3:
        file_size = len(uploaded_file.getvalue()) / 1024
        st.metric("💾 Size", f"{file_size:.1f} KB")
    st.markdown("</div>", unsafe_allow_html=True)

    # Analyze button
    colA, colB, colC = st.columns([1, 2, 1])
    with colB:
        analyze_btn = st.button("🚀 Analyze Dataset (Cloud Demo)", use_container_width=True, type="primary")

    if analyze_btn:
        with st.spinner("🔍 Running EDA..."):
            numeric_summary = {}
            try:
                numeric_summary = df.describe().round(2).to_dict()
            except Exception:
                numeric_summary = {}

            analysis = {
                "rows": df.shape[0],
                "columns": df.shape[1],
                "column_names": df.columns.tolist(),
                "missing_values": df.isnull().sum().to_dict(),
                "data_types": df.dtypes.astype(str).to_dict(),
                "numeric_summary": numeric_summary
            }

            st.session_state.analysis = analysis

        # Show overview
        st.markdown("""
        <div class="card">
            <h2 style="color: #e0e0e0; font-size: 1.8rem; font-weight: 700; margin: 0 0 1rem 0; padding: 0;">
                📌 Dataset Overview
            </h2>
        """, unsafe_allow_html=True)

        ov1, ov2 = st.columns(2)
        with ov1:
            st.metric("Total Rows", f"{analysis['rows']:,}")
        with ov2:
            st.metric("Total Columns", analysis["columns"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Missing & types
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("""
            <div class="card">
                <h2 style="color: #e0e0e0; font-size: 1.8rem; font-weight: 700; margin: 0 0 1rem 0; padding: 0;">
                    🧩 Missing Values
                </h2>
            """, unsafe_allow_html=True)
            missing_df = pd.DataFrame(list(analysis["missing_values"].items()), columns=["Column", "Missing Count"])
            st.dataframe(missing_df, use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("""
            <div class="card">
                <h2 style="color: #e0e0e0; font-size: 1.8rem; font-weight: 700; margin: 0 0 1rem 0; padding: 0;">
                    🧾 Data Types
                </h2>
            """, unsafe_allow_html=True)
            types_df = pd.DataFrame(list(analysis["data_types"].items()), columns=["Column", "Data Type"])
            st.dataframe(types_df, use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Cloud "report" text
        cloud_summary = f"""Cloud Demo Summary
- Rows: {analysis['rows']:,}
- Columns: {analysis['columns']}
- Missing values: {sum(analysis['missing_values'].values()):,} total
- Numeric summary is available for numeric columns
- Charts are available below

Note:
- AI/Ollama insights are available in LOCAL mode only.
"""

        pdf = generate_pdf_report(cloud_summary)
        st.download_button(
            "📄 Download PDF Report (Cloud Demo)",
            data=pdf,
            file_name="data_analysis_report_cloud_demo.pdf",
            mime="application/pdf",
            use_container_width=True
        )

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
            Explore your data through charts. (Cloud Demo Mode)
        </p>
    """, unsafe_allow_html=True)

    df = st.session_state.df
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    if numeric_cols:
        st.markdown("""
        <div style="background: rgba(45, 52, 54, 0.5); padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem; border: 1px solid rgba(76, 175, 80, 0.2);">
            <h3 style="color: #e0e0e0; font-size: 1.1rem; margin: 0 0 1rem 0;">📊 Variable Selection</h3>
        """, unsafe_allow_html=True)

        filter_col1, filter_col2 = st.columns(2)

        with filter_col1:
            selected_col = st.selectbox("📈 Primary Variable (Y-axis)", numeric_cols, key="primary_var_cloud")

        secondary_col = None
        selected_vars = [selected_col]
        multi_select = False

        with filter_col2:
            if st.session_state.selected_chart_type in ["🔍 Scatter Plot"]:
                if len(numeric_cols) > 1:
                    secondary_col = st.selectbox(
                        "📈 Secondary Variable (X-axis)",
                        [col for col in numeric_cols if col != selected_col],
                        key="secondary_var_cloud"
                    )
            elif st.session_state.selected_chart_type in ["📈 Line Chart", "📊 Area Chart"]:
                multi_select = st.checkbox("📊 Show Multiple Variables", key="multi_var_cloud")
                if multi_select and len(numeric_cols) > 1:
                    selected_vars = st.multiselect(
                        "Select Variables",
                        numeric_cols,
                        default=[selected_col],
                        key="multi_vars_cloud"
                    )
                    if not selected_vars:
                        selected_vars = [selected_col]
                else:
                    selected_vars = [selected_col]

        if categorical_cols and st.session_state.selected_chart_type in ["📈 Line Chart", "📊 Area Chart", "🥧 Pie Chart"]:
            group_by = st.selectbox("📂 Group By (Optional)", ["None"] + categorical_cols, key="group_by_cloud")
            if group_by == "None":
                group_by = None
        else:
            group_by = None

        st.markdown("</div>", unsafe_allow_html=True)

        chart_types = [
            "Line Chart", "Area Chart", "Pie Chart",
            "Histogram", "Box Plot", "Scatter Plot", "Correlation"
        ]

        st.markdown('<div class="chart-buttons-container">', unsafe_allow_html=True)
        cols = st.columns(len(chart_types))
        for idx, chart_type in enumerate(chart_types):
            with cols[idx]:
                if st.button(chart_type, key=f"chart_btn_cloud_{idx}", use_container_width=True):
                    st.session_state.selected_chart_type = chart_type
        st.markdown("</div>", unsafe_allow_html=True)

        active_chart = st.session_state.selected_chart_type
        active_idx = chart_types.index(active_chart) if active_chart in chart_types else 0
        st.markdown(f"""
        <style>
        .chart-buttons-container [data-testid="column"] {{
            flex: 1 1 0% !important;
            min-width: 0 !important;
            width: 0 !important;
        }}
        .chart-buttons-container [data-testid="column"] > div {{
            width: 100% !important;
        }}
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
        .chart-buttons-container [data-testid="column"]:nth-of-type({active_idx + 1}) .stButton > button {{
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.3) 0%, rgba(76, 175, 80, 0.15) 100%) !important;
            border: 2px solid rgba(76, 175, 80, 0.8) !important;
            color: #4CAF50 !important;
            box-shadow: 0 0 20px rgba(76, 175, 80, 0.6), 0 4px 15px rgba(76, 175, 80, 0.4) !important;
            text-shadow: 0 0 10px rgba(76, 175, 80, 0.8) !important;
        }}
        </style>
        """, unsafe_allow_html=True)

        # Chart rendering (same as your app.py logic)
        if st.session_state.selected_chart_type == "📈 Line Chart":
            st.markdown("### 📈 Line Chart Visualization")
            if multi_select and len(selected_vars) > 0:
                chart_data = df[selected_vars]
                if group_by:
                    chart_data = df.groupby(group_by)[selected_vars].mean()
                st.line_chart(chart_data, height=450)
            else:
                chart_data = df[selected_col]
                if group_by:
                    chart_data = df.groupby(group_by)[selected_col].mean()
                st.line_chart(chart_data, height=450)

        elif st.session_state.selected_chart_type == "📊 Area Chart":
            st.markdown("### 📊 Area Chart Visualization")
            if multi_select and len(selected_vars) > 0:
                chart_data = df[selected_vars]
                if group_by:
                    chart_data = df.groupby(group_by)[selected_vars].mean()
                st.area_chart(chart_data, height=450)
            else:
                chart_data = df[selected_col]
                if group_by:
                    chart_data = df.groupby(group_by)[selected_col].mean()
                st.area_chart(chart_data, height=450)

        elif st.session_state.selected_chart_type == "🥧 Pie Chart":
            st.markdown("### 🥧 Distribution Pie Chart")

            if group_by:
                pie_data = df.groupby(group_by)[selected_col].sum().head(10)
                title = f"Distribution of {selected_col} by {group_by}"
            else:
                pie_data = df[selected_col].value_counts().head(10)
                title = f"Distribution of {selected_col}"

            if len(pie_data) > 0:
                fig, ax = plt.subplots(figsize=(7, 5), facecolor="#2d3436")
                ax.set_facecolor("#2d3436")
                colors = plt.cm.viridis(np.linspace(0, 1, len(pie_data)))

                ax.pie(
                    pie_data.values,
                    labels=pie_data.index,
                    autopct="%1.1f%%",
                    colors=colors,
                    startangle=90,
                    textprops={"color": "#e0e0e0", "fontsize": 9, "fontweight": "bold"},
                )
                ax.set_title(title, color="#e0e0e0", fontsize=14, fontweight="bold", pad=20)
                st.pyplot(fig)
            else:
                st.warning("⚠️ No data available for pie chart.")

        elif st.session_state.selected_chart_type == "📉 Histogram":
            st.markdown("### 📉 Histogram Distribution")
            data = df[selected_col].dropna()

            fig, ax = plt.subplots(figsize=(10, 6), facecolor="#2d3436")
            ax.set_facecolor("#2d3436")
            ax.hist(data, bins=30, alpha=0.7, edgecolor="white")
            ax.set_title(f"Histogram of {selected_col}", color="#e0e0e0", fontsize=14, fontweight="bold")
            ax.set_xlabel(selected_col, color="#e0e0e0")
            ax.set_ylabel("Frequency", color="#e0e0e0")
            ax.tick_params(colors="#e0e0e0")
            ax.grid(True, alpha=0.2)
            st.pyplot(fig)

        elif st.session_state.selected_chart_type == "📊 Box Plot":
            st.markdown("### 📊 Box Plot Analysis")
            data = df[selected_col].dropna()

            fig, ax = plt.subplots(figsize=(10, 6), facecolor="#2d3436")
            ax.set_facecolor("#2d3436")
            ax.boxplot([data], labels=[selected_col], patch_artist=True)
            ax.set_title(f"Box Plot of {selected_col}", color="#e0e0e0", fontsize=14, fontweight="bold")
            ax.tick_params(colors="#e0e0e0")
            ax.grid(True, alpha=0.2)
            st.pyplot(fig)

        elif st.session_state.selected_chart_type == "🔍 Scatter Plot":
            st.markdown("### 🔍 Scatter Plot Analysis")
            if len(numeric_cols) > 1 and secondary_col:
                x = df[secondary_col]
                y = df[selected_col]

                fig, ax = plt.subplots(figsize=(11, 7), facecolor="#2d3436")
                ax.set_facecolor("#2d3436")
                ax.scatter(x, y, alpha=0.6, s=50)
                ax.set_xlabel(secondary_col, color="#e0e0e0")
                ax.set_ylabel(selected_col, color="#e0e0e0")
                ax.set_title(f"{selected_col} vs {secondary_col}", color="#e0e0e0", fontsize=14, fontweight="bold")
                ax.tick_params(colors="#e0e0e0")
                ax.grid(True, alpha=0.2)
                st.pyplot(fig)
            else:
                st.info("ℹ️ Need 2 numeric columns. Select a secondary variable.")

        elif st.session_state.selected_chart_type == "🔥 Correlation":
            st.markdown("### 🔥 Correlation Heatmap")
            if len(numeric_cols) > 1:
                selected_corr_cols = st.multiselect(
                    "📊 Select variables for correlation",
                    numeric_cols,
                    default=numeric_cols[:min(10, len(numeric_cols))],
                    key="corr_vars_cloud",
                )

                if len(selected_corr_cols) > 1:
                    corr = df[selected_corr_cols].corr()
                    st.dataframe(
                        corr.style.background_gradient(cmap="coolwarm", axis=None).format("{:.3f}"),
                        use_container_width=True,
                    )
                else:
                    st.warning("⚠️ Select at least 2 variables.")
            else:
                st.info("ℹ️ Need at least 2 numeric columns for correlation.")
    else:
        st.info("ℹ️ No numeric columns found in your dataset.")

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# Question section (Cloud-safe)
# --------------------------------------------------
st.markdown("---")
st.markdown("""
<div class="card-question">
    <h2 style="color: #e0e0e0; font-size: 1.5rem; font-weight: 700; margin: 0 0 0.75rem 0; padding: 0;">
        💬 Ask a Question About Your Data (Cloud Demo)
    </h2>
    <p style="color: #b0b0b0; margin: 0 0 1rem 0; font-size: 0.95rem;">
        In cloud demo mode, we show smart charts based on keywords.
        AI answers require LOCAL mode with Ollama.
    </p>
""", unsafe_allow_html=True)

question = st.text_input(
    "💭 Ask anything (e.g., 'Show trends', 'Compare values', 'Distribution')",
    placeholder="Type your question here...",
    label_visibility="collapsed",
)

if question and st.session_state.df is not None:
    q = question.lower()
    df = st.session_state.df
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

    # Smart chart suggestions (cloud-safe)
    if numeric_cols:
        if "trend" in q or "over time" in q:
            st.markdown("### 📈 Trend View")
            st.line_chart(df[numeric_cols], height=400)
        elif "distribution" in q:
            st.markdown("### 🥧 Distribution View")
            col = numeric_cols[0]
            pie_data = df[col].value_counts().head(10)
            fig, ax = plt.subplots(figsize=(10, 6), facecolor="#2d3436")
            ax.set_facecolor("#2d3436")
            pie_data.plot.pie(autopct="%1.1f%%", ax=ax, textprops={"color": "#e0e0e0"})
            ax.title.set_color("#e0e0e0")
            st.pyplot(fig)
        elif "compare" in q:
            st.markdown("### 📊 Comparison View")
            st.bar_chart(df[numeric_cols], height=400)

    st.warning("🤖 AI answers are disabled on Streamlit Cloud. Run locally to use Ollama-powered Q&A.")
elif question:
    st.warning("⚠️ Please upload a dataset first.")

st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #b0b0b0;">
    <p style="font-size: 0.9rem; margin: 0;">
        Cloud Demo: EDA + Charts + PDF (No AI). <br/>
        Local Mode: Full AI features using Ollama.
    </p>
</div>
""", unsafe_allow_html=True)
