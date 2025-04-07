import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("data/mit_courses_with_years.csv")

df = load_data()

# Sidebar — Filters
st.sidebar.title("🎛️ Filters")

years = sorted(df["year"].unique())
departments = sorted(df["department"].unique())
all_keywords = ['ai', 'data', 'machine learning', 'python', 'sql', 'statistics']

selected_years = st.sidebar.multiselect("Select Years", years, default=years[-3:])
selected_departments = st.sidebar.multiselect("Select Departments", departments, default=['EECS', 'Mathematics'])

selected_keywords = st.sidebar.multiselect(
    "Keywords (select multiple)",
    options=all_keywords,
    default=all_keywords[:5]
)

# Filter data
filtered_df = df[
    df["year"].isin(selected_years) &
    df["department"].isin(selected_departments)
]

# Count keyword mentions
def count_keywords(text, keywords):
    return {kw: text.lower().count(kw.lower()) for kw in keywords}

keyword_counts = {kw: [] for kw in selected_keywords}
year_labels = []

for year in sorted(filtered_df["year"].unique()):
    yearly_data = filtered_df[filtered_df["year"] == year]
    combined_text = " ".join(yearly_data["description"].dropna().tolist())
    counts = count_keywords(combined_text, selected_keywords)
    for kw in selected_keywords:
        keyword_counts[kw].append(counts[kw])
    year_labels.append(str(year))

# 📊 Keyword Trends Over Time
st.markdown("### 📈 Keyword Trends Over Time")

df_chart = pd.DataFrame(keyword_counts, index=year_labels)
fig = px.line(df_chart, x=df_chart.index, y=df_chart.columns,
              markers=True,
              labels={"value": "Mentions", "index": "Year"},
              color_discrete_sequence=px.colors.qualitative.Safe)

fig.update_layout(height=400, margin=dict(t=10, r=10, l=10, b=10))

st.plotly_chart(fig, use_container_width=True)

# 📦 Keyword Mentions by Department
st.markdown("### 🏛️ Keyword Mentions by Department")

dept_counts = []

for dept in selected_departments:
    dept_data = filtered_df[filtered_df["department"] == dept]
    combined_text = " ".join(dept_data["description"].dropna().tolist())
    counts = count_keywords(combined_text, selected_keywords)
    counts["Department"] = dept
    dept_counts.append(counts)

df_dept = pd.DataFrame(dept_counts).set_index("Department")

fig_bar = px.bar(df_dept, barmode="stack",
                 labels={"value": "Mentions", "Department": "Department"},
                 color_discrete_sequence=px.colors.qualitative.Safe)

fig_bar.update_layout(height=400, margin=dict(t=10, r=10, l=10, b=10))
st.plotly_chart(fig_bar, use_container_width=True)

# ☁️ Word Cloud
st.markdown("### ☁️ Word Cloud of Course Descriptions")

combined_text = " ".join(filtered_df["description"].dropna().tolist())
wordcloud = WordCloud(background_color="white", width=800, height=400).generate(combined_text)

buf = BytesIO()
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.tight_layout(pad=0)
plt.savefig(buf, format="png")
st.image(Image.open(buf), use_column_width=True)

# ⬇️ Download Filtered Data
st.markdown("### ⬇️ Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "filtered_courses.csv", "text/csv")

# ✅ Summary Stats
st.markdown(f"**Total Courses Matching Filters: {filtered_df.shape[0]}**")

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit. | MIT Curriculum Trend Analyzer")
