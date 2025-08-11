import streamlit as st
import pandas as pd
import ipaddress
import json
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit.components.v1 as components

# Set page configuration
st.set_page_config(
    page_title="Enhanced Firewall Analyzer",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .rule-card {
        background: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .status-accept {
        color: #28a745;
        font-weight: bold;
    }
    .status-drop {
        color: #dc3545;
        font-weight: bold;
    }
    .status-reject {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitFirewallAnalyzer:
    def __init__(self):
        self.rules = []
        self.initialize_session_state()
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'rules' not in st.session_state:
            st.session_state.rules = []
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        if 'theme' not in st.session_state:
            st.session_state.theme = "light"
            
    def detect_missing_rules(self, rules):
        """Detect missing firewall rules"""
        missing_rules = []
        for rule in rules:
            if len(rule) >= 7:
                rule_number, protocol, source_ip, source_port, destination_ip, destination_port, action = rule
                if action.upper() == 'ACCEPT' and not self.is_ip_in_range(source_ip, destination_ip):
                    missing_rules.append(rule_number)
        return missing_rules
    
    def detect_redundant_rules(self, rules):
        """Detect redundant firewall rules"""
        redundant_rules = []
        for i, rule in enumerate(rules):
            if len(rule) >= 7:
                rule_number, protocol, source_ip, source_port, destination_ip, destination_port, action = rule
                for j, other_rule in enumerate(rules):
                    if i != j and len(other_rule) >= 7:
                        other_rule_number, other_protocol, other_source_ip, other_source_port, other_destination_ip, other_destination_port, other_action = other_rule
                        if (action.upper() == other_action.upper() and 
                            protocol.lower() == other_protocol.lower() and 
                            source_ip == other_source_ip and 
                            destination_ip == other_destination_ip):
                            redundant_rules.append(rule_number)
        return list(set(redundant_rules))
    
    def detect_outdated_rules(self, rules):
        """Detect outdated firewall rules"""
        outdated_rules = []
        for rule in rules:
            if len(rule) >= 7:
                rule_number, protocol, source_ip, source_port, destination_ip, destination_port, action = rule
                if (protocol.lower() == 'tcp' and 
                    str(source_port).isdigit() and int(source_port) > 1024 and 
                    str(destination_port).isdigit() and int(destination_port) > 1024):
                    outdated_rules.append(rule_number)
        return outdated_rules
    
    def is_ip_in_range(self, source_ip, destination_ip):
        """Check if IP is in range"""
        try:
            source_ip = source_ip.strip().rstrip(',')
            destination_ip = destination_ip.strip().rstrip(',')
            source_network = ipaddress.ip_network(source_ip, strict=False)
            destination_network = ipaddress.ip_network(destination_ip, strict=False)
            return source_network.subnet_of(destination_network)
        except ValueError:
            return False
    
    def load_sample_rules(self):
        """Load sample firewall rules"""
        return [
            ["1", "tcp", "0.0.0.0/0", "any", "192.168.1.100", "80", "ACCEPT"],
            ["2", "tcp", "0.0.0.0/0", "any", "192.168.1.100", "443", "ACCEPT"],
            ["3", "tcp", "192.168.1.0/24", "any", "192.168.1.100", "22", "ACCEPT"],
            ["4", "tcp", "0.0.0.0/0", "any", "192.168.1.100", "3389", "DROP"],
            ["5", "tcp", "10.0.0.0/8", "any", "192.168.1.200", "3306", "ACCEPT"],
            ["6", "tcp", "0.0.0.0/0", "any", "192.168.1.200", "3306", "DROP"]
        ]
    
    def create_dashboard_metrics(self, rules):
        """Create dashboard metrics"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Rules", len(rules))
            
        with col2:
            accept_rules = sum(1 for rule in rules if len(rule) >= 7 and rule[6].upper() == "ACCEPT")
            st.metric("Accept Rules", accept_rules)
            
        with col3:
            drop_rules = sum(1 for rule in rules if len(rule) >= 7 and rule[6].upper() == "DROP")
            st.metric("Drop Rules", drop_rules)
            
        with col4:
            protocols = list(set(rule[1] for rule in rules if len(rule) >= 2))
            st.metric("Protocols", len(protocols))
    
    def create_rule_visualization(self, rules):
        """Create rule visualization charts"""
        if not rules:
            return
            
        # Create DataFrame
        df = pd.DataFrame(rules, columns=["Rule", "Protocol", "Source", "Source_Port", "Destination", "Destination_Port", "Action"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Action distribution pie chart
            action_counts = df['Action'].value_counts()
            fig = px.pie(values=action_counts.values, names=action_counts.index, 
                        title="Action Distribution", hole=0.3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Protocol distribution bar chart
            protocol_counts = df['Protocol'].value_counts()
            fig = px.bar(x=protocol_counts.index, y=protocol_counts.values,
                        title="Protocol Distribution", labels={'x': 'Protocol', 'y': 'Count'})
            st.plotly_chart(fig, use_container_width=True)
    
    def create_rule_table(self, rules):
        """Create interactive rule table"""
        if not rules:
            st.info("No rules loaded. Please load firewall rules.")
            return
            
        df = pd.DataFrame(rules, columns=["Rule", "Protocol", "Source", "Source_Port", "Destination", "Destination_Port", "Action"])
        
        # Add color coding for actions
        def color_action(val):
            color = 'green' if val == 'ACCEPT' else 'red' if val == 'DROP' else 'orange'
            return f'color: {color}'
        
        styled_df = df.style.applymap(color_action, subset=['Action'])
        
        st.dataframe(styled_df, use_container_width=True)
    
    def create_analysis_report(self, rules):
        """Create comprehensive analysis report"""
        if not rules:
            st.warning("No rules to analyze")
            return
            
        missing = self.detect_missing_rules(rules)
        redundant = self.detect_redundant_rules(rules)
        outdated = self.detect_outdated_rules(rules)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Missing Rules", len(missing))
            if missing:
                st.write("Rules:", ", ".join(missing))
        
        with col2:
            st.metric("Redundant Rules", len(redundant))
            if redundant:
                st.write("Rules:", ", ".join(redundant))
        
        with col3:
            st.metric("Outdated Rules", len(outdated))
            if outdated:
                st.write("Rules:", ", ".join(outdated))
    
    def create_rule_editor(self):
        """Create interactive rule editor"""
        st.subheader("🔧 Rule Editor")
        
        with st.form("add_rule_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                rule_number = st.number_input("Rule Number", min_value=1, value=1)
                protocol = st.selectbox("Protocol", ["tcp", "udp", "icmp", "any"])
                source_ip = st.text_input("Source IP/CIDR", "0.0.0.0/0")
                source_port = st.text_input("Source Port", "any")
                
            with col2:
                destination_ip = st.text_input("Destination IP/CIDR", "192.168.1.100")
                destination_port = st.text_input("Destination Port", "80")
                action = st.selectbox("Action", ["ACCEPT", "DROP", "REJECT"])
                
            submitted = st.form_submit_button("Add Rule")
            
            if submitted:
                try:
                    # Validate IP addresses
                    ipaddress.ip_network(source_ip, strict=False)
                    ipaddress.ip_network(destination_ip, strict=False)
                    
                    new_rule = [str(rule_number), protocol, source_ip, source_port, destination_ip, destination_port, action]
                    st.session_state.rules.append(new_rule)
                    st.success("Rule added successfully!")
                    st.rerun()
                    
                except ValueError as e:
                    st.error(f"Invalid IP address: {e}")
    
    def create_export_functionality(self):
        """Create export functionality"""
        st.subheader("📤 Export Rules")
        
        if st.session_state.rules:
            # Create CSV
            df = pd.DataFrame(st.session_state.rules, 
                            columns=["Rule", "Protocol", "Source", "Source_Port", "Destination", "Destination_Port", "Action"])
            
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f"firewall_rules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # Create JSON
            json_data = json.dumps(st.session_state.rules, indent=2)
            st.download_button(
                label="Download as JSON",
                data=json_data,
                file_name=f"firewall_rules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    def create_file_uploader(self):
        """Create file uploader"""
        st.subheader("📁 Upload Firewall Rules")
        
        uploaded_file = st.file_uploader("Choose a file", type=['txt', 'json', 'csv'])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.json'):
                    rules = json.load(uploaded_file)
                elif uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                    rules = df.values.tolist()
                else:
                    # Assume text file format
                    content = uploaded_file.read().decode('utf-8')
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                    rules = [line.split() for line in lines]
                
                st.session_state.rules = rules
                st.success(f"Loaded {len(rules)} rules from {uploaded_file.name}")
                
            except Exception as e:
                st.error(f"Error loading file: {e}")

def main():
    st.markdown('<h1 class="main-header">🔥 Enhanced Firewall Analyzer</h1>', unsafe_allow_html=True)
    
    analyzer = StreamlitFirewallAnalyzer()
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Navigation")
        
        # Load sample rules
        if st.button("Load Sample Rules"):
            st.session_state.rules = analyzer.load_sample_rules()
            st.success("Sample rules loaded!")
        
        # Theme toggle
        theme = st.selectbox("Theme", ["Light", "Dark"])
        st.session_state.theme = theme.lower()
        
        # File upload
        analyzer.create_file_uploader()
    
    # Main content
    if st.session_state.rules:
        # Dashboard
        st.header("📊 Dashboard")
        analyzer.create_dashboard_metrics(st.session_state.rules)
        
        # Visualizations
        st.header("📈 Visualizations")
        analyzer.create_rule_visualization(st.session_state.rules)
        
        # Rules table
        st.header("📋 Firewall Rules")
        analyzer.create_rule_table(st.session_state.rules)
        
        # Analysis
        st.header("🔍 Analysis Report")
        analyzer.create_analysis_report(st.session_state.rules)
        
        # Rule editor
        analyzer.create_rule_editor()
        
        # Export functionality
        analyzer.create_export_functionality()
        
    else:
        st.info("👋 Welcome! Please load firewall rules using the sidebar to get started.")
        
        # Quick start guide
        with st.expander("📖 Quick Start Guide"):
            st.markdown("""
            ### How to use this analyzer:
            1. **Load Sample Rules**: Click the button in the sidebar to load sample firewall rules
            2. **Upload Your Rules**: Upload your own firewall rules file (TXT, JSON, or CSV)
            3. **Analyze Rules**: View comprehensive analysis including missing, redundant, and outdated rules
            4. **Visualize Data**: See interactive charts and visualizations
            5. **Edit Rules**: Add new rules using the interactive editor
            6. **Export Results**: Download your rules in CSV or JSON format
            
            ### Supported File Formats:
            - **TXT**: Space-separated values
            - **JSON**: Array of arrays
            - **CSV**: Standard CSV format with headers
            """)

if __name__ == "__main__":
    main()  
#run with
#cd interfaceUI
#streamlit run streamlit_app.py