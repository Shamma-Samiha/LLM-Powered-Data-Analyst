# frontend/app_cloud.py
"""
Streamlit Cloud version (EDA + Charts only).
✅ No FastAPI backend required
✅ No Ollama / subprocess (Streamlit Cloud doesn't support local Ollama)
✅ Works fully on Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")


# -----------------------------
# Session state
# -----------------------------
if "df" not in st.session_state:
    st.session_state.df = None

if "selected_chart_type" not in st.session_state:
    st.session_state.selected_chart_type = "Line Chart"


# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="LLM Powered Data Analyst (Cloud Demo)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# -----------------------------
# CSS (reuse your styling)
# -----------------------------
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
.main { color: #e0e0e0; }
p, div, span, label { color: #e0e0e0 !important; }
.card {
    background: rgba(45, 52, 54, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 1.5rem 1.5rem 1rem 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(76, 175, 80, 0.2);
}
.top-bar {
    background: rgba(45, 52, 54, 0.95) !important;
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 2rem 2.5rem !important;
    margin: 0 auto 2rem auto !important;
    max-width: 95% !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    border: 1px solid rgba(76,175,80,0.2);
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-height: 120px;
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
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="top-bar">
  <div style="width:100%; text-align:center;">
    <h1 style="font-size:2.5rem;
               background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
               -webkit-background-clip:text;
               -webkit-text-fill-color:transparent;
               font-weight:800; margin:0 0 1rem 0;">
      LLM Powered Data Analyst
    </h1>
    <p style="color:#b0b0b0; font-size:1.1rem; line-height:1.6; margin:0;">
      Streamlit Cloud demo (EDA + Charts). Local AI (Ollama) runs only on your machine.
    </p>
  </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------
# Helpers
# -----------------------------
def compute_eda(df: pd.DataFrame) -> dict:
    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "numeric_summary": df.select_dtypes(include=["number"]).describe().round(2).to_dict()
    }


def simple_summary_text(df: pd.DataFrame, eda: dict) -> str:
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    missing_total = int(sum(eda["missing_values"].values()))
    top_missing = sorted(eda["missing_values"].items(), key=lambda x: x[1], reverse=True)[:5]

    lines = []
    lines.append(f"- This dataset has **{eda['rows']:,} rows** and **{eda['columns']} columns**.")
    if numeric_cols:
        lines.append(f"- Numeric columns: **{len(numeric_cols)}** (example: {', '.join(numeric_cols[:3])}{'...' if len(numeric_cols)>3 else ''}).")
    if cat_cols:
        lines.append(f"- Categorical columns: **{len(cat_cols)}** (example: {', '.join(cat_cols[:3])}{'...' if len(cat_cols)>3 else ''}).")
    lines.append(f"- Total missing values: **{missing_total:,}**.")
    if missing_total > 0:
        lines.append("- Columns with most missing values: " + ", ".join([f"**{c}** ({v})" for c, v in top_missing if v > 0]) + ".")
    lines.append("- Use the chart section below to explore distributions, outliers, correlations, and trends.")
    return "\n".join(lines)


# -----------------------------
# Upload
# -----------------------------
st.markdown("""
<div class="card">
  <h2 style="margin:0 0 0.75rem 0;">📁 Upload Your Data File</h2>
  <p style="color:#b0b0b0; margin:0 0 1rem 0;">
    Upload a CSV or Excel file. (Cloud demo runs EDA + charts only.)
  </p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx", "xls"],
    label_visibility="collapsed"
)

if uploaded_file:
    # Load df
    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.session_state.df = df

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.success(f"✅ File selected: **{uploaded_file.name}**")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("📊 Rows", f"{len(df):,}")
    with c2:
        st.metric("📋 Columns", len(df.columns))
    with c3:
        size_kb = len(uploaded_file.getvalue()) / 1024
        st.metric("💾 Size", f"{size_kb:.1f} KB")

    st.markdown("</div>", unsafe_allow_html=True)

    # EDA
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📌 Dataset Overview (Cloud EDA)")
    eda = compute_eda(df)

    o1, o2 = st.columns(2)
    with o1:
        st.metric("Total Rows", f"{eda['rows']:,}")
    with o2:
        st.metric("Total Columns", eda["columns"])

    colA, colB = st.columns(2)
    with colA:
        st.subheader("🧩 Missing Values")
        missing_df = pd.DataFrame(list(eda["missing_values"].items()), columns=["Column", "Missing Count"])
        st.dataframe(missing_df, use_container_width=True, hide_index=True)

    with colB:
        st.subheader("🧾 Data Types")
        types_df = pd.DataFrame(list(eda["data_types"].items()), columns=["Column", "Data Type"])
        st.dataframe(types_df, use_container_width=True, hide_index=True)

    st.subheader("📝 Quick Summary (No LLM on Cloud)")
    st.markdown(simple_summary_text(df, eda))
    st.caption("Note: The AI/Ollama explanation runs locally in your full version, not on Streamlit Cloud.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Preview
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔎 Data Preview")
    st.dataframe(df.head(20), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Visualizations
# -----------------------------
if st.session_state.df is not None:
    st.markdown("---")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Data Visualizations")

    df = st.session_state.df
    numeric_cols = df.select_dtypes(include=["int64", "float64", "int32", "float32"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    if not numeric_cols:
        st.info("ℹ️ No numeric columns found. Upload a dataset with numeric columns to generate charts.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            selected_col = st.selectbox("📈 Primary Numeric Column", numeric_cols)

        secondary_col = None
        with filter_col2:
            if len(numeric_cols) > 1:
                secondary_col = st.selectbox(
                    "📌 Secondary Numeric Column (for scatter)",
                    ["None"] + [c for c in numeric_cols if c != selected_col]
                )
                if secondary_col == "None":
                    secondary_col = None

        group_by = None
        if categorical_cols:
            group_by = st.selectbox("📂 Group By (Optional)", ["None"] + categorical_cols)
            if group_by == "None":
                group_by = None

        chart_types = ["Line Chart", "Area Chart", "Pie Chart", "Histogram", "Box Plot", "Scatter Plot", "Correlation"]
        cols = st.columns(len(chart_types))
        for i, ct in enumerate(chart_types):
            with cols[i]:
                if st.button(ct, use_container_width=True, key=f"chart_{ct}"):
                    st.session_state.selected_chart_type = ct

        st.markdown(f"### ✅ Selected: {st.session_state.selected_chart_type}")

        # Plot
        ct = st.session_state.selected_chart_type

        if ct == "Line Chart":
            chart_data = df.groupby(group_by)[selected_col].mean() if group_by else df[selected_col]
            st.line_chart(chart_data, height=450)

        elif ct == "Area Chart":
            chart_data = df.groupby(group_by)[selected_col].mean() if group_by else df[selected_col]
            st.area_chart(chart_data, height=450)

        elif ct == "Pie Chart":
            if group_by:
                pie_data = df.groupby(group_by)[selected_col].mean().sort_values(ascending=False).head(10)
                title = f"{selected_col} (mean) by {group_by}"
            else:
                pie_data = df[selected_col].value_counts().head(10)
                title = f"Top values of {selected_col}"

            fig, ax = plt.subplots(figsize=(7, 5))
            ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%", startangle=90)
            ax.set_title(title)
            st.pyplot(fig)

        elif ct == "Histogram":
            fig, ax = plt.subplots(figsize=(10, 6))
            data = df[selected_col].dropna()
            ax.hist(data, bins=30)
            ax.set_title(f"Histogram of {selected_col}")
            ax.set_xlabel(selected_col)
            ax.set_ylabel("Frequency")
            st.pyplot(fig)

        elif ct == "Box Plot":
            fig, ax = plt.subplots(figsize=(10, 6))
            if group_by:
                groups = df[group_by].dropna().unique()[:15]
                data_to_plot = [df[df[group_by] == g][selected_col].dropna().values for g in groups]
                ax.boxplot(data_to_plot, labels=[str(g) for g in groups])
                ax.set_title(f"Box Plot of {selected_col} by {group_by}")
                plt.xticks(rotation=45, ha="right")
            else:
                ax.boxplot(df[selected_col].dropna().values, labels=[selected_col])
                ax.set_title(f"Box Plot of {selected_col}")
            st.pyplot(fig)

        elif ct == "Scatter Plot":
            if secondary_col is None:
                st.warning("Select a secondary numeric column to draw a scatter plot.")
            else:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.scatter(df[secondary_col], df[selected_col], alpha=0.6)
                ax.set_title(f"{selected_col} vs {secondary_col}")
                ax.set_xlabel(secondary_col)
                ax.set_ylabel(selected_col)
                st.pyplot(fig)

        elif ct == "Correlation":
            if len(numeric_cols) < 2:
                st.info("Need at least 2 numeric columns for correlation.")
            else:
                corr_cols = st.multiselect(
                    "Select columns for correlation",
                    numeric_cols,
                    default=numeric_cols[: min(10, len(numeric_cols))]
                )
                if len(corr_cols) < 2:
                    st.warning("Select at least 2 columns.")
                else:
                    corr = df[corr_cols].corr()
                    st.dataframe(corr.style.background_gradient(cmap="coolwarm"), use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Ask questions (Cloud-safe)
# -----------------------------
st.markdown("---")
st.markdown("""
<div class="card">
  <h2 style="margin:0 0 0.5rem 0;">💬 Questions (Cloud Demo)</h2>
  <p style="color:#b0b0b0; margin:0;">
    Streamlit Cloud can't run Ollama locally. For AI answers, run the full local version.
    Here you can ask EDA-style questions like: missing values, columns, shape, etc.
  </p>
</div>
""", unsafe_allow_html=True)

q = st.text_input("Ask a basic question (cloud-safe)", placeholder="e.g., Which column has the most missing values?")

if q and st.session_state.df is not None:
    df = st.session_state.df
    eda = compute_eda(df)
    ql = q.lower()

    if "missing" in ql:
        missing = pd.Series(eda["missing_values"]).sort_values(ascending=False)
        top = missing.head(10)
        st.write("Top columns with missing values:")
        st.dataframe(top.reset_index().rename(columns={"index": "Column", 0: "Missing"}), use_container_width=True, hide_index=True)
    elif "rows" in ql or "shape" in ql:
        st.write(f"Rows: {eda['rows']:,}, Columns: {eda['columns']}")
    elif "columns" in ql:
        st.write("Columns:")
        st.write(eda["column_names"])
    else:
        st.info("Cloud demo supports basic EDA answers. For full AI Q&A, run local version with FastAPI + Ollama.")


# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:2rem; color:#b0b0b0;">
  <p style="margin:0; font-size:0.9rem;">
    Cloud demo: EDA + Charts. Full version (local): FastAPI + Ollama for AI explanations.
  </p>
</div>
""", unsafe_allow_html=True)
