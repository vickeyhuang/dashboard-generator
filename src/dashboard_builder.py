# src/dashboard_builder.py
"""
Dashboard structure module - added a download function and blocked pie chart
Version: 2026.02.12 - Fixed bar chart height auto-adaptation
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
        print(f"\n📋 Create a full Dashboard...")
        
        # Save the column name
        self.column_display_name = column_display_name
        self.column_plural_name = column_plural_name
        self.custom_title = custom_title
        
        # Prepare data - keep the same order with table name
        projects, to_do_values, in_progress_values, blocked_values, done_values, completion_pcts, totals = \
            self._prepare_data(project_data, original_order)
        
        max_total = max(totals) if totals else 100
        
        # Create a dashboard file with timestamp
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Custom title for the generated dashboard
        if custom_title:
            filename_base = custom_title.lower().replace(' ', '_').replace('dashboard', '').strip('_')
            dashboard_filename = f"{filename_base}_{timestamp}.html"
        else:
            dashboard_filename = f"dashboard_{timestamp}.html"

        dashboard_path = os.path.join(output_dir, dashboard_filename)
        
        # Create a full HTML
        full_html = self._generate_dashboard_html(
            project_data, total_row, projects, to_do_values, 
            in_progress_values, blocked_values, done_values, completion_pcts, 
            max_total, dashboard_path
        )
    
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"✅ Dashboard saved: {dashboard_path}")
        
        return dashboard_path
    
    def _prepare_data(self, project_data, original_order):
        """Prepare data - keep the same order with table name"""
        projects = []
        to_do_values = []
        in_progress_values = []
        blocked_values = []
        done_values = []
        completion_pcts = []
        totals = []
        
        for project in original_order:
            for row in project_data:
                if row['Project'] == project:
                    projects.append(row['Project'])
                    to_do_values.append(int(row['To Do']))
                    in_progress_values.append(int(row['In Progress']))
                    blocked_values.append(int(row['Blocked']))
                    done_values.append(int(row['Done']))
                    completion_pcts.append(int(row['Completion_Percent']))
                    totals.append(int(row['Total']))
                    break
        
        return projects, to_do_values, in_progress_values, blocked_values, done_values, completion_pcts, totals

    def _create_pie_charts_section(self, project_data, total_row, projects_order):
        """Create pie chart section"""
        column_name = self.column_display_name if hasattr(self, 'column_display_name') else "Project"
        
        total_done = sum(row['Done'] for row in project_data)
        
        # Using the default value when the data is null
        if total_done == 0:
            total_done = 1
        
        # Pie chart1: Status distribution
        todo_val = int(total_row.get('To Do', 0))
        in_progress_val = int(total_row.get('In Progress', 0))
        blocked_val = int(total_row.get('Blocked', 0))
        done_val = int(total_row.get('Done', 0))
        total_val = int(total_row.get('Total', 0))
        
        # Calculate the percentage (round 0)
        status_percentages = [0, 0, 0, 0]
        if total_val > 0:
            status_percentages = [
                round(done_val / total_val * 100),
                round(in_progress_val / total_val * 100),
                round(blocked_val / total_val * 100),
                round(todo_val / total_val * 100)
            ]
        
        # Pie chart2: Issue completion distribution
        project_done_values = []
        project_names = []
        
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
        
        # Generate colors for blocked chart
        green_colors = [
            '#065f46',  # Dark green
            '#047857',  # Medium green
            '#059669',  # Medium-light green
            '#10b981',  # Light green
            '#34d399',  # Lighter green
            '#6ee7b7',  # Very light green
            '#a7f3d0',  # Extremely green
            '#d1fae5',  # Lightest
        ]
        
        # Sort done projects by count (highest first)
        sorted_pairs = sorted(zip(project_names, project_done_values), key=lambda x: x[1], reverse=True)
        project_names, project_done_values = zip(*sorted_pairs)
        project_names = list(project_names)
        project_done_values = list(project_done_values)
        
        # Calculte project completion percentages(round 0)
        project_percentages = []
        for value in project_done_values:
            if total_done > 0:
                project_percentages.append(round(value / total_done * 100, 0))
            else:
                project_percentages.append(0)
        
        # Pie chart3：Blocked distribution
        blocked_projects = []
        blocked_values = []
        
        for project in project_data:
            if project['Blocked'] > 0:
                # Truncate long project names
                project_name = project['Project']
                if len(project_name) > 25:
                    project_name = project_name[:22] + '...'
                blocked_projects.append(project_name)
                blocked_values.append(int(project['Blocked']))
        
        total_blocked = sum(blocked_values) if blocked_values else 0
        
        # Generate colors for blocked - gradient of reds
        red_colors = [
            '#ef4444',  # Bright red
            '#f87171',  # Light red
            '#fca5a5',  # Lighter red
            '#fecaca',  # Very light red
            '#fee2e2',  # Almost pink
            '#dc2626',  # Dark red
            '#b91c1c',  # Darker red
            '#991b1b',  # Deep red
            '#7f1d1d',  # Very deep red
            '#450a0a'   # Burgundy
        ]
        
        # Sort blocked projects by count (highest first)
        if blocked_projects:
            sorted_pairs = sorted(zip(blocked_projects, blocked_values), key=lambda x: x[1], reverse=True)
            blocked_projects, blocked_values = zip(*sorted_pairs)
            blocked_projects = list(blocked_projects)
            blocked_values = list(blocked_values)
            
            # Calculate percentages for blocked chart
            blocked_percentages = []
            for value in blocked_values:
                pct = round((value / total_blocked * 100), 0) if total_blocked > 0 else 0
                blocked_percentages.append(pct)
        else:
            blocked_percentages = []
        
        # Ensure the formal consistent via json.dumps
        project_names_str = json.dumps(project_names)
        project_done_values_str = json.dumps(project_done_values)
        project_percentages_str = json.dumps(project_percentages)
        status_percentages_str = json.dumps(status_percentages)
        
        # Done chart colors for JSON
        done_colors_str = json.dumps(green_colors[:len(project_names)] if project_names else [])
        
        # Blocked chart data for JSON
        blocked_projects_str = json.dumps(blocked_projects)
        blocked_values_str = json.dumps(blocked_values)
        blocked_colors_str = json.dumps(red_colors[:len(blocked_projects)] if blocked_projects else [])
        blocked_percentages_str = json.dumps(blocked_percentages)
        
        # Decide pie chart2 3 titles
        pie_chart2_title = f"Done Issues by {column_name}"
        pie_chart3_title = f"Blocked Issues by {column_name}"
        
        # Calculate Blocked Rate
        blocked_rate = 0
        if total_row['Total'] > 0:
            blocked_rate = round((total_row['Blocked'] / total_row['Total'] * 100))
        
        # Create pie chart senction HTML structure
        pie_charts_html = f"""
        <!-- First: Three pie charts -->
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; margin-bottom: 40px;">
            <!-- PieChart1: Status distribution -->
            <div class="card">
                <h2 class="card-title">Total Issues by Status</h2>
                <div class="pie-container">
                    <canvas id="statusPieChart" width="400" height="400"></canvas>
                </div>
            </div>
            
            <!-- PieChart2: {column_name.lower()} Completion Rate -->
            <div class="card">
                <h2 class="card-title" style="color: #047857;">{pie_chart2_title}</h2>
                <div class="pie-container">
                    <canvas id="projectPieChart" width="400" height="400"></canvas>
                </div>
            </div>
            
            <!-- PieChart3: {column_name.lower()} Blocked Rate -->
            <div class="card">
                <h2 class="card-title" style="color: #ef4444;">{pie_chart3_title}</h2>
                <div class="pie-container">
                    <canvas id="blockedPieChart" width="400" height="400"></canvas>
                </div>
            </div>
        </div>
        
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Start initial pie chart...');
            
            // Setup global tooltip z-index
            Chart.defaults.plugins.tooltip.zIndex = 99999;
            
            // ========== PieChart1: Status Distribution ==========
            const statusCtx = document.getElementById('statusPieChart');
            if (!statusCtx) {{
                console.error('Not find status PieChart canvas');
                return;
            }}
            
            console.log('Status pie chart initing...');
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
                        
                        const centerX = chart.width / 2;
                        const centerY = chart.height / 2;
                        
                        ctx.font = 'bold 28px "Segoe UI", Arial, sans-serif';
                        ctx.fillStyle = '#1e293b';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText('{total_val}', centerX, centerY - 8);
                        
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
                        
                        meta.data.forEach((slice, index) => {{
                            const value = chart.data.datasets[0].data[index];
                            const percentage = percentages[index];
                            
                            if (slice && (slice.endAngle - slice.startAngle) > 0.2 && value > 0) {{
                                const angle = slice.startAngle + (slice.endAngle - slice.startAngle) / 2;
                                const distance = slice.innerRadius + (slice.outerRadius - slice.innerRadius) / 2;
                                
                                const x = slice.x + Math.cos(angle) * distance;
                                const y = slice.y + Math.sin(angle) * distance;
                                
                                ctx.fillText(`${{percentage}}%`, x, y);
                            }}
                        }});
                        
                        ctx.restore();
                    }}
                }}]
            }});
            
            console.log('Status pie chart init completion');
            
            // ========== PieChart2: Done Distribution ==========
            const projectCtx = document.getElementById('projectPieChart');
            if (!projectCtx) {{
                console.error('Not find done PieChart canvas');
                return;
            }}
            
            console.log('Done pie chart initing...');
            
            // No done data showing
            if ({len(project_names)} === 0) {{
                const ctx = projectCtx.getContext('2d');
                ctx.save();
                ctx.font = '16px "Segoe UI", Arial, sans-serif';
                ctx.fillStyle = '#94a3b8';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText('No project data', projectCtx.width/2, projectCtx.height/2);
                ctx.restore();
            }} else {{
                const projectChart = new Chart(projectCtx.getContext('2d'), {{
                    type: 'doughnut',
                    data: {{
                        labels: {project_names_str},
                        datasets: [{{
                            data: {project_done_values_str},
                            backgroundColor: {done_colors_str},
                            borderWidth: 2,
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
                                        const value = context.raw;
                                        const total = {total_done};
                                        const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                                        return ` ${{context.label}}: ${{value}} issues (${{percentage}}%)`;
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
                            
                            const centerX = chart.width / 2;
                            const centerY = chart.height / 2;
                            
                            ctx.font = 'bold 24px "Segoe UI", Arial, sans-serif';
                            ctx.fillStyle = '#10b981';
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.fillText('{total_done}', centerX, centerY - 8);
                            
                            ctx.font = 'bold 13px "Segoe UI", Arial, sans-serif';
                            ctx.fillStyle = '#64748b';
                            ctx.fillText('DONE', centerX, centerY + 16);
                            
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
                            ctx.font = 'bold 11px "Segoe UI", Arial, sans-serif';
                            ctx.fillStyle = 'white';
                            
                            meta.data.forEach((slice, index) => {{
                                const value = chart.data.datasets[0].data[index];
                                const percentage = percentages[index];
                                
                                if (slice && (slice.endAngle - slice.startAngle) > 0.2 && value > 0) {{
                                    const angle = slice.startAngle + (slice.endAngle - slice.startAngle) / 2;
                                    const distance = slice.innerRadius + (slice.outerRadius - slice.innerRadius) / 2;
                                    
                                    const x = slice.x + Math.cos(angle) * distance;
                                    const y = slice.y + Math.sin(angle) * distance;
                                    
                                    ctx.fillText(`${{percentage}}%`, x, y);
                                }}
                            }});
                            
                            ctx.restore();
                        }}
                    }}]
                }});
            }}
            
            console.log('Done pie chart init completion');
            
            // ========== PieChart3: Blocked Distribution ==========
            const blockedCtx = document.getElementById('blockedPieChart');
            if (!blockedCtx) {{
                console.error('找不到blockedPieChart canvas元素');
                return;
            }}
            
            console.log('Blocked pie chart initing...');
            
            // No blocked data showing
            if ({len(blocked_projects)} === 0) {{
                const ctx = blockedCtx.getContext('2d');
                ctx.save();
                ctx.font = '16px "Segoe UI", Arial, sans-serif';
                ctx.fillStyle = '#94a3b8';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText('No blocked issues', blockedCtx.width/2, blockedCtx.height/2);
                ctx.restore();
            }} else {{
                const blockedChart = new Chart(blockedCtx.getContext('2d'), {{
                    type: 'doughnut',
                    data: {{
                        labels: {blocked_projects_str},
                        datasets: [{{
                            data: {blocked_values_str},
                            backgroundColor: {blocked_colors_str},
                            borderWidth: 2,
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
                                        const value = context.raw;
                                        const total = {total_blocked};
                                        const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                                        return ` ${{context.label}}: ${{value}} issues (${{percentage}}%)`;
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
                        id: 'centerTextBlocked',
                        afterDraw: function(chart) {{
                            const ctx = chart.ctx;
                            ctx.save();
                            
                            const centerX = chart.width / 2;
                            const centerY = chart.height / 2;
                            
                            ctx.font = 'bold 24px "Segoe UI", Arial, sans-serif';
                            ctx.fillStyle = '#ef4444';
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.fillText('{total_blocked}', centerX, centerY - 8);
                            
                            ctx.font = 'bold 13px "Segoe UI", Arial, sans-serif';
                            ctx.fillStyle = '#64748b';
                            ctx.fillText('BLOCKED', centerX, centerY + 16);
                            
                            ctx.restore();
                        }}
                    }}, {{
                        id: 'percentageLabelsBlocked',
                        afterDraw: function(chart) {{
                            const ctx = chart.ctx;
                            const meta = chart.getDatasetMeta(0);
                            const total = {total_blocked};
                            const percentages = {blocked_percentages_str};
                            
                            ctx.save();
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.font = 'bold 11px "Segoe UI", Arial, sans-serif';
                            ctx.fillStyle = 'white';
                            
                            meta.data.forEach((slice, index) => {{
                                const value = chart.data.datasets[0].data[index];
                                const percentage = percentages[index];
                                
                                if (slice && (slice.endAngle - slice.startAngle) > 0.2 && value > 0) {{
                                    const angle = slice.startAngle + (slice.endAngle - slice.startAngle) / 2;
                                    const distance = slice.innerRadius + (slice.outerRadius - slice.innerRadius) / 2;
                                    
                                    const x = slice.x + Math.cos(angle) * distance;
                                    const y = slice.y + Math.sin(angle) * distance;
                                    
                                    ctx.fillText(`${{percentage}}%`, x, y);
                                }}
                            }});
                            
                            ctx.restore();
                        }}
                    }}]
                }});
            }}
            
            console.log('Blocked pie chart init completion');
        }});
        </script>
        """
    
        return pie_charts_html
    
    def _create_bar_chart_section(self, projects, to_do_values, in_progress_values, blocked_values, done_values, completion_pcts, max_total):
        """Create bar chart section - with dynamic height based on project count"""
        
        # 根据项目数量动态计算高度
        projects_count = len(projects)
        
        # 每个条固定高度 32px，加上图例和标题空间 150px
        bar_height_per_item = 32
        extra_height = 150

        bar_percentage = 0.85      # 条宽度
        category_percentage = 0.9  # 类别间距（越大间距越小）

        total_chart_height = projects_count * bar_height_per_item + extra_height
        
        # 设置最小高度和最大高度限制
        min_height = 400
        max_height = 2000
        final_height = max(min_height, min(total_chart_height, max_height))
        
        # ========== 简化为2个档位 ==========
        if projects_count > 12:
            # Many projects
            circle_size = 32              # 圆圈大小
            circle_font_size = "0.65rem"   # 圆圈字体
            bar_thickness = 22            # 条形厚度
            y_axis_font_size = 13         # Y轴字体
            title_font_size = "1.2rem"    # 标题字体
            label_font_size = "0.7rem"    # 标签字体
        else:
            # Less projects
            circle_size = 38              # 圆圈大小
            circle_font_size = "0.85rem"  # 圆圈字体
            bar_thickness = 24            # 条形厚度
            y_axis_font_size = 14         # Y轴字体
            title_font_size = "1.5rem"    # 标题字体
            label_font_size = "0.8rem"    # 标签字体
        
        # 动态计算标签容器宽度
        label_container_width = circle_size + 15
        
        # 动态计算条形图最大X轴值
        max_value = max([to_do_values[i] + in_progress_values[i] + blocked_values[i] + done_values[i] 
                        for i in range(projects_count)]) if projects_count > 0 else 100
        x_axis_max = int(max_value * 1.08)
        
        # 转换numpy类型为Python原生类型
        projects_str = json.dumps(projects)
        to_do_values_str = json.dumps([int(x) for x in to_do_values])
        in_progress_values_str = json.dumps([int(x) for x in in_progress_values])
        blocked_values_str = json.dumps([int(x) for x in blocked_values])
        done_values_str = json.dumps([int(x) for x in done_values])
        completion_pcts_str = json.dumps([int(x) for x in completion_pcts])
        
        bar_chart_html = f"""
        <!-- 第二部分：条形图 -->
        <div class="bar-chart-section">
            <div class="card">
                <h2 class="card-title" style="font-size: {title_font_size};">{self.column_plural_name if hasattr(self, 'column_plural_name') else 'Projects'} Delivery Progress</h2>
                <div class="bar-chart-container" style="height: {final_height}px; min-height: {min_height}px;">
                    <div class="chart-wrapper">
                        <div class="chart-canvas-container">
                            <canvas id="barChart"></canvas>
                        </div>
                        <div class="completion-labels-container" id="completionLabels" style="width: {label_container_width}px;"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <style>
            /* 确保canvas容器正确显示 */
            .chart-canvas-container {{
                position: relative;
                flex: 1;
                overflow: visible !important;
            }}
            
            #barChart {{
                width: 100% !important;
                height: auto !important;
                min-height: {final_height - 50}px;
            }}
            
            /* 右侧圆圈标签字体 */
            .completion-circle {{
                font-size: {circle_font_size} !important;
                font-weight: 700;
            }}
            
            /* 悬停标签字体 */
            .project-label {{
                font-size: {label_font_size} !important;
            }}
        </style>
        
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const ctx = document.getElementById('barChart').getContext('2d');
            
            // 数据
            const projects = {projects_str};
            const toDoValues = {to_do_values_str};
            const inProgressValues = {in_progress_values_str};
            const blockedValues = {blocked_values_str};
            const doneValues = {done_values_str};
            const completionPcts = {completion_pcts_str};
            const projectsCount = {projects_count};
            
            // 创建堆叠条形图
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
                            barPercentage: {bar_percentage},
                            categoryPercentage: {category_percentage}

                        }},
                        {{
                            label: 'In Progress',
                            data: inProgressValues,
                            backgroundColor: '#3b82f6',
                            borderWidth: 0.5,
                            borderColor: '#ffffff',
                            borderRadius: 3,
                            hoverBackgroundColor: '#2563eb',
                            barPercentage: {bar_percentage},
                            categoryPercentage: {category_percentage}
                        }},
                        {{
                            label: 'Blocked',
                            data: blockedValues,
                            backgroundColor: '#ef4444',
                            borderWidth: 0.5,
                            borderColor: '#ffffff',
                            borderRadius: 3,
                            hoverBackgroundColor: '#dc2626',
                            barPercentage: {bar_percentage},
                            categoryPercentage: {category_percentage}
                        }},
                        {{
                            label: 'To Do',
                            data: toDoValues,
                            backgroundColor: '#94a3b8',
                            borderWidth: 0.5,
                            borderColor: '#ffffff',
                            borderRadius: 3,
                            hoverBackgroundColor: '#64748b',
                            barPercentage: {bar_percentage},
                            categoryPercentage: {category_percentage}
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
                                    size: 13
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
                                    size: {y_axis_font_size},
                                    weight: '500'
                                }}
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{ 
                            display: true,
                            position: 'top',
                            labels: {{
                                font: {{
                                    size: 12
                                }}
                            }}
                        }},
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
            
            // 创建右侧完成率标签
            function createCompletionLabels() {{
                const container = document.getElementById('completionLabels');
                if (!container) return;
                
                container.innerHTML = '';
                
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
                    
                    const projectLabel = document.createElement('div');
                    projectLabel.className = 'project-label';
                    let projectName = projects[index];
                    projectLabel.textContent = `${{projectName}}\\nCompletion: ${{percent}}%`;
                    
                    const circleDiv = document.createElement('div');
                    circleDiv.className = 'completion-circle';
                    circleDiv.style.width = '{circle_size}px';
                    circleDiv.style.height = '{circle_size}px';
                    circleDiv.style.lineHeight = '{circle_size}px';
                    circleDiv.style.textAlign = 'center';
                    circleDiv.style.borderRadius = '50%';
                    
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
            
            function updateLabelPositions() {{
                const container = document.getElementById('completionLabels');
                if (!container) return;
                
                const yScale = chart.scales.y;
                if (!yScale) return;
                
                const meta = chart.getDatasetMeta(0);
                const barPositions = [];
                
                for (let i = 0; i < projectsCount; i++) {{
                    const position = yScale.getPixelForValue(i);
                    barPositions.push(position);
                }}
                
                const circleHeight = {circle_size};
                
                for (let i = 0; i < projectsCount; i++) {{
                    const label = document.getElementById(`completion-label-${{i}}`);
                    if (!label) continue;
                    
                    const barCenter = barPositions[i];
                    const topPosition = barCenter - (circleHeight / 2);
                    label.style.top = `${{topPosition}}px`;
                    label.style.height = `${{circleHeight}}px`;
                }}
            }}
            
            function schedulePositionUpdates() {{
                setTimeout(updateLabelPositions, 300);
                
                chart.options.animation = {{
                    onComplete: function() {{
                        setTimeout(updateLabelPositions, 200);
                    }},
                    duration: 800
                }};
                
                window.addEventListener('resize', function() {{
                    setTimeout(updateLabelPositions, 300);
                }});
            }}
            
            createCompletionLabels();
            schedulePositionUpdates();
            setInterval(updateLabelPositions, 1000);
        }});
        </script>
        """
        
        return bar_chart_html
    
    def _create_explanations_section(self):
        """Create explanations section"""
        explanations_html = """
        <!-- 说明部分 -->
        <div class="explanations-section">
            <div class="card">
                <h2 class="card-title">Dashboard Explanations</h2>
                
                <div class="explanation-group">
                    <h3>📊 Status Mapping Explanation</h3>
                    <p>The status categories in this dashboard are mapped from Jira statuses as follows:</p>
                    <ul>
                        <li><strong>To Do</strong> = To Do + Backlog + Prioritized + Up Next + Selected for Development</li>
                        <li><strong>In Progress</strong> = In Progress + In Review + Waiting for Release + Dev + STG + PRD</li>
                        <li><strong>Blocked</strong> = Blocked</li>
                        <li><strong>Done</strong> = Done + Completed + Closed + Resolved + Released</li>
                    </ul>
                    <p>This mapping provides a simplified view of project progress by consolidating related statuses into four main categories for clearer tracking and reporting.</p>
                </div>
                
                <div class="explanation-group">
                    <h3>🎯 Completion Percentage Circles Explanation</h3>
                    <p>The colored circles on the right side of the Delivery Progress chart indicate the completion percentage for each project:</p>
                    <div class="legend-container">
                        <div class="legend-item">
                            <span class="legend-circle high-completion"></span>
                            <span><strong>High Completion Rate (≥80%)</strong> - On track or ahead of schedule</span>
                        </div>
                        <div class="legend-item">
                            <span class="legend-circle medium-completion"></span>
                            <span><strong>Medium Completion Rate (50-79%)</strong> - Steady progress</span>
                        </div>
                        <div class="legend-item">
                            <span class="legend-circle low-completion"></span>
                            <span><strong>Low Completion Rate (&lt;50%)</strong> - Needs attention</span>
                        </div>
                    </div>
                    <p>Completion percentage is calculated as: <strong>Done Issues / Total Issues × 100%</strong></p>
                </div>
            </div>
        </div>
        """
        
        return explanations_html
    
    def _create_table_html(self, project_data, total_row):
        """Create data table HTML - with dynamic column name, add Blocked column"""
        column_display_name = self.column_display_name if hasattr(self, 'column_display_name') else "Project"
        column_plural_name = self.column_plural_name if hasattr(self, 'column_plural_name') else "Projects"
        
        # 表格标题使用复数，列头使用单数
        table_title = f"{column_plural_name} Progress Details"
        column_header = column_display_name

        table_rows = []
        
        # 项目行
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
                <td><span class="status-badge status-blocked">{row['Blocked']}</span></td>
                <td><span class="status-badge status-done" style="background-color: #10b981; color: white;">{row['Done']}</span></td>
                <td>{row['Total']}</td>
                <td class="completion-cell {completion_class}">{row['Completion %']}</td>
            </tr>
            """)
        
        # Total rows
        table_rows.append(f"""
        <tr class="total-row">
            <td>TOTAL</td>
            <td>{total_row['To Do']}</td>
            <td>{total_row['In Progress']}</td>
            <td>{total_row['Blocked']}</td>
            <td>{total_row['Done']}</td>
            <td>{total_row['Total']}</td>
            <td class="completion-cell">{total_row['Completion %']}</td>
        </tr>
        """)
        
        table_html = f"""
        <!-- Third section: Table -->
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
        """Create a full page"""
        column_display_name = self.column_display_name if hasattr(self, 'column_display_name') else "Project"
        column_plural_name = self.column_plural_name if hasattr(self, 'column_plural_name') else "Projects"
        
        # Calculate Blocked Rate
        blocked_rate = 0
        if total_row['Total'] > 0:
            blocked_rate = round((total_row['Blocked'] / total_row['Total'] * 100), 1)
        
        # Ensure risk ranking
        if blocked_rate >= 10:
            risk_level = "High"
            risk_color = "#ef4444"
            risk_bg = "#fef2f2"
        elif blocked_rate >= 5:
            risk_level = "Medium"
            risk_color = "#f59e0b"
            risk_bg = "#fffbeb"
        else:
            risk_level = "Low"
            risk_color = "#10b981"
            risk_bg = "#f0fdf4"
        
        # Ensure primary Title
        if hasattr(self, 'custom_title') and self.custom_title:
            dashboard_title = self.custom_title
            page_title = self.custom_title
        else:
            # use the default title
            dashboard_title = f"{column_plural_name} Delivery Dashboard"
            page_title = f"{column_plural_name} Delivery Dashboard"
        
        # Create pie charts section
        pie_charts_html = self._create_pie_charts_section(project_data, total_row, projects)
        
        # Create bar charts section
        bar_chart_html = self._create_bar_chart_section(projects, to_do_values, in_progress_values, 
                                                      blocked_values, done_values, completion_pcts, max_total)
        
        # Create table section
        table_html = self._create_table_html(project_data, total_row)
        
        # Create explanations section
        explanations_html = self._create_explanations_section()
        
        # Fetched current time
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # Full HTML template
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
            
            /* Common Cards Style */
            .card {{
                background: white;
                border-radius: 16px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
                padding: 25px 30px 30px 30px;
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
            
            /* 页头样式 */
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
            
            /* 下载按钮样式 */
            .download-container {{
                position: absolute;
                right: 0;
                top: 0;
                display: flex;
                gap: 10px;
            }}
            
            .download-btn {{
                background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
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
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
            }}
            
            .download-btn:active {{
                transform: translateY(0);
            }}
            
            .download-btn.download-image {{
                background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }}
            
            .download-btn.download-image:hover {{
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
            }}
            
            .download-btn svg {{
                width: 18px;
                height: 18px;
            }}
            
            /* Download Hits */
            .download-hint {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                background-color: #2563eb;
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
               2. Overview Section - 7 cards
               =============================== */
            .overview-section {{
                display: grid;
                grid-template-columns: repeat(7, 1fr);
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
            
            /* 状态颜色 */
            .overview-todo .overview-value {{ color: #94a3b8; }}
            .overview-progress .overview-value {{ color: #3b82f6; }}
            .overview-blocked .overview-value {{ color: #ef4444; }}
            .overview-done .overview-value {{ color: #059669; }}
            .overview-total .overview-value {{ color: #1e293b; }}
            .overview-completion .overview-value {{ color: #059669; }}
            
            /* ===============================
               3. Pie Charts Section - Three
               =============================== */
            .pie-container {{
                position: relative;
                height: 300px;
                margin: 10px 0;
                overflow: visible !important;
            }}
            
            /* ===============================
               4. Bar Chart Section - 自适应高度
               =============================== */
            .bar-chart-section {{
                margin-bottom: 35px;
            }}
            
            .bar-chart-container {{
                position: relative;
                margin: 8px 0 8px;
                width: 100%;
                overflow: visible !important;
            }}
            
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
            
            .completion-labels-container {{
                position: absolute;
                right: 0;
                top: 0;
                z-index: 100;
                overflow: visible !important;
            }}
            
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
            
            .completion-circle {{
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                color: white;
                box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
                transition: all 0.2s ease;
                z-index: 103;
                flex-shrink: 0;
            }}
            
            .completion-label:hover .completion-circle {{
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
                transform: scale(1.05);
            }}
            
            /* ===============================
               5. Table Section
               =============================== */
            .table-section {{
                margin-bottom: 40px;
            }}
            
            .table-container {{
                background: white;
                border-radius: 16px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
                padding: 30px;
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
                font-size: 0.9rem;
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
            
            .status-todo {{ 
                background: #94a3b8 !important; 
                color: white !important;
                border: none !important;
            }}
            .status-progress {{ 
                background: #3b82f6 !important; 
                color: white !important;
                border: none !important;
            }}
            .status-blocked {{ 
                background: #ef4444 !important; 
                color: white !important;
                border: none !important;
            }}
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
            
            /* ===============================
               7. Responsive Design
               =============================== */
            @media (max-width: 1400px) {{
                .overview-section {{
                    grid-template-columns: repeat(4, 1fr);
                }}
                
                [style*="grid-template-columns: repeat(3, 1fr)"] {{
                    grid-template-columns: repeat(2, 1fr) !important;
                }}
            }}
            
            @media (max-width: 1200px) {{
                body {{
                    min-width: auto;
                    padding: 20px 15px;
                }}
                
                .overview-section {{
                    grid-template-columns: repeat(3, 1fr);
                }}
                
                [style*="grid-template-columns: repeat(3, 1fr)"] {{
                    grid-template-columns: 1fr !important;
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
            
            <!-- Overiew Section 7 Cards -->
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
                
                <div class="overview-card overview-completion" style="background: white; border-left: 4px solid #059669;">
                    <div class="overview-value">{total_row['Completion %']}</div>
                    <div class="overview-label">Completion Rate</div>
                </div>
                
                <!-- Block Rate Card -->
                <div class="overview-card" style="background: white; border-left: 4px solid #ef4444;">
                    <div class="overview-value" style="color: #ef4444;">{blocked_rate}%</div>
                    <div class="overview-label">Blocked Rate</div>
                </div>
            </div>
            
            <!-- Three Pie Charts -->
            {pie_charts_html}
            
            <!-- Bar Chart Section -->
            {bar_chart_html}
            
            <!-- Table Section -->
            {table_html}
            
            <!-- Explanations -->
            {explanations_html}
            
            <!-- Download tips -->
            <div class="download-hint" id="downloadHint">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <span>Dashboard image is downloading...</span>
            </div>
    </div>
        
    <!-- Download JavaScript -->
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        console.log('Dashboard loaded');
        
        const downloadImageBtn = document.getElementById('downloadImageBtn');
        const downloadHint = document.getElementById('downloadHint');
        
        async function downloadDashboardImage() {{
            console.log('Starting dashboard image export...');
            
            showDownloadHint('Preparing dashboard image...');
            if (downloadImageBtn) {{
                downloadImageBtn.disabled = true;
                downloadImageBtn.innerHTML = 'Preparing...';
            }}
            
            try {{
                // 1. 先确保原始页面的圆圈位置正确
                if (typeof updateLabelPositions === 'function') {{
                    updateLabelPositions();
                }}
                
                await new Promise(resolve => setTimeout(resolve, 300));
                
                // 2. 获取当前图表实例和位置信息
                const chartInstances = Chart.instances ? Object.values(Chart.instances) : [];
                const barChart = chartInstances.find(c => c.canvas && c.canvas.id === 'barChart');
                
                if (!barChart) {{
                    throw new Error('Bar chart not found');
                }}
                
                // 3. 获取每个条的位置信息
                const yScale = barChart.scales.y;
                const projectsCount = document.querySelectorAll('.completion-label').length;
                
                // 获取圆圈大小
                const firstCircle = document.querySelector('.completion-circle');
                let circleSize = 38;
                if (firstCircle) {{
                    const circleHeight = firstCircle.offsetHeight;
                    if (circleHeight > 0) {{
                        circleSize = circleHeight;
                    }}
                }}
                
                // 4. 保存每个圆圈应该的 top 位置
                const circlePositions = [];
                for (let i = 0; i < projectsCount; i++) {{
                    const barCenter = yScale.getPixelForValue(i);
                    const topPosition = barCenter - (circleSize / 2);
                    circlePositions.push(topPosition);
                }}
                
                // 5. 转换图表为图片
                const chartImages = await convertChartsToImages();
                
                // 6. 创建临时页面并传入位置信息
                const tempContainer = await createScreenshotPage(chartImages, circlePositions, circleSize);
                
                // 7. 等待图片加载
                await waitForImages(tempContainer);
                
                // 8. 截图并下载
                await captureAndDownload(tempContainer);
                
                showDownloadHint('Dashboard image downloaded successfully!');
                console.log('✅ Image download completed');
                
            }} catch (error) {{
                console.error('Download failed:', error);
                try {{
                    console.log('Trying fallback method...');
                    await backupScreenshotMethod();
                    showDownloadHint('Dashboard image downloaded successfully!');
                }} catch (backupError) {{
                    console.error('Fallback method failed:', backupError);
                    showDownloadHint('Download failed, please try again');
                }}
            }} finally {{
                if (downloadImageBtn) {{
                    downloadImageBtn.disabled = false;
                    downloadImageBtn.innerHTML = 'Download Dashboard Image';
                }}
                setTimeout(() => {{
                    if (downloadHint) {{
                        downloadHint.classList.remove('show');
                    }}
                }}, 3000);
            }}
        }}
        
        async function convertChartsToImages() {{
            const chartImages = {{}};
            
            if (typeof Chart !== 'undefined') {{
                const charts = Object.values(Chart.instances || {{}});
                
                // 先更新位置
                if (typeof updateLabelPositions === 'function') {{
                    updateLabelPositions();
                }}
                
                await new Promise(resolve => setTimeout(resolve, 200));
                
                charts.forEach((chart) => {{
                    try {{
                        const canvas = chart.canvas;
                        if (canvas && canvas.id) {{
                            const dataURL = canvas.toDataURL('image/png', 1.0);
                            chartImages[canvas.id] = dataURL;
                            console.log(`✅ Chart ${{canvas.id}} converted to image`);
                        }}
                    }} catch (error) {{
                        console.error(`Chart conversion failed:`, error);
                    }}
                }});
            }}
            
            return chartImages;
        }}
        
        async function createScreenshotPage(chartImages, circlePositions, circleSize) {{
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
            
            const dashboard = document.querySelector('.dashboard-container').cloneNode(true);
            
            const elementsToRemove = dashboard.querySelectorAll(
                '.explanations-section, .download-container, .download-hint'
            );
            elementsToRemove.forEach(el => el.remove());
            
            // 替换 canvas 为图片
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
                
                img.width = canvas.width;
                img.height = canvas.height;
                
                if (chartImages[canvas.id]) {{
                    img.src = chartImages[canvas.id];
                }} else {{
                    try {{
                        img.src = canvas.toDataURL('image/png');
                    }} catch (e) {{
                        createChartPlaceholder(img, canvas);
                    }}
                }}
                
                if (canvas.parentNode) {{
                    canvas.parentNode.replaceChild(img, canvas);
                }}
            }});
            
            // 使用传入的位置信息重新定位圆圈
            const completionLabels = dashboard.querySelectorAll('.completion-label');
            for (let i = 0; i < completionLabels.length && i < circlePositions.length; i++) {{
                const label = completionLabels[i];
                label.style.position = 'absolute';
                label.style.top = `${{circlePositions[i]}}px`;
                label.style.height = `${{circleSize}}px`;
            }}
            
            // 确保圆圈容器有相对定位
            const labelsContainer = dashboard.querySelector('#completionLabels');
            if (labelsContainer) {{
                labelsContainer.style.position = 'relative';
                labelsContainer.style.height = '100%';
            }}
            
            tempContainer.appendChild(dashboard);
            document.body.appendChild(tempContainer);
            
            return tempContainer;
        }}
        
        function createChartPlaceholder(img, canvas) {{
            const width = canvas.width || 400;
            const height = canvas.height || 300;
            
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
                
                if (loadedCount === images.length) {{
                    resolve();
                }}
                
                setTimeout(resolve, 2000);
            }});
        }}
        
        async function captureAndDownload(tempContainer) {{
            return new Promise((resolve, reject) => {{
                try {{
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
                            y: 0
                        }}).then(canvas => {{
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
        
        async function backupScreenshotMethod() {{
            return new Promise((resolve, reject) => {{
                try {{
                    const elementsToHide = document.querySelectorAll(
                        '.explanations-section, .download-container'
                    );
                    const originalStyles = [];
                    
                    elementsToHide.forEach((el, index) => {{
                        originalStyles[index] = el.style.cssText;
                        el.style.cssText = 'display: none !important;';
                    }});
                    
                    if (typeof Chart !== 'undefined') {{
                        const charts = Object.values(Chart.instances || {{}});
                        charts.forEach(chart => {{
                            try {{
                                chart.update('none');
                                chart.render();
                            }} catch (e) {{}}
                        }});
                    }}
                    
                    setTimeout(() => {{
                        html2canvas(document.body, {{
                            scale: 1.5,
                            backgroundColor: '#f8fafc',
                            logging: false
                        }}).then(canvas => {{
                            const link = document.createElement('a');
                            const timestamp = new Date().toISOString()
                                .slice(0, 19)
                                .replace(/:/g, '-');
                            const filename = `dashboard-backup-${{timestamp}}.png`;
                            
                            link.download = filename;
                            link.href = canvas.toDataURL('image/png');
                            link.click();
                            
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
        
        function showDownloadHint(message) {{
            if (downloadHint) {{
                const span = downloadHint.querySelector('span');
                if (span) {{
                    span.textContent = message;
                }}
                downloadHint.classList.add('show');
            }}
        }}
        
        if (downloadImageBtn) {{
            downloadImageBtn.addEventListener('click', downloadDashboardImage);
        }}
    }});
    </script>
</body>
</html>"""
        
        return html_template