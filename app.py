
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Marketing Campaign Performance",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Marketing Campaign Performance Insights")
st.markdown(
    "### End-to-End Data Analysis and Campaign Performance Dashboard"
)

st.write(
    "This project analyzes marketing campaign performance "
    "across companies, channels, customer segments, dates and locations."
)

# --------------------------------------------------
# 2. LOAD DATASET
# --------------------------------------------------

DATA_URL = (
    "https://raw.githubusercontent.com/ArchanaInsights/"
    "Datasets/main/marketing_campaign.csv"
)

DATA_FOLDER = Path("data")
DATA_FOLDER.mkdir(exist_ok=True)

DATA_FILE = DATA_FOLDER / "marketing_campaign.csv"


@st.cache_data
def load_data():
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.read_csv(DATA_URL)
        df.to_csv(DATA_FILE, index=False)

    return df


try:
    df = load_data()
except Exception as e:
    st.error("Unable to load the dataset. Check your internet connection.")
    st.code(str(e))
    st.stop()


# --------------------------------------------------
# 3. DATA CLEANING
# --------------------------------------------------

df.columns = df.columns.str.strip()

# Handle possible column-name variation
if "Channels_Used" in df.columns and "Channel_Used" not in df.columns:
    df.rename(columns={"Channels_Used": "Channel_Used"}, inplace=True)

# Remove duplicate records
df.drop_duplicates(inplace=True)

# Remove duplicate Campaign_ID records
if "Campaign_ID" in df.columns:
    df.drop_duplicates(subset=["Campaign_ID"], inplace=True)

# Clean currency values
df["Acquisition_Cost"] = pd.to_numeric(
    df["Acquisition_Cost"]
    .astype(str)
    .str.replace(r"[$,]", "", regex=True),
    errors="coerce"
)

# Clean Duration
df["Duration"] = pd.to_numeric(
    df["Duration"]
    .astype(str)
    .str.extract(r"(\d+)")[0],
    errors="coerce"
)

# Convert Date to datetime
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Convert numeric columns
numeric_columns = [
    "Conversion_Rate",
    "ROI",
    "Clicks",
    "Impressions",
    "Engagement_Score",
    "Acquisition_Cost",
    "Duration"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Remove rows with missing important analysis values
df.dropna(
    subset=[
        "Campaign_Type",
        "Channel_Used",
        "Conversion_Rate",
        "Acquisition_Cost",
        "ROI",
        "Date"
    ],
    inplace=True
)

# Create a folder for outputs
OUTPUT_FOLDER = Path("outputs")
OUTPUT_FOLDER.mkdir(exist_ok=True)

# --------------------------------------------------
# 4. SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

companies = ["All"] + sorted(df["Company"].dropna().unique().tolist())
channels = ["All"] + sorted(df["Channel_Used"].dropna().unique().tolist())
campaign_types = ["All"] + sorted(df["Campaign_Type"].dropna().unique().tolist())

selected_company = st.sidebar.selectbox(
    "Select Company", companies
)

selected_channel = st.sidebar.selectbox(
    "Select Channel", channels
)

selected_campaign = st.sidebar.selectbox(
    "Select Campaign Type", campaign_types
)

filtered_df = df.copy()

if selected_company != "All":
    filtered_df = filtered_df[
        filtered_df["Company"] == selected_company
    ]

if selected_channel != "All":
    filtered_df = filtered_df[
        filtered_df["Channel_Used"] == selected_channel
    ]

if selected_campaign != "All":
    filtered_df = filtered_df[
        filtered_df["Campaign_Type"] == selected_campaign
    ]

# --------------------------------------------------
# 5. KEY PERFORMANCE INDICATORS
# --------------------------------------------------

st.header("1. Campaign Performance Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Campaigns",
    f"{len(filtered_df):,}"
)

c2.metric(
    "Average Conversion Rate",
    f"{filtered_df['Conversion_Rate'].mean():.2%}"
)

c3.metric(
    "Average ROI",
    f"{filtered_df['ROI'].mean():.2f}"
)

c4.metric(
    "Average Acquisition Cost",
    f"${filtered_df['Acquisition_Cost'].mean():,.2f}"
)

st.divider()

# --------------------------------------------------
# 6. DESCRIPTIVE ANALYSIS
# --------------------------------------------------

st.header("2. Descriptive Analysis")

with st.expander("View Dataset Information"):

    st.subheader("First Five Rows")
    st.dataframe(df.head())

    st.subheader("Dataset Shape")
    st.write("Rows and Columns:", df.shape)

    st.subheader("Dataset Information")
    info_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Non-Null Values": df.notna().sum().values
    })
    st.dataframe(info_df)

    st.subheader("Descriptive Statistics")
    st.dataframe(df.describe(include="all").T)

    st.subheader("Unique Campaign IDs")
    st.write(df["Campaign_ID"].nunique())

    st.subheader("Unique Locations")
    st.write(df["Location"].unique().tolist())

    st.subheader("Unique Customer Segments")
    st.write(df["Customer_Segment"].unique().tolist())

    st.subheader("Campaign Type Counts")
    st.dataframe(df["Campaign_Type"].value_counts())

    st.subheader("Channel Counts")
    st.dataframe(df["Channel_Used"].value_counts())

    st.subheader("Missing Values")
    st.dataframe(df.isnull().sum().to_frame("Missing Values"))

# --------------------------------------------------
# 7. CAMPAIGN PERFORMANCE ANALYSIS
# --------------------------------------------------

st.header("3. Campaign Performance Analysis")

# Chart 1: Acquisition Cost vs ROI

fig1 = px.scatter(
    filtered_df,
    x="Acquisition_Cost",
    y="ROI",
    color="Campaign_Type",
    title="Acquisition Cost vs ROI",
    hover_data=["Company", "Channel_Used"]
)

st.plotly_chart(fig1, use_container_width=True)

# Chart 2: Conversion Rate by Channel and Campaign Type

conversion_channel = (
    filtered_df.groupby(
        ["Channel_Used", "Campaign_Type"],
        as_index=False
    )["Conversion_Rate"].mean()
)

fig2 = px.bar(
    conversion_channel,
    x="Channel_Used",
    y="Conversion_Rate",
    color="Campaign_Type",
    barmode="group",
    title="Average Conversion Rate by Channel and Campaign Type"
)

st.plotly_chart(fig2, use_container_width=True)

# Chart 3: Engagement Score Box Plot

fig3 = px.box(
    filtered_df,
    x="Campaign_Type",
    y="Engagement_Score",
    color="Campaign_Type",
    title="Engagement Score Distribution by Campaign Type"
)

st.plotly_chart(fig3, use_container_width=True)

# Chart 4: Average ROI by Company

roi_company = (
    filtered_df.groupby("Company", as_index=False)["ROI"]
    .mean()
    .sort_values("ROI", ascending=False)
)

fig4 = px.bar(
    roi_company,
    x="Company",
    y="ROI",
    color="ROI",
    title="Average ROI by Company"
)

st.plotly_chart(fig4, use_container_width=True)

# Chart 5: Engagement and Conversion Correlation Heatmap

corr = filtered_df[
    ["Engagement_Score", "Conversion_Rate"]
].corr()

fig5 = px.imshow(
    corr,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    title="Engagement Score and Conversion Rate Correlation"
)

st.plotly_chart(fig5, use_container_width=True)

# --------------------------------------------------
# 8. CUSTOMER SEGMENTATION
# --------------------------------------------------

st.header("4. Customer Segmentation Analysis")

# Chart 6: Target Audience Count

audience_count = (
    filtered_df["Target_Audience"]
    .value_counts()
    .reset_index()
)

audience_count.columns = ["Target_Audience", "Count"]

fig6 = px.bar(
    audience_count,
    x="Target_Audience",
    y="Count",
    color="Count",
    title="Distribution of Target Audience"
)

st.plotly_chart(fig6, use_container_width=True)

# Chart 7: Highest Conversion Segment for Each Language

language_segment = (
    filtered_df.groupby(
        ["Language", "Customer_Segment"],
        as_index=False
    )["Conversion_Rate"].mean()
)

best_segments = (
    language_segment.sort_values(
        "Conversion_Rate",
        ascending=False
    )
    .drop_duplicates(subset=["Language"])
)

st.subheader("Best Customer Segment by Language")
st.dataframe(best_segments)

fig7 = px.bar(
    best_segments,
    x="Language",
    y="Conversion_Rate",
    color="Customer_Segment",
    title="Highest Conversion Customer Segment by Language"
)

st.plotly_chart(fig7, use_container_width=True)

# Chart 8: Acquisition Cost by Segment and Channel

fig8 = px.box(
    filtered_df,
    x="Customer_Segment",
    y="Acquisition_Cost",
    color="Channel_Used",
    title="Acquisition Cost by Customer Segment and Channel"
)

st.plotly_chart(fig8, use_container_width=True)

# Chart 9: Average Conversion Rate by Language

language_conversion = (
    filtered_df.groupby("Language", as_index=False)
    ["Conversion_Rate"].mean()
)

fig9 = px.bar(
    language_conversion,
    x="Language",
    y="Conversion_Rate",
    color="Conversion_Rate",
    title="Average Conversion Rate by Language"
)

st.plotly_chart(fig9, use_container_width=True)

# --------------------------------------------------
# 9. CHANNEL EFFECTIVENESS
# --------------------------------------------------

st.header("5. Channel Effectiveness Analysis")

# Chart 10: Engagement by Channel and Campaign Type

channel_engagement = (
    filtered_df.groupby(
        ["Channel_Used", "Campaign_Type"],
        as_index=False
    )["Engagement_Score"].mean()
)

fig10 = px.bar(
    channel_engagement,
    x="Channel_Used",
    y="Engagement_Score",
    color="Campaign_Type",
    barmode="group",
    title="Engagement Score by Channel and Campaign Type"
)

st.plotly_chart(fig10, use_container_width=True)

# Chart 11: Total ROI by Channel

channel_roi = (
    filtered_df.groupby("Channel_Used", as_index=False)["ROI"]
    .sum()
)

fig11 = px.pie(
    channel_roi,
    names="Channel_Used",
    values="ROI",
    title="Distribution of Total ROI by Channel",
    hole=0.35
)

st.plotly_chart(fig11, use_container_width=True)

# Chart 12: Clicks vs Impressions

fig12 = px.scatter(
    filtered_df,
    x="Impressions",
    y="Clicks",
    color="Channel_Used",
    title="Clicks vs Impressions by Channel",
    hover_data=["Company"]
)

st.plotly_chart(fig12, use_container_width=True)

# --------------------------------------------------
# 10. TIME-BASED ANALYSIS
# --------------------------------------------------

st.header("6. Time-Based Analysis")

# Chart 13: Duration Distribution

fig13 = px.histogram(
    filtered_df,
    x="Duration",
    nbins=20,
    title="Distribution of Campaign Duration"
)

st.plotly_chart(fig13, use_container_width=True)

# Chart 14: Conversion Rate Over Date by Company

date_company = (
    filtered_df.groupby(
        [pd.Grouper(key="Date", freq="ME"), "Company"],
        as_index=False
    )["Conversion_Rate"].mean()
)

fig14 = px.line(
    date_company,
    x="Date",
    y="Conversion_Rate",
    color="Company",
    markers=True,
    title="Conversion Rate Over Time by Company"
)

st.plotly_chart(fig14, use_container_width=True)

# Chart 15: Engagement Score Over Date

date_engagement = (
    filtered_df.groupby(
        pd.Grouper(key="Date", freq="ME")
    )["Engagement_Score"]
    .mean()
    .reset_index()
)

fig15 = px.line(
    date_engagement,
    x="Date",
    y="Engagement_Score",
    markers=True,
    title="Engagement Score Trend Over Time"
)

st.plotly_chart(fig15, use_container_width=True)

# --------------------------------------------------
# 11. GEOGRAPHIC ANALYSIS
# --------------------------------------------------

st.header("7. Geographic Analysis")

# Chart 16: Average Acquisition Cost by Location

location_cost = (
    filtered_df.groupby("Location", as_index=False)
    ["Acquisition_Cost"].mean()
    .sort_values("Acquisition_Cost", ascending=False)
)

fig16 = px.bar(
    location_cost,
    x="Location",
    y="Acquisition_Cost",
    color="Acquisition_Cost",
    title="Average Acquisition Cost by Location"
)

st.plotly_chart(fig16, use_container_width=True)

# Chart 17: Conversion Rate by Location and Target Audience

location_conversion = (
    filtered_df.groupby(
        ["Location", "Target_Audience"],
        as_index=False
    )["Conversion_Rate"].mean()
)

fig17 = px.bar(
    location_conversion,
    x="Location",
    y="Conversion_Rate",
    color="Target_Audience",
    barmode="group",
    title="Conversion Rate by Location and Target Audience"
)

st.plotly_chart(fig17, use_container_width=True)

# Chart 18: ROI by Location

location_roi = (
    filtered_df.groupby("Location", as_index=False)["ROI"]
    .sum()
)

fig18 = px.pie(
    location_roi,
    names="Location",
    values="ROI",
    title="Proportion of ROI by Location"
)

st.plotly_chart(fig18, use_container_width=True)

# --------------------------------------------------
# 12. AUTOMATIC BUSINESS INSIGHTS
# --------------------------------------------------

st.header("8. Key Business Insights")

if not filtered_df.empty:

    best_company = (
        filtered_df.groupby("Company")["ROI"].mean().idxmax()
    )

    best_channel = (
        filtered_df.groupby("Channel_Used")
        ["Conversion_Rate"].mean().idxmax()
    )

    best_location = (
        filtered_df.groupby("Location")
        ["Acquisition_Cost"].mean().idxmax()
    )

    best_language = (
        filtered_df.groupby("Language")
        ["Conversion_Rate"].mean().idxmax()
    )

    best_segment = (
        filtered_df.groupby("Customer_Segment")
        ["Conversion_Rate"].mean().idxmax()
    )

    col1, col2 = st.columns(2)

    col1.success(f"Highest Average ROI Company: {best_company}")
    col1.info(f"Best Conversion Channel: {best_channel}")

    col2.warning(f"Highest Average Acquisition Cost Location: {best_location}")
    col2.info(f"Best Performing Language: {best_language}")

    st.success(f"Best Converting Customer Segment: {best_segment}")

    st.subheader("Recommendations")

    st.write(
        "1. Focus on channels that generate higher conversion rates."
    )

    st.write(
        "2. Analyze high acquisition cost locations to improve marketing efficiency."
    )

    st.write(
        "3. Invest in customer segments that demonstrate stronger conversion rates."
    )

    st.write(
        "4. Monitor engagement trends to improve campaign performance."
    )

    st.write(
        "5. Compare company ROI before allocating future campaign budgets."
    )

else:
    st.warning("No data available for the selected filters.")

# --------------------------------------------------
# 13. DOWNLOAD ANALYSIS DATA
# --------------------------------------------------

st.header("9. Download Results")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Cleaned Dataset",
    data=csv_data,
    file_name="cleaned_marketing_campaign.csv",
    mime="text/csv"
)

st.success("Marketing Campaign Analysis Completed Successfully!")

st.caption("Developed using Python, Pandas, Plotly and Streamlit.")
