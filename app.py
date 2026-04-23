#!/usr/bin/env python3
# app.py
"""
Streamlit Web Application for Delivery Dashboard Generator
Upload data file, generate visualization dashboard online - Full width display
"""

import streamlit as st
import pandas as pd
import os
import sys
import io
import tempfile
from datetime import datetime
import base64
from pathlib import Path

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_processor import DataProcessor
from chart_generator import ChartGenerator
from dashboard_builder import DashboardBuilder
from report_generator import ReportGenerator

# ==================== Page Configuration ====================
st.set_page_config(
    page_title="Delivery Dashboard Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== Custom CSS ====================
st.markdown("""
<style>
    /* Main container padding control */
    .main > div {
        padding-right: 30px !important;
        padding-left: 30px !important;
        padding-top: 50px !important;
    }
    
    /* Block container spacing */
    .block-container {
        padding-right: 30px !important;
        padding-left: 30px !important;
        padding-top: 50px !important;
        max-width: 100% !important;
    }
    
    /* Main header style */
    .main-header {
        text-align: center;
        padding: 1rem 0 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 30px;
        color: white;
    }
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0px;
    }
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-bottom: 0px;
    }
    
    /* Success message box */
    .success-box {
        background-color: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Upload area */
    .upload-area {
        border: 2px dashed #cbd5e1;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        background-color: #f8fafc;
    }
    
    /* Download panel style */
    .download-panel {
        background-color: #f8fafc;
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
    }
    .download-panel h3 {
        color: #1e293b;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    /* Download button style */
    .download-btn {
        display: inline-block;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 500;
        text-align: center;
        transition: all 0.3s ease;
        margin-right: 1rem;
        margin-bottom: 0.5rem;
    }
    .download-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Dashboard container */
    .dashboard-container {
        background-color: #f8fafc;
        border-radius: 16px;
        padding: 0;
        border: 1px solid #e2e8f0;
        overflow: hidden;
    }
    
    /* Stats card */
    .stats-card {
        background-color: white;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .stats-number {
        font-size: 2rem;
        font-weight: 700;
        color: #3b82f6;
    }
    .stats-label {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #94a3b8;
        font-size: 0.8rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 2rem;
    }
    
    /* Reduce top margin for first element after header */
    .element-container:first-of-type {
        margin-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)


def load_uploaded_file(uploaded_file):
    """Load uploaded file"""
    if uploaded_file is None:
        return None
    
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_extension == 'csv':
            content = uploaded_file.getvalue().decode('utf-8')
            if '\t' in content[:500]:
                df = pd.read_csv(io.StringIO(content), sep='\t')
            else:
                df = pd.read_csv(io.StringIO(content))
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        else:
            st.error(f"Unsupported file format: {file_extension}, please use CSV or Excel file")
            return None
        return df
    except Exception as e:
        st.error(f"File loading failed: {e}")
        return None


def validate_dataframe(df):
    """Validate DataFrame format"""
    if 'Project' not in df.columns:
        for col in df.columns:
            col_lower = col.lower()
            if 'project' in col_lower or 'parent' in col_lower or 'team' in col_lower:
                df = df.rename(columns={col: 'Project'})
            elif 'todo' in col_lower or 'to do' in col_lower:
                df = df.rename(columns={col: 'To Do'})
            elif 'progress' in col_lower or 'in progress' in col_lower:
                df = df.rename(columns={col: 'In Progress'})
            elif 'done' in col_lower or 'completed' in col_lower:
                df = df.rename(columns={col: 'Done'})
            elif 'blocked' in col_lower:
                df = df.rename(columns={col: 'Blocked'})
    
    if 'Project' not in df.columns:
        st.error("❌ Cannot find project column, please ensure Project column exists")
        return None
    
    return df


# ==================== Main Page ====================

def main():
    # Header area
    st.markdown("""
    <div class="main-header">
        <h1>📊 Delivery Dashboard Generator</h1>
        <p>Upload Jira data file, generate visualization dashboard with one click</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== Sidebar ====================
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # File upload
        uploaded_file = st.file_uploader(
            "📁 Upload Data File",
            type=['csv', 'xlsx', 'xls'],
            help="Support CSV and Excel formats, file should contain Project, To Do, In Progress, Done columns"
        )
        
        st.markdown("---")
        
        # Dashboard title configuration
        st.markdown("## 📝 Dashboard Title")
        title_mode = st.radio(
            "Title Mode",
            ["Default", "Portfolio Name", "Project Name"]
        )
        
        custom_title = None
        if title_mode == "Portfolio Name":
            portfolio_name = st.text_input("Portfolio Name", placeholder="e.g., Merchant Experience")
            if portfolio_name:
                custom_title = f"{portfolio_name} Portfolio Dashboard"
        elif title_mode == "Project Name":
            project_name = st.text_input("Project Name", placeholder="e.g., Squad Self Service")
            if project_name:
                custom_title = f"{project_name} Project Dashboard"
        
        st.markdown("---")
        
        # Instructions
        with st.expander("📖 Instructions"):
            st.markdown("""
            **Data Format Requirements:**
            - Required columns: `Project`, `To Do`, `In Progress`, `Done`
            - Optional columns: `Blocked`, `Backlog`, `Prioritised`
            
            **How to Get Data:**
            1. Create Filter in Jira
            2. Use Two Dimensional Filter component
            3. Select Status for X-axis, Project for Y-axis
            4. Copy generated table
            5. Save as CSV file and upload
            """)
        
        st.markdown("---")
        
        # Sample data download
        st.markdown("## 📥 Sample Template")
        if st.button("📄 Generate Sample Data Template"):
            sample_data = pd.DataFrame({
                'Project': ['Team A', 'Team B', 'Team C', 'Total:'],
                'To Do': [12, 8, 20, 40],
                'In Progress': [18, 15, 10, 43],
                'Blocked': [2, 0, 8, 10],
                'Done': [45, 62, 30, 137],
                'T:': [77, 85, 68, 230]
            })
            csv = sample_data.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="sample_data.csv">⬇️ Click to download sample_data.csv</a>'
            st.markdown(href, unsafe_allow_html=True)
    
    # ==================== Main Content Area ====================
    
    if uploaded_file is not None:
        # Load data
        with st.spinner("Loading data..."):
            df = load_uploaded_file(uploaded_file)
        
        if df is not None:
            # Validate data
            df = validate_dataframe(df)
            
            if df is not None:
                # Process data
                with st.spinner("Processing data..."):
                    processor = DataProcessor()
                    processed_df, original_order, has_explicit_total, explicit_total_row = processor.process_data(df)
                    project_data = processor.get_project_data(processed_df, original_order)
                    total_row = processor.get_total_row(processed_df, has_explicit_total, explicit_total_row)
                    column_display_name = processor.get_column_display_name(df)
                    column_plural_name = processor.get_column_plural_name(df)
                
                # Success message
                st.markdown(f"""
                <div class="success-box">
                    ✅ Data loaded successfully! Total <strong>{len(project_data)}</strong> teams/projects
                </div>
                """, unsafe_allow_html=True)
                
                if custom_title:
                    st.info(f"📋 Dashboard Title: {custom_title}")
                
                # Create temporary directory and generate Dashboard
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Generate full Dashboard
                    dashboard_builder = DashboardBuilder(processor.colors, processor.overview_colors)
                    dashboard_path = dashboard_builder.create_dashboard(
                        project_data, total_row, original_order, temp_dir,
                        column_display_name, column_plural_name,
                        custom_title=custom_title
                    )
                    
                    # Read generated Dashboard HTML
                    if os.path.exists(dashboard_path):
                        with open(dashboard_path, 'r', encoding='utf-8') as f:
                            dashboard_html = f.read()
                        dashboard_filename = os.path.basename(dashboard_path)
                    
                    # ==================== Dashboard Preview (Full Width) ====================
                    st.markdown("## 📊 Dashboard Preview")
                    
                    # Embed Dashboard HTML
                    if dashboard_path and os.path.exists(dashboard_path):
                        st.components.v1.html(dashboard_html, height=900, scrolling=True)
                    else:
                        st.info("Generating dashboard...")
                    
                    st.markdown("---")
                    
                    # ==================== Download Panel (Below Dashboard) ====================
                    
                    # # Stats cards
                    # col1, col2, col3, col4, col5 = st.columns(5)
                    
                    # with col1:
                    #     st.markdown(f"""
                    #     <div class="stats-card">
                    #         <div class="stats-number">{len(project_data)}</div>
                    #         <div class="stats-label">Teams/Projects</div>
                    #     </div>
                    #     """, unsafe_allow_html=True)
                    
                    # with col2:
                    #     st.markdown(f"""
                    #     <div class="stats-card">
                    #         <div class="stats-number">{total_row['Total']}</div>
                    #         <div class="stats-label">Total Issues</div>
                    #     </div>
                    #     """, unsafe_allow_html=True)
                    
                    # with col3:
                    #     st.markdown(f"""
                    #     <div class="stats-card">
                    #         <div class="stats-number">{total_row['Done']}</div>
                    #         <div class="stats-label">Completed</div>
                    #     </div>
                    #     """, unsafe_allow_html=True)
                    
                    # with col4:
                    #     st.markdown(f"""
                    #     <div class="stats-card">
                    #         <div class="stats-number">{total_row.get('Blocked', 0)}</div>
                    #         <div class="stats-label">Blocked</div>
                    #     </div>
                    #     """, unsafe_allow_html=True)
                    
                    # with col5:
                    #     st.markdown(f"""
                    #     <div class="stats-card">
                    #         <div class="stats-number">{total_row['Completion %']}</div>
                    #         <div class="stats-label">Completion Rate</div>
                    #     </div>
                    #     """, unsafe_allow_html=True)
                    
                    # st.markdown("---")
                    
                    # Export buttons row
                    st.markdown("### 📥 Export Files")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Download full Dashboard HTML
                        if dashboard_path and os.path.exists(dashboard_path):
                            with open(dashboard_path, 'r', encoding='utf-8') as f:
                                dashboard_html_content = f.read()
                            dashboard_b64 = base64.b64encode(dashboard_html_content.encode()).decode()
                            st.markdown(f'''
                            <a href="data:text/html;base64,{dashboard_b64}" download="{dashboard_filename}" class="download-btn" style="background-color: #3b82f6; color: white; display: inline-block; width: auto;">
                                📊 Download Full Dashboard (HTML)
                            </a>
                            ''', unsafe_allow_html=True)
                    
                    with col2:
                        # Prepare table data for export
                        table_data = []
                        for p in project_data:
                            row = {
                                column_display_name: p['Project'],
                                'To Do': int(p['To Do']),
                                'In Progress': int(p['In Progress']),
                                'Blocked': int(p.get('Blocked', 0)),
                                'Done': int(p['Done']),
                                'Total': int(p['Total']),
                                'Completion Rate': f"{p['Completion %']}"
                            }
                            table_data.append(row)
                        
                        table_data.append({
                            column_display_name: 'Total',
                            'To Do': int(total_row['To Do']),
                            'In Progress': int(total_row['In Progress']),
                            'Blocked': int(total_row.get('Blocked', 0)),
                            'Done': int(total_row['Done']),
                            'Total': int(total_row['Total']),
                            'Completion Rate': total_row['Completion %']
                        })
                        
                        df_table = pd.DataFrame(table_data)
                        
                        # Export CSV
                        csv_data = df_table.to_csv(index=False)
                        b64_csv = base64.b64encode(csv_data.encode()).decode()
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.markdown(f'''
                        <a href="data:file/csv;base64,{b64_csv}" download="dashboard_data_{timestamp}.csv" class="download-btn" style="background-color: #10b981; color: white; display: inline-block; width: auto;">
                            📥 Export Data as CSV
                        </a>
                        ''', unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # ==================== Detailed Data Table (Collapsible) ====================
                    with st.expander("📋 View Detailed Data Table"):
                        st.dataframe(df_table, use_container_width=True, hide_index=True)
                    
                    # ==================== Status Mapping Explanation (Collapsible) ====================
                    with st.expander("📖 Status Mapping Explanation"):
                        st.markdown("""
                        ### Status Mapping Rules
                        
                        | Dashboard Status | Jira Status Mapping |
                        |-----------------|---------------------|
                        | **To Do** | To Do, Backlog, Prioritised, Up Next, Selected for Development |
                        | **In Progress** | In Progress, In Review, Dev, STG, PRD, Waiting for Release |
                        | **Blocked** | Blocked, Paused |
                        | **Done** | Done, Completed, Released, Closed, Resolved |
                        
                        ### Completion Rate Calculation
                        > **Completion Rate = Done / Total × 100%**
                        
                        ### Completion Rate Color Legend
                        - 🟢 **Green (≥80%)**: On track or ahead of schedule
                        - 🟡 **Yellow (50-79%)**: Steady progress
                        - 🔴 **Red (<50%)**: Needs attention
                        """)
                
                # Footer
                st.markdown(f"""
                <div class="footer">
                    🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                    📊 Delivery Dashboard Generator | Auto-generated from Jira data
                </div>
                """, unsafe_allow_html=True)
    
    else:
        # Prompt when no file uploaded
        st.markdown("""
        <div class="upload-area">
            <h3>📂 Please upload data file from the sidebar</h3>
            <p>Support CSV or Excel format</p>
            <p style="color: #94a3b8; font-size: 0.9rem;">Dashboard will be automatically generated after upload</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature preview
        st.markdown("## 📊 Dashboard Includes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📈 Key Metrics Cards
            - To Do / In Progress / Blocked / Done
            - Total Issues / Completion Rate / Blocked Rate
            
            ### 🥧 Multi-dimensional Pie Charts
            - Issue Status Distribution
            - Completion Distribution by Project
            - Blocked Distribution by Project
            """)
        
        with col2:
            st.markdown("""
            ### 📊 Team Delivery Bar Chart
            - Stacked bar chart showing status distribution
            - Completion rate annotations
            
            ### 📋 Detailed Data Table
            - Complete raw data
            - Support export
            """)
        
        st.info("💡 **Tip**: Click 'Generate Sample Data Template' in the sidebar to download a sample file and understand the data format requirements")


if __name__ == "__main__":
    main()