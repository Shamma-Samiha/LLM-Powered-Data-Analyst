# frontend/app_cloud.py
# Streamlit Cloud version (EDA-only): no FastAPI, no Ollama, no subprocess.
# Includes: Dataset Overview card heading inside the top empty card,
# Data Preview heading inside its card, Data Visualizations heading inside its card,
# and PDF report generation (ReportLab).

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# --------------------------------------------------
# Session state
# --------------------------------------------------
if "df" not in st.session_state:
    st.session_state.df = None

if "selected_chart_type" not in st.session_state:
    st.session_state.selected_chart_type = "Line Chart"


# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="LLM Powered Data Analyst (Cloud EDA)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# --------------------------------------------------
# Custom CSS (keep your theme)
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
.main, p, div, span, label { color: #e0e0e0 !important; }

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

h1, h2, h3, h4, h5, h6 { color: #e0e0e0 !important; font-weight: 700; }

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

.stTextInput > div > div > input {
    background: rgba(61, 74, 82, 0.8) !important;
    color: #e0e0e0 !important;
    border-radius: 8px;
    border: 1px solid rgba(76, 175, 80, 0.3);
}

hr { border-color: rgba(76, 175, 80, 0.3); }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Small helpers to ensure headings go INSIDE the card
# --------------------------------------------------
def card_start(title: str, subtitle: str | None = None):
    st.markdown(f"""
    <div class="card">
        <h2 style="margin: 0 0 0.75rem 0; padding: 0; font-size: 1.8rem;">
            {title}
        </h2>
        {"<p style='color:#b0b0b0; margin: 0 0 1.25rem 0;'>" + subtitle + "</p>" if subtitle else ""}
    """, unsafe_allow_html=True)

def card_end():
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# PDF Generator (Cloud friendly)
# --------------------------------------------------
def generate_pdf_report_cloud(
    df: pd.DataFrame,
    basic_summary: dict,
    notes: str | None = None
) -> BytesIO:
    buffer = BytesIO()
    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elems = []

    elems.append(Paragraph("LLM Powered Data Analyst - Cloud EDA Report", styles["Title"]))
    elems.append(Spacer(1, 12))

    elems.append(Paragraph("<b>Dataset Overview</b>", styles["Heading2"]))
    elems.append(Paragraph(f"Rows: {basic_summary['rows']}", styles["BodyText"]))
    elems.append(Paragraph(f"Columns: {basic_summary['cols']}", styles["BodyText"]))
    elems.append(Spacer(1, 10))

    elems.append(Paragraph("<b>Columns</b>", styles["Heading2"]))
    cols_text = ", ".join([str(c) for c in df.columns.tolist()])
    elems.append(Paragraph(cols_text, styles["BodyText"]))
    elems.append(Spacer(1, 10))

    elems.append(Paragraph("<b>Missing Values (Top)</b>", styles["Heading2"]))
    missing = df.isna().sum().sort_values(ascending=False)
    top_missing = missing[missing > 0].head(10)
    if len(top_missing) == 0:
        elems.append(Paragraph("No missing values found.", styles["BodyText"]))
    else:
        for k, v in top_missing.items():
            elems.append(Paragraph(f"- {k}: {int(v)}", styles["BodyText"]))
    elems.append(Spacer(1, 10))

    elems.append(Paragraph("<b>Numeric Summary (Quick)</b>", styles["Heading2"]))
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not num_cols:
        elems.append(Paragraph("No numeric columns found.", styles["BodyText"]))
    else:
        desc = df[num_cols].describe().round(2)
        # Keep it short in PDF: first few columns only
        show_cols = num_cols[:6]
        for c in show_cols:
            elems.append(Paragraph(f"<b>{c}</b>", styles["BodyText"]))
            elems.append(Paragraph(
                f"min={desc.loc['min', c]}, 25%={desc.loc['25%', c]}, "
                f"median={desc.loc['50%', c]}, mean={desc.loc['mean', c]}, "
                f"75%={desc.loc['75%', c]}, max={desc.loc['max', c]}",
                styles["BodyText"]
            ))
            elems.append(Spacer(1, 6))

    if notes:
        elems.append(Spacer(1, 12))
        elems.append(Paragraph("<b>Notes</b>", styles["Heading2"]))
        elems.append(Paragraph(notes, styles["BodyText"]))

    doc.build(elems)
    buffer.seek(0)
    return buffer


# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown("""
<div class="top-bar">
    <div style="width: 100%; text-align: center;">
        <h1 style="font-size: 2.5rem;
                   background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   font-weight: 800; margin: 0 0 1rem 0;">
            LLM Powered Data Analyst
        </h1>
        <p style="color: #b0b0b0; font-size: 1.1rem; margin: 0;">
            Streamlit Cloud demo: EDA + charts + PDF report (no backend / no Ollama).
        </p>
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# Upload
# --------------------------------------------------
card_start("📁 Upload Your Data File", "Upload CSV / XLSX / XLS to run Cloud EDA.")
uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx", "xls"],
    label_visibility="collapsed"
)
card_end()

if uploaded_file:
    # Load df
    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.session_state.df = df

    # Basic summary
    basic_summary = {
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "size_kb": float(len(uploaded_file.getvalue()) / 1024.0)
    }

    # --------------------------------------------------
    # ✅ Dataset Overview heading INSIDE the card
    # --------------------------------------------------
    card_start("📌 Dataset Overview (Cloud EDA)", "Quick stats + missing values + data types (computed locally).")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Rows", f"{basic_summary['rows']:,}")
    with c2:
        st.metric("Columns", f"{basic_summary['cols']:,}")
    with c3:
        st.metric("File Size", f"{basic_summary['size_kb']:.1f} KB")

    # Missing + dtypes
    colA, colB = st.columns(2)

    with colA:
        st.markdown("### 🧩 Missing Values")
        missing_df = (df.isna().sum()
                      .sort_values(ascending=False)
                      .reset_index())
        missing_df.columns = ["Column", "Missing Count"]
        st.dataframe(missing_df, use_container_width=True, hide_index=True)

    with colB:
        st.markdown("### 🧾 Data Types")
        types_df = (df.dtypes.astype(str)
                    .reset_index())
        types_df.columns = ["Column", "Data Type"]
        st.dataframe(types_df, use_container_width=True, hide_index=True)

    # PDF Download (added back ✅)
    pdf_notes = "This is the Streamlit Cloud (EDA-only) version. For AI explanations, run locally with FastAPI + Ollama."
    pdf = generate_pdf_report_cloud(df, basic_summary, notes=pdf_notes)

    st.download_button(
        "📄 Download PDF Report",
        data=pdf,
        file_name="cloud_eda_report.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    card_end()

    # --------------------------------------------------
    # ✅ Data Preview heading INSIDE the card
    # --------------------------------------------------
    card_start("🔎 Data Preview", "First rows of your dataset (editable view is not enabled).")
    st.dataframe(df.head(30), use_container_width=True)
    card_end()

    # --------------------------------------------------
    # ✅ Data Visualizations heading INSIDE the card
    # --------------------------------------------------
    card_start("📊 Data Visualizations", "Choose a chart type and variables. All charts generated locally.")

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    if not numeric_cols:
        st.info("No numeric columns found, so charts are limited.")
        card_end()
    else:
        # Chart selection controls
        chart_types = ["Line Chart", "Area Chart", "Pie Chart", "Histogram", "Box Plot", "Scatter Plot", "Correlation"]
        selected_chart = st.radio(
            "Chart Type",
            chart_types,
            horizontal=True,
            index=chart_types.index(st.session_state.selected_chart_type) if st.session_state.selected_chart_type in chart_types else 0
        )
        st.session_state.selected_chart_type = selected_chart

        left, right = st.columns(2)
        with left:
            y_col = st.selectbox("Primary numeric column", numeric_cols, index=0)

        x_col = None
        group_by = None

        with right:
            if selected_chart == "Scatter Plot" and len(numeric_cols) > 1:
                x_options = [c for c in numeric_cols if c != y_col]
                x_col = st.selectbox("Secondary numeric column (X-axis)", x_options, index=0)
            if selected_chart in ["Line Chart", "Area Chart", "Pie Chart"] and categorical_cols:
                group_by = st.selectbox("Group by (optional)", ["None"] + categorical_cols)
                if group_by == "None":
                    group_by = None

        # Render chart
        if selected_chart == "Line Chart":
            data = df.groupby(group_by)[y_col].mean() if group_by else df[y_col]
            st.line_chart(data, height=450)

        elif selected_chart == "Area Chart":
            data = df.groupby(group_by)[y_col].mean() if group_by else df[y_col]
            st.area_chart(data, height=450)

        elif selected_chart == "Pie Chart":
            if group_by:
                pie_data = df.groupby(group_by)[y_col].sum().sort_values(ascending=False).head(10)
                title = f"{y_col} sum by {group_by} (Top 10)"
            else:
                pie_data = df[y_col].value_counts().head(10)
                title = f"Top 10 values of {y_col}"

            fig, ax = plt.subplots(figsize=(8, 5), facecolor="#2d3436")
            ax.set_facecolor("#2d3436")
            ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
            ax.set_title(title, color="#e0e0e0")
            st.pyplot(fig)

        elif selected_chart == "Histogram":
            fig, ax = plt.subplots(figsize=(10, 5), facecolor="#2d3436")
            ax.set_facecolor("#2d3436")
            ax.hist(df[y_col].dropna(), bins=30)
            ax.set_title(f"Histogram of {y_col}", color="#e0e0e0")
            ax.tick_params(colors="#e0e0e0")
            st.pyplot(fig)

        elif selected_chart == "Box Plot":
            fig, ax = plt.subplots(figsize=(8, 5), facecolor="#2d3436")
            ax.set_facecolor("#2d3436")
            ax.boxplot(df[y_col].dropna(), vert=True)
            ax.set_title(f"Box plot of {y_col}", color="#e0e0e0")
            ax.tick_params(colors="#e0e0e0")
            st.pyplot(fig)

        elif selected_chart == "Scatter Plot":
            if x_col is None:
                st.info("Pick a secondary numeric column to build the scatter plot.")
            else:
                fig, ax = plt.subplots(figsize=(9, 6), facecolor="#2d3436")
                ax.set_facecolor("#2d3436")
                ax.scatter(df[x_col], df[y_col], alpha=0.6)
                ax.set_xlabel(x_col, color="#e0e0e0")
                ax.set_ylabel(y_col, color="#e0e0e0")
                ax.set_title(f"{y_col} vs {x_col}", color="#e0e0e0")
                ax.tick_params(colors="#e0e0e0")
                st.pyplot(fig)

        elif selected_chart == "Correlation":
            if len(numeric_cols) < 2:
                st.info("Need at least 2 numeric columns for correlation.")
            else:
                selected_corr_cols = st.multiselect(
                    "Select numeric columns (max recommended: ~10)",
                    numeric_cols,
                    default=numeric_cols[: min(10, len(numeric_cols))]
                )
                if len(selected_corr_cols) < 2:
                    st.warning("Select at least 2 columns.")
                else:
                    corr = df[selected_corr_cols].corr()
                    st.dataframe(
                        corr.style.background_gradient(cmap="coolwarm", axis=None).format("{:.3f}"),
                        use_container_width=True
                    )

        card_end()

else:
    st.info("Upload a dataset to see the Cloud EDA overview, preview, charts, and PDF report.")


# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #b0b0b0;">
  <p style="font-size: 0.9rem; margin: 0;">
    Built with ❤️ using Streamlit + Pandas + Matplotlib + ReportLab.
    Cloud version is EDA-only (AI runs locally with FastAPI + Ollama).
  </p>
</div>
""", unsafe_allow_html=True)
