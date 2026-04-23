# src/chart_generator.py
"""
Charts generate module
Response for generate kinds of charts
Support dynamic column names
"""

import plotly.graph_objects as go
import os

class ChartGenerator:
    def __init__(self, colors):
        self.colors = colors
    
    def create_pie_chart(self, total_row, output_dir, column_display_name="Project"):
        """Create pie charts - keep the consistent order with tabel"""
        print(f"\n🎨 Create pie chart...")
        
        labels = ['Done', 'In Progress', 'Blocked', 'To Do'] 
        values = [total_row['Done'], total_row['In Progress'], total_row['Blocked'], total_row['To Do']]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            marker_colors=[self.colors['Done'], 
                          self.colors['In Progress'], 
                          self.colors['Blocked'], # Blocked color #ef4444
                          self.colors['To Do']],
            textinfo='percent',
            textposition='outside'
        )])
        
        fig.update_layout(
            title_text='Total Issue Status %',
            title_x=0.5,
            title_font_size=16,
            height=400,
            showlegend=True,
            annotations=[
                dict(
                    text=f"Total<br>{total_row['Total']}",
                    x=0.5, y=0.5,
                    font_size=18,
                    showarrow=False
                )
            ],
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        pie_path = os.path.join(output_dir, 'pie_chart.html')
        fig.write_html(pie_path)
        print(f"✅ Pie chart saved: {pie_path}")
        return pie_path
    
    def create_bar_chart(self, project_data, original_order, total_row, output_dir, 
                        column_display_name="Project", column_plural_name="Projects"):
        """Create bar chart with the percentage line - using dynamic name"""
        print(f"\n📊 Create bar chart...")
        
        # Decide the title based on the column name
        if column_display_name and column_display_name.lower() == "project":
            # When columnName is Project, using Projects
            chart_title = "Projects Delivery Progress"
        elif column_display_name and column_display_name.lower() == "parent":
            # When columnName is Parent, using Parent
            chart_title = "Parent Delivery Progress"
        elif column_display_name:
            chart_title = f"{column_display_name} Delivery Progress"
        else:
            chart_title = "Projects Delivery Progress"
        
        # Prepare data as the original order
        projects = []
        to_do_values = []
        in_progress_values = []
        blocked_values = []  # new
        done_values = []
        completion_pcts = []
        totals = []
        
        for project in original_order:
            for row in project_data:
                if row['Project'] == project:
                    projects.append(row['Project'])
                    to_do_values.append(row['To Do'])
                    in_progress_values.append(row['In Progress'])
                    blocked_values.append(row['Blocked'])  # new
                    done_values.append(row['Done'])
                    completion_pcts.append(row['Completion_Percent'])
                    totals.append(row['Total'])
                    break
        
        max_total = max(totals) if totals else 100
        
        # Create figure
        fig = go.Figure()
        
        # Add bar as Done,In Progress,To Do order
        fig.add_trace(go.Bar(
            y=projects,
            x=done_values,
            name='Done',
            orientation='h',
            marker_color=self.colors['Done'],
            text=done_values,
            textposition='inside',
            textfont_color='white'
        ))
        
        fig.add_trace(go.Bar(
            y=projects,
            x=in_progress_values,
            name='In Progress',
            orientation='h',
            marker_color=self.colors['In Progress'],
            text=in_progress_values,
            textposition='inside',
            textfont_color='white'
        ))

        fig.add_trace(go.Bar(
            y=projects,
            x=blocked_values,
            name='Blocked',  # new add
            orientation='h',
            marker_color='#ef4444',  # red
            text=blocked_values,
            textposition='inside',
            textfont_color='white'
        ))
        
        fig.add_trace(go.Bar(
            y=projects,
            x=to_do_values,
            name='To Do',
            orientation='h',
            marker_color=self.colors['To Do'],
            text=to_do_values,
            textposition='inside',
            textfont_color='white'
        ))
        
        # Add the completion label of right side
        completion_x_position = max_total * 1.1
        
        # Add percentage points
        for i, (project, pct) in enumerate(zip(projects, completion_pcts)):
            fig.add_annotation(
                text=f"<b>{int(pct)}%</b>",
                x=completion_x_position,
                y=project,
                showarrow=False,
                font=dict(size=12, color=self.colors['Percentage']),
                bgcolor="white",
                bordercolor=self.colors['Percentage'],
                borderwidth=1,
                borderpad=4
            )
        
        # Update the layout
        fig.update_layout(
            title_text=chart_title,
            title_x=0.5,
            title_font_size=16,
            barmode='stack',
            height=500,
            # width=900,
            yaxis=dict(
                title=column_display_name if column_display_name else "Projects",
                categoryorder='array',
                categoryarray=projects,
                autorange="reversed",
                showgrid=True,
                tickfont=dict(size=12),
                ticklabelstandoff=10
            ),
            xaxis=dict(
                title="Number of Issues",
                title_standoff=60,
                range=[0, max_total * 1.2],
                showgrid=True,
                gridcolor='#f1f5f9',
                tickfont=dict(size=12)
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=80, b=100, l=150, r=200),
            hovermode='y unified',
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Add the right title - Completion %
        fig.add_annotation(
            text="<b>Completion %</b>",
            xref="paper",
            yref="paper",
            x=0.98,
            y=1.05,
            showarrow=False,
            font=dict(size=14, color='black'),
            xanchor='right'
        )
        
        # Save Bar chart
        bar_path = os.path.join(output_dir, 'delivery_progress.html')
        fig.write_html(bar_path)
        print(f"✅ Bar chart saved: {bar_path}")
        return bar_path