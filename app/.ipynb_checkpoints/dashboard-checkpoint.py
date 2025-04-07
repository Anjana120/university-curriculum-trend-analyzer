# /app/dashboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="University Curriculum Trend Analyzer", layout="wide")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("data/mit_courses_with_years.csv")

df = load_data()
df.dropna(subset=["description"], inplace=True)
df["description"] = df["description"].str.lower()

# Sidebar filters
st.sidebar.title("Filters")
selected_years = st.sidebar.multiselect("Select Years", sorted(df["year"].unique()), default=sorted(df["year"].unique()))
selected_departments = st.sidebar.multiselect("Select Departments", df["department"].unique(), default=df["department"].unique())

# Filter data
filtered_df = df[df["year"].isin(selected_years) & df["department"].isin(selected_departments)]

# Keyword input
default_keywords = ["python", "machine learning", "data", "ai", "statistics", "sql"]
keywords = st.sidebar.text_input("Keywords (comma-separated)", ", ".join(default_keywords))
keywords = [kw.strip().lower() for kw in keywords.split(",") if kw.strip()]

# Compute keyword frequencies
st.title("📊 University Curriculum Trend Analyzer")

st.markdown(f"**Total Courses Matching Filters:** {len(filtered_df)}")


if not filtered_df.empty:
    # Count by department
    dept_counts = {dept: {kw: 0 for kw in keywords} for dept in filtered_df["department"].unique()}
    for _, row in filtered_df.iterrows():
        desc = row["description"]
        dept = row["department"]
        for kw in keywords:
            if kw in desc:
                dept_counts[dept][kw] += 1
    dept_df = pd.DataFrame(dept_counts).T

    # Plot bar chart
    with st.expander("📊 Keyword Mentions by Department", expanded=True):
         st.bar_chart(dept_df)

    # Add download button for filtered data
    st.subheader("⬇️ Download Filtered Data")
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_courses.csv",
    mime="text/csv"
)


    # Trend over time
    yearly_counts = []
    for year in sorted(filtered_df["year"].unique()):
        temp = filtered_df[filtered_df["year"] == year]
        all_text = " ".join(temp["description"])
        counts = {kw: all_text.count(kw) for kw in keywords}
        counts["year"] = year
        yearly_counts.append(counts)
    trend_df = pd.DataFrame(yearly_counts).set_index("year")

    with st.expander("📈 Keyword Trends Over Time", expanded=True):
         st.line_chart(trend_df)



else:
    st.warning("No data found for the selected filters.")

# Generate word cloud
from wordcloud import WordCloud

with st.expander("☁️ Word Cloud of Course Descriptions", expanded=True):
    text = " ".join(filtered_df["description"])
    if text.strip():
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        st.image(wordcloud.to_array(), use_column_width=True)
    else:
        st.info("Not enough text to generate a word cloud.")

