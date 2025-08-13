#!/usr/bin/env python3
"""
Gerador de Relatório PDF para Análise de Pesquisa
================================================
"""

import json
from pathlib import Path
from datetime import datetime

def create_pdf_report():
    """Create a simple PDF report from the analysis"""
    
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
    
    # Create simple HTML report (which can be printed to PDF)
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
            @media print {{ 
                body {{ margin: 20px; }} 
                .no-print {{ display: none; }}
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