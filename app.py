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
    page_icon="🛒",
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
def load_data():
    """Load and cache the supermarket dataset"""
    try:
        df = pd.read_csv(DATASET_FILENAME)
        return df
    except FileNotFoundError:
        st.error(f"Dataset file '{DATASET_FILENAME}' not found! Please update the filename at the top of the code.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading dataset: {str(e)}")
        st.stop()

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
            label="💎 Luxury Sales",
            value=f"LKR {luxury_revenue:,.0f}",
            delta=f"{luxury_share:.1f}% of total",
            help="Premium category performance"
        )
    
    with col2:
        fresh_revenue = df['fresh_sales'].sum()
        fresh_share = (fresh_revenue / total_revenue) * 100
        st.metric(
            label="🥬 Fresh Sales",
            value=f"LKR {fresh_revenue:,.0f}",
            delta=f"{fresh_share:.1f}% of total",
            help="Fresh produce performance"
        )
    
    with col3:
        dry_revenue = df['dry_sales'].sum()
        dry_share = (dry_revenue / total_revenue) * 100
        st.metric(
            label="📦 Dry Goods Sales",
            value=f"LKR {dry_revenue:,.0f}",
            delta=f"{dry_share:.1f}% of total",
            help="Dry goods category performance"
        )
    
    with col4:
        top_city = df.groupby('outlet_city')['Total_sales'].sum().idxmax()
        top_city_revenue = df.groupby('outlet_city')['Total_sales'].sum().max()
        st.metric(
            label="🏆 Top Performing City",
            value=top_city,
            delta=f"LKR {top_city_revenue:,.0f}",
            help="Highest revenue generating city"
        )
    
    with col5:
        high_value_customers = len(df[df['Total_sales'] > df['Total_sales'].quantile(0.8)])
        st.metric(
            label="⭐ Premium Customers",
            value=f"{high_value_customers:,}",
            delta=f"LKR {avg_basket_value:,.0f} avg basket",
            help="Top 20% customers by spending"
        )

def create_sales_distribution_sunburst(df):
    """Create interactive sunburst chart for sales distribution"""
    # Prepare data for sunburst
    sales_data = []
    
    for city in df['outlet_city'].unique():
        city_data = df[df['outlet_city'] == city]
        city_total = city_data['Total_sales'].sum()
        
        # City level
        sales_data.append({
            'ids': city,
            'labels': city,
            'parents': '',
            'values': city_total
        })
        
        # Category level for each city
        luxury_total = city_data['luxury_sales'].sum()
        fresh_total = city_data['fresh_sales'].sum()
        dry_total = city_data['dry_sales'].sum()
        
        sales_data.extend([
            {'ids': f"{city}_Luxury", 'labels': 'Luxury', 'parents': city, 'values': luxury_total},
            {'ids': f"{city}_Fresh", 'labels': 'Fresh', 'parents': city, 'values': fresh_total},
            {'ids': f"{city}_Dry", 'labels': 'Dry Goods', 'parents': city, 'values': dry_total}
        ])
    
    df_sunburst = pd.DataFrame(sales_data)
    
    fig = go.Figure(go.Sunburst(
        ids=df_sunburst['ids'],
        labels=df_sunburst['labels'],
        parents=df_sunburst['parents'],
        values=df_sunburst['values'],
        branchvalues="total",
        hovertemplate='<b>%{label}</b><br>Revenue: LKR %{value:,.0f}<br>% of Parent: %{percentParent}<extra></extra>',
        maxdepth=2
    ))
    
    fig.update_layout(
        title="Revenue Breakdown: Cities & Categories",
        height=600,
        paper_bgcolor="rgba(0,0,0,0)"
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
            colorscale='Plasma',
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

def create_category_comparison_radar(df):
    """Create radar chart for category performance comparison"""
    city_avg = df.groupby('outlet_city').agg({
        'luxury_sales': 'mean',
        'fresh_sales': 'mean',
        'dry_sales': 'mean'
    }).reset_index()
    
    # Normalize data for radar chart
    for col in ['luxury_sales', 'fresh_sales', 'dry_sales']:
        city_avg[f'{col}_norm'] = (city_avg[col] - city_avg[col].min()) / (city_avg[col].max() - city_avg[col].min())
    
    fig = go.Figure()
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA726', '#AB47BC', '#26A69A', '#FF7043']
    
    for i, city in enumerate(city_avg['outlet_city'][:7]):  # Limit to 7 cities for clarity
        city_data = city_avg[city_avg['outlet_city'] == city]
        
        fig.add_trace(go.Scatterpolar(
            r=[
                city_data['luxury_sales_norm'].iloc[0],
                city_data['fresh_sales_norm'].iloc[0],
                city_data['dry_sales_norm'].iloc[0]
            ],
            theta=['Luxury Sales', 'Fresh Sales', 'Dry Goods Sales'],
            fill='toself',
            name=city,
            line_color=colors[i % len(colors)],
            opacity=0.7
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="City Performance Comparison - Normalized Sales Categories",
        height=600,
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_cluster_analysis_treemap(df):
    """Create treemap for cluster analysis"""
    cluster_data = df.groupby(['cluster_catgeory', 'outlet_city']).agg({
        'Total_sales': 'sum',
        'Customer_ID': 'nunique'
    }).reset_index()
    
    fig = go.Figure(go.Treemap(
        labels=cluster_data['outlet_city'],
        parents=cluster_data['cluster_catgeory'],
        values=cluster_data['Total_sales'],
        texttemplate="<b>%{label}</b><br>LKR %{value:,.0f}",
        hovertemplate='<b>%{label}</b><br>' +
                     'Cluster: %{parent}<br>' +
                     'Revenue: LKR %{value:,.0f}<br>' +
                     'Customers: %{customdata}<extra></extra>',
        customdata=cluster_data['Customer_ID'],
        textposition="middle center"
    ))
    
    fig.update_layout(
        title="Revenue Distribution by Customer Clusters & Cities",
        height=600,
        paper_bgcolor="rgba(0,0,0,0)"
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

def create_customer_insights_box(df):
    """Create customer insights summary"""
    insights = []
    
    # Top spending customer segment
    top_segment = df.groupby('cluster_catgeory')['Total_sales'].sum().idxmax()
    top_segment_revenue = df.groupby('cluster_catgeory')['Total_sales'].sum().max()
    insights.append(f"🎯 **{top_segment}** is our highest revenue segment with LKR {top_segment_revenue:,.0f}")
    
    # Most valuable city
    top_city = df.groupby('outlet_city')['Total_sales'].sum().idxmax()
    top_city_customers = df[df['outlet_city'] == top_city]['Customer_ID'].nunique()
    insights.append(f"🏆 **{top_city}** leads with {top_city_customers:,} customers")
    
    # Category leader
    categories = {'Luxury': df['luxury_sales'].sum(), 
                 'Fresh': df['fresh_sales'].sum(), 
                 'Dry Goods': df['dry_sales'].sum()}
    top_category = max(categories, key=categories.get)
    insights.append(f"📈 **{top_category}** dominates sales with LKR {categories[top_category]:,.0f}")
    
    # Customer spending pattern
    high_spenders = len(df[df['Total_sales'] > df['Total_sales'].quantile(0.9)])
    total_customers = df['Customer_ID'].nunique()
    insights.append(f"⭐ {high_spenders:,} customers ({(high_spenders/total_customers)*100:.1f}%) are premium spenders")
    
    return insights

# Main Dashboard
def main():
    # Load data
    df = load_data()
    
    # Header
    st.markdown('<h1 class="main-header">🛒 Sri Lanka Supermarket Chain Analytics</h1>', unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.header("🎛️ Dashboard Controls")
    
    # City filter
    all_cities = ['All Cities'] + sorted(df['outlet_city'].unique().tolist())
    selected_cities = st.sidebar.multiselect(
        "🏙️ Select Cities:",
        options=df['outlet_city'].unique(),
        default=df['outlet_city'].unique()
    )
    
    # Customer segment filter
    all_segments = ['All Segments'] + sorted(df['cluster_catgeory'].unique().tolist())
    selected_segments = st.sidebar.multiselect(
        "👥 Select Customer Segments:",
        options=df['cluster_catgeory'].unique(),
        default=df['cluster_catgeory'].unique()
    )
    
    # Sales range filter
    min_sales = int(df['Total_sales'].min())
    max_sales = int(df['Total_sales'].max())
    sales_range = st.sidebar.slider(
        "💰 Total Sales Range (LKR):",
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
    **📊 Dataset Overview**
    - **Records:** {len(filtered_df):,} of {len(df):,}
    - **Cities:** {filtered_df['outlet_city'].nunique()}
    - **Customers:** {filtered_df['Customer_ID'].nunique():,}
    - **Segments:** {filtered_df['cluster_catgeory'].nunique()}
    """)
    
    # Hero metrics
    create_hero_metrics(filtered_df)
    
    # Customer insights
    st.header("💡 Key Business Insights")
    insights = create_customer_insights_box(filtered_df)
    
    col_insight1, col_insight2 = st.columns(2)
    with col_insight1:
        for insight in insights[:2]:
            st.info(insight)
    with col_insight2:
        for insight in insights[2:]:
            st.info(insight)
    
    # Interactive visualizations
    st.header("📊 Interactive Analytics")
    
    # First row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_sunburst = create_sales_distribution_sunburst(filtered_df)
        st.plotly_chart(fig_sunburst, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_racing = create_city_performance_racing_bar(filtered_df)
        st.plotly_chart(fig_racing, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Second row
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    fig_scatter = create_customer_segment_analysis(filtered_df)
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Third row
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_radar = create_category_comparison_radar(filtered_df)
        st.plotly_chart(fig_radar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_treemap = create_cluster_analysis_treemap(filtered_df)
        st.plotly_chart(fig_treemap, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Fourth row
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    fig_heatmap = create_sales_trends_heatmap(filtered_df)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance metrics table
    st.header("📈 Detailed Performance Metrics")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    metrics_table = create_performance_metrics_table(filtered_df)
    st.dataframe(metrics_table, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Data explorer
    with st.expander("🔍 Raw Data Explorer"):
        st.subheader("Filtered Dataset")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Download options
        col_d1, col_d2, col_d3 = st.columns(3)
        
        with col_d1:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"supermarket_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col_d2:
            # Summary statistics
            summary_stats = filtered_df.describe()
            summary_csv = summary_stats.to_csv()
            st.download_button(
                label="📊 Download Summary Stats",
                data=summary_csv,
                file_name=f"summary_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col_d3:
            # City-wise summary
            city_summary = create_performance_metrics_table(filtered_df)
            city_csv = city_summary.to_csv(index=False)
            st.download_button(
                label="🏙️ Download City Summary",
                data=city_csv,
                file_name=f"city_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; padding: 30px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; color: white; margin-top: 30px;'>
            <h3 style='margin: 0; font-weight: 300;'>🛒 Sri Lanka Supermarket Chain Analytics Dashboard</h3>
            <p style='margin: 10px 0 0 0; opacity: 0.8;'>
                Empowering data-driven decisions across {len(df['outlet_city'].unique())} cities • 
                {len(df):,} transactions analyzed • Built with ❤️ using Streamlit & Plotly
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()