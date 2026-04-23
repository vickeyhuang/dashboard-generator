# src/data_processor.py
"""
data processor module
response for data clean, transfer and summary
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

class DataProcessor:
    def __init__(self):
        """init data processor"""
        # status mapping
        self.status_mapping = {
            # To Do Status Group
            'To Do': 'To Do',
            'Backlog': 'To Do',
            'Prioritised': 'To Do',
            'Prioritized': 'To Do',
            'Up Next': 'To Do',
            'Selected for Development': 'To Do',
            'On Hold': 'To Do',
            
            # In Progress Status Group
            'In Progress': 'In Progress',
            
            # Blocked Status Group
            'Blocked': 'Blocked',
            'Block': 'Blocked',
            'Paused': 'Blocked',
            
            # Other In Progress
            'In Review': 'In Progress',
            'Dev': 'In Progress',
            'STG': 'In Progress',
            'DevTarget': 'In Progress',
            'Dev Complete': 'In Progress',
            'In Development': 'In Progress',
            'In Testing': 'In Progress',
            'Testing': 'In Progress',
            'Waiting for Release': 'In Progress',
            'Awaiting Review': 'In Progress',
            'Awaiting Release': 'In Progress',
            'PRD': 'In Progress',
            'Validate': 'In Progress',
            'Ready for Prod/Follow up': 'In Progress',
            'Awaiting CR Approval': 'In Progress',
            
            # Done Status Group
            'Done': 'Done',
            'Completed': 'Done',
            'Released': 'Done',
            'Closed': 'Done',
            'Resolved': 'Done',
            'Engineering Done': 'Done',
        }
        
        # color config
        self.colors = {
            'To Do': '#94a3b8',      # gray
            'In Progress': '#3b82f6', # blue
            'Blocked': '#ef4444',     # red - new
            'Done': '#10b981',        # green
            'Percentage': '#8b5cf6'   # purple
        }
        
        # Overview card color
        self.overview_colors = {
            'todo': '#94a3b8',
            'in_progress': '#3b82f6',
            'blocked': '#ef4444',     # new
            'done': '#10b981',
            'total': '#1e293b',
            'completion': '#8b5cf6'
        }
        
        # Status order
        self.status_order = ['To Do', 'In Progress', 'Blocked', 'Done']
        
        # Default column name
        self.default_column_names = ['project', 'issue', 'task', 'item', 'card']
    
    def process_data(self, df):
        """Process original data, response the processed data of DataFram and original order"""
        print("🔄 Processing data...")

        # Save original data for using the column name detection
        self.raw_df = df.copy()
        
        # Check if showing the total line
        has_explicit_total = False
        explicit_total_row = None
        
        # Check the total line more exact
        first_col_name = df.columns[0]
        for idx, row in df.iterrows():
            first_val = str(row[first_col_name]).strip()
            first_val_lower = first_val.lower()
            
            # Detect more exact total line
            is_total_row = (
                # Start by Total (exclude total name)
                first_val_lower == 'total' or
                first_val_lower.startswith('total ') or
                first_val_lower.startswith('total:') or
                first_val_lower.startswith('total unique') or
                # Other confirmed totals
                first_val_lower == 'totals' or
                first_val_lower == 'all' or
                first_val_lower == 'total issues'
            )
            
            # note: exclude the line with 'total', e.g. "Project X Total"
            # must start as 'total'
            
            if is_total_row:
                has_explicit_total = True
                explicit_total_row = row
                df = df.drop(idx)
                print(f"✅ detect total line(excluded): {first_val}")
                break
        
        # process each line data
        processed_rows = []
        original_order = []
        
        for idx, row in df.iterrows():
            processed_row = self._process_row(row)
            project_name = processed_row['Project']
            
            if project_name and project_name not in ['', 'nan', 'NaN']:
                processed_rows.append(processed_row)
                original_order.append(project_name)
        
        # Create processed DataFrame
        processed_df = pd.DataFrame(processed_rows)
        
        # Ensure all required columns existing
        required_columns = ['To Do', 'In Progress', 'Blocked', 'Done', 'Total', 'Completion %', 'Completion_Percent']
        for col in required_columns:
            if col not in processed_df.columns:
                processed_df[col] = 0 if col != 'Completion %' else '0%'
        
        print(f"✅ Data process completion: {len(processed_df)} items")
        return processed_df, original_order, has_explicit_total, explicit_total_row
    
    def _process_row(self, row):
        """Process single line data"""
        # Fetch project name in the first column
        project = ""
        row_dict = row.to_dict()
        
        # Try find columns
        for key, value in row_dict.items():
            if key == 'Project' or 'project' in str(key).lower() or 'parent' in str(key).lower():
                project = str(value).split('\t')[0].split('\n')[0].strip()
                break
        
        # Using the first column if no project column
        if not project and len(row_dict) > 0:
            first_key = list(row_dict.keys())[0]
            project = str(row_dict[first_key]).split('\t')[0].split('\n')[0].strip()
        
        # Init counter - add blcoked_count
        to_do_count = 0
        in_progress_count = 0
        blocked_count = 0  # new
        done_count = 0
        
        # Through each column(exclude project column)
        for key, value in row_dict.items():
            # Skip the project column
            key_str = str(key)
            if key_str == 'Project' or 'project' in key_str.lower() or 'parent' in key_str.lower():
                continue
            
            # Skip the total column
            key_clean = key_str.strip()
            if key_clean in ['T:', 'T', 'Total', 'Total:', 'Totals']:
                continue
            
            # Transfer value to group
            try:
                if isinstance(value, str):
                    value = value.replace(',', '').strip()
                    if value == '' or value.lower() in ['nan', 'null', 'none', '-', 'n/a']:
                        num_value = 0
                    else:
                        num_value = int(float(value))
                else:
                    num_value = int(float(value)) if pd.notna(value) else 0
            except (ValueError, TypeError):
                num_value = 0
            
            # when the value > 0
            if num_value > 0:
                column_status = key_str.strip()
                mapped_status = self._map_status(column_status)
                
                # Based on the accumlated status after mapping
                if mapped_status == 'To Do':
                    to_do_count += num_value
                elif mapped_status == 'In Progress':
                    in_progress_count += num_value
                elif mapped_status == 'Blocked':  # new
                    blocked_count += num_value
                elif mapped_status == 'Done':
                    done_count += num_value
        
        # total count
        total_count = to_do_count + in_progress_count + blocked_count + done_count
        
        # completion percentage
        completion_pct = round((done_count / total_count * 100)) if total_count > 0 else 0
        
        return {
            'Project': project,
            'To Do': int(to_do_count),
            'In Progress': int(in_progress_count),
            'Blocked': int(blocked_count),  # new
            'Done': int(done_count),
            'Total': int(total_count),
            'Completion %': f"{completion_pct}%",
            'Completion_Percent': completion_pct
        }
    
    def _map_status(self, status_str):
        """map status string to standard status in exact match"""
        if not status_str:
            return 'To Do'
        
        # clean status string
        status_lower = status_str.strip().lower()
        
        # exact match mapping - add blocked
        exact_mapping = {
            # To Do
            'to do': 'To Do',
            'todo': 'To Do',
            'backlog': 'To Do',
            'prioritised': 'To Do',
            'prioritized': 'To Do',
            'up next': 'To Do',
            'upnext': 'To Do',
            'selected for development': 'To Do',
            'selectedfordevelopment': 'To Do',
            'on hold': 'To Do',
            'onhold': 'To Do',
            
            # In Progress
            'in progress': 'In Progress',
            'inprogress': 'In Progress',
            'in review': 'In Progress',
            'inreview': 'In Progress',
            'dev': 'In Progress',
            'stg': 'In Progress',
            'devtarget': 'In Progress',
            'dev complete': 'In Progress',
            'devcomplete': 'In Progress',
            'in development': 'In Progress',
            'indevelopment': 'In Progress',
            'in testing': 'In Progress',
            'intesting': 'In Progress',
            'testing': 'In Progress',
            'waiting for release': 'In Progress',
            'waitingforrelease': 'In Progress',
            'awaiting release': 'In Progress',
            'awaitingrelease': 'In Progress',
            'awaiting review': 'In Progress',
            'awaitingreview': 'In Progress',
            'prd': 'In Progress',
            'validate': 'In Progress',
            'ready for prod/follow up': 'In Progress',
            'awaiting cr approval': 'In Progress',
            
            # Blocked - new
            'blocked': 'Blocked',
            'block': 'Blocked',
            'paused': 'Blocked',
            
            # Done
            'done': 'Done',
            'completed': 'Done',
            'released': 'Done',
            'closed': 'Done',
            'resolved': 'Done',
            'engineering done': 'Done',
        }
        
        # first try exact match
        if status_lower in exact_mapping:
            return exact_mapping[status_lower]
        
        # try to remove the space and special characters
        clean_status = status_lower.replace(' ', '').replace('_', '').replace('-', '')
        if clean_status in exact_mapping:
            return exact_mapping[clean_status]
        
        # return unknown
        return 'unknown'
    
    def get_total_row(self, processed_df, has_explicit_total=False, explicit_total_row=None):
        """fetch the total line - deal with the totals in two ways"""
        if processed_df.empty:
            return pd.Series({
                'Project': 'Total',
                'To Do': 0,
                'In Progress': 0,
                'Blocked': 0,
                'Done': 0,
                'Total': 0,
                'Completion %': '0%',
                'Completion_Percent': 0
            })
        
        # case1: reprocess it when total line is existing
        if has_explicit_total and explicit_total_row is not None:
            print("📊 reprocess the total data")
            # reprocess the total data, ensure the mapping correct
            processed_total = self._process_row(explicit_total_row)
            processed_total['Project'] = 'Total'
            return pd.Series(processed_total)
        
        # case2: auto calculate when total line is not existing
        print("📊 auto calculate the total")
        total_done = processed_df['Done'].sum()
        total_total = processed_df['Total'].sum()
        completion_pct = round((total_done / total_total * 100)) if total_total > 0 else 0
        
        return pd.Series({
            'Project': 'Total',
            'To Do': int(processed_df['To Do'].sum()),
            'In Progress': int(processed_df['In Progress'].sum()),
            'Blocked': int(processed_df['Blocked'].sum()),
            'Done': int(total_done),
            'Total': int(total_total),
            'Completion %': f"{completion_pct}%",
            'Completion_Percent': completion_pct
        })
    
    def get_project_data(self, processed_df, original_order):
        """fetch item data and order as the original series"""
        if processed_df.empty:
            return []
        
        # create project data
        project_data = []
        
        for project_name in original_order:
            if project_name in processed_df['Project'].values:
                project_row = processed_df[processed_df['Project'] == project_name].iloc[0]
                project_data.append({
                    'Project': project_name,
                    'To Do': project_row['To Do'],
                    'In Progress': project_row['In Progress'],
                    'Blocked': project_row['Blocked'],  # new
                    'Done': project_row['Done'],
                    'Total': project_row['Total'],
                    'Completion %': project_row['Completion %'],
                    'Completion_Percent': project_row['Completion_Percent']
                })
        
        return project_data
    
    def get_column_display_name(self, df=None):
        """detect column name"""
        # detect from the first column if DataFrame provided
        if df is not None and not df.empty:
            first_col = df.columns[0]
            # clean column name and remove possible special characters
            clean_name = str(first_col).split(':')[0].split('(')[0].strip()
            
            print(f"🔍 detected column name: original column name='{first_col}', cleaned='{clean_name}'")
            
            # Regular column name mapping
            column_name_mapping = {
                'project': 'Project',
                'parent': 'Parent',
                'team': 'Team',
                'squad': 'Squad',
                'component': 'Component',
                'epic': 'Epic',
                'initiative': 'Initiative',
                'issue': 'Issue',
                'task': 'Task',
                'item': 'Item'
            }
            
            lower_name = clean_name.lower()
            for key, value in column_name_mapping.items():
                if key in lower_name:
                    print(f"✅ mapped column name: '{lower_name}' -> '{value}'")
                    return value
            
            # default return the first capitalize column name
            result = clean_name.capitalize()
            print(f"⚠️  using default column name: '{result}'")
            return result
        
        # return the default data when no data
        print("⚠️  no data, use the default column name: 'Project'")
        return "Project"
    
    def get_column_plural_name(self, df=None):
        """fetch column name(plural) - based on singular"""
        singular_name = self.get_column_display_name(df)
        
        print(f"🔍 generate plural rules: singular='{singular_name}'")
        
        # special plural rules
        plural_rules = {
            'Project': 'Projects',
            'Parent': 'Parents', 
            'Team': 'Teams',
            'Squad': 'Squads',
            'Component': 'Components',
            'Epic': 'Epics',
            'Initiative': 'Initiatives',
            'Issue': 'Issues',
            'Task': 'Tasks',
            'Item': 'Items'
        }
        
        if singular_name in plural_rules:
            result = plural_rules[singular_name]
            print(f"✅ special plural rules: '{singular_name}' -> '{result}'")
            return result
        
        # general plural rules (singular+s,es,ies)
        if singular_name.endswith('y'):
            result = singular_name[:-1] + 'ies'
        else:
            result = singular_name + 's'
        
        print(f"✅ general plural rules: '{singular_name}' -> '{result}'")
        return result

if __name__ == "__main__":
    # test code
    processor = DataProcessor()
    print("✅ DataProcessor init successfully")
    print(f"status mapping: {list(processor.status_mapping.keys())[:5]}...")
    print(f"color config: {processor.colors}")