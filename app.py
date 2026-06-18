import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Video Game Sales Dashboard", layout="wide")
st.title("🎮 Video Game Sales Dashboard")
st.write("Explore global video game sales by year, platform, and region.")


@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_dataset (1).csv")
    return df

df = load_data()


st.sidebar.header("Filters")


min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
)


all_platforms = sorted(df["Platform"].unique())
selected_platforms = st.sidebar.multiselect(
    "Select Platform(s)",
    options=all_platforms,
    default=all_platforms,
)


sales_options = {
    "Global Sales": "Global_Sales",
    "North America Sales": "NA_Sales",
    "Europe Sales": "EU_Sales",
    "Japan Sales": "JP_Sales",
}
selected_label = st.sidebar.radio("Select Sales Region", options=list(sales_options.keys()))
sales_col = sales_options[selected_label]


filtered_df = df[
    (df["Year"] >= year_range[0])
    & (df["Year"] <= year_range[1])
    & (df["Platform"].isin(selected_platforms))
]

if filtered_df.empty:
    st.warning("No data matches the selected filters. Try widening your selection.")
    st.stop()

# ---------- KPI row ----------
col1, col2, col3 = st.columns(3)
col1.metric("Total Games", f"{len(filtered_df):,}")
col2.metric(f"Total {selected_label}", f"{filtered_df[sales_col].sum():,.2f}M")
col3.metric("Platforms Selected", len(selected_platforms))

st.divider()

# ---------- Charts ----------
chart_col1, chart_col2 = st.columns(2)

# Bar chart: sales by genre
with chart_col1:
    st.subheader(f"{selected_label} by Genre")
    genre_sales = (
        filtered_df.groupby("Genre")[sales_col]
        .sum()
        .reset_index()
        .sort_values(sales_col, ascending=False)
    )
    fig_bar = px.bar(
        genre_sales,
        x="Genre",
        y=sales_col,
        labels={sales_col: selected_label},
        color="Genre",
    )
    st.plotly_chart(fig_bar, use_container_width=True)


with chart_col2:
    st.subheader(f"{selected_label} Share by Platform")
    platform_sales = (
        filtered_df.groupby("Platform")[sales_col]
        .sum()
        .reset_index()
        .sort_values(sales_col, ascending=False)
    )
    top_n = 8
    if len(platform_sales) > top_n:
        top = platform_sales.head(top_n)
        other_sum = platform_sales[top_n:][sales_col].sum()
        other_row = pd.DataFrame({"Platform": ["Other"], sales_col: [other_sum]})
        platform_sales = pd.concat([top, other_row], ignore_index=True)
    fig_pie = px.pie(
        platform_sales,
        names="Platform",
        values=sales_col,
    )
    st.plotly_chart(fig_pie, use_container_width=True)


st.subheader(f"{selected_label} Trend Over Time")
yearly_sales = (
    filtered_df.groupby("Year")[sales_col]
    .sum()
    .reset_index()
    .sort_values("Year")
)
fig_line = px.line(
    yearly_sales,
    x="Year",
    y=sales_col,
    markers=True,
    labels={sales_col: selected_label},
)
st.plotly_chart(fig_line, use_container_width=True)


with st.expander("View Filtered Raw Data"):
    st.dataframe(filtered_df)
