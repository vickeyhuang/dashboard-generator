# src/report_generator.py
"""
report generator module
response for generating kinds of reports
support dynamical column name showing
"""

import pandas as pd
import os
import glob

class ReportGenerator:
    def generate_html_report(self, project_data, total_row, output_dir, column_display_name="Project", dashboard_path=None):
        """Generate HTML report - using dynamic column name"""
        print(f"\n📄 Generate HTML report（{column_display_name}）...")
        
        # Decide the title based on column name
        if column_display_name and column_display_name.lower() == "project":
            report_title = "Projects Summary Report"
        elif column_display_name:
            report_title = f"{column_display_name} Summary Report"
        else:
            report_title = "Summary Report"
        
        # Determine dashboard filename
        if dashboard_path and os.path.exists(dashboard_path):
            # Use the provided dashboard path
            dashboard_filename = os.path.basename(dashboard_path)
        else:
            # Fallback: find the latest dashboard file
            dashboard_files = glob.glob(os.path.join(output_dir, "dashboard_*.html"))
            if dashboard_files:
                latest_dashboard = max(dashboard_files, key=os.path.getmtime)
                dashboard_filename = os.path.basename(latest_dashboard)
                print(f"   Using latest dashboard: {dashboard_filename}")
            else:
                dashboard_filename = "dashboard.html"
                print("   Using default dashboard filename")

        # Create table title
        table_rows = ""
        for row in project_data:
            table_rows += f"""
                <tr>
                    <td>{row['Project']}</td>
                    <td>{row['To Do']}</td>
                    <td>{row['In Progress']}</td>
                    <td>{row['Blocked']}</td>
                    <td>{row['Done']}</td>
                    <td>{row['Total']}</td>
                    <td><strong>{row['Completion %']}</strong></td>
                </tr>"""
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{report_title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .summary {{ 
            display: flex; 
            justify-content: space-around; 
            margin: 20px 0; 
            padding: 20px;
            background: #f5f5f5;
            border-radius: 10px;
        }}
        .summary-item {{ text-align: center; }}
        .summary-number {{ font-size: 24px; font-weight: bold; }}
        .todo {{ color: #FF6B6B; }}
        .progress {{ color: #4ECDC4; }}
        .blocked {{color: #ef4444;}}
        .done {{ color: #45B7D1; }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 20px;
        }}
        th, td {{ 
            padding: 10px; 
            border: 1px solid #ddd; 
            text-align: left;
        }}
        th {{ background: #f5f5f5; }}
        .links {{ margin: 20px 0; text-align: center; }}
        .link {{ 
            display: inline-block;
            margin: 0 10px;
            padding: 10px 20px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{report_title}</h1>
            <p>Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-item">
                <div class="summary-number todo">{total_row['To Do']}</div>
                <div>To Do</div>
            </div>
            <div class="summary-item">
                <div class="summary-number progress">{total_row['In Progress']}</div>
                <div>In Progress</div>
            </div>
            <div class="summary-item">
                <div class="summary-number blocked">{total_row['Blocked']}</div>
                <div>Blocked</div>
            </div>
            <div class="summary-item">
                <div class="summary-number done">{total_row['Done']}</div>
                <div>Done</div>
            </div>
            <div class="summary-item">
                <div class="summary-number">{total_row['Total']}</div>
                <div>Total Issues</div>
            </div>
            <div class="summary-item">
                <div class="summary-number">{total_row['Completion %']}</div>
                <div>Completion Rate</div>
            </div>
        </div>
        
        <div class="links">
            <a href="{dashboard_filename}" class="link" target="_blank">View Complete Dashboard</a>
            <a href="pie_chart.html" class="link" target="_blank">View Pie Chart</a>
            <a href="delivery_progress.html" class="link" target="_blank">View Delivery Progress</a>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>{column_display_name if column_display_name else 'Project'}</th>
                    <th>To Do</th>
                    <th>In Progress</th>
                    <th>Blocked</th>
                    <th>Done</th>
                    <th>Total</th>
                    <th>Completion %</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
                <tr style="background: #f5f5f5; font-weight: bold;">
                    <td>TOTAL</td>
                    <td>{total_row['To Do']}</td>
                    <td>{total_row['In Progress']}</td>
                    <td>{total_row['Blocked']}</td>
                    <td>{total_row['Done']}</td>
                    <td>{total_row['Total']}</td>
                    <td>{total_row['Completion %']}</td>
                </tr>
            </tbody>
        </table>
        
        <div style="margin-top: 20px; padding: 10px; background: #f5f5f5; border-radius: 5px;">
            <p><strong>Status Mapping:</strong> To Do = To Do + Backlog + Prioritised | In Progress = In Progress + Review | Blocked = Blocked | Done = Done</p>
        </div>
    </div>
</body>
</html>"""
        
        report_path = os.path.join(output_dir, 'report.html')
        with open(report_path, 'w') as f:
            f.write(html)
        
        print(f"✅ HTML report saved: {report_path}")
        return report_path
    
    def save_csv_files(self, project_data, total_row, output_dir):
        """Saved CSV file"""
        print("\n💾 save data file...")
        
        # Details data
        if project_data:
            df = pd.DataFrame(project_data)
            csv_path = os.path.join(output_dir, 'detailed_analysis.csv')
            df[['Project', 'To Do', 'In Progress', 'Blocked', 'Done', 'Total', 'Completion %']].to_csv(csv_path, index=False)
            print(f"✅ Details data saved: {csv_path}")
        
        # Summary data
        summary = pd.DataFrame({
            'Metric': ['Total Issues', 'To Do', 'In Progress', 'Blocked', 'Done', 'Completion %'],
            'Value': [
                str(total_row['Total']),
                str(total_row['To Do']),
                str(total_row['In Progress']),
                str(total_row['Blocked']),
                str(total_row['Done']),
                total_row['Completion %']
            ]
        })
        summary_path = os.path.join(output_dir, 'summary.csv')
        summary.to_csv(summary_path, index=False)
        print(f"✅ Summary data saved: {summary_path}")