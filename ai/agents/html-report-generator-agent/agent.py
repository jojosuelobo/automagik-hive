"""
HTML Report Generator Agent - Professional Survey Report Generation
================================================================

This agent creates professional HTML reports with interactive charts
for stakeholder presentations of survey data analysis.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from lib.logging import logger
from lib.utils.version_factory import create_agent


def generate_html_report(survey_data: Dict[str, Any], file_info: Dict[str, Any] = None) -> str:
    """
    Generate a complete HTML report from survey data
    
    Args:
        survey_data: Survey analysis data from survey-data-analyzer-agent
        file_info: Original Excel file information
        
    Returns:
        Complete HTML report as string
    """
    
    logger.info("Generating HTML report...")
    
    # Extract data
    questions = survey_data.get("survey_questions", {})
    summary = survey_data.get("survey_summary", {})
    overview = summary.get("overview", {})
    
    # Generate report sections
    html_content = generate_html_template()
    html_content += generate_header_section(file_info, overview)
    html_content += generate_executive_summary(overview, summary)
    html_content += generate_overview_section(overview)
    html_content += generate_charts_section(questions)
    html_content += generate_insights_section(summary)
    html_content += generate_footer_section()
    
    # Close HTML
    html_content += """
    </body>
    </html>
    """
    
    logger.info("HTML report generated successfully")
    return html_content


def generate_html_template() -> str:
    """Generate the base HTML template with CSS and JavaScript"""
    
    return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Pesquisa - Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            color: #7f8c8d;
            font-size: 1.2em;
        }
        
        .section {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .section h2 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .chart-container {
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .chart-wrapper {
            position: relative;
            height: 400px;
            margin: 20px 0;
        }
        
        .question-header {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0 10px 0;
        }
        
        .question-title {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        
        .question-meta {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        .insights-list {
            list-style: none;
        }
        
        .insights-list li {
            background: #e8f6f3;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #1abc9c;
            border-radius: 5px;
        }
        
        .footer {
            text-align: center;
            color: white;
            padding: 20px;
            margin-top: 30px;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .section {
                padding: 20px;
            }
        }
        
        .executive-summary {
            background: linear-gradient(135deg, #1abc9c, #16a085);
            color: white;
            border-radius: 10px;
            padding: 30px;
            margin: 30px 0;
        }
        
        .executive-summary h3 {
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .highlight {
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
"""


def generate_header_section(file_info: Dict[str, Any] = None, overview: Dict[str, Any] = None) -> str:
    """Generate the header section with title and basic info"""
    
    current_date = datetime.now().strftime("%d/%m/%Y às %H:%M")
    total_responses = overview.get("total_possible_responses", 0) if overview else 0
    total_questions = overview.get("total_questions", 0) if overview else 0
    
    return f"""
        <div class="header">
            <h1>📊 Relatório de Pesquisa</h1>
            <p class="subtitle">Dashboard Interativo de Análise de Dados</p>
            <p><strong>Gerado em:</strong> {current_date}</p>
            {f'<p><strong>Respondentes:</strong> {total_responses} | <strong>Perguntas:</strong> {total_questions}</p>' if total_responses > 0 else ''}
        </div>
"""


def generate_executive_summary(overview: Dict[str, Any], summary: Dict[str, Any]) -> str:
    """Generate executive summary section"""
    
    total_questions = overview.get("total_questions", 0)
    total_responses = overview.get("total_possible_responses", 0)
    avg_response_rate = overview.get("avg_response_rate", 0)
    
    # Generate key insights
    viz_recommendations = summary.get("visualization_recommendations", [])
    key_insights = []
    
    if avg_response_rate > 80:
        key_insights.append(f"✅ Alta taxa de participação ({avg_response_rate:.1f}%)")
    elif avg_response_rate > 50:
        key_insights.append(f"⚠️ Taxa moderada de participação ({avg_response_rate:.1f}%)")
    else:
        key_insights.append(f"❌ Baixa taxa de participação ({avg_response_rate:.1f}%)")
    
    if total_questions >= 10:
        key_insights.append(f"📝 Pesquisa abrangente com {total_questions} perguntas")
    
    if len(viz_recommendations) > 0:
        key_insights.append(f"📈 {len(viz_recommendations)} visualizações recomendadas")
    
    insights_html = "".join([f"<div class='highlight'>{insight}</div>" for insight in key_insights])
    
    return f"""
        <div class="executive-summary">
            <h3>📋 Resumo Executivo</h3>
            <p>Esta pesquisa coletou dados de <strong>{total_responses} respondentes</strong> através de <strong>{total_questions} perguntas</strong>, 
            alcançando uma taxa média de resposta de <strong>{avg_response_rate:.1f}%</strong>.</p>
            
            <h4>Principais Insights:</h4>
            {insights_html}
        </div>
"""


def generate_overview_section(overview: Dict[str, Any]) -> str:
    """Generate overview statistics section"""
    
    total_questions = overview.get("total_questions", 0)
    total_responses = overview.get("total_possible_responses", 0)
    avg_response_rate = overview.get("avg_response_rate", 0)
    question_types = overview.get("question_types", {})
    
    # Generate question types stats
    types_html = ""
    for q_type, count in question_types.items():
        type_label = {
            "yes_no": "Sim/Não",
            "multiple_choice_few": "Múltipla Escolha (Poucas)",
            "multiple_choice_many": "Múltipla Escolha (Muitas)",
            "likert_scale": "Escala Likert",
            "scale_numeric": "Escala Numérica",
            "text_response": "Resposta Livre"
        }.get(q_type, q_type.replace("_", " ").title())
        
        types_html += f"""
            <div class="stat-card">
                <div class="stat-number">{count}</div>
                <div class="stat-label">{type_label}</div>
            </div>
        """
    
    return f"""
        <div class="section">
            <h2>📈 Visão Geral dos Dados</h2>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_responses}</div>
                    <div class="stat-label">Total de Respondentes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_questions}</div>
                    <div class="stat-label">Perguntas Analisadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{avg_response_rate:.1f}%</div>
                    <div class="stat-label">Taxa Média de Resposta</div>
                </div>
            </div>
            
            <h3>Tipos de Perguntas</h3>
            <div class="stats-grid">
                {types_html}
            </div>
        </div>
"""


def generate_charts_section(questions: Dict[str, Any]) -> str:
    """Generate charts section with interactive visualizations"""
    
    charts_html = """
        <div class="section">
            <h2>📊 Análise Detalhada por Pergunta</h2>
    """
    
    for i, (q_name, q_data) in enumerate(questions.items()):
        if q_data.get("total_responses", 0) == 0:
            continue
            
        question_type = q_data.get("question_type", "unknown")
        total_responses = q_data.get("total_responses", 0)
        response_rate = q_data.get("response_rate", 0)
        frequency_analysis = q_data.get("frequency_analysis", {})
        
        chart_id = f"chart_{i}"
        
        # Generate chart data - sort by frequency (descending) then alphabetically
        sorted_items = sorted(
            frequency_analysis.items(),
            key=lambda x: (-x[1]["count"], x[0])  # Sort by count desc, then label asc
        )
        labels = [item[0] for item in sorted_items]
        data_values = [item[1]["count"] for item in sorted_items]
        percentages = [item[1]["percentage"] for item in sorted_items]
        
        # Determine chart type
        chart_type = determine_chart_type(question_type, len(labels))
        
        # Clean question name for display
        display_name = q_name.replace("pesquisa300625_screen", "Pergunta ")
        
        charts_html += f"""
            <div class="question-header">
                <div class="question-title">{display_name}</div>
                <div class="question-meta">
                    Tipo: {get_type_label(question_type)} | 
                    Respostas: {total_responses} | 
                    Taxa: {response_rate:.1f}%
                </div>
            </div>
            
            <div class="chart-container">
                <div class="chart-wrapper">
                    <canvas id="{chart_id}"></canvas>
                </div>
                
                <script>
                    const ctx_{i} = document.getElementById('{chart_id}').getContext('2d');
                    new Chart(ctx_{i}, {{
                        type: '{chart_type}',
                        data: {{
                            labels: {json.dumps(labels)},
                            datasets: [{{
                                label: 'Respostas',
                                data: {json.dumps(data_values)},
                                backgroundColor: {generate_colors(len(labels))},
                                borderColor: {generate_border_colors(len(labels))},
                                borderWidth: 2
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {{
                                legend: {{
                                    position: 'bottom',
                                    labels: {{
                                        padding: 20,
                                        usePointStyle: true
                                    }}
                                }},
                                tooltip: {{
                                    callbacks: {{
                                        label: function(context) {{
                                            const label = context.label || '';
                                            const value = context.raw;
                                            const percentage = {json.dumps(percentages)}[context.dataIndex];
                                            return label + ': ' + value + ' (' + percentage.toFixed(1) + '%)';
                                        }}
                                    }}
                                }}
                            }},
                            scales: {generate_scales_config(chart_type)}
                        }}
                    }});
                </script>
            </div>
        """
    
    charts_html += "</div>"
    return charts_html


def determine_chart_type(question_type: str, num_options: int) -> str:
    """Determine the best chart type for the data"""
    
    if question_type == "yes_no":
        return "doughnut"
    elif question_type in ["multiple_choice_few", "multiple_choice_many"]:
        if num_options <= 5:
            return "pie"
        else:
            return "bar"
    elif question_type == "likert_scale":
        return "bar"
    elif question_type == "scale_numeric":
        return "line"
    else:
        return "bar"


def get_type_label(question_type: str) -> str:
    """Get user-friendly label for question type"""
    
    labels = {
        "yes_no": "Sim/Não",
        "multiple_choice_few": "Múltipla Escolha",
        "multiple_choice_many": "Múltipla Escolha",
        "likert_scale": "Escala Likert",
        "scale_numeric": "Escala Numérica",
        "text_response": "Resposta Livre"
    }
    return labels.get(question_type, question_type.replace("_", " ").title())


def generate_colors(count: int) -> str:
    """Generate color palette for charts"""
    
    colors = [
        'rgba(52, 152, 219, 0.8)',   # Blue
        'rgba(231, 76, 60, 0.8)',    # Red
        'rgba(46, 204, 113, 0.8)',   # Green
        'rgba(155, 89, 182, 0.8)',   # Purple
        'rgba(241, 196, 15, 0.8)',   # Yellow
        'rgba(230, 126, 34, 0.8)',   # Orange
        'rgba(26, 188, 156, 0.8)',   # Turquoise
        'rgba(149, 165, 166, 0.8)',  # Gray
        'rgba(52, 73, 94, 0.8)',     # Dark Blue
        'rgba(192, 57, 43, 0.8)'     # Dark Red
    ]
    
    # Repeat colors if we need more
    extended_colors = colors * ((count // len(colors)) + 1)
    return json.dumps(extended_colors[:count])


def generate_border_colors(count: int) -> str:
    """Generate border colors for charts"""
    
    colors = [
        'rgba(52, 152, 219, 1)',
        'rgba(231, 76, 60, 1)',
        'rgba(46, 204, 113, 1)',
        'rgba(155, 89, 182, 1)',
        'rgba(241, 196, 15, 1)',
        'rgba(230, 126, 34, 1)',
        'rgba(26, 188, 156, 1)',
        'rgba(149, 165, 166, 1)',
        'rgba(52, 73, 94, 1)',
        'rgba(192, 57, 43, 1)'
    ]
    
    extended_colors = colors * ((count // len(colors)) + 1)
    return json.dumps(extended_colors[:count])


def generate_scales_config(chart_type: str) -> str:
    """Generate scales configuration for different chart types"""
    
    if chart_type in ["pie", "doughnut"]:
        return "{}"
    
    return """{
        y: {
            beginAtZero: true,
            grid: {
                color: 'rgba(0,0,0,0.1)'
            }
        },
        x: {
            grid: {
                color: 'rgba(0,0,0,0.1)'
            }
        }
    }"""


def generate_insights_section(summary: Dict[str, Any]) -> str:
    """Generate insights and recommendations section"""
    
    viz_recommendations = summary.get("visualization_recommendations", [])
    question_breakdown = summary.get("question_breakdown", {})
    
    # Generate insights based on data
    insights = []
    
    # Response rate insights
    high_response_questions = [q for q, data in question_breakdown.items() 
                             if data.get("response_rate", 0) > 90]
    low_response_questions = [q for q, data in question_breakdown.items() 
                            if data.get("response_rate", 0) < 50]
    
    if high_response_questions:
        insights.append(f"🎯 Perguntas com alta participação: {len(high_response_questions)} questões tiveram mais de 90% de respostas")
    
    if low_response_questions:
        insights.append(f"⚠️ Atenção necessária: {len(low_response_questions)} questões tiveram baixa participação (<50%)")
    
    # Chart type insights
    chart_types_count = {}
    for rec in viz_recommendations:
        chart_type = rec.get("recommended_chart", "")
        chart_types_count[chart_type] = chart_types_count.get(chart_type, 0) + 1
    
    if chart_types_count:
        most_common_chart = max(chart_types_count.items(), key=lambda x: x[1])
        insights.append(f"📊 Tipo de visualização mais recomendado: {most_common_chart[0]} ({most_common_chart[1]} vezes)")
    
    insights_html = "".join([f"<li>{insight}</li>" for insight in insights])
    
    return f"""
        <div class="section">
            <h2>💡 Insights e Recomendações</h2>
            
            <ul class="insights-list">
                {insights_html}
                <li>📈 Dados prontos para análise mais aprofundada e tomada de decisões</li>
                <li>🔄 Recomenda-se acompanhar tendências em futuras pesquisas</li>
            </ul>
            
            <h3>Recomendações de Ação</h3>
            <ul class="insights-list">
                <li>🎯 Focar em perguntas com baixa taxa de resposta para melhorar engajamento</li>
                <li>📊 Utilizar visualizações recomendadas para apresentações executivas</li>
                <li>🔍 Investigar padrões interessantes identificados nos dados</li>
                <li>📅 Planejar pesquisas de follow-up baseadas nos resultados</li>
            </ul>
        </div>
"""


def generate_footer_section() -> str:
    """Generate footer section"""
    
    generation_time = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    
    return f"""
        <div class="footer">
            <p>Relatório gerado automaticamente pelo Excel Processing Workflow</p>
            <p>{generation_time}</p>
        </div>
"""


def save_html_report(html_content: str, filename: str = None) -> str:
    """Save HTML report to file"""
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_pesquisa_{timestamp}.html"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"HTML report saved to: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error saving HTML report: {str(e)}")
        raise


# Agent factory function
async def get_html_report_generator_agent(**kwargs):
    """Factory function to create HTML report generator agent"""
    return await create_agent("html-report-generator-agent", **kwargs) 