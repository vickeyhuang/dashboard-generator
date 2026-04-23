#!/usr/bin/env python3
# main.py
"""
Merchant Experience Dashboard Generator
Main entrance
"""

import os
import sys
import argparse
from datetime import datetime

# Add src path to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import load_data
from data_processor import DataProcessor
from chart_generator import ChartGenerator
from dashboard_builder import DashboardBuilder
from report_generator import ReportGenerator

def main():
    """main"""
    print("=" * 60)
    print("📊 Delivery Dashboard Generator")
    print("=" * 60)
    
    # Parse argument - using two positional paras
    parser = argparse.ArgumentParser(description='Generate Delivery Dashboard')
    parser.add_argument('input_file', help='Input file path (CSV or Excel)')
    parser.add_argument('output_dir', nargs='?', default='output', 
                       help='Output direction path (option, defaul: output)')
    parser.add_argument('--debug', action='store_true', help='Enable debugging mode')

    # new
    parser.add_argument('--portfolio', help='domainName (e.g. Merchant Experience)')
    parser.add_argument('--project', help='projectName (e.g. Squad Self Service)')
    
    args = parser.parse_args()
    
    # Verify parameter: provide only one between protfolio and project
    if args.portfolio and args.project:
        print("❌ error: can't sepcify both --portfolio and --project parameters at the same time")
        print("Please use only one of them.")
        sys.exit(1)

    try:
        # Create output direction
        output_dir = args.output_dir
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Output dir: {os.path.abspath(output_dir)}")

        # Ensure Dashboard title
        dashboard_title = None
        if args.portfolio:
            dashboard_title = f"{args.portfolio} Portfolio Dashboard"
            print(f"🏷️  Use portfolio name: {args.portfolio}")
            print(f"📋 Dashboard title: {dashboard_title}")
        elif args.project:
            dashboard_title = f"{args.project} Project Dashboard"
            print(f"🏷️  Use project name: {args.project}")
            print(f"📋 Dashboard title: {dashboard_title}")
        else:
            print("🏷️  Use default title")
        
        # Load data
        df = load_data(args.input_file)
        print(f"📈 Original data shape: {df.shape}")
        
        if args.debug:
            print("\n🔍 Debugging mode: showing first 5 lines data")
            print(df.head())
            print("\n🔍 ColumnName:")
            print(df.columns.tolist())
        
        # Process data
        processor = DataProcessor()
        processed_df, original_order, has_explicit_total, explicit_total_row = processor.process_data(df)
        
        if args.debug:
            print("\n🔍 Processed data:")
            print(processed_df.head())
        
        # Fetch column name - input the original df
        column_display_name = processor.get_column_display_name(df)  # input the original df
        column_plural_name = processor.get_column_plural_name(df)    # input the original df

        print(f"📝 columnName: singular='{column_display_name}', plural='{column_plural_name}'")
        
        # Get project data
        project_data = processor.get_project_data(processed_df, original_order)
        
        # Get total row
        total_row = processor.get_total_row(processed_df, has_explicit_total, explicit_total_row)
        
        print(f"\n📊 Summary:")
        print(f"   To Do: {total_row['To Do']}")
        print(f"   In Progress: {total_row['In Progress']}")
        print(f"   Blocked: {total_row['Blocked']}")
        # print(f"   Blocked: {total_row.get('Blocked', 0)}")  # new Blocked status
        print(f"   Done: {total_row['Done']}")
        print(f"   Total: {total_row['Total']}")
        print(f"   Completion: {total_row['Completion %']}")
        
        # Generate charts
        print("\n" + "=" * 40)
        print("🎨 Generate chart...")
        print("=" * 40)
        
        chart_gen = ChartGenerator(processor.colors)
        
        # Generate pie chart
        pie_chart_path = chart_gen.create_pie_chart(total_row, output_dir, column_display_name)
        
        # Generate bar chart
        bar_chart_path = chart_gen.create_bar_chart(
            project_data, original_order, total_row, output_dir, 
            column_display_name, column_plural_name
        )
        
        # Generate Dashboard
        print("\n" + "=" * 40)
        print("📋 Generate Dashboard...")
        print("=" * 40)
        
        dashboard_builder = DashboardBuilder(processor.colors, processor.overview_colors)
        
        dashboard_path = dashboard_builder.create_dashboard(
            project_data, total_row, original_order, output_dir,
            column_display_name, column_plural_name,
            custom_title=dashboard_title # pass custom title
        )
        
        # Generate report
        print("\n" + "=" * 40)
        print("📄 Generate report...")
        print("=" * 40)
        
        report_gen = ReportGenerator()
        report_path = report_gen.generate_html_report(
            project_data, total_row, output_dir, column_display_name
        )
        
        # Save CSV file
        report_gen.save_csv_files(project_data, total_row, output_dir)
        
        # Print completion
        print("\n" + "=" * 60)
        print("✅ Generate completion! ")
        print("=" * 60)

        # Print title info
        if dashboard_title:
            print(f"\n📋 Dashboard Title: {dashboard_title}")
        else:
            print(f"\n📋 Dashboard Title: {column_plural_name} Delivery Dashboard")

        # Get dashboard file name
        dashboard_filename = os.path.basename(dashboard_path)

        print(f"\n📋 Generate file:")
        print(f"   1. Completed Dashboard: {dashboard_filename}")
        print(f"   2. HTML Report: {os.path.basename(report_path)}")
        print(f"   3. Pie Chart: {os.path.basename(pie_chart_path)}")
        print(f"   4. Bar Chart: {os.path.basename(bar_chart_path)}")
        print(f"   5. Details data: detailed_analysis.csv")
        print(f"   6. Summary data: summary.csv")
        
        print(f"\n📁 File path: {os.path.abspath(output_dir)}")
        
        # Open Dashboard in the web Browser
        try:
            import webbrowser
            webbrowser.open(f'file://{os.path.abspath(dashboard_path)}')
            print(f"\n🌐 Opened Dashboard in the webBrowser")
        except:
            print(f"\n📝 To check Dashboard, please open: {dashboard_path}")
        
        print("\n" + "=" * 60)
        
    except FileNotFoundError as e:
        print(f"\n❌ File error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Value error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()