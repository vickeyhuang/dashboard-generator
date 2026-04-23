# src/dashboard_builder.py
"""
Dashboard struction module - added a download function
"""

import plotly.graph_objects as go
import os
import pandas as pd
from datetime import datetime
import json
import math

class DashboardBuilder:
    def __init__(self, colors, overview_colors):
        self.colors = colors
        self.overview_colors = overview_colors
    
    def create_dashboard(self, project_data, total_row, original_order, output_dir, column_display_name="Project", column_plural_name="Projects", custom_title=None):
        """Create a full Dashboard - dynamic column name and plural names"""
        print(f"\n📋 Create a full Dashboard（{column_plural_name}）...")
        
        # Save the column name
        self.column_display_name = column_display_name
        self.column_plural_name = column_plural_name
        self.custom_title = custom_title # save custom title
        
        # Prepare data - keep the same order with table name
        projects, to_do_values, in_progress_values, blocked_values, done_values, completion_pcts, totals = \
            self._prepare_data(project_data, original_order)
        
        max_total = max(totals) if totals else 100
        
        # Save Dashboard
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dashboard_filename = f"dashboard_{timestamp}.html"
        dashboard_path = os.path.join(output_dir, dashboard_filename)
        
        # Create a full HTML - fetch a correct method name
        full_html = self._generate_dashboard_html(
            project_data, total_row, projects, to_do_values, 
            in_progress_values, blocked_values, done_values, completion_pcts, 
            max_total, dashboard_path
        )
    
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"✅ Dashboard: {dashboard_path}")

        # also generate a latest dashboard without timestamp 
        # latest_path = os.path.join(output_dir, 'dashboard_latest.html')
        # try:
        #     import shutil
        #     shutil.copy2(dashboard_path, latest_path)
        #     print(f"📄 Latest copy dashboard: {latest_path}")
        # except Exception as e:
        #     print(f"⚠️ Can't create latest copy dashboard: {e}")
        
        return dashboard_path
    
    def _prepare_data(self, project_data, original_order):
        """Prepare data - keep the same order with table name"""
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
        
        return projects, to_do_values, in_progress_values, blocked_values, done_values, completion_pcts, totals
    
    def _create_pie_charts_section(self, project_data, total_row, projects_order):
        """Create pie chart section"""
        column_name = self.column_display_name if hasattr(self, 'column_display_name') else "Project"
        
        total_done = sum(row['Done'] for row in project_data)
        
        # Using the default value when teh data is null
        if total_done == 0:
            total_done = 1
        
        # Pie chart1: Status distribution
        todo_val = int(total_row.get('To Do', 0))
        in_progress_val = int(total_row.get('In Progress', 0))
        blocked_val = int(total_row.get('Blocked', 0))  # new
        done_val = int(total_row.get('Done', 0))
        total_val = int(total_row.get('Total', 0))
        
        # Calculate the percentage (round 0)
        status_percentages = [0, 0, 0]
        if total_val > 0:
            status_percentages = [
                round(done_val / total_val * 100),
                round(in_progress_val / total_val * 100),
                round(blocked_val / total_val * 100),  # new
                round(todo_val / total_val * 100)
            ]
        
        # Pie chart2: Issue completion distribution
        project_done_values = []
        project_names = []
        project_colors = ['#10b981', '#3b82f6', '#ef4444', '#06b6d4', '#f59e0b', '#8b5cf6']
        
        for i, project in enumerate(projects_order):
            for row in project_data:
                if row['Project'] == project:
                    project_names.append(row['Project'])
                    project_done_values.append(int(row['Done']))
                    break
        
        # Add a default value when project name is empty
        if not project_names:
            project_names = ['Project A', 'Project B', 'Project C']
            project_done_values = [100, 150, 200]
            total_done = 450
        
        # Calculte project completion percentages(round 0)
        project_percentages = []
        for value in project_done_values:
            if total_done > 0:
                project_percentages.append(round(value / total_done * 100))
            else:
                project_percentages.append(0)
        
        # Ensure all values with int fomart
        project_done_values = [int(v) for v in project_done_values]
        project_percentages = [int(p) for p in project_percentages]
        
        # Ensure the formal consistent via json.dumps
        import json
        project_names_str = json.dumps(project_names)
        project_done_values_str = json.dumps(project_done_values)
        project_percentages_str = json.dumps(project_percentages)
        status_percentages_str = json.dumps(status_percentages)
        
        # Fixed: the right color names
        quoted_colors = ['"' + color + '"' for color in project_colors[:len(project_names)]]
        project_colors_str = '[' + ', '.join(quoted_colors) + ']'
        
        # Pie chart2's title
        pie_chart2_title = f"Done Issues Distribution by {column_name}"
        
        # Create pie chart senction's HTML structure
        pie_charts_html = f"""
        <!-- First: Two pie charts -->
        <div class="pie-charts-section">
            <!-- PieChart1: Status Distribution -->
            <div class="card">
                <h2 class="card-title">Total Issues Distribution by Status</h2>
                <div class="pie-container">
                    <canvas id="statusPieChart" width="400" height="400"></canvas>
                </div>
            </div>
            
            <!-- PieChart2: {column_name.lower()}Completion -->
            <div class="card">
                <h2 class="card-title">{pie_chart2_title}</h2>
                <div class="pie-container">
                    <canvas id="projectPieChart" width="400" height="400"></canvas>
                </div>
            </div>
        </div>
        
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Start initial pie chart...');
            
            // Setup global tooltip z-index
            Chart.defaults.plugins.tooltip.zIndex = 99999;
            
            // PieChart1: Status distribution
            const statusCtx = document.getElementById('statusPieChart');
            if (!statusCtx) {{
                console.error('Not find statusPieChart canvas element');
                return;
            }}
            
            console.log('Init pie chart status...');
            const statusChart = new Chart(statusCtx.getContext('2d'), {{
                type: 'doughnut',
                data: {{
                    labels: ['Done', 'In Progress', 'Blocked', 'To Do'],
                    datasets: [{{
                        data: [{done_val}, {in_progress_val}, {blocked_val}, {todo_val}],
                        backgroundColor: ['#10b981', '#3b82f6', '#ef4444', '#94a3b8'],
                        borderWidth: 2,
                        borderColor: '#ffffff',
                        hoverOffset: 12
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '55%',
                    plugins: {{
                        legend: {{
                            display: false
                        }},
                        tooltip: {{
                            enabled: true,
                            zIndex: 99999,
                            callbacks: {{
                                label: function(context) {{
                                    const value = context.parsed;
                                    const total = {total_val};
                                    const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                                    return `${{context.label}}: ${{value}} (${{percentage}}%)`;
                                }}
                            }}
                        }}
                    }},
                    layout: {{
                        padding: {{
                            top: 15,
                            bottom: 15,
                            left: 15,
                            right: 15
                        }}
                    }}
                }},
                plugins: [{{
                    id: 'centerText',
                    afterDraw: function(chart) {{
                        const ctx = chart.ctx;
                        ctx.save();
                        
                        // Fill the text
                        const centerX = chart.width / 2;
                        const centerY = chart.height / 2;
                        
                        // First line: a bigger number
                        ctx.font = 'bold 28px "Segoe UI", Arial, sans-serif';
                        ctx.fillStyle = '#1e293b';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText('{total_val}', centerX, centerY - 8);
                        
                        // Second line: a smaller name
                        ctx.font = 'bold 16px "Segoe UI", Arial, sans-serif';
                        ctx.fillStyle = '#64748b';
                        ctx.fillText('TOTAL', centerX, centerY + 18);
                        
                        ctx.restore();
                    }}
                }}, {{
                    id: 'percentageLabels',
                    afterDraw: function(chart) {{
                        const ctx = chart.ctx;
                        const meta = chart.getDatasetMeta(0);
                        const total = {total_val};
                        const percentages = {status_percentages_str};
                        
                        ctx.save();
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.font = 'bold 13px "Segoe UI", Arial, sans-serif';
                        ctx.fillStyle = 'white';
                        
                        // Show the percentage in slices center
                        meta.data.forEach((slice, index) => {{
                            const value = chart.data.datasets[0].data[index];
                            const percentage = percentages[index];
                            
                            // Show the percentage only in big slice
                            if (slice && (slice.endAngle - slice.startAngle) > 0.2 && value > 0) {{
                                // Calculte the center position of fanshaped
                                const angle = slice.startAngle + (slice.endAngle - slice.startAngle) / 2;
                                const distance = slice.innerRadius + (slice.outerRadius - slice.innerRadius) / 2;
                                
                                const x = slice.x + Math.cos(angle) * distance;
                                const y = slice.y + Math.sin(angle) * distance;
                                
                                // Fill a white percentage text
                                ctx.fillText(`${{percentage}}%`, x, y);
                            }}
                        }});
                        
                        ctx.restore();
                    }}
                }}]
            }});
            
            console.log('Status pie chart init completion');
            
            // Pie chart2: Issues completion distribution by project
            const projectCtx = document.getElementById('projectPieChart');
            if (!projectCtx) {{
                console.error('Not find projectPieChart canvas element');
                return;
            }}
            
            console.log('Init project pie chart...');
            const projectChart = new Chart(projectCtx.getContext('2d'), {{
                type: 'doughnut',
                data: {{
                    labels: {project_names_str},
                    datasets: [{{
                        data: {project_done_values_str},
                        backgroundColor: {project_colors_str},
                        borderWidth: 1.5,
                        borderColor: '#ffffff',
                        hoverOffset: 10
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '55%',
                    plugins: {{
                        legend: {{
                            display: false
                        }},
                        tooltip: {{
                            enabled: true,
                            zIndex: 99999,
                            callbacks: {{
                                label: function(context) {{
                                    const value = context.parsed;
                                    const total = {total_done};
                                    const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                                    return `${{context.label}}: ${{value}} (${{percentage}}%)`;
                                }}
                            }}
                        }}
                    }},
                    layout: {{
                        padding: {{
                            top: 15,
                            bottom: 15,
                            left: 15,
                            right: 15
                        }}
                    }}
                }},
                plugins: [{{
                    id: 'centerTextProject',
                    afterDraw: function(chart) {{
                        const ctx = chart.ctx;
                        ctx.save();
                        
                        // Fill a center text
                        const centerX = chart.width / 2;
                        const centerY = chart.height / 2;
                        
                        // First line: a bigger number
                        ctx.font = 'bold 26px "Segoe UI", Arial, sans-serif';
                        ctx.fillStyle = '#1e293b';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText('{total_done}', centerX, centerY - 8);
                        
                        // Second line: a smaller total
                        ctx.font = 'bold 14px "Segoe UI", Arial, sans-serif';
                        ctx.fillStyle = '#64748b';
                        ctx.fillText('TOTAL DONE', centerX, centerY + 16);
                        
                        ctx.restore();
                    }}
                }}, {{
                    id: 'percentageLabelsProject',
                    afterDraw: function(chart) {{
                        const ctx = chart.ctx;
                        const meta = chart.getDatasetMeta(0);
                        const total = {total_done};
                        const percentages = {project_percentages_str};
                        
                        ctx.save();
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.font = 'bold 12px "Segoe UI", Arial, sans-serif';
                        ctx.fillStyle = 'white';
                        
                        // Show the percentage in slices center
                        meta.data.forEach((slice, index) => {{
                            const value = chart.data.datasets[0].data[index];
                            const percentage = percentages[index];
                            
                            // Show the percentage only in big slice
                            if (slice && (slice.endAngle - slice.startAngle) > 0.2 && value > 0) {{
                                // Calculate the center position of fanshapped
                                const angle = slice.startAngle + (slice.endAngle - slice.startAngle) / 2;
                                const distance = slice.innerRadius + (slice.outerRadius - slice.innerRadius) / 2;
                                
                                const x = slice.x + Math.cos(angle) * distance;
                                const y = slice.y + Math.sin(angle) * distance;
                                
                                // Fill white percentage text
                                ctx.fillText(`${{percentage}}%`, x, y);
                            }}
                        }});
                        
                        ctx.restore();
                    }}
                }}]
            }});
            
            console.log('Project pie chart initial completion');
        }});
        </script>
        """
    
        return pie_charts_html
    
    def _create_bar_chart_section(self, projects, to_do_values, in_progress_values, blocked_values, done_values, completion_pcts, max_total):
        """Create bar chart section - fix the circle size issue"""
        
        # Dynamic adjust on project counts
        projects_count = len(projects)
        
        # Dynamic calculate the size of Circle(based on the project counts）
        if projects_count > 13:
            circle_size = 28  # Smaller circles are used when many items
        elif projects_count > 10:
            circle_size = 32
        elif projects_count > 6:
            circle_size = 36
        else:
            circle_size = 40
        
        # Dynamic calculate the label container width
        label_container_width = circle_size + 20
        
        # Dynamic calculate the max value of Bar chart's X axis
        max_value = max([to_do_values[i] + in_progress_values[i] + blocked_values[i] + done_values[i] 
                        for i in range(projects_count)]) if projects_count > 0 else 100
        x_axis_max = max_value * 1.05  # add a little space in the right
        
        # 动态计算字体大小
        if circle_size <= 28:
            circle_font_size = "0.75rem"
        elif circle_size <= 32:
            circle_font_size = "0.8rem"
        elif circle_size <= 36:
            circle_font_size = "0.85rem"
        else:
            circle_font_size = "0.9rem"
        
        # Ensure data format consistent via json.dumps
        projects_str = json.dumps(projects)
        to_do_values_str = json.dumps([int(x) for x in to_do_values])
        in_progress_values_str = json.dumps([int(x) for x in in_progress_values])
        blocked_values_str = json.dumps([int(x) for x in blocked_values])  # 新增
        done_values_str = json.dumps([int(x) for x in done_values])
        completion_pcts_str = json.dumps([int(x) for x in completion_pcts])
        
        bar_chart_html = f"""
        <!-- Second：Bar Chart Section -->
        <div class="bar-chart-section">
            <div class="card">
                <h2 class="card-title">{self.column_plural_name if hasattr(self, 'column_plural_name') else 'Projects'} Delivery Progress</h2>
                <div class="bar-chart-container">
                    <div class="chart-wrapper">
                        <div class="chart-canvas-container">
                            <canvas id="barChart"></canvas>
                        </div>
                        <div class="completion-labels-container" id="completionLabels" style="width: {label_container_width}px;"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const ctx = document.getElementById('barChart').getContext('2d');
            
            // Data
            const projects = {projects_str};
            const toDoValues = {to_do_values_str};
            const inProgressValues = {in_progress_values_str};
            const blockedValues = {blocked_values_str};  // new
            const doneValues = {done_values_str};
            const completionPcts = {completion_pcts_str};
            const projectsCount = {projects_count};
            
            // Create stacked bar chart
            let chart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: projects.map(p => p.length > 25 ? p.substring(0, 22) + '...' : p),
                    datasets: [
                        {{
                            label: 'Done',
                            data: doneValues,
                            backgroundColor: '#10b981',
                            borderWidth: 0.5,
                            borderColor: '#ffffff',
                            borderRadius: 3,
                            hoverBackgroundColor: '#059669',
                            barPercentage: 0.8,
                            categoryPercentage: 0.85
                        }},
                        {{
                            label: 'In Progress',
                            data: inProgressValues,
                            backgroundColor: '#3b82f6',
                            borderWidth: 0.5,
                            borderColor: '#ffffff',
                            borderRadius: 3,
                            hoverBackgroundColor: '#2563eb',
                            barPercentage: 0.8,
                            categoryPercentage: 0.85
                        }},
                        {{
                            label: 'Blocked',  // new
                            data: blockedValues,
                            backgroundColor: '#ef4444',
                            borderWidth: 0.5,
                            borderColor: '#ffffff',
                            borderRadius: 3,
                            hoverBackgroundColor: '#dc2626',
                            barPercentage: 0.8,
                            categoryPercentage: 0.85
                        }},
                        {{
                            label: 'To Do',
                            data: toDoValues,
                            backgroundColor: '#94a3b8',
                            borderWidth: 0.5,
                            borderColor: '#ffffff',
                            borderRadius: 3,
                            hoverBackgroundColor: '#64748b',
                            barPercentage: 0.8,
                            categoryPercentage: 0.85
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    scales: {{
                        x: {{
                            beginAtZero: true,
                            stacked: true,
                            max: {x_axis_max},
                            grid: {{
                                display: true,
                                color: '#f1f5f9'
                            }},
                            ticks: {{
                                font: {{
                                    size: 11
                                }}
                            }}
                        }},
                        y: {{
                            stacked: true,
                            grid: {{
                                display: false
                            }},
                            ticks: {{
                                font: {{
                                    size: {12 if projects_count > 10 else 13},
                                    weight: '500'
                                }}
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            mode: 'nearest',
                            intersect: true,
                            backgroundColor: 'rgba(30, 41, 59, 0.95)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#475569',
                            borderWidth: 1,
                            cornerRadius: 6,
                            padding: 12,
                            displayColors: false,
                            zIndex: 99999,
                            callbacks: {{
                                label: function(context) {{
                                    return `${{context.dataset.label}}: ${{context.parsed.x}}`;
                                }},
                                afterLabel: function(context) {{
                                    const projectIndex = context.dataIndex;
                                    const datasetIndex = context.datasetIndex;
                                    
                                    // Display the complation rate when it's done
                                    if (datasetIndex === 0) {{
                                        return `Completion: ${{completionPcts[projectIndex]}}%`;
                                    }}
                                    return '';
                                }}
                            }}
                        }}
                    }},
                    interaction: {{
                        mode: 'nearest',
                        intersect: true,
                        axis: 'y'
                    }}
                }}
            }});
            
            // Create the completion label in the right
            function createCompletionLabels() {{
                const container = document.getElementById('completionLabels');
                if (!container) return;
                
                container.innerHTML = '';
                
                // Add CSS class based on project counts
                if (projectsCount > 13) {{
                    container.classList.add('many-projects');
                }} else if (projectsCount > 10) {{
                    container.classList.add('medium-projects');
                }}
                
                completionPcts.forEach((percent, index) => {{
                    const labelDiv = document.createElement('div');
                    labelDiv.className = 'completion-label';
                    labelDiv.id = `completion-label-${{index}}`;
                    labelDiv.style.position = 'absolute';
                    labelDiv.style.display = 'flex';
                    labelDiv.style.flexDirection = 'column';
                    labelDiv.style.alignItems = 'center';
                    labelDiv.style.justifyContent = 'center';
                    labelDiv.style.width = '100%';
                    
                    // Create the hovering name
                    const projectLabel = document.createElement('div');
                    projectLabel.className = 'project-label';
                    
                    // Show project name and completion rate
                    let projectName = projects[index];
                    projectLabel.textContent = `${{projectName}}\\nCompletion: ${{percent}}%`;
                    
                    // Create completion circle
                    const circleDiv = document.createElement('div');
                    circleDiv.className = 'completion-circle';
                    circleDiv.style.width = '{circle_size}px';
                    circleDiv.style.height = '{circle_size}px';
                    circleDiv.style.lineHeight = '{circle_size}px';
                    circleDiv.style.fontSize = '{circle_font_size}';
                    circleDiv.style.fontWeight = '700';
                    circleDiv.style.textAlign = 'center';
                    circleDiv.style.borderRadius = '50%';
                    
                    // Set the color based on the completion rate
                    let bgColor;
                    if (percent >= 80) {{
                        bgColor = '#059669';
                    }} else if (percent >= 50) {{
                        bgColor = '#f59e0b';
                    }} else {{
                        bgColor = '#dc2626';
                    }}
                    
                    circleDiv.style.backgroundColor = bgColor;
                    circleDiv.style.color = 'white';
                    circleDiv.style.boxShadow = '0 3px 6px rgba(0, 0, 0, 0.1)';
                    circleDiv.textContent = `${{percent}}%`;
                    
                    labelDiv.appendChild(projectLabel);
                    labelDiv.appendChild(circleDiv);
                    
                    container.appendChild(labelDiv);
                }});
            }}
            
            createCompletionLabels();
            
            // 🎯 Improved label positions
            function updateLabelPositions() {{
                const container = document.getElementById('completionLabels');
                if (!container) return;
                
                // Fetch bar chart's y scale
                const yScale = chart.scales.y;
                if (!yScale) return;
                
                // Fetch bar element
                const meta = chart.getDatasetMeta(0);
                
                // Calculte each bar's position
                const barPositions = [];
                const barHeights = [];
                
                for (let i = 0; i < projectsCount; i++) {{
                    // Fetch bar center's position
                    const position = yScale.getPixelForValue(i);
                    barPositions.push(position);
                    
                    // Fetch bar's height（from Chart.js metadata）
                    if (meta && meta.data[i]) {{
                        const bar = meta.data[i];
                        barHeights.push(bar.height);
                    }} else {{
                        // Give estimation when can't fetch
                        const prevPosition = i > 0 ? yScale.getPixelForValue(i-1) : position - 40;
                        const nextPosition = i < projectsCount-1 ? yScale.getPixelForValue(i+1) : position + 40;
                        barHeights.push(Math.abs(nextPosition - prevPosition) / 2 || 40);
                    }}
                }}
                
                // Circle Hight
                const circleHeight = {circle_size};
                
                // Update each label's position
                for (let i = 0; i < projectsCount; i++) {{
                    const label = document.getElementById(`completion-label-${{i}}`);
                    if (!label) continue;
                    
                    // Bar Center Positions
                    const barCenter = barPositions[i];
                    
                    // Calculate lable's top position: BarCenter - CircleHight/2
                    const topPosition = barCenter - (circleHeight / 2);
                    
                    label.style.top = `${{topPosition}}px`;
                    label.style.height = `${{circleHeight}}px`;
                    
                    // Record debug info
                    if (i === 0) {{
                        console.log('📏 Position debug:');
                        console.log('  BarCenter:', barCenter);
                        console.log('  CircleHeight:', circleHeight);
                        console.log('  Calculated TopPosition:', topPosition);
                    }}
                }}
                
                console.log('✅ Circle position updated, ProjectCounts:', projectsCount, 'Circle size:', {circle_size});
            }}
            
            // 🎯 More reliable location update mechanism
            function schedulePositionUpdates() {{
                // Update after initial delay
                setTimeout(updateLabelPositions, 300);
                
                // Update after chart animation
                chart.options.animation = {{
                    onComplete: function() {{
                        setTimeout(updateLabelPositions, 200);
                    }},
                    duration: 800
                }};
                
                // Monitor window size update
                window.addEventListener('resize', function() {{
                    setTimeout(updateLabelPositions, 300);
                }});
                
                // Monitor chart update
                chart.options.transition = {{
                    onComplete: function() {{
                        setTimeout(updateLabelPositions, 200);
                    }}
                }};
            }}
            
            createCompletionLabels();
            schedulePositionUpdates();
            
            setInterval(updateLabelPositions, 1000);
        }});
        </script>
        """
        
        return bar_chart_html
    
    def _create_explanations_section(self):
        """Create Explanations Section"""
        explanations_html = """
        <!-- Explanations -->
        <div class="explanations-section">
            <div class="card">
                <h2 class="card-title">Dashboard Explanations</h2>
                
                <div class="explanation-group">
                    <h3>📊 Status Mapping Explanation</h3>
                    <p>The status categories in this dashboard are mapped from Jira statuses as follows:</p>
                    <ul>
                        <li><strong>To Do</strong> = To Do + Backlog + Prioritized + Up Next</li>
                        <li><strong>In Progress</strong> = In Progress + Blocked + Review + In Testing + Waiting for Release</li>
                        <li><strong>Blocked</strong> = Blocked</li>
                        <li><strong>Done</strong> = Done + Closed + Resolved + Completed</li>
                    </ul>
                    <p>This mapping provides a simplified view of project progress by consolidating related statuses into four main categories for clearer tracking and reporting.</p>
                </div>
                
                <div class="explanation-group">
                    <h3>🎯 Completion Percentage Circles Explanation</h3>
                    <p>The colored circles on the right side of the Project Delivery Progress chart indicate the completion percentage for each project:</p>
                    <div class="legend-container">
                        <div class="legend-item">
                            <span class="legend-circle high-completion"></span>
                            <span><strong>High Completion Rate (≥80%)</strong> - Project is on track or ahead of schedule</span>
                        </div>
                        <div class="legend-item">
                            <span class="legend-circle medium-completion"></span>
                            <span><strong>Medium Completion Rate (50-79%)</strong> - Project is making steady progress</span>
                        </div>
                        <div class="legend-item">
                            <span class="legend-circle low-completion"></span>
                            <span><strong>Low Completion Rate (&lt;50%)</strong> - Project needs attention or is behind schedule</span>
                        </div>
                    </div>
                    <p>Completion percentage is calculated as: <strong>Done Issues / Total Issues × 100%</strong></p>
                </div>
            </div>
        </div>
        """
        
        return explanations_html
    
    def _create_table_html(self, project_data, total_row):
        column_display_name = self.column_display_name if hasattr(self, 'column_display_name') else "Project"
        column_plural_name = self.column_plural_name if hasattr(self, 'column_plural_name') else "Projects"
        
        table_title = f"{column_plural_name} Progress Details"
        column_header = column_display_name

        table_rows = []
        
        # Items
        for row in project_data:
            completion_pct = row['Completion_Percent']
            
            if completion_pct >= 80:
                completion_class = "completion-high"
            elif completion_pct >= 50:
                completion_class = "completion-medium"
            else:
                completion_class = "completion-low"
            
            table_rows.append(f"""
            <tr>
                <td class="project-name">{row['Project']}</td>
                <td><span class="status-badge status-todo">{row['To Do']}</span></td>
                <td><span class="status-badge status-progress">{row['In Progress']}</span></td>
                <td><span class="status-badge status-blocked">{row['Blocked']}</span></td>  <!-- 新增 -->
                <td><span class="status-badge status-done" style="background-color: #10b981; color: white;">{row['Done']}</span></td>
                <td>{row['Total']}</td>
                <td class="completion-cell {completion_class}">{row['Completion %']}</td>
            </tr>
            """)
        
        # 总计行
        table_rows.append(f"""
        <tr class="total-row">
            <td>TOTAL</td>
            <td>{total_row['To Do']}</td>
            <td>{total_row['In Progress']}</td>
            <td>{total_row['Blocked']}</td>  <!-- new -->
            <td>{total_row['Done']}</td>
            <td>{total_row['Total']}</td>
            <td class="completion-cell">{total_row['Completion %']}</td>
        </tr>
        """)
        
        table_html = f"""
        <!-- Third: Table section -->
        <div class="table-section">
            <div class="table-container">
                <h2 class="card-title">{table_title}</h2>
                <table>
                    <thead>
                        <tr>
                            <th>{column_header}</th>
                            <th width="10%">To Do</th>
                            <th width="10%">In Progress</th>
                            <th width="10%">Blocked</th>
                            <th width="10%">Done</th>
                            <th width="10%">Total</th>
                            <th width="10%" class="completion-header">Completion</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(table_rows)}
                    </tbody>
                </table>
            </div>
        </div>
        """
        
        return table_html
    
    def _generate_dashboard_html(self, project_data, total_row, projects, to_do_values, in_progress_values, blocked_values, done_values, completion_pcts, max_total, dashboard_path):
        
        """Create a full page - added download function"""
        column_display_name = self.column_display_name if hasattr(self, 'column_display_name') else "Project"
        column_plural_name = self.column_plural_name if hasattr(self, 'column_plural_name') else "Projects"
        
        # Ensure primary Title
        if hasattr(self, 'custom_title') and self.custom_title:
            # use custom title
            dashboard_title = self.custom_title
            page_title = self.custom_title
        else:
            # use the default title
            dashboard_title = f"{column_plural_name} Delivery Dashboard"
            page_title = f"{column_plural_name} Delivery Dashboard"
        
        # Create pie charts section
        pie_charts_html = self._create_pie_charts_section(project_data, total_row, projects)
        
        # Create bar chart section
        bar_chart_html = self._create_bar_chart_section(projects, to_do_values, in_progress_values, blocked_values, done_values, completion_pcts, max_total)
        
        # Create table section
        table_html = self._create_table_html(project_data, total_row)
        
        # Create explanations section
        explanations_html = self._create_explanations_section()
        
        # Fetched current time
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # Full HTML Template - restore orignal style
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <!-- Using Stable Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <!-- Added html2canvas libs for Screenshot -->
    <script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
    <style>
            /* ===============================
               1. Basic Style
               =============================== */
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            
            body {{
                background-color: #f8fafc;
                padding: 30px 20px;
                color: #334155;
                min-width: 1200px;
            }}
            
            .dashboard-container {{
                max-width: 1600px;
                margin: 0 auto;
            }}
            
            /* Common Card Style */
            .card {{
                background: white;
                border-radius: 16px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
                padding: 28px 30px 30px 30px;
                transition: transform 0.3s ease;
                height: 100%;
            }}
            
            .card:hover {{
                transform: translateY(-5px);
            }}
            
            .card-title {{
                font-size: 1.5rem;
                color: #1e293b;
                margin-bottom: 22px;
                padding-bottom: 14px;
                border-bottom: 2px solid #f1f5f9;
                font-weight: 600;
            }}
            
            /* Header Style */
            .header {{
                text-align: center;
                margin-bottom: 40px;
                padding: 0 20px;
                position: relative;
            }}
            
            .header h1 {{
                color: #1e293b;
                font-size: 2.4rem;
                margin-bottom: 10px;
                font-weight: 700;
            }}
            
            .header p {{
                color: #64748b;
                font-size: 1rem;
                margin: 0 auto;
                line-height: 1.6;
                font-style: italic;
            }}
            
            /* Download Container Style */
            .download-container {{
                position: absolute;
                right: 0;
                top: 0;
                display: flex;
                gap: 10px;
            }}
            
            .download-btn {{
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 0.95rem;
                font-weight: 600;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }}
            
            .download-btn:hover {{
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
            }}
            
            .download-btn:active {{
                transform: translateY(0);
            }}
            
            .download-btn.download-image {{
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            }}
            
            .download-btn.download-image:hover {{
                background: linear-gradient(135deg, #059669 0%, #047857 100%);
                box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
            }}
            
            .download-btn svg {{
                width: 18px;
                height: 18px;
            }}
            
            /* Download hints */
            .download-hint {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                background-color: #10b981;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: 500;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
                z-index: 1000;
                opacity: 0;
                transform: translateY(20px);
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .download-hint.show {{
                opacity: 1;
                transform: translateY(0);
            }}
            
            /* ===============================
               2. Overview Section
               =============================== */
            .overview-section {{
                display: grid;
                grid-template-columns: repeat(6, 1fr);
                gap: 15px;
                margin-bottom: 40px;
            }}
            
            .overview-card {{
                background: white;
                border-radius: 16px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
                padding: 25px;
                transition: transform 0.3s ease;
                text-align: center;
            }}
            
            .overview-card:hover {{
                transform: translateY(-5px);
            }}
            
            .overview-value {{
                font-size: 2.8rem;
                font-weight: 700;
                margin-bottom: 8px;
                line-height: 1;
            }}
            
            .overview-label {{
                font-size: 1rem;
                color: #64748b;
                font-weight: 500;
            }}
            
            /* Status Color */
            .overview-todo .overview-value {{ color: #94a3b8; }}
            .overview-progress .overview-value {{ color: #3b82f6; }}
            .overview-blocked .overview-value {{ color: #ef4444; }}
            .overview-done .overview-value {{ color: #10b981; }}
            .overview-total .overview-value {{ color: #1e293b; }}
            .overview-completion .overview-value {{ color: #8b5cf6; }}
            
            /* ===============================
               3. Pie Charts Section
               =============================== */
            .pie-charts-section {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin-bottom: 40px;
            }}
            
            /* Pie Container Style */
            .pie-container {{
                position: relative;
                height: 350px;
                margin: 10px 0;
                overflow: visible !important;
            }}
            
            /* ===============================
               4. Bar Chart Section
               =============================== */
            .bar-chart-section {{
                margin-bottom: 35px;
            }}
            
            /* Bar Chart Container Style */
            .bar-chart-container {{
                position: relative;
                height: 450px;
                margin: 8px 0 20px;
                width: 100%;
                overflow: visible !important;
            }}
            
            /* Chart Wrapper */
            .chart-wrapper {{
                position: relative;
                display: flex;
                height: 100%;
                width: 100%;
                margin: 0 auto;
            }}
            
            .chart-canvas-container {{
                flex: 1;
                position: relative;
                margin-right: 10px;
                overflow: visible !important;
            }}
            
            /* Completion Labels Container Style */
            .completion-labels-container {{
                position: absolute;
                right: 0;
                top: 0;
                width: 40px;
                height: 100%;
                z-index: 100;
                overflow: visible !important;
            }}
            
            /* Many Project Style Adjustment */
            .completion-labels-container.many-projects {{
                width: 50px !important;
            }}
            
            .completion-labels-container.medium-projects {{
                width: 45px !important;
            }}
            
            /* Completion Lable Style */
            .completion-label {{
                position: absolute;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
                cursor: pointer;
                transition: transform 0.2s ease;
                width: 100%;
                z-index: 101;
            }}
            
            .completion-label:hover {{
                transform: scale(1.05);
                z-index: 102;
            }}
            
            /* Project Label Hovering */
            .project-label {{
                position: absolute;
                right: calc(100% + 10px);
                background-color: rgba(30, 41, 59, 0.95);
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 0.7rem !important;
                font-weight: 500;
                white-space: normal;
                word-wrap: break-word;
                opacity: 0;
                visibility: hidden;
                transition: opacity 0.3s ease, visibility 0.3s ease;
                z-index: 99999 !important;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
                pointer-events: none;
                text-align: left;
                min-width: 180px;
                max-width: 250px;
                line-height: 1.5;
            }}
            
            .project-label::after {{
                content: '';
                position: absolute;
                top: 50%;
                right: -6px;
                transform: translateY(-50%);
                border-left: 6px solid rgba(30, 41, 59, 0.95);
                border-top: 6px solid transparent;
                border-bottom: 6px solid transparent;
            }}
            
            .completion-label:hover .project-label {{
                opacity: 1;
                visibility: visible;
            }}
            
            /* Completion Circle Style */
            .completion-circle {{
                width: 38px;
                height: 38px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 0.95rem !important;
                color: white;
                box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
                transition: all 0.2s ease;
                z-index: 103;
            }}
            
            /* Many Project Completion Circle */
            .completion-labels-container.many-projects .completion-circle {{
                width: 28px !important;
                height: 28px !important;
                font-size: 0.7rem !important;
                line-height: 28px !important;
            }}
            
            .completion-labels-container.medium-projects .completion-circle {{
                width: 32px !important;
                height: 32px !important;
                font-size: 0.8rem !important;
                line-height: 32px !important;
            }}
            
            .completion-label:hover .completion-circle {{
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
                transform: scale(1.05);
            }}
            
            /* ===============================
               5. Table Section
               =============================== */
            .table-section {{
                margin-bottom: 30px;
            }}
            
            .table-container {{
                background: white;
                border-radius: 16px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
                padding: 25px;
                overflow-x: auto;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                min-width: 800px;
                font-size: 0.9rem;
            }}
            
            thead {{
                background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
            }}
            
            th {{
                padding: 14px 10px;
                text-align: left;
                color: #1e293b;
                font-weight: 600;
                border-bottom: 2px solid #cbd5e1;
                font-size: 0.95rem;
            }}
            
            th.completion-header {{
                text-align: center;
            }}
            
            td {{
                padding: 12px 10px;
                border-bottom: 1px solid #e2e8f0;
            }}
            
            tr:hover {{
                background-color: #f8fafc;
            }}
            
            tr.total-row {{
                background-color: #f8fafc;
                font-weight: 600;
            }}
            
            .completion-cell {{
                font-weight: 600;
                text-align: center !important;
                font-size: 1rem;
                padding: 12px 6px;
            }}
            
            .completion-high {{ color: #10b981; }}
            .completion-medium {{ color: #f59e0b; }}
            .completion-low {{ color: #ef4444; }}
            
            .status-badge {{
                display: inline-block;
                padding: 4px 10px;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 500;
                min-width: 50px;
                text-align: center;
            }}
            
            .status-todo {{ background: #94a3b8; color: white; }}
            .status-progress {{ background: #3b82f6; color: white; }}
            .status-blocked {{ background: #ef4444; color: white; }}  # red
            .status-done {{
                background: #10b981 !important; 
                color: white !important;
                border: none !important;
            }}
            
            .project-name {{
                font-weight: 500;
                color: #1e293b;
            }}
            
            /* ===============================
               6. Explanations Section
               =============================== */
            .explanations-section {{
                margin-bottom: 40px;
            }}
            
            .explanation-group {{
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid #e2e8f0;
            }}
            
            .explanation-group:last-child {{
                border-bottom: none;
                margin-bottom: 0;
                padding-bottom: 0;
            }}
            
            .explanation-group h3 {{
                color: #1e293b;
                font-size: 1.2rem;
                margin-bottom: 15px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .explanation-group p {{
                color: #475569;
                line-height: 1.6;
                margin-bottom: 12px;
            }}
            
            .explanation-group ul {{
                color: #475569;
                line-height: 1.6;
                margin-left: 20px;
                margin-bottom: 12px;
            }}
            
            .explanation-group li {{
                margin-bottom: 6px;
            }}
            
            .explanation-group strong {{
                color: #1e293b;
            }}
            
            /* Legend Container Style */
            .legend-container {{
                background-color: #f8fafc;
                border-radius: 10px;
                padding: 15px;
                margin: 15px 0;
            }}
            
            .legend-item {{
                display: flex;
                align-items: center;
                margin-bottom: 10px;
            }}
            
            .legend-item:last-child {{
                margin-bottom: 0;
            }}
            
            .legend-circle {{
                width: 16px;
                height: 16px;
                border-radius: 50%;
                margin-right: 10px;
                flex-shrink: 0;
            }}
            
            .high-completion {{
                background-color: #059669;
            }}
            
            .medium-completion {{
                background-color: #f59e0b;
            }}
            
            .low-completion {{
                background-color: #dc2626;
            }}
            
            /* Responsive - Simply Basic Section */
            @media (max-width: 1200px) {{
                body {{
                    min-width: auto;
                    padding: 20px 15px;
                }}
                
                .overview-section {{
                    grid-template-columns: repeat(3, 1fr);
                }}
                
                .pie-charts-section {{
                    grid-template-columns: 1fr;
                    gap: 40px;
                }}
                
                .bar-chart-container {{
                    height: 400px;
                }}
                
                .completion-circle {{
                    width: 34px;
                    height: 34px;
                    font-size: 0.85rem !important;
                }}
                
                .download-container {{
                    position: static;
                    justify-content: center;
                    margin-top: 20px;
                }}
                
                .header {{
                    text-align: center;
                }}
            }}
    </style>
</head>
<body>
    <div class="dashboard-container" id="dashboardContent">
            <div class="header">
                <h1>📊 {dashboard_title}</h1>
                <p>Generated on {current_time}</p>
                <div class="download-container">
                    <button class="download-btn download-image" id="downloadImageBtn">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        Download Dashboard Image
                    </button>
                </div>
            </div>
            
            <!-- Overview Section -->
            <div class="overview-section">
                <div class="overview-card overview-todo">
                    <div class="overview-value">{total_row['To Do']}</div>
                    <div class="overview-label">To Do</div>
                </div>
                
                <div class="overview-card overview-progress">
                    <div class="overview-value">{total_row['In Progress']}</div>
                    <div class="overview-label">In Progress</div>
                </div>

                <div class="overview-card overview-blocked">
                    <div class="overview-value">{total_row['Blocked']}</div>
                    <div class="overview-label">Blocked</div>
                </div>
                
                <div class="overview-card overview-done">
                    <div class="overview-value">{total_row['Done']}</div>
                    <div class="overview-label">Done</div>
                </div>
                
                <div class="overview-card overview-total">
                    <div class="overview-value">{total_row['Total']}</div>
                    <div class="overview-label">Total Issues</div>
                </div>
                
                <div class="overview-card overview-completion">
                    <div class="overview-value">{total_row['Completion %']}</div>
                    <div class="overview-label">Completion Rate</div>
                </div>
            </div>
            
            {pie_charts_html}
            
            {bar_chart_html}
            
            {table_html}
            
            {explanations_html}
            
            <!-- Download Hints -->
            <div class="download-hint" id="downloadHint">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <span>Dashboard image is downloading...</span>
            </div>
    </div>
        
    <!-- Download Function with JavaScript - Improved-->
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        console.log('Dashboard loaded');
        
        const downloadImageBtn = document.getElementById('downloadImageBtn');
        const downloadHint = document.getElementById('downloadHint');
        
        // Main download function
        async function downloadDashboardImage() {{
            console.log('Starting dashboard image export...');
            
            // Show hint
            showDownloadHint('Preparing dashboard image...');
            if (downloadImageBtn) {{
                downloadImageBtn.disabled = true;
                downloadImageBtn.innerHTML = 'Preparing...';
            }}
            
            try {{
                // 1. Convert all Chart.js charts to images
                const chartImages = await convertChartsToImages();
                
                // 2. Create temporary page with chart images
                const tempContainer = await createScreenshotPage(chartImages);
                
                // 3. Wait for all images to load
                await waitForImages(tempContainer);
                
                // 4. Capture and download
                await captureAndDownload(tempContainer);
                
                showDownloadHint('Dashboard image downloaded successfully!');
                console.log('✅ Image download completed');
                
            }} catch (error) {{
                console.error('Download failed:', error);
                
                // Fallback method
                try {{
                    console.log('Trying fallback method...');
                    await backupScreenshotMethod();
                    showDownloadHint('Dashboard image downloaded successfully!');
                }} catch (backupError) {{
                    console.error('Fallback method failed:', backupError);
                    showDownloadHint('Download failed, please try again');
                }}
                
            }} finally {{
                // Restore button state
                if (downloadImageBtn) {{
                    downloadImageBtn.disabled = false;
                    downloadImageBtn.innerHTML = 'Download Dashboard Image';
                }}
                
                // Hide hint after 3 seconds
                setTimeout(() => {{
                    if (downloadHint) {{
                        downloadHint.classList.remove('show');
                    }}
                }}, 3000);
            }}
        }}
        
        // 1. Convert all Chart.js charts to images
        async function convertChartsToImages() {{
            const chartImages = {{}};
            
            if (typeof Chart !== 'undefined') {{
                const charts = Object.values(Chart.instances || {{}});
                
                // Force all charts to re-render
                charts.forEach(chart => {{
                    try {{
                        chart.update('none');
                        chart.render();
                    }} catch (e) {{
                        console.warn('Chart update failed:', e);
                    }}
                }});
                
                // Wait for rendering
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // Convert each chart to image
                charts.forEach((chart, index) => {{
                    try {{
                        const canvas = chart.canvas;
                        if (canvas && canvas.id) {{
                            // Create high-quality image
                            const dataURL = canvas.toDataURL('image/png', 1.0);
                            chartImages[canvas.id] = dataURL;
                            console.log(`✅ Chart ${{canvas.id}} converted to image`);
                        }}
                    }} catch (error) {{
                        console.error(`❌ Chart conversion failed:`, error);
                    }}
                }});
            }}
            
            return chartImages;
        }}
        
        // 2. Create temporary page with chart images
        async function createScreenshotPage(chartImages) {{
            // Create temporary container
            const tempContainer = document.createElement('div');
            tempContainer.id = 'screenshot-page';
            tempContainer.style.cssText = `
                position: fixed;
                left: 0;
                top: 0;
                width: 1600px;
                min-height: 2000px;
                background-color: #f8fafc;
                padding: 30px 20px;
                z-index: 99999;
                box-sizing: border-box;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #334155;
            `;
            
            // Clone dashboard content
            const dashboard = document.querySelector('.dashboard-container').cloneNode(true);
            
            // Remove unwanted sections
            const elementsToRemove = dashboard.querySelectorAll(
                '.explanations-section, .download-container, .download-hint'
            );
            elementsToRemove.forEach(el => el.remove());
            
            // Replace canvas elements with images
            const canvases = dashboard.querySelectorAll('canvas');
            canvases.forEach(canvas => {{
                const img = document.createElement('img');
                img.style.cssText = `
                    display: block;
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    background: white;
                `;
                
                // Set image dimensions same as original canvas
                img.width = canvas.width;
                img.height = canvas.height;
                
                // Use converted chart images
                if (chartImages[canvas.id]) {{
                    img.src = chartImages[canvas.id];
                    console.log(`🖼️ Using chart image: ${{canvas.id}}`);
                }} else {{
                    // If chart conversion failed, use canvas data URL
                    try {{
                        img.src = canvas.toDataURL('image/png');
                    }} catch (e) {{
                        // Create placeholder
                        createChartPlaceholder(img, canvas);
                    }}
                }}
                
                // Replace canvas
                if (canvas.parentNode) {{
                    canvas.parentNode.replaceChild(img, canvas);
                }}
            }});
            
            // Ensure proper styling for containers
            const containers = dashboard.querySelectorAll('.pie-container, .bar-chart-container');
            containers.forEach(container => {{
                container.style.cssText = `
                    position: relative;
                    overflow: visible !important;
                    margin: 10px 0;
                `;
            }});
            
            tempContainer.appendChild(dashboard);
            document.body.appendChild(tempContainer);
            
            return tempContainer;
        }}
        
        // Create chart placeholder
        function createChartPlaceholder(img, canvas) {{
            const width = canvas.width || 400;
            const height = canvas.height || 300;
            
            // Create SVG placeholder
            const svg = `
                <svg xmlns="http://www.w3.org/2000/svg" width="${{width}}" height="${{height}}" viewBox="0 0 ${{width}} ${{height}}">
                    <rect width="100%" height="100%" fill="#f1f5f9" rx="8" ry="8"/>
                    <text x="50%" y="50%" text-anchor="middle" dy="0" fill="#64748b" 
                          font-family="Arial" font-size="16" font-weight="500">
                        Chart Preview
                    </text>
                    <text x="50%" y="60%" text-anchor="middle" dy="0" fill="#94a3b8" 
                          font-family="Arial" font-size="14">
                        (Click download to regenerate)
                    </text>
                </svg>
            `;
            
            img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg)));
        }}
        
        // 3. Wait for all images to load
        function waitForImages(container) {{
            return new Promise((resolve) => {{
                const images = container.querySelectorAll('img');
                let loadedCount = 0;
                
                if (images.length === 0) {{
                    resolve();
                    return;
                }}
                
                images.forEach(img => {{
                    if (img.complete) {{
                        loadedCount++;
                    }} else {{
                        img.onload = () => {{
                            loadedCount++;
                            if (loadedCount === images.length) {{
                                resolve();
                            }}
                        }};
                        img.onerror = () => {{
                            loadedCount++;
                            if (loadedCount === images.length) {{
                                resolve();
                            }}
                        }};
                    }}
                }});
                
                // Check if all already loaded
                if (loadedCount === images.length) {{
                    resolve();
                }}
                
                // Timeout protection
                setTimeout(resolve, 2000);
            }});
        }}
        
        // 4. Capture and download
        async function captureAndDownload(tempContainer) {{
            return new Promise((resolve, reject) => {{
                try {{
                    // Wait for layout to stabilize
                    setTimeout(() => {{
                        html2canvas(tempContainer, {{
                            scale: 1.5,
                            useCORS: true,
                            backgroundColor: '#f8fafc',
                            logging: false,
                            allowTaint: false,
                            width: tempContainer.scrollWidth,
                            height: tempContainer.scrollHeight,
                            x: 0,
                            y: 0,
                            onclone: function(clonedDoc) {{
                                // Ensure all content is visible in cloned document
                                const images = clonedDoc.querySelectorAll('img');
                                images.forEach(img => {{
                                    img.style.display = 'block';
                                    img.style.visibility = 'visible';
                                }});
                            }}
                        }}).then(canvas => {{
                            // Download image
                            const link = document.createElement('a');
                            const timestamp = new Date().toISOString()
                                .slice(0, 19)
                                .replace(/:/g, '-');
                            const filename = `dashboard-${{timestamp}}.png`;
                            
                            link.download = filename;
                            link.href = canvas.toDataURL('image/png', 1.0);
                            
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                            
                            // Clean up temporary container
                            document.body.removeChild(tempContainer);
                            
                            resolve();
                        }}).catch(error => {{
                            document.body.removeChild(tempContainer);
                            reject(error);
                        }});
                    }}, 500);
                    
                }} catch (error) {{
                    if (tempContainer && tempContainer.parentNode) {{
                        document.body.removeChild(tempContainer);
                    }}
                    reject(error);
                }}
            }});
        }}
        
        // Fallback method: screenshot current page directly
        async function backupScreenshotMethod() {{
            return new Promise((resolve, reject) => {{
                try {{
                    // Hide unwanted sections
                    const elementsToHide = document.querySelectorAll(
                        '.explanations-section, .download-container'
                    );
                    const originalStyles = [];
                    
                    elementsToHide.forEach((el, index) => {{
                        originalStyles[index] = el.style.cssText;
                        el.style.cssText = 'display: none !important;';
                    }});
                    
                    // Force charts to render
                    if (typeof Chart !== 'undefined') {{
                        const charts = Object.values(Chart.instances || {{}});
                        charts.forEach(chart => {{
                            try {{
                                chart.update('none');
                                chart.render();
                            }} catch (e) {{}}
                        }});
                    }}
                    
                    // Wait for rendering
                    setTimeout(() => {{
                        // Screenshot entire page
                        html2canvas(document.body, {{
                            scale: 1.5,
                            backgroundColor: '#f8fafc',
                            logging: false
                        }}).then(canvas => {{
                            // Download
                            const link = document.createElement('a');
                            const timestamp = new Date().toISOString()
                                .slice(0, 19)
                                .replace(/:/g, '-');
                            const filename = `dashboard-backup-${{timestamp}}.png`;
                            
                            link.download = filename;
                            link.href = canvas.toDataURL('image/png');
                            link.click();
                            
                            // Restore styles
                            elementsToHide.forEach((el, index) => {{
                                el.style.cssText = originalStyles[index] || '';
                            }});
                            
                            resolve();
                        }});
                    }}, 1000);
                    
                }} catch (error) {{
                    reject(error);
                }}
            }});
        }}
        
        // Show hint
        function showDownloadHint(message) {{
            if (downloadHint) {{
                const span = downloadHint.querySelector('span');
                if (span) {{
                    span.textContent = message;
                }}
                downloadHint.classList.add('show');
            }}
        }}
        
        // Bind download button
        if (downloadImageBtn) {{
            downloadImageBtn.addEventListener('click', downloadDashboardImage);
        }}
    }});
    </script>
</body>
</html>"""
        
        return html_template