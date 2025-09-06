import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Safety & Quality Events Dashboard", layout="wide")

# Title and overview
st.title("Safety & Quality Events Dashboard (2025)")
st.markdown("""
This dashboard provides a comprehensive analysis of safety, service, and operational events recorded in 2025. It
highlights trends, root causes, corrective actions, and status distribution for all reported occurrences, enabling
management to identify key risk areas, monitor closure rates, and prioritize improvement actions.
""")

# Create sample data
monthly_data = pd.DataFrame({
    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Not Inc', 'Apr 25'],
    'Events': [22, 17, 13, 13, 9, 5, 5, 14, 1, 1]
})

root_causes = pd.DataFrame({
    'Cause': ['Other', 'EAGS violation', 'DL93 delays', 'DL93 EXT A/C LATE', 'Wrong selection', 'Security Coordinator', 'Reminder to SDU'],
    'Count': [72, 13, 6, 4, 3, 2, 1]
})

# Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Events", "105")
with col2:
    st.metric("Open Events", "5")
with col3:
    st.metric("Closed Events", "100")

# Event Volume Trend
st.subheader("Event Volume Trend by Month")
fig_trend = px.line(monthly_data, x='Month', y='Events', markers=True)
fig_trend.update_layout(xaxis_title="Month", yaxis_title="Number of Events")
st.plotly_chart(fig_trend, use_container_width=True)

# Key Insights for Trend
st.markdown("""
### Key Insights
- Event volume peaked in January (22) then declined to a low in June before a modest rebound in August (14)
- A sharp drop occurs from August (14) to April 25 (1), indicating reporting gaps or data cutoff
""")

# Two columns for Root Cause Distribution and Events by Type
col1, col2 = st.columns(2)

with col1:
    st.subheader("Root Cause Distribution")
    fig_pie = px.pie(root_causes, values='Count', names='Cause', hole=0.6)
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("""
    ### Key Insights
    - The "Other" category dominates root causes, accounting for over half of all incidents (72)
    - EAGS violations (13) and DL93 delays (6) are the next most common specific causes
    """)

# Sample data for Events by Type and Status
events_type = pd.DataFrame({
    'Type': ['NE delay report', 'Service Report', 'Security Report', 'Internal Report'],
    'Closed': [25, 18, 8, 4],
    'Open': [4, 3, 1, 1]
})

with col2:
    st.subheader("Events by Type and Status")
    fig_events = go.Figure()
    fig_events.add_trace(go.Bar(name='Closed', x=events_type['Type'], y=events_type['Closed']))
    fig_events.add_trace(go.Bar(name='Open', x=events_type['Type'], y=events_type['Open']))
    fig_events.update_layout(barmode='stack')
    st.plotly_chart(fig_events, use_container_width=True)

# Events by SDU
st.subheader("Events by SDU")
sdu_data = pd.DataFrame({
    'SDU': ['ABS', 'ASK', 'ASW'],
    'Events': [4, 4, 101]
})

fig_sdu = px.bar(sdu_data, x='Events', y='SDU', orientation='h')
fig_sdu.update_layout(yaxis_title="SDU", xaxis_title="Number of Events")
st.plotly_chart(fig_sdu, use_container_width=True)

# Final Insights
st.markdown("""
### Additional Key Insights
- "NE delay report" has the highest event count (29) and the greatest variety of root causes (26)
- "Service Report and GSR" is second in volume (21) but shows lower diversity in root causes (4)
- Aviation Security Occurrence Report has fewer events (3) but multiple statuses (3), suggesting more complex resolutions
""")