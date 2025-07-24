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
    st.title("Sales Dashboard - Overview")

    selected_city = st.sidebar.selectbox("Select Outlet City", options=df['outlet_city'].unique())
    filtered_df = df[df['outlet_city'] == selected_city]

    # KPIs
    st.markdown("### Key Metrics")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Sales", f"{filtered_df['Total_sales'].sum():,.0f}")
    kpi2.metric("Avg. Luxury Sales", f"{filtered_df['luxury_sales'].mean():.2f}")
    kpi3.metric("Unique Customers", f"{filtered_df['Customer_ID'].nunique()}")
    kpi4.metric("Most Common Cluster", filtered_df['cluster_name'].mode()[0])

    # Charts
    st.markdown("### Visual Insights")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            px.bar(filtered_df.groupby('cluster_name')['Total_sales'].sum().reset_index(),
                   x='cluster_name', y='Total_sales', color='cluster_name',
                   title='Total Sales by Cluster'),
            use_container_width=True
        )

    with c2:
        st.plotly_chart(
            px.pie(filtered_df, names='cluster_name', values='Total_sales', hole=0.4,
                   title='Sales Distribution by Cluster'),
            use_container_width=True
        )

    st.plotly_chart(
        px.box(filtered_df, x='cluster_name', y='luxury_sales', color='cluster_name',
               title='Luxury Sales Distribution by Cluster'),
        use_container_width=True
    )

# ---- Cluster Analysis Page ----
elif page == "Cluster Analysis":
    st.title("Cluster-based Analysis")

    selected_cluster = st.sidebar.selectbox("Select Cluster Name", options=df['cluster_name'].unique())
    cluster_df = df[df['cluster_name'] == selected_cluster]

    st.markdown(f"### Insights for Cluster: {selected_cluster}")

    # Donut Charts
    col1, col2, col3 = st.columns(3)
    with col1:
        donut1 = px.pie(cluster_df, names='outlet_city', values='dry_sales', hole=0.5,
                        title="Dry Sales by City")
        st.plotly_chart(donut1, use_container_width=True)

    with col2:
        donut2 = px.pie(cluster_df, names='outlet_city', values='luxury_sales', hole=0.5,
                        title="Luxury Sales by City")
        st.plotly_chart(donut2, use_container_width=True)

    with col3:
        donut3 = px.pie(cluster_df, names='outlet_city', values='fresh_sales', hole=0.5,
                        title="Fresh Sales by City")
        st.plotly_chart(donut3, use_container_width=True)

    # Detailed KPI Metrics with Tabs
    st.markdown("### Sales Summary by Type")

    kpi_col = st.container()
    with kpi_col:
        tab1, tab2, tab3, tab4 = st.tabs(["Total Sales", "Luxury Sales", "Dry Sales", "Fresh Sales"])

        with tab1:
            t1, t2 = st.columns(2)
            t1.metric("Total Sales - Sum", f"{cluster_df['Total_sales'].sum():,.0f}")
            t2.metric("Total Sales - Average", f"{cluster_df['Total_sales'].mean():.2f}")

        with tab2:
            l1, l2 = st.columns(2)
            l1.metric("Luxury Sales - Sum", f"{cluster_df['luxury_sales'].sum():,.0f}")
            l2.metric("Luxury Sales - Average", f"{cluster_df['luxury_sales'].mean():.2f}")

        with tab3:
            d1, d2 = st.columns(2)
            d1.metric("Dry Sales - Sum", f"{cluster_df['dry_sales'].sum():,.0f}")
            d2.metric("Dry Sales - Average", f"{cluster_df['dry_sales'].mean():.2f}")

        with tab4:
            f1, f2 = st.columns(2)
            f1.metric("Fresh Sales - Sum", f"{cluster_df['fresh_sales'].sum():,.0f}")
            f2.metric("Fresh Sales - Average", f"{cluster_df['fresh_sales'].mean():.2f}")


    # Additional Charts
    ch1, ch2 = st.columns(2)
    with ch1:
        st.plotly_chart(
            px.histogram(cluster_df, x='outlet_city', y='Total_sales', histfunc='sum',
                         title='Total Sales by City'),
            use_container_width=True
        )
    # Sunburst Chart: Sales Hierarchy by City and Customer
    with ch2:
        # Group and filter cities with total sales > 1
        stacked_df = cluster_df.groupby('outlet_city')[['luxury_sales', 'dry_sales', 'fresh_sales']].sum()
        stacked_df['Total_sales'] = stacked_df.sum(axis=1)
        stacked_df = stacked_df[stacked_df['Total_sales'] > 1].drop(columns='Total_sales').reset_index()

# Create stacked bar chart
        stacked_bar = px.bar(
            stacked_df,
            x='outlet_city',
            y=['luxury_sales', 'dry_sales', 'fresh_sales'],
            title='Sales Breakdown by Outlet City (Filtered: Total Sales > 1)',
            labels={'value': 'Sales Amount', 'outlet_city': 'Outlet City', 'variable': 'Sales Type'},
            color_discrete_sequence=px.colors.qualitative.Plotly
        )

        st.plotly_chart(stacked_bar, use_container_width=True)





    st.plotly_chart(
        px.violin(cluster_df, y='luxury_sales', x='outlet_city', color='outlet_city',
                  title='Luxury Sales Spread by City'),
        use_container_width=True
    )

    with st.expander("View Cluster Data"):
        st.dataframe(cluster_df)
