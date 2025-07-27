import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# ===== DATASET CONFIGURATION =====
# Replace with your actual dataset filename
DATASET_FILENAME = "GrowEasyAnalytics_1.csv"
# ===== END DATASET CONFIGURATION =====

# Page configuration
st.set_page_config(
    page_title="Sri Lanka Supermarket Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 20px rgba(255, 107, 107, 0.3)); }
        to { filter: drop-shadow(0 0 30px rgba(78, 205, 196, 0.5)); }
    }
    
    .hero-kpi {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        animation: pulse 3s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }
    
    .chart-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def create_customer_insights_box(df):
    """Create customer insights summary"""
    insights = []
    
    # Top spending customer segment
    top_segment = df.groupby('cluster_catgeory')['Total_sales'].sum().idxmax()
    top_segment_revenue = df.groupby('cluster_catgeory')['Total_sales'].sum().max()
    insights.append(f"**{top_segment}** is our highest revenue segment with LKR {top_segment_revenue:,.0f}")
    
    # Most valuable city
    top_city = df.groupby('outlet_city')['Total_sales'].sum().idxmax()
    top_city_customers = df[df['outlet_city'] == top_city]['Customer_ID'].nunique()
    insights.append(f"**{top_city}** leads with {top_city_customers:,} customers")
    
    # Category leader
    categories = {'Luxury': df['luxury_sales'].sum(), 
                 'Fresh': df['fresh_sales'].sum(), 
                 'Dry Goods': df['dry_sales'].sum()}
    top_category = max(categories, key=categories.get)
    insights.append(f"**{top_category}** dominates sales with LKR {categories[top_category]:,.0f}")
    
    # Customer spending pattern
    high_spenders = len(df[df['Total_sales'] > df['Total_sales'].quantile(0.9)])
    total_customers = df['Customer_ID'].nunique()
    insights.append(f"{high_spenders:,} customers ({(high_spenders/total_customers)*100:.1f}%) are premium spenders")
    
    return insights

# Main Dashboard
def main():
    # Load data
    df = pd.read_csv("GrowEasyAnalytics_1.csv")
    
    # Header
    st.markdown('<h1 class="main-header">Sri Lanka Supermarket Chain Analytics</h1>', unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.header("Dashboard Controls")
    
    # City filter
    all_cities = ['All Cities'] + sorted(df['outlet_city'].unique().tolist())
    selected_cities = st.sidebar.multiselect(
        "Select Cities:",
        options=df['outlet_city'].unique(),
        default=df['outlet_city'].unique()
    )
    
    # Customer segment filter
    all_segments = ['All Segments'] + sorted(df['cluster_catgeory'].unique().tolist())
    selected_segments = st.sidebar.multiselect(
        "Select Customer Segments:",
        options=df['cluster_catgeory'].unique(),
        default=df['cluster_catgeory'].unique()
    )
    
    # Sales range filter
    min_sales = int(df['Total_sales'].min())
    max_sales = int(df['Total_sales'].max())
    sales_range = st.sidebar.slider(
        "Total Sales Range (LKR):",
        min_value=min_sales,
        max_value=max_sales,
        value=(min_sales, max_sales),
        step=1000,
        format="LKR %d"
    )
    
    # Apply filters
    filtered_df = df[
        (df['outlet_city'].isin(selected_cities)) &
        (df['cluster_catgeory'].isin(selected_segments)) &
        (df['Total_sales'] >= sales_range[0]) &
        (df['Total_sales'] <= sales_range[1])
    ]
    
    # Dataset info
    st.sidebar.info(f"""
    **Dataset Overview**
    - **Records:** {len(filtered_df):,} of {len(df):,}
    - **Cities:** {filtered_df['outlet_city'].nunique()}
    - **Customers:** {filtered_df['Customer_ID'].nunique():,}
    - **Segments:** {filtered_df['cluster_catgeory'].nunique()}
    """)
    
    # Hero metrics
    create_hero_metrics(filtered_df)
    
    # Customer insights
    st.header("Key Business Insights")
    insights = create_customer_insights_box(filtered_df)
    
    col_insight1, col_insight2 = st.columns(2)
    with col_insight1:
        for insight in insights[:2]:
            st.info(insight)
    with col_insight2:
        for insight in insights[2:]:
            st.info(insight)
    
    # Interactive visualizations
    st.header("Interactive Analytics Dashboard")
    
    # First row - Main donut charts
    st.subheader("Sales Distribution Analysis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_category = create_category_donut_chart(filtered_df)
        st.plotly_chart(fig_category, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_city = create_city_revenue_donut(filtered_df)
        st.plotly_chart(fig_city, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_cluster = create_cluster_donut_chart(filtered_df)
        st.plotly_chart(fig_cluster, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Second row - Category-specific donut charts
    st.subheader("Category-Specific Performance")
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_luxury = create_top_cities_luxury_donut(filtered_df)
        st.plotly_chart(fig_luxury, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col5:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_fresh = create_fresh_sales_donut(filtered_df)
        st.plotly_chart(fig_fresh, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col6:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_tiers = create_customer_spending_tiers_donut(filtered_df)
        st.plotly_chart(fig_tiers, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Third row - Additional donut chart and bar chart
    st.subheader("Advanced Analytics")
    col7, col8 = st.columns(2)
    
    with col7:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_cluster_breakdown = create_cluster_category_breakdown_donut(filtered_df)
        st.plotly_chart(fig_cluster_breakdown, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col8:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_racing = create_city_performance_racing_bar(filtered_df)
        st.plotly_chart(fig_racing, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Fourth row - Scatter plot and heatmap
    st.subheader("Customer Behavior Analysis")
    col9, col10 = st.columns(2)
    
    with col9:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_scatter = create_customer_segment_analysis(filtered_df)
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col10:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_heatmap = create_sales_trends_heatmap(filtered_df)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance metrics table
    st.header("Detailed Performance Metrics")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    metrics_table = create_performance_metrics_table(filtered_df)
    st.dataframe(metrics_table, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Data explorer
    with st.expander("Raw Data Explorer"):
        st.subheader("Filtered Dataset")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Download options
        col_d1, col_d2, col_d3 = st.columns(3)
        
        with col_d1:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"supermarket_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col_d2:
            # Summary statistics
            summary_stats = filtered_df.describe()
            summary_csv = summary_stats.to_csv()
            st.download_button(
                label="Download Summary Stats",
                data=summary_csv,
                file_name=f"summary_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col_d3:
            # City-wise summary
            city_summary = create_performance_metrics_table(filtered_df)
            city_csv = city_summary.to_csv(index=False)
            st.download_button(
                label="Download City Summary",
                data=city_csv,
                file_name=f"city_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; padding: 30px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; color: white; margin-top: 30px;'>
            <h3 style='margin: 0; font-weight: 300;'>Sri Lanka Supermarket Chain Analytics Dashboard</h3>
            <p style='margin: 10px 0 0 0; opacity: 0.8;'>
                Empowering data-driven decisions across {len(df['outlet_city'].unique())} cities • 
                {len(df):,} transactions analyzed • Built with Streamlit & Plotly
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
def create_hero_metrics(df):
    """Create stunning hero metrics for supermarket chain"""
    total_revenue = df['Total_sales'].sum()
    total_customers = df['Customer_ID'].nunique()
    total_outlets = df['outlet_city'].nunique()
    avg_basket_value = df['Total_sales'].mean()
    
    # Hero Revenue Display
    st.markdown(f"""
    <div class="hero-kpi">
        <h1 style='font-size: 4rem; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
            LKR {total_revenue:,.0f}
        </h1>
        <h3 style='margin: 0; font-weight: 300; opacity: 0.9;'>Total Chain Revenue</h3>
        <p style='margin: 10px 0 0 0; opacity: 0.8;'>Across {total_outlets} cities • {total_customers:,} customers</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Performance Indicators
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        luxury_revenue = df['luxury_sales'].sum()
        luxury_share = (luxury_revenue / total_revenue) * 100
        st.metric(
            label="Luxury Sales",
            value=f"LKR {luxury_revenue:,.0f}",
            delta=f"{luxury_share:.1f}% of total",
            help="Premium category performance"
        )
    
    with col2:
        fresh_revenue = df['fresh_sales'].sum()
        fresh_share = (fresh_revenue / total_revenue) * 100
        st.metric(
            label="Fresh Sales",
            value=f"LKR {fresh_revenue:,.0f}",
            delta=f"{fresh_share:.1f}% of total",
            help="Fresh produce performance"
        )
    
    with col3:
        dry_revenue = df['dry_sales'].sum()
        dry_share = (dry_revenue / total_revenue) * 100
        st.metric(
            label="Dry Goods Sales",
            value=f"LKR {dry_revenue:,.0f}",
            delta=f"{dry_share:.1f}% of total",
            help="Dry goods category performance"
        )
    
    with col4:
        top_city = df.groupby('outlet_city')['Total_sales'].sum().idxmax()
        top_city_revenue = df.groupby('outlet_city')['Total_sales'].sum().max()
        st.metric(
            label="Top Performing City",
            value=top_city,
            delta=f"LKR {top_city_revenue:,.0f}",
            help="Highest revenue generating city"
        )
    
    with col5:
        high_value_customers = len(df[df['Total_sales'] > df['Total_sales'].quantile(0.8)])
        st.metric(
            label="Premium Customers",
            value=f"{high_value_customers:,}",
            delta=f"LKR {avg_basket_value:,.0f} avg basket",
            help="Top 20% customers by spending"
        )

def create_category_donut_chart(df):
    """Create main category distribution donut chart"""
    categories = {
        'Luxury Sales': df['luxury_sales'].sum(),
        'Fresh Sales': df['fresh_sales'].sum(),
        'Dry Goods Sales': df['dry_sales'].sum()
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=list(categories.keys()),
        values=list(categories.values()),
        hole=0.6,
        marker=dict(
            colors=['#FF6B6B', '#4ECDC4', '#45B7D1'],
            line=dict(color='#FFFFFF', width=2)
        ),
        textinfo='label+percent+value',
        texttemplate='<b>%{label}</b><br>%{percent}<br>LKR %{value:,.0f}',
        hovertemplate='<b>%{label}</b><br>Revenue: LKR %{value:,.0f}<br>Percentage: %{percent}<extra></extra>',
        textposition='auto',
        textfont=dict(size=12)
    )])
    
    fig.update_layout(
        title={
            'text': "Sales Distribution by Category",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2E2E2E'}
        },
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=-0.2, 
            xanchor="center", 
            x=0.5
        ),
        annotations=[dict(
            text='Category<br>Distribution', 
            x=0.5, y=0.5, 
            font_size=16, 
            showarrow=False,
            font_color='#2E2E2E'
        )],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_city_revenue_donut(df):
    """Create city-wise revenue donut chart"""
    city_revenue = df.groupby('outlet_city')['Total_sales'].sum().sort_values(ascending=False)
    
    # Take top 10 cities and group others
    if len(city_revenue) > 10:
        top_cities = city_revenue.head(10)
        others_sum = city_revenue.tail(len(city_revenue) - 10).sum()
        if others_sum > 0:
            top_cities['Others'] = others_sum
        city_data = top_cities
    else:
        city_data = city_revenue
    
    fig = go.Figure(data=[go.Pie(
        labels=city_data.index,
        values=city_data.values,
        hole=0.5,
        marker=dict(
            colors=px.colors.qualitative.Set3[:len(city_data)],
            line=dict(color='#FFFFFF', width=2)
        ),
        textinfo='label+percent',
        texttemplate='<b>%{label}</b><br>%{percent}',
        hovertemplate='<b>%{label}</b><br>Revenue: LKR %{value:,.0f}<br>Share: %{percent}<extra></extra>',
        textfont=dict(size=11)
    )])
    
    fig.update_layout(
        title={
            'text': "Revenue Distribution by City",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2E2E2E'}
        },
        height=500,
        showlegend=True,
        legend=dict(
            orientation="v", 
            yanchor="middle", 
            y=0.5, 
            xanchor="left", 
            x=1.05
        ),
        annotations=[dict(
            text='City<br>Performance', 
            x=0.5, y=0.5, 
            font_size=14, 
            showarrow=False,
            font_color='#2E2E2E'
        )],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_cluster_donut_chart(df):
    """Create customer cluster distribution donut chart"""
    cluster_data = df.groupby('cluster_catgeory')['Total_sales'].sum()
    
    fig = go.Figure(data=[go.Pie(
        labels=cluster_data.index,
        values=cluster_data.values,
        hole=0.6,
        marker=dict(
            colors=['#FF9999', '#66B2FF', '#99FF99', '#FFB366', '#FF6B9D', '#C4B5FD'],
            line=dict(color='#FFFFFF', width=2)
        ),
        textinfo='label+percent',
        texttemplate='<b>%{label}</b><br>%{percent}',
        hovertemplate='<b>%{label}</b><br>Revenue: LKR %{value:,.0f}<br>Share: %{percent}<extra></extra>',
        pull=[0.1 if v == cluster_data.max() else 0 for v in cluster_data.values],
        textfont=dict(size=11)
    )])
    
    fig.update_layout(
        title={
            'text': "Revenue by Customer Segments",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2E2E2E'}
        },
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=-0.2, 
            xanchor="center", 
            x=0.5
        ),
        annotations=[dict(
            text='Customer<br>Segments', 
            x=0.5, y=0.5, 
            font_size=14, 
            showarrow=False,
            font_color='#2E2E2E'
        )],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_top_cities_luxury_donut(df):
    """Create luxury sales distribution donut for top cities"""
    city_luxury = df.groupby('outlet_city')['luxury_sales'].sum().sort_values(ascending=False).head(8)
    
    fig = go.Figure(data=[go.Pie(
        labels=city_luxury.index,
        values=city_luxury.values,
        hole=0.55,
        marker=dict(
            colors=px.colors.sequential.Plasma[:len(city_luxury)],
            line=dict(color='#FFFFFF', width=2)
        ),
        textinfo='label+percent',
        texttemplate='<b>%{label}</b><br>%{percent}',
        hovertemplate='<b>%{label}</b><br>Luxury Sales: LKR %{value:,.0f}<br>Share: %{percent}<extra></extra>',
        textfont=dict(size=10)
    )])
    
    fig.update_layout(
        title={
            'text': "Luxury Sales by Top Cities",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2E2E2E'}
        },
        height=500,
        showlegend=True,
        legend=dict(
            orientation="v", 
            yanchor="middle", 
            y=0.5, 
            xanchor="left", 
            x=1.05
        ),
        annotations=[dict(
            text='Luxury<br>Markets', 
            x=0.5, y=0.5, 
            font_size=14, 
            showarrow=False,
            font_color='#2E2E2E'
        )],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_fresh_sales_donut(df):
    """Create fresh sales distribution donut for top cities"""
    city_fresh = df.groupby('outlet_city')['fresh_sales'].sum().sort_values(ascending=False).head(8)
    
    fig = go.Figure(data=[go.Pie(
        labels=city_fresh.index,
        values=city_fresh.values,
        hole=0.55,
        marker=dict(
            colors=px.colors.sequential.Greens[:len(city_fresh)],
            line=dict(color='#FFFFFF', width=2)
        ),
        textinfo='label+percent',
        texttemplate='<b>%{label}</b><br>%{percent}',
        hovertemplate='<b>%{label}</b><br>Fresh Sales: LKR %{value:,.0f}<br>Share: %{percent}<extra></extra>',
        textfont=dict(size=10)
    )])
    
    fig.update_layout(
        title={
            'text': "Fresh Produce Sales by Top Cities",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2E2E2E'}
        },
        height=500,
        showlegend=True,
        legend=dict(
            orientation="v", 
            yanchor="middle", 
            y=0.5, 
            xanchor="left", 
            x=1.05
        ),
        annotations=[dict(
            text='Fresh<br>Produce', 
            x=0.5, y=0.5, 
            font_size=14, 
            showarrow=False,
            font_color='#2E2E2E'
        )],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_customer_spending_tiers_donut(df):
    """Create customer spending tiers donut chart"""
    # Create spending tiers
    df_copy = df.copy()
    spending_ranges = pd.cut(df_copy['Total_sales'], 
                           bins=[0, 2000, 5000, 10000, 20000, float('inf')],
                           labels=['Low (0-2K)', 'Medium (2K-5K)', 'High (5K-10K)', 
                                  'Premium (10K-20K)', 'VIP (20K+)'])
    
    tier_counts = spending_ranges.value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=tier_counts.index,
        values=tier_counts.values,
        hole=0.6,
        marker=dict(
            colors=['#FFE4E1', '#FFB6C1', '#FFA07A', '#FF7F50', '#FF6347'],
            line=dict(color='#FFFFFF', width=2)
        ),
        textinfo='label+percent+value',
        texttemplate='<b>%{label}</b><br>%{percent}<br>%{value} customers',
        hovertemplate='<b>%{label}</b><br>Customers: %{value}<br>Percentage: %{percent}<extra></extra>',
        textfont=dict(size=10)
    )])
    
    fig.update_layout(
        title={
            'text': "Customer Distribution by Spending Tiers",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2E2E2E'}
        },
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=-0.2, 
            xanchor="center", 
            x=0.5
        ),
        annotations=[dict(
            text='Spending<br>Tiers', 
            x=0.5, y=0.5, 
            font_size=14, 
            showarrow=False,
            font_color='#2E2E2E'
        )],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_cluster_category_breakdown_donut(df):
    """Create detailed cluster category breakdown donut"""
    cluster_stats = df.groupby('cluster_catgeory').agg({
        'Customer_ID': 'nunique',
        'Total_sales': 'sum'
    })
    
    # Calculate average spending per customer for each cluster
    cluster_stats['avg_spending'] = cluster_stats['Total_sales'] / cluster_stats['Customer_ID']
    cluster_avg_spending = cluster_stats['avg_spending']
    
    fig = go.Figure(data=[go.Pie(
        labels=cluster_avg_spending.index,
        values=cluster_avg_spending.values,
        hole=0.5,
        marker=dict(
            colors=px.colors.qualitative.Pastel[:len(cluster_avg_spending)],
            line=dict(color='#FFFFFF', width=2)
        ),
        textinfo='label+value',
        texttemplate='<b>%{label}</b><br>LKR %{value:,.0f}',
        hovertemplate='<b>%{label}</b><br>Avg Spending: LKR %{value:,.0f}<br>Share: %{percent}<extra></extra>',
        textfont=dict(size=11)
    )])
    
    fig.update_layout(
        title={
            'text': "Average Customer Spending by Segment",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2E2E2E'}
        },
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=-0.2, 
            xanchor="center", 
            x=0.5
        ),
        annotations=[dict(
            text='Average<br>Spending', 
            x=0.5, y=0.5, 
            font_size=14, 
            showarrow=False,
            font_color='#2E2E2E'
        )],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_city_performance_racing_bar(df):
    """Create interactive racing bar chart for city performance"""
    city_stats = df.groupby('outlet_city').agg({
        'Total_sales': 'sum',
        'Customer_ID': 'nunique',
        'luxury_sales': 'sum',
        'fresh_sales': 'sum',
        'dry_sales': 'sum'
    }).reset_index()
    
    city_stats = city_stats.sort_values('Total_sales', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=city_stats['outlet_city'],
        x=city_stats['Total_sales'],
        orientation='h',
        marker=dict(
            color=city_stats['Total_sales'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Revenue (LKR)", x=1.02)
        ),
        text=[f'LKR {x:,.0f}' for x in city_stats['Total_sales']],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>' +
                     'Total Revenue: LKR %{x:,.0f}<br>' +
                     'Customers: %{customdata[0]:,}<br>' +
                     'Luxury Sales: LKR %{customdata[1]:,.0f}<br>' +
                     'Fresh Sales: LKR %{customdata[2]:,.0f}<br>' +
                     'Dry Sales: LKR %{customdata[3]:,.0f}<extra></extra>',
        customdata=city_stats[['Customer_ID', 'luxury_sales', 'fresh_sales', 'dry_sales']].values
    ))
    
    fig.update_layout(
        title="City Performance Ranking",
        xaxis_title="Total Revenue (LKR)",
        yaxis_title="Cities",
        height=600,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_customer_segment_analysis(df):
    """Create customer segmentation scatter plot"""
    fig = px.scatter(
        df.sample(10000) if len(df) > 10000 else df,  # Sample for performance
        x='luxury_sales',
        y='fresh_sales',
        size='Total_sales',
        color='cluster_catgeory',
        hover_data=['Customer_ID', 'outlet_city', 'dry_sales'],
        title="Customer Spending Pattern Analysis",
        labels={
            'luxury_sales': 'Luxury Spending (LKR)',
            'fresh_sales': 'Fresh Produce Spending (LKR)',
            'cluster_catgeory': 'Customer Segment'
        },
        color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA726', '#AB47BC']
    )
    
    fig.update_layout(
        height=600,
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode='closest'
    )
    
    fig.update_traces(
        hovertemplate='<b>Customer: %{customdata[0]}</b><br>' +
                     'City: %{customdata[1]}<br>' +
                     'Luxury: LKR %{x:,.0f}<br>' +
                     'Fresh: LKR %{y:,.0f}<br>' +
                     'Dry Goods: LKR %{customdata[2]:,.0f}<br>' +
                     'Total: LKR %{marker.size:,.0f}<extra></extra>'
    )
    
    return fig

def create_sales_trends_heatmap(df):
    """Create advanced heatmap for sales analysis"""
    heatmap_data = df.groupby(['outlet_city', 'cluster_catgeory']).agg({
        'Total_sales': 'sum',
        'Customer_ID': 'nunique'
    }).reset_index()
    
    pivot_revenue = heatmap_data.pivot(index='outlet_city', columns='cluster_catgeory', values='Total_sales')
    pivot_revenue = pivot_revenue.fillna(0)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_revenue.values,
        x=pivot_revenue.columns,
        y=pivot_revenue.index,
        colorscale='Viridis',
        text=np.round(pivot_revenue.values, 0),
        texttemplate="%{text:,.0f}",
        textfont={"size": 10},
        hovertemplate='<b>%{y} - %{x}</b><br>Revenue: LKR %{z:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Revenue Heatmap: Cities vs Customer Segments",
        xaxis_title="Customer Segments",
        yaxis_title="Cities",
        height=500,
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_performance_metrics_table(df):
    """Create comprehensive performance metrics table"""
    city_metrics = df.groupby('outlet_city').agg({
        'Total_sales': ['sum', 'mean', 'count'],
        'Customer_ID': 'nunique',
        'luxury_sales': ['sum', 'mean'],
        'fresh_sales': ['sum', 'mean'],
        'dry_sales': ['sum', 'mean']
    }).round(2)
    
    # Flatten column names
    city_metrics.columns = ['_'.join(col).strip() for col in city_metrics.columns]
    city_metrics = city_metrics.reset_index()
    
    # Rename columns for better display
    city_metrics.columns = [
        'City', 'Total Revenue', 'Avg Basket Value', 'Transactions',
        'Unique Customers', 'Luxury Revenue', 'Avg Luxury Spend',
        'Fresh Revenue', 'Avg Fresh Spend', 'Dry Revenue', 'Avg Dry Spend'
    ]
    
    # Format currency columns
    currency_cols = ['Total Revenue', 'Avg Basket Value', 'Luxury Revenue', 
                    'Avg Luxury Spend', 'Fresh Revenue', 'Avg Fresh Spend', 
                    'Dry Revenue', 'Avg Dry Spend']
    
    for col in currency_cols:
        city_metrics[col] = city_metrics[col].apply(lambda x: f"LKR {x:,.0f}")
    
    return city_metrics.sort_values('City')

if __name__ == "__main__":
    main()
def load_data():
    """Load and cache the supermarket dataset"""
    try:
        df = pd.read_csv(DATASET_FILENAME)
        
        # Check if the required columns exist and fix column names if needed
        expected_columns = ['Customer_ID', 'outlet_city', 'luxury_sales', 'fresh_sales', 
                          'dry_sales', 'cluster_name', 'Total_sales']
        
        # Handle the cluster_category vs cluster_catgeory naming issue
        if 'cluster_category' in df.columns and 'cluster_catgeory' not in df.columns:
            df = df.rename(columns={'cluster_category': 'cluster_catgeory'})
        elif 'cluster_catgeory' not in df.columns and 'cluster_category' not in df.columns:
            st.error("Column 'cluster_catgeory' or 'cluster_category' not found in dataset!")
            st.error(f"Available columns: {list(df.columns)}")
            st.stop()
        
        # Verify all required columns exist
        missing_columns = []
        for col in expected_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if 'cluster_catgeory' not in df.columns:
            missing_columns.append('cluster_catgeory')
            
        if missing_columns:
            st.error(f"Missing required columns: {missing_columns}")
            st.error(f"Available columns in your dataset: {list(df.columns)}")
            st.stop()
            
        return df
        
    except FileNotFoundError:
        st.error(f"Dataset file '{DATASET_FILENAME}' not found!")
        st.info("Please ensure your CSV file is:")
        st.info("1. Located in the same directory as this script")
        st.info("2. Named correctly in the DATASET_FILENAME variable")
        st.info("3. Uploaded to your deployment platform if using cloud hosting")
        
        # Provide file upload option as fallback
        st.subheader("Upload your dataset instead:")
        uploaded_file = st.file_uploader("Choose your CSV file", type="csv")
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                # Apply the same column checks as above
                if 'cluster_category' in df.columns and 'cluster_catgeory' not in df.columns:
                    df = df.rename(columns={'cluster_category': 'cluster_catgeory'})
                return df
            except Exception as e:
                st.error(f"Error reading uploaded file: {str(e)}")
                st.stop()
        else:
            st.stop()
            
    except Exception as e:
        st.error(f"Error loading dataset: {str(e)}")
        st.error("Please check your dataset format and column names")
        
        # Show file upload option as fallback
        st.subheader("Try uploading your dataset:")
        uploaded_file = st.file_uploader("Choose your CSV file", type="csv")
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                if 'cluster_category' in df.columns and 'cluster_catgeory' not in df.columns:
                    df = df.rename(columns={'cluster_category': 'cluster_catgeory'})
                return df
            except Exception as e:
                st.error(f"Error reading uploaded file: {str(e)}")
                st.stop()
        else:
            st.stop()

