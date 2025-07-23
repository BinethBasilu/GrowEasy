import streamlit as st
import pandas as pd
import plotly.express as px

# Set Streamlit page config
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# Load dataset
df = pd.read_csv("df_GrowEasyAnalytics.csv")  # Replace with your dataset path

# Sidebar Navigation
page = st.sidebar.selectbox("Select Page", ["Overview", "Cluster Analysis"])

# ---- Overview Page ----
if page == "Overview":
    st.title("🏪 Sales Dashboard - Overview")

    selected_city = st.sidebar.selectbox("Select Outlet City", options=df['outlet_city'].unique())
    filtered_df = df[df['outlet_city'] == selected_city]

    # KPIs
    st.markdown("### Key Metrics")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Sales", f"{filtered_df['Total_sales'].sum():,.0f}")
    kpi2.metric("Avg. Luxury Sales", f"{filtered_df['luxury_sales'].mean():.2f}")
    kpi3.metric("Unique Customers", f"{filtered_df['customer_ID'].nunique()}")
    kpi4.metric("Most Common Cluster", filtered_df['cluster_name'].mode()[0])

    # Charts
    st.markdown("### Visual Insights")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(filtered_df.groupby('cluster_name')['Total_sales'].sum().reset_index(),
                               x='cluster_name', y='Total_sales', color='cluster_name',
                               title='Total Sales by Cluster'), use_container_width=True)
    with c2:
        st.plotly_chart(px.pie(filtered_df, names='cluster_name', values='Total_sales',
                               title='Sales Distribution by Cluster'), use_container_width=True)

    st.plotly_chart(px.box(filtered_df, x='cluster_name', y='luxury_sales', color='cluster_name',
                           title='Luxury Sales Distribution by Cluster'), use_container_width=True)

# ---- Cluster Analysis Page ----
elif page == "Cluster Analysis":
    st.title("📊 Cluster-based Analysis")
    selected_cluster = st.sidebar.selectbox("Select Cluster Name", options=df['cluster_name'].unique())
    cluster_df = df[df['cluster_name'] == selected_cluster]

    st.markdown(f"### Insights for Cluster: {selected_cluster}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"{cluster_df['Total_sales'].sum():,.0f}")
    col2.metric("Average Dry Sales", f"{cluster_df['dry_sales'].mean():.2f}")
    col3.metric("Fresh Sales Total", f"{cluster_df['fresh_sales'].sum():,.0f}")

    ch1, ch2 = st.columns(2)
    with ch1:
        st.plotly_chart(px.histogram(cluster_df, x='outlet_city', y='Total_sales', histfunc='sum',
                                     title='Total Sales by City'), use_container_width=True)
    with ch2:
        st.plotly_chart(px.scatter(cluster_df, x='fresh_sales', y='dry_sales', color='outlet_city',
                                   title='Fresh vs Dry Sales by Outlet'), use_container_width=True)

    st.plotly_chart(px.violin(cluster_df, y='luxury_sales', x='outlet_city', color='outlet_city',
                              title='Luxury Sales Spread by City'), use_container_width=True)

    with st.expander("📄 View Cluster Data"):
        st.dataframe(cluster_df)
