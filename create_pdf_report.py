#!/usr/bin/env python3
"""
Gerador de Relatório PDF para Análise de Pesquisa
================================================
"""

import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import re

def detect_multiple_choice_question(col_data):
    """Detect if a question is multiple choice based on data patterns"""
    if len(col_data) == 0:
        return False
    
    # Check for common multiple choice patterns
    sample_responses = col_data.head(50).astype(str)
    
    # Pattern 1: JSON-like arrays ["0_Option","1_Option"]
    json_pattern = sample_responses.str.contains(r'\[".*"\]', na=False).sum()
    
    # Pattern 2: Comma-separated values with prefixes
    comma_pattern = sample_responses.str.contains(r'\d+_.*,\d+_.*', na=False).sum()
    
    # Pattern 3: Multiple quoted options
    quote_pattern = sample_responses.str.contains(r'".*",".*"', na=False).sum()
    
    # If more than 30% of samples show multiple choice patterns
    total_patterns = json_pattern + comma_pattern + quote_pattern
    return (total_patterns / len(sample_responses)) > 0.3

def parse_multiple_choice_data(col_data):
    """Parse multiple choice data and return individual option counts"""
    option_counts = {}
    total_respondents = len(col_data)
    
    for response in col_data:
        if pd.isna(response) or response == '':
            continue
            
        response_str = str(response).strip()
        options = []
        
        # Parse JSON-like format: ["0_Option","1_Option"]
        if response_str.startswith('[') and response_str.endswith(']'):
            try:
                # Remove brackets and split by comma
                inner = response_str[1:-1]
                raw_options = [opt.strip().strip('"') for opt in inner.split('","')]
                options.extend(raw_options)
            except:
                # Fallback: treat as single option
                options.append(response_str)
        
        # Parse comma-separated format: "0_Option","1_Option" or 0_Option,1_Option
        elif ',' in response_str:
            # Split by comma and clean quotes
            raw_options = [opt.strip().strip('"') for opt in response_str.split(',')]
            options.extend(raw_options)
        
        else:
            # Single option
            options.append(response_str)
        
        # Count each option
        for option in options:
            if option and option.strip():
                # Clean option text: remove numeric prefixes and underscores
                cleaned = option.strip()
                
                # Remove numeric prefixes like "0_", "1_", etc.
                cleaned = re.sub(r'^\d+_', '', cleaned)
                
                # Replace underscores with spaces
                cleaned = cleaned.replace('_', ' ')
                
                # Clean up common formatting issues
                cleaned = cleaned.replace('(ex.:', '(ex.: ')
                cleaned = cleaned.strip()
                
                if cleaned:
                    option_counts[cleaned] = option_counts.get(cleaned, 0) + 1
    
    # Sort by frequency and return top options
    sorted_options = sorted(option_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_options[:15], total_respondents  # Limit to top 15 options

def load_survey_data_and_create_charts(analysis_data):
    """Load survey data and create inline charts"""
    
    # Load the original Excel file
    file_path = analysis_data['metadata']['file_path']
    df = pd.read_excel(file_path)
    
    # Filter survey columns
    survey_cols = [col for col in df.columns if 'pesquisa' in col.lower()]
    survey_data = df[survey_cols].copy()
    
    charts_html = {}
    text_data = {}
    
    for col in survey_cols:
        col_data = survey_data[col].dropna()
        if len(col_data) == 0:
            continue
            
        stats = analysis_data['statistics'].get(col, {})
        chart_type = stats.get('chart_type', 'unknown')
        
        # Check if this is a multiple choice question
        is_multiple_choice = detect_multiple_choice_question(col_data)
        
        if is_multiple_choice:
            # Handle multiple choice questions with horizontal bar chart
            option_data, total_respondents = parse_multiple_choice_data(col_data)
            
            if option_data:
                options = [item[0] for item in option_data]
                counts = [item[1] for item in option_data]
                
                # Create horizontal bar chart for multiple choice
                fig = go.Figure(data=go.Bar(
                    x=counts,
                    y=options,
                    orientation='h',
                    marker=dict(
                        color=counts,
                        colorscale='viridis',
                        showscale=False
                    ),
                    hovertemplate='<b>%{y}</b><br>' +
                                'Respostas: %{x}<br>' +
                                'Percentual: %{customdata:.1f}%<extra></extra>',
                    customdata=[(count/total_respondents)*100 for count in counts]
                ))
                
                fig.update_layout(
                    title="Canais de Descoberta do Aplicativo (Multipla Selecao)",
                    title_font_size=16,
                    xaxis_title="Numero de Respondentes",
                    yaxis_title="Canais de Descoberta",
                    height=500,
                    margin=dict(l=20, r=20, t=60, b=20),
                    showlegend=False,
                    yaxis={'categoryorder': 'total ascending'}  # Order by value
                )
                
                # Add subtitle
                fig.add_annotation(
                    text=f"Multipla selecao permitida | Total: {total_respondents:,} respondentes",
                    xref="paper", yref="paper",
                    x=0.5, y=1.05,
                    showarrow=False,
                    font=dict(size=12, color="#666"),
                    xanchor='center'
                )
                
                charts_html[col] = fig.to_html(include_plotlyjs='inline', div_id=f"chart_{col.replace('/', '_')}")
        
        elif chart_type == 'categorical':
            # Create inline chart for categorical data
            value_counts = col_data.value_counts()
            
            # Use pie chart for binary data (2 options), bar chart for more options
            if len(value_counts) == 2:
                # Pie chart for binary data (e.g., SIM/NÃO)
                fig = px.pie(
                    values=value_counts.values,
                    names=value_counts.index,
                    title=f"Distribuição de Respostas - {col}",
                    color_discrete_sequence=['#667eea', '#764ba2']
                )
                
                fig.update_traces(
                    textposition='inside', 
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>%{value} respostas<br>%{percent}<extra></extra>'
                )
                
                fig.update_layout(
                    height=400,
                    title_font_size=14,
                    margin=dict(l=20, r=20, t=40, b=20),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
                )
            else:
                # Bar chart for multiple options
                fig = px.bar(
                    x=value_counts.values,
                    y=value_counts.index,
                    orientation='h',
                    title=f"Distribuição de Respostas - {col}",
                    labels={'x': 'Número de Respostas', 'y': 'Opções'},
                    color=value_counts.values,
                    color_continuous_scale='viridis'
                )
                
                fig.update_layout(
                    height=400,
                    title_font_size=14,
                    xaxis_title_font_size=12,
                    yaxis_title_font_size=12,
                    margin=dict(l=20, r=20, t=40, b=20),
                    showlegend=False
                )
            
            # Convert to HTML without external dependencies
            charts_html[col] = fig.to_html(include_plotlyjs='inline', div_id=f"chart_{col.replace('/', '_')}")
            
        elif chart_type == 'textual':
            # Collect text responses for combobox
            value_counts = col_data.value_counts()
            text_data[col] = {
                'total_unique': len(value_counts),
                'responses': list(value_counts.items())[:50],  # Limit to top 50
                'has_more': len(value_counts) > 50
            }
    
    return charts_html, text_data

def create_pdf_report():
    """Create a comprehensive PDF report with integrated charts"""
    
    # Find the latest analysis
    outputs_dir = Path("data/surveys/outputs")
    analysis_dirs = [d for d in outputs_dir.glob("analysis_*") if d.is_dir()]
    
    if not analysis_dirs:
        print("❌ Nenhuma análise encontrada")
        return
    
    # Get the most recent analysis
    latest_analysis = max(analysis_dirs, key=lambda x: x.stat().st_mtime)
    json_file = latest_analysis / "analysis_results.json"
    
    if not json_file.exists():
        print("❌ Arquivo de resultados não encontrado")
        return
    
    # Load analysis data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Load survey data and create inline charts
    print("📊 Carregando dados da pesquisa e criando gráficos...")
    charts_html, text_data = load_survey_data_and_create_charts(data)
    
    # Create comprehensive HTML report with integrated charts
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Relatório de Análise de Pesquisa</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            .header {{ text-align: center; border-bottom: 3px solid #667eea; padding-bottom: 20px; margin-bottom: 30px; }}
            .section {{ margin-bottom: 30px; }}
            .stats-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            .stats-table th, .stats-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            .stats-table th {{ background-color: #f8f9fa; font-weight: bold; }}
            .highlight {{ background-color: #e3f2fd; padding: 15px; border-left: 4px solid #2196f3; margin: 15px 0; }}
            .insight {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0; }}
            h1 {{ color: #667eea; }}
            h2 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            .summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }}
            .summary-item {{ text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
            .summary-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
            /* Estilos para gráficos integrados */
            .question-analysis {{ margin: 30px 0; padding: 20px; background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; }}
            .question-title {{ color: #667eea; font-size: 1.3em; margin-bottom: 15px; font-weight: bold; }}
            .chart-container {{ width: 70%; margin: 0 auto 20px auto; }}
            .text-responses {{ margin-top: 15px; }}
            .responses-dropdown {{ margin: 10px 0; }}
            .responses-dropdown details {{ background: #f8f9fa; border: 1px solid #ddd; border-radius: 5px; padding: 10px; }}
            .responses-dropdown summary {{ cursor: pointer; font-weight: bold; color: #667eea; padding: 5px; }}
            .responses-grid {{ max-height: 300px; overflow-y: auto; padding: 10px; background: white; border-radius: 4px; margin-top: 10px; }}
            .response-item {{ padding: 8px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }}
            .response-text {{ flex: 1; }}
            .response-count {{ font-weight: bold; color: #667eea; }}
            .stats-summary {{ background: #f0f8ff; padding: 10px; border-radius: 5px; margin-bottom: 15px; }}
            
            @media print {{ 
                body {{ margin: 20px; }} 
                .no-print {{ display: none; }}
                .chart-container {{ width: 90%; }}
                .responses-grid {{ max-height: 200px; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Relatório Executivo - Análise de Pesquisa</h1>
            <p><strong>Data da Análise:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
            <p><strong>Arquivo Fonte:</strong> {data['metadata']['file_path']}</p>
        </div>
        
        <div class="section">
            <h2>📈 Resumo Executivo</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="summary-number">{data['metadata']['total_rows']:,}</div>
                    <div>Total de Respostas</div>
                </div>
                <div class="summary-item">
                    <div class="summary-number">{data['metadata']['survey_columns']}</div>
                    <div>Perguntas da Pesquisa</div>
                </div>
                <div class="summary-item">
                    <div class="summary-number">{data['metadata']['total_columns']}</div>
                    <div>Colunas Totais</div>
                </div>
                <div class="summary-item">
                    <div class="summary-number">{len([col for col, stats in data['statistics'].items() if stats.get('chart_type') == 'categorical'])}</div>
                    <div>Perguntas Categóricas</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Análise Detalhada por Pergunta</h2>
            <table class="stats-table">
                <thead>
                    <tr>
                        <th>Pergunta</th>
                        <th>Tipo</th>
                        <th>Total Respostas</th>
                        <th>Valores Únicos</th>
                        <th>Dados Faltantes</th>
                        <th>Taxa de Completude</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add table rows for each survey question
    for col, stats in data['statistics'].items():
        completion_rate = (stats['total_responses'] / data['metadata']['total_rows']) * 100
        html_report += f"""
                    <tr>
                        <td>{col}</td>
                        <td>{stats['chart_type'].title()}</td>
                        <td>{stats['total_responses']:,}</td>
                        <td>{stats['unique_values']:,}</td>
                        <td>{stats['missing_values']:,}</td>
                        <td>{completion_rate:.1f}%</td>
                    </tr>
        """
    
    html_report += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>📊 Visualizações Detalhadas por Pergunta</h2>
    """
    
    # Add integrated charts section
    for col, stats in data['statistics'].items():
        chart_type = stats.get('chart_type', 'unknown')
        
        # Detect if this is a multiple choice question for display purposes
        df = pd.read_excel(data['metadata']['file_path'])
        col_data = df[col].dropna() if col in df.columns else pd.Series()
        is_multiple_choice_display = detect_multiple_choice_question(col_data)
        
        # Determine display type
        display_type = "Múltipla Seleção" if is_multiple_choice_display else chart_type.title()
        
        html_report += f"""
            <div class="question-analysis">
                <div class="question-title">📋 {col}</div>
                <div class="stats-summary">
                    <strong>Tipo:</strong> {display_type} | 
                    <strong>Respostas:</strong> {stats['total_responses']:,} | 
                    <strong>Valores únicos:</strong> {stats['unique_values']:,} | 
                    <strong>Taxa de completude:</strong> {(stats['total_responses'] / data['metadata']['total_rows']) * 100:.1f}%
                </div>
        """
        
        # Check if this column has a chart (categorical or multiple choice)
        if col in charts_html:
            # Display chart for any type of data that has a chart
            html_report += f"""
                <div class="chart-container">
                    {charts_html[col]}
                </div>
            """
        elif chart_type == 'textual' and col in text_data:
            # Display text responses in expandable dropdown
            text_info = text_data[col]
            html_report += f"""
                <div class="text-responses">
                    <div class="responses-dropdown">
                        <details>
                            <summary>Ver todas as {text_info['total_unique']} respostas únicas</summary>
                            <div class="responses-grid">
            """
            
            for response, count in text_info['responses']:
                html_report += f"""
                                <div class="response-item">
                                    <div class="response-text">{response}</div>
                                    <div class="response-count">{count}x</div>
                                </div>
                """
            
            if text_info['has_more']:
                html_report += """
                                <div class="response-item" style="font-style: italic; color: #666;">
                                    <div class="response-text">... e mais respostas</div>
                                    <div class="response-count">—</div>
                                </div>
                """
            
            html_report += """
                            </div>
                        </details>
                    </div>
                </div>
            """
        
        html_report += """
            </div>
        """
    
    html_report += """
        </div>
        
        <div class="section">
            <h2>💡 Insights Principais</h2>
    """
    
    # Generate insights based on the data
    categorical_questions = [col for col, stats in data['statistics'].items() if stats.get('chart_type') == 'categorical']
    textual_questions = [col for col, stats in data['statistics'].items() if stats.get('chart_type') == 'textual']
    
    # Low completion questions
    low_completion = [col for col, stats in data['statistics'].items() 
                     if (stats['total_responses'] / data['metadata']['total_rows']) < 0.5]
    
    html_report += f"""
            <div class="insight">
                <strong>📋 Distribuição por Tipo de Pergunta:</strong>
                <ul>
                    <li><strong>{len(categorical_questions)} perguntas categóricas</strong> (múltipla escolha, escalas)</li>
                    <li><strong>{len(textual_questions)} perguntas textuais</strong> (respostas abertas)</li>
                </ul>
            </div>
    """
    
    if low_completion:
        html_report += f"""
            <div class="highlight">
                <strong>⚠️ Atenção - Baixa Taxa de Completude:</strong>
                <ul>
        """
        for col in low_completion:
            completion_rate = (data['statistics'][col]['total_responses'] / data['metadata']['total_rows']) * 100
            html_report += f"<li>{col}: {completion_rate:.1f}% de completude</li>"
        html_report += """
                </ul>
                <p><em>Recomendação: Revisar formulário para melhorar a experiência do usuário.</em></p>
            </div>
        """
    
    # Most engaging questions
    high_completion = [col for col, stats in data['statistics'].items() 
                      if (stats['total_responses'] / data['metadata']['total_rows']) > 0.95]
    
    if high_completion:
        html_report += f"""
            <div class="insight">
                <strong>✅ Perguntas com Alta Engajamento:</strong>
                <ul>
        """
        for col in high_completion:
            completion_rate = (data['statistics'][col]['total_responses'] / data['metadata']['total_rows']) * 100
            html_report += f"<li>{col}: {completion_rate:.1f}% de completude</li>"
        html_report += """
                </ul>
                <p><em>Estas perguntas tiveram excelente taxa de resposta.</em></p>
            </div>
        """
    
    html_report += """
        </div>
        
        <div class="section">
            <h2>🎯 Recomendações</h2>
            <div class="highlight">
                <h3>Próximas Ações Sugeridas:</h3>
                <ol>
                    <li><strong>Análise Aprofundada:</strong> Revisar as respostas textuais para identificar padrões e temas recorrentes</li>
                    <li><strong>Segmentação:</strong> Analisar respostas por grupos demográficos ou comportamentais</li>
                    <li><strong>Melhoria do Formulário:</strong> Otimizar perguntas com baixa taxa de completude</li>
                    <li><strong>Dashboard Interativo:</strong> Usar o dashboard HTML para exploração detalhada dos dados</li>
                    <li><strong>Monitoramento:</strong> Implementar coleta contínua para acompanhar tendências</li>
                </ol>
            </div>
        </div>
        
        <div class="section">
            <h2>📁 Arquivos Gerados</h2>
            <ul>
                <li><strong>dashboard.html:</strong> Dashboard interativo com visualizações</li>
                <li><strong>analysis_results.json:</strong> Dados estruturados para análises adicionais</li>
                <li><strong>charts/:</strong> Gráficos individuais por pergunta</li>
            </ul>
        </div>
        
        <div style="margin-top: 50px; text-align: center; color: #666; border-top: 1px solid #eee; padding-top: 20px;">
            <p>🤖 Relatório gerado automaticamente pelo <strong>Automagik Hive Survey Analyzer</strong></p>
            <p>Para dúvidas ou suporte técnico, consulte a documentação do projeto</p>
        </div>
        
        <div class="no-print" style="margin-top: 30px; text-align: center;">
            <p><em>Para gerar PDF: Use Ctrl+P (ou Cmd+P) e selecione "Salvar como PDF"</em></p>
        </div>
    </body>
    </html>
    """
    
    # Save the report
    report_file = latest_analysis / "relatorio_executivo.html"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"✅ Relatório executivo criado: {report_file}")
    print("💡 Para gerar PDF: Abra o arquivo HTML e use Ctrl+P > Salvar como PDF")
    
    return str(report_file)

if __name__ == "__main__":
    create_pdf_report()