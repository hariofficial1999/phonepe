import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

# ----------------------------------
# CONFIG & DATABASE CONNECTION
# ----------------------------------
# ----------------------------------
# CONFIG & DATABASE CONNECTION
# ----------------------------------
st.set_page_config(page_title="PhonePe ", layout="wide")

@st.cache_resource
def get_engine():
    engine = create_engine("mysql+pymysql://root:Password%40123@localhost:3306/phonepe")
    return engine

try:
    engine = get_engine()
    # Test connection
    with engine.connect() as conn:
        pass
except Exception as e:
    st.error(f"Database Connection Error: {e}")
    st.stop()

# ----------------------------------
# HELPER FUNCTIONS
# ----------------------------------
def get_data(table_name):
    query = f"SELECT * FROM {table_name}"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    # Normalize headers to lowercase to avoid case-sensitivity issues
    df.columns = df.columns.str.strip().str.lower()
    return df

def filter_dataframe(df, year, quarter, state):
    # df columns are already lowercase from get_data
    if year != "All":
        df = df[df["year"] == int(year)]
    if quarter != "All":
        df = df[df["quarter"] == int(quarter)]
    if state != "All":
        df = df[df["state"] == state]
    return df

def render_5_charts(df, category_col, metric_count, metric_amount, title_prefix):
    """
    Renders 5 standardized charts.
    Assumes all input column names are lowercase.
    """
    
    # --- 1. DATA TABLE ---
    st.subheader(f"1. {title_prefix} - Data Overview")
    st.dataframe(df.head(100), use_container_width=True)

    # --- 2. PIE CHART ---
    st.subheader(f"2. {title_prefix} - Distribution")
    col1, col2 = st.columns(2)
    
    # Determine the column to use for Pie Charts (Category or State)
    # Fallback to 'state' if category_col is not present
    pie_col = category_col if category_col in df.columns else "state"
    
    with col1:
        if pie_col in df.columns:
            pie_data = df.groupby(pie_col)[metric_amount].sum().reset_index()
            fig_pie = px.pie(pie_data, names=pie_col, values=metric_amount, title=f"Amount Distribution by {pie_col}", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.warning(f"Column {pie_col} not found for Pie Chart.")

    with col2:
        if pie_col in df.columns:
            pie_data_2 = df.groupby(pie_col)[metric_count].sum().reset_index()
            fig_pie_2 = px.pie(pie_data_2, names=pie_col, values=metric_count, title=f"Count Distribution by {pie_col}", hole=0.4)
            st.plotly_chart(fig_pie_2, use_container_width=True)
        else:
            st.warning(f"Column {pie_col} not found for Pie Chart.")

    # --- 3. RELATIONSHIPS (Scatter, Bar, Histogram) ---
    st.subheader(f"3. {title_prefix} - Relationships")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        # Scatter: Count vs Amount
        # Using 'year' for color
        fig_scatter = px.scatter(df, x=metric_count, y=metric_amount, color="year", size=metric_amount, 
                                 title="Count vs Amount Correlation", 
                                 hover_data=[category_col] if category_col in df.columns else None)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col4:
        # Bar: Top Categories
        bar_col = category_col if category_col in df.columns else "state"
        if bar_col in df.columns:
            bar_data = df.groupby(bar_col)[[metric_count, metric_amount]].sum().reset_index().sort_values(metric_amount, ascending=False).head(10)
            fig_bar = px.bar(bar_data, x=bar_col, y=metric_amount, color=metric_count, title=f"Top 10 {bar_col} by Amount")
            st.plotly_chart(fig_bar, use_container_width=True)

    with col5:
        # Histogram: Amount Distribution
        fig_hist = px.histogram(df, x=metric_amount, title=f"Distribution of {metric_amount}", color="year")
        st.plotly_chart(fig_hist, use_container_width=True)

    # --- 4. INSIGHTS (Heatmap & Stats) ---
    st.subheader(f"4. {title_prefix} - Additional Insights")
    col5, col6 = st.columns(2)
    
    with col5:
        # Correlation Heatmap
        numeric_df = df.select_dtypes(include=['float64', 'int64'])
        if not numeric_df.empty:
            corr = numeric_df.corr()
            fig_heat = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
            st.plotly_chart(fig_heat, use_container_width=True)
            
    with col6:
        # Summary Metrics
        total_amt = df[metric_amount].sum()
        total_cnt = df[metric_count].sum()
        avg_amt = df[metric_amount].mean()
        
        st.markdown("### Key Metrics")
        st.metric(label="Total Amount", value=f"₹ {total_amt:,.0f}")
        st.metric(label="Total Count", value=f"{total_cnt:,.0f}")
        st.metric(label="Average Amount", value=f"₹ {avg_amt:,.0f}")

    # --- 5. TRENDS ---
    st.subheader(f"5. {title_prefix} - Trends Over Time")
    
    # Line Chart: Amount over Time
    # Group by year and quarter
    trend_data = df.groupby(['year', 'quarter'])[metric_amount].sum().reset_index()
    trend_data['Period'] = trend_data['year'].astype(str) + "-Q" + trend_data['quarter'].astype(str)
    
    fig_line = px.line(trend_data, x='Period', y=metric_amount, markers=True, title="Total Amount Trend over Quarters")
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Stacked Bar: Category over Time
    stack_col = category_col if category_col in df.columns else "state"
    if stack_col in df.columns:
        stack_data = df.groupby(['year', stack_col])[metric_amount].sum().reset_index()
        fig_stack = px.bar(stack_data, x="year", y=metric_amount, color=stack_col, title=f"Yearly Trend by {stack_col}")
        st.plotly_chart(fig_stack, use_container_width=True)

    # --- 6. ADVANCED ANALYTICS (Box Plot, Area Chart) ---
    st.subheader(f"6. {title_prefix} - Advanced Analytics")
    col7, col8 = st.columns(2)
    
    with col7:
        # Box Plot: Amount Distribution by Category
        box_col = category_col if category_col in df.columns else "state"
        if box_col in df.columns:
            fig_box = px.box(df, x=box_col, y=metric_amount, title=f"Amount Distribution by {box_col}", color=box_col)
            st.plotly_chart(fig_box, use_container_width=True)
    
    with col8:
        # Area Chart: Count Trend over Time
        area_data = df.groupby(['year', 'quarter'])[metric_count].sum().reset_index()
        area_data['Period'] = area_data['year'].astype(str) + "-Q" + area_data['quarter'].astype(str)
        
        fig_area = px.area(area_data, x='Period', y=metric_count, title="Total Count Trend over Quarters", markers=True)
        st.plotly_chart(fig_area, use_container_width=True)


# ----------------------------------
# NAVIGATION & FILTERS
# ----------------------------------
st.sidebar.title("📌 Navigation")
page = st.sidebar.selectbox("Select Page", ["Home", "Analysis"])

if page == "Home":
    # --- HOME PAGE LOGIC ---
    
    # Custom CSS for the "PhonePe Pulse" look with enhanced dark theme
    st.markdown("""
        <style>
        .main {
            background-color: #0d0221;
        }
        .stMetric {
            background-color: #1a0b3e;
            padding: 20px;
            border-radius: 15px;
            border: 2px solid #5a3d8a;
            box-shadow: 0 4px 15px rgba(138, 43, 226, 0.3);
        }
        .stMetric:hover {
            border-color: #9d4edd;
            box-shadow: 0 6px 20px rgba(157, 78, 221, 0.5);
        }
        h1, h2, h3 {
            color: #ffffff;
            text-shadow: 0 0 10px rgba(157, 78, 221, 0.5);
        }
        .metric-card {
            background: linear-gradient(135deg, #1a0b3e 0%, #2d1b69 100%);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #5a3d8a;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📱 PhonePe  | INDIA'S DIGITAL PAYMENT ")
    
    # 1. Fetch Aggregated Data from ALL tables
    try:
        # === TRANSACTIONS DATA ===
        # Aggregate Transactions
        query_agg_trans = """
            SELECT SUM(transaction_count) as total_trans_count, 
                   SUM(transaction_amount) as total_trans_amount 
            FROM agg_trans
        """
        with engine.connect() as conn:
            df_agg_trans = pd.read_sql(query_agg_trans, conn)
        
        # Map Transactions
        query_map_trans = """
            SELECT SUM(transaction_count) as map_trans_count, 
                   SUM(transaction_amount) as map_trans_amount 
            FROM map_trans
        """
        with engine.connect() as conn:
            df_map_trans = pd.read_sql(query_map_trans, conn)
        
        # Top Transactions
        query_top_trans = """
            SELECT SUM(transaction_count) as top_trans_count, 
                   SUM(transaction_amount) as top_trans_amount 
            FROM top_trans
        """
        with engine.connect() as conn:
            df_top_trans = pd.read_sql(query_top_trans, conn)
        
        # === INSURANCE DATA ===
        # Aggregate Insurance
        query_agg_ins = """
            SELECT SUM(insurance_count) as total_ins_count, 
                   SUM(insurance_amount) as total_ins_amount 
            FROM agg_insur
        """
        with engine.connect() as conn:
            df_agg_ins = pd.read_sql(query_agg_ins, conn)
        
        # Map Insurance
        query_map_ins = """
            SELECT SUM(insurance_count) as map_ins_count, 
                   SUM(insurance_amount) as map_ins_amount 
            FROM map_insur
        """
        with engine.connect() as conn:
            df_map_ins = pd.read_sql(query_map_ins, conn)
        
        # Top Insurance
        query_top_ins = """
            SELECT SUM(insurance_count) as top_ins_count, 
                   SUM(insurance_amount) as top_ins_amount 
            FROM top_insur
        """
        with engine.connect() as conn:
            df_top_ins = pd.read_sql(query_top_ins, conn)
        
        # === USERS DATA ===
        # Note: agg_user table has different schema (user_count, not registered_users)
        # So we only use map_user and top_users for registered users aggregation
        
        # Map Users
        query_map_users = """
            SELECT SUM(registered_users) as map_registered_users,
                   SUM(app_opens) as total_app_opens
            FROM map_user
        """
        with engine.connect() as conn:
            df_map_users = pd.read_sql(query_map_users, conn)
        
        # Top Users
        query_top_users = """
            SELECT SUM(registered_users) as top_registered_users 
            FROM top_users
        """
        with engine.connect() as conn:
            df_top_users = pd.read_sql(query_top_users, conn)
        
        # Calculate totals with proper None handling
        total_transactions = (
            ((df_agg_trans['total_trans_count'].iloc[0] if not df_agg_trans.empty else 0) or 0) +
            ((df_map_trans['map_trans_count'].iloc[0] if not df_map_trans.empty else 0) or 0) +
            ((df_top_trans['top_trans_count'].iloc[0] if not df_top_trans.empty else 0) or 0)
        )
        
        total_trans_amount = (
            ((df_agg_trans['total_trans_amount'].iloc[0] if not df_agg_trans.empty else 0) or 0) +
            ((df_map_trans['map_trans_amount'].iloc[0] if not df_map_trans.empty else 0) or 0) +
            ((df_top_trans['top_trans_amount'].iloc[0] if not df_top_trans.empty else 0) or 0)
        )
        
        total_insurance = (
            ((df_agg_ins['total_ins_count'].iloc[0] if not df_agg_ins.empty else 0) or 0) +
            ((df_map_ins['map_ins_count'].iloc[0] if not df_map_ins.empty else 0) or 0) +
            ((df_top_ins['top_ins_count'].iloc[0] if not df_top_ins.empty else 0) or 0)
        )
        
        total_ins_amount = (
            ((df_agg_ins['total_ins_amount'].iloc[0] if not df_agg_ins.empty else 0) or 0) +
            ((df_map_ins['map_ins_amount'].iloc[0] if not df_map_ins.empty else 0) or 0) +
            ((df_top_ins['top_ins_amount'].iloc[0] if not df_top_ins.empty else 0) or 0)
        )
        
        total_users = (
            ((df_map_users['map_registered_users'].iloc[0] if not df_map_users.empty else 0) or 0) +
            ((df_top_users['top_registered_users'].iloc[0] if not df_top_users.empty else 0) or 0)
        )
        
        total_app_opens = (df_map_users['total_app_opens'].iloc[0] if not df_map_users.empty else 0) or 0
        
        # === STATE-WISE DATA FOR 3D MAP ===
        # Aggregate all state-wise data
        query_state_map = """
            SELECT 
                COALESCE(t.state, i.state, u.state) as state,
                COALESCE(SUM(t.transaction_amount), 0) as trans_amount,
                COALESCE(SUM(t.transaction_count), 0) as trans_count,
                COALESCE(SUM(i.insurance_amount), 0) as ins_amount,
                COALESCE(SUM(i.insurance_count), 0) as ins_count,
                COALESCE(SUM(u.registered_users), 0) as users
            FROM agg_trans t
            FULL OUTER JOIN agg_insur i ON t.state = i.state
            FULL OUTER JOIN agg_users u ON COALESCE(t.state, i.state) = u.state
            GROUP BY COALESCE(t.state, i.state, u.state)
        """
        
        # Fallback query for MySQL (doesn't support FULL OUTER JOIN)
        query_state_map_mysql = """
            SELECT 
                state,
                SUM(transaction_amount) as trans_amount,
                SUM(transaction_count) as trans_count,
                0 as ins_amount,
                0 as ins_count,
                0 as users
            FROM agg_trans
            GROUP BY state
            
            UNION ALL
            
            SELECT 
                state,
                0 as trans_amount,
                0 as trans_count,
                SUM(insurance_amount) as ins_amount,
                SUM(insurance_count) as ins_count,
                0 as users
            FROM agg_insur
            GROUP BY state
            

        """
        
        with engine.connect() as conn:
            df_state_raw = pd.read_sql(query_state_map_mysql, conn)
        
        # Aggregate the union results
        df_map = df_state_raw.groupby('state').agg({
            'trans_amount': 'sum',
            'trans_count': 'sum',
            'ins_amount': 'sum',
            'ins_count': 'sum',
            'users': 'sum'
        }).reset_index()
        
        # Calculate total value for map (transactions + insurance)
        df_map['total_value'] = df_map['trans_amount'] + df_map['ins_amount']
        
        # Map state names from database format to GeoJSON format
        # Database has: 'andaman-&-nicobar-islands', GeoJSON expects: 'Andaman & Nicobar Islands'
        def format_state_name(state):
            """Convert database state name to GeoJSON format"""
            # Replace hyphens with spaces and title case
            state = state.replace('-', ' ').title()
            # Fix special cases
            state = state.replace('&', '&')  # Ensure & is preserved
            state = state.replace('And', 'and')  # Fix 'And' to 'and'
            return state
        
        df_map['state'] = df_map['state'].apply(format_state_name)
        
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        total_transactions = 0
        total_trans_amount = 0
        total_insurance = 0
        total_ins_amount = 0
        total_users = 0
        total_app_opens = 0
        df_map = pd.DataFrame(columns=['state', 'total_value', 'trans_amount', 'ins_amount', 'users'])

    # 2. Layout: Map on Left, Stats on Right
    col_map, col_stats = st.columns([2.5, 1])
    
    with col_map:
        st.subheader("🗺️ All India - Aggregated Payment Ecosystem")
        
        # Load GeoJSON for India
        geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        
        if not df_map.empty:
            # Get state coordinates (approximate centers for major states)
            state_coords = {
                'Andaman & Nicobar Islands': (11.7401, 92.6586),
                'Andhra Pradesh': (15.9129, 79.7400),
                'Arunachal Pradesh': (28.2180, 94.7278),
                'Assam': (26.2006, 92.9376),
                'Bihar': (25.0961, 85.3131),
                'Chandigarh': (30.7333, 76.7794),
                'Chhattisgarh': (21.2787, 81.8661),
                'Dadra and Nagar Haveli and Daman and Diu': (20.1809, 73.0169),
                'Delhi': (28.7041, 77.1025),
                'Goa': (15.2993, 74.1240),
                'Gujarat': (22.2587, 71.1924),
                'Haryana': (29.0588, 76.0856),
                'Himachal Pradesh': (31.1048, 77.1734),
                'Jammu & Kashmir': (33.7782, 76.5762),
                'Jharkhand': (23.6102, 85.2799),
                'Karnataka': (15.3173, 75.7139),
                'Kerala': (10.8505, 76.2711),
                'Ladakh': (34.1526, 77.5771),
                'Lakshadweep': (10.5667, 72.6417),
                'Madhya Pradesh': (22.9734, 78.6569),
                'Maharashtra': (19.7515, 75.7139),
                'Manipur': (24.6637, 93.9063),
                'Meghalaya': (25.4670, 91.3662),
                'Mizoram': (23.1645, 92.9376),
                'Nagaland': (26.1584, 94.5624),
                'Odisha': (20.9517, 85.0985),
                'Puducherry': (11.9416, 79.8083),
                'Punjab': (31.1471, 75.3412),
                'Rajasthan': (27.0238, 74.2179),
                'Sikkim': (27.5330, 88.5122),
                'Tamil Nadu': (11.1271, 78.6569),
                'Telangana': (18.1124, 79.0193),
                'Tripura': (23.9408, 91.9882),
                'Uttar Pradesh': (26.8467, 80.9462),
                'Uttarakhand': (30.0668, 79.0193),
                'West Bengal': (22.9868, 87.8550)
            }
            
            # Add coordinates to dataframe
            df_map['lat'] = df_map['state'].map(lambda x: state_coords.get(x, (None, None))[0])
            df_map['lon'] = df_map['state'].map(lambda x: state_coords.get(x, (None, None))[1])
            
            # Create base choropleth layer
            fig_map = px.choropleth(
                df_map,
                geojson=geojson_url,
                featureidkey='properties.ST_NM',
                locations='state',
                color='total_value',
                color_continuous_scale=[
                    [0.0, '#0d0221'],
                    [0.2, '#240046'],
                    [0.4, '#5a189a'],
                    [0.6, '#9d4edd'],
                    [0.8, '#e0aaff'],
                    [1.0, '#ffffff']
                ],
                range_color=(0, df_map['total_value'].max()),
                hover_data={
                    'state': True,
                    'total_value': ':,.0f',
                    'trans_amount': ':,.0f',
                    'ins_amount': ':,.0f',
                    'users': ':,.0f'
                },
                labels={
                    'total_value': 'Total Value (₹)',
                    'trans_amount': 'Transactions (₹)',
                    'ins_amount': 'Insurance (₹)',
                    'users': 'Registered Users'
                }
            )
            
            # Add 3D scatter overlay for particle effect
            fig_scatter = px.scatter_geo(
                df_map.dropna(subset=['lat', 'lon']),
                lat='lat',
                lon='lon',
                size='total_value',
                color='total_value',
                hover_name='state',
                hover_data={
                    'total_value': ':,.0f',
                    'trans_amount': ':,.0f',
                    'ins_amount': ':,.0f',
                    'users': ':,.0f',
                    'lat': False,
                    'lon': False
                },
                color_continuous_scale=[
                    [0.0, '#5a189a'],
                    [0.5, '#9d4edd'],
                    [1.0, '#ffffff']
                ],
                size_max=50
            )
            
            # Combine both traces
            for trace in fig_scatter.data:
                trace.marker.line = dict(color='rgba(255, 255, 255, 0.8)', width=2)
                trace.marker.opacity = 0.8
                fig_map.add_trace(trace)
            
            # Update geo layout for India focus
            fig_map.update_geos(
                projection_type="natural earth",
                fitbounds="locations",
                visible=False,
                showcountries=False,
                showcoastlines=False,
                showland=False,
                showlakes=False,
                showrivers=False,
                bgcolor='rgba(13, 2, 33, 0.0)'
            )
            
            # Enhanced layout
            fig_map.update_layout(
                height=750,
                margin={"r":0,"t":40,"l":0,"b":0},
                paper_bgcolor='rgba(13, 2, 33, 0.0)',
                plot_bgcolor='rgba(13, 2, 33, 0.0)',
                font=dict(
                    family="Inter, sans-serif",
                    size=12,
                    color='white'
                ),
                showlegend=False,
                coloraxis_colorbar=dict(
                    title=dict(
                        text="Total Value (₹)",
                        font=dict(size=14, color='white')
                    ),
                    thickness=20,
                    len=0.7,
                    bgcolor='rgba(26, 11, 62, 0.6)',
                    bordercolor='rgba(157, 78, 221, 0.5)',
                    borderwidth=2,
                    tickfont=dict(color='white', size=11),
                    tickformat=',.0f',
                    x=1.02
                ),
                hoverlabel=dict(
                    bgcolor='rgba(26, 11, 62, 0.95)',
                    bordercolor='rgba(157, 78, 221, 0.8)',
                    font=dict(
                        family="Inter, sans-serif",
                        size=13,
                        color='white'
                    )
                )
            )
            
            # Update choropleth traces
            fig_map.update_traces(
                selector=dict(type='choropleth'),
                marker=dict(
                    line=dict(
                        color='rgba(157, 78, 221, 0.8)',
                        width=2
                    )
                ),
                hovertemplate='<b>%{location}</b><br>' +
                             'Total Value: ₹%{z:,.0f}<br>' +
                             '<extra></extra>'
            )
            
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No data available for map.")


    with col_stats:
        st.markdown("### 💳 Transactions")
        st.markdown(f"<h1 style='color: #00d2ff; font-size: 2.5em;'>{total_transactions:,.0f}</h1>", unsafe_allow_html=True)
        st.markdown("**All PhonePe transactions**")
        st.markdown(f"<p style='color: #9d4edd; font-size: 1.2em;'>₹ {total_trans_amount:,.0f}</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 🛡️ Insurance")
        st.markdown(f"<h1 style='color: #ff006e; font-size: 2.5em;'>{total_insurance:,.0f}</h1>", unsafe_allow_html=True)
        st.markdown("**Total Insurance Policies**")
        st.markdown(f"<p style='color: #9d4edd; font-size: 1.2em;'>₹ {total_ins_amount:,.0f}</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 👥 Users")
        st.markdown(f"<h1 style='color: #06ffa5; font-size: 2.5em;'>{total_users:,.0f}</h1>", unsafe_allow_html=True)
        st.markdown("**Registered Users**")
        st.markdown(f"<p style='color: #9d4edd; font-size: 1.2em;'>{total_app_opens:,.0f} App Opens</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 📊 Top States")
        # Fetch top 5 states by total value
        if not df_map.empty:
            top_states = df_map.nlargest(5, 'total_value')
            for idx, row in top_states.iterrows():
                st.markdown(f"**{row['state']}**: ₹ {row['total_value']:,.0f}")
                st.progress(min(row['total_value'] / df_map['total_value'].max(), 1.0))
    
    # 3. Additional Metrics Section
    st.markdown("---")
    st.markdown("## 📈 Comprehensive Metrics Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Aggregate Transactions",
            value=f"₹ {df_agg_trans['total_trans_amount'].iloc[0]:,.0f}" if not df_agg_trans.empty and df_agg_trans['total_trans_amount'].iloc[0] is not None else "₹ 0",
            delta=f"{df_agg_trans['total_trans_count'].iloc[0]:,.0f} Count" if not df_agg_trans.empty and df_agg_trans['total_trans_count'].iloc[0] is not None else "0"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Map Transactions",
            value=f"₹ {df_map_trans['map_trans_amount'].iloc[0]:,.0f}" if not df_map_trans.empty and df_map_trans['map_trans_amount'].iloc[0] is not None else "₹ 0",
            delta=f"{df_map_trans['map_trans_count'].iloc[0]:,.0f} Count" if not df_map_trans.empty and df_map_trans['map_trans_count'].iloc[0] is not None else "0"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Top Transactions",
            value=f"₹ {df_top_trans['top_trans_amount'].iloc[0]:,.0f}" if not df_top_trans.empty and df_top_trans['top_trans_amount'].iloc[0] is not None else "₹ 0",
            delta=f"{df_top_trans['top_trans_count'].iloc[0]:,.0f} Count" if not df_top_trans.empty and df_top_trans['top_trans_count'].iloc[0] is not None else "0"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Total Payment Value",
            value=f"₹ {total_trans_amount:,.0f}",
            delta="All Sources"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Insurance Metrics Row
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Aggregate Insurance",
            value=f"₹ {df_agg_ins['total_ins_amount'].iloc[0]:,.0f}" if not df_agg_ins.empty and df_agg_ins['total_ins_amount'].iloc[0] is not None else "₹ 0",
            delta=f"{df_agg_ins['total_ins_count'].iloc[0]:,.0f} Policies" if not df_agg_ins.empty and df_agg_ins['total_ins_count'].iloc[0] is not None else "0"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col6:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Map Insurance",
            value=f"₹ {df_map_ins['map_ins_amount'].iloc[0]:,.0f}" if not df_map_ins.empty and df_map_ins['map_ins_amount'].iloc[0] is not None else "₹ 0",
            delta=f"{df_map_ins['map_ins_count'].iloc[0]:,.0f} Policies" if not df_map_ins.empty and df_map_ins['map_ins_count'].iloc[0] is not None else "0"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col7:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Top Insurance",
            value=f"₹ {df_top_ins['top_ins_amount'].iloc[0]:,.0f}" if not df_top_ins.empty and df_top_ins['top_ins_amount'].iloc[0] is not None else "₹ 0",
            delta=f"{df_top_ins['top_ins_count'].iloc[0]:,.0f} Policies" if not df_top_ins.empty and df_top_ins['top_ins_count'].iloc[0] is not None else "0"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col8:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Total Insurance Value",
            value=f"₹ {total_ins_amount:,.0f}",
            delta="All Sources"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # User Metrics Row
    col9, col10, col11 = st.columns(3)
    
    with col9:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Map Users",
            value=f"{df_map_users['map_registered_users'].iloc[0]:,.0f}" if not df_map_users.empty and df_map_users['map_registered_users'].iloc[0] is not None else "0",
            delta=f"{df_map_users['total_app_opens'].iloc[0]:,.0f} Opens" if not df_map_users.empty and df_map_users['total_app_opens'].iloc[0] is not None else "0"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col10:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Top Users",
            value=f"{df_top_users['top_registered_users'].iloc[0]:,.0f}" if not df_top_users.empty and df_top_users['top_registered_users'].iloc[0] is not None else "0",
            delta="Registered"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col11:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Total Users",
            value=f"{total_users:,.0f}",
            delta="Map + Top"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ===================================================================================
# ANALYSIS PAGE
# ===================================================================================
st.title("📊 Business Case Study")

case_studies = [
    "Transaction Analysis for Market Expansion",
    "Insurance Transactions Analysis",
    "Decoding Transaction Dynamics on PhonePe",
    "User Registration Analysis",
    "Insurance Engagement Analysis"
]

selected_case = st.selectbox("Choose Case Study:", case_studies)
st.markdown("---")
case_submit = st.button("Submit", key="case_submit_btn")

# --- GLOBAL FILTERS ---
# We need to load data first to populate filters.
# NOTE: All column names below must be lowercase because we normalize them in get_data()

if selected_case in ["Transaction Analysis for Market Expansion", "Decoding Transaction Dynamics on PhonePe"]:
    table_name = "agg_trans"
    cat_col = "transaction_type"
    met_cnt = "transaction_count"
    met_amt = "transaction_amount"
elif selected_case in ["Insurance Transactions Analysis", "Insurance Engagement Analysis"]:
    table_name = "agg_insur"
    cat_col = "state" 
    met_cnt = "insurance_count"
    met_amt = "insurance_amount"
elif selected_case == "User Registration Analysis":
    table_name = "map_user"
    cat_col = "district" # or state
    met_cnt = "registered_users"
    met_amt = "app_opens" 

df = get_data(table_name)

# Sidebar Form for Filters
with st.form("filter_form"):
    st.markdown("### 🔍 Filters")
    
    # Filter Options
    # Ensure we access lowercase columns
    year_list = ["All"] + sorted(df["year"].unique().tolist())
    quarter_list = ["All"] + sorted(df["quarter"].unique().tolist())
    state_list = ["All"] + sorted(df["state"].unique().tolist())

    sel_year = st.selectbox("Select Year", year_list)
    sel_quarter = st.selectbox("Select Quarter", quarter_list)
    sel_state = st.selectbox("Select State", state_list)
    
    submitted = st.form_submit_button("Apply Filters")

# ===================================================================================
# RENDER CHARTS
# ===================================================================================

if submitted:
    # Apply Filters
    df_filtered = filter_dataframe(df, sel_year, sel_quarter, sel_state)
    
    if df_filtered.empty:
        st.warning("No data available for the selected filters.")
    else:
        render_5_charts(df_filtered, cat_col, met_cnt, met_amt, selected_case)
else:
    st.info("☝🏻 Please select filters from the sidebar and click 'Apply Filters' to view the dashboard.")
