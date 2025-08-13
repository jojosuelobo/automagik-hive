#!/usr/bin/env python3
"""
Simple Survey Data Analyzer - No AI Required
============================================

Direct Excel processing without LLM to avoid token limits.
Creates a basic dashboard from survey data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
from pathlib import Path
import json
from datetime import datetime
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def analyze_survey_data(file_path: str):
    """Analyze survey data without AI dependencies"""
    
    print("🔬 ANALISANDO DADOS DE PESQUISA (SEM IA)")
    print("=" * 50)
    print(f"📁 Arquivo: {file_path}")
    print(f"🕐 Início: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Load Excel file
    try:
        df = pd.read_excel(file_path)
        print(f"✅ Dados carregados: {len(df)} linhas, {len(df.columns)} colunas")
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {e}")
        return
    
    # Filter survey columns (pesquisa pattern)
    survey_cols = [col for col in df.columns if 'pesquisa' in col.lower()]
    
    if not survey_cols:
        print("❌ Nenhuma coluna de pesquisa encontrada")
        return
    
    print(f"🔍 Encontradas {len(survey_cols)} colunas de pesquisa:")
    for i, col in enumerate(survey_cols, 1):
        print(f"   {i}. {col}")
    print()
    
    # Create output directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(f"data/surveys/outputs/analysis_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    charts_dir = output_dir / "charts"
    charts_dir.mkdir(exist_ok=True)
    
    # Filter dataset to survey columns only
    survey_data = df[survey_cols].copy()
    
    # Basic statistics
    print("📊 ESTATÍSTICAS BÁSICAS:")
    print("-" * 30)
    
    stats_summary = {}
    chart_info = []
    
    for col in survey_cols:
        print(f"\n🔹 {col}:")
        
        # Remove null values for analysis
        col_data = survey_data[col].dropna()
        
        if len(col_data) == 0:
            print("   - Sem dados válidos")
            continue
            
        # Determine data type and create appropriate chart
        unique_values = col_data.nunique()
        total_values = len(col_data)
        
        print(f"   - Total de respostas: {total_values}")
        print(f"   - Valores únicos: {unique_values}")
        print(f"   - Dados faltantes: {survey_data[col].isna().sum()}")
        
        # Store stats
        stats_summary[col] = {
            "total_responses": int(total_values),
            "unique_values": int(unique_values),
            "missing_values": int(survey_data[col].isna().sum()),
            "data_type": str(col_data.dtype)
        }
        
        # Create visualizations based on data characteristics
        if unique_values <= 20:  # Categorical data
            print("   - Tipo: Categórico")
            stats_summary[col]["chart_type"] = "categorical"
            
            # Value counts
            value_counts = col_data.value_counts()
            print(f"   - Valores mais comuns: {dict(value_counts.head(3))}")
            
            # Create bar chart
            fig = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title=f"Distribuição - {col}",
                labels={'x': 'Respostas', 'y': 'Frequência'},
                color=value_counts.values,
                color_continuous_scale='viridis'
            )
            fig.update_layout(
                title_font_size=16,
                xaxis_title_font_size=14,
                yaxis_title_font_size=14
            )
            
            chart_file = charts_dir / f"chart_{col.replace('/', '_')}.html"
            fig.write_html(chart_file)
            chart_info.append({
                "column": col,
                "type": "categorical",
                "file": chart_file.name,
                "description": f"Distribuição de respostas para {col}"
            })
            
        elif pd.api.types.is_numeric_dtype(col_data):  # Numerical data
            print("   - Tipo: Numérico")
            stats_summary[col]["chart_type"] = "numerical"
            
            # Basic stats
            print(f"   - Média: {col_data.mean():.2f}")
            print(f"   - Mediana: {col_data.median():.2f}")
            print(f"   - Min/Max: {col_data.min():.2f} / {col_data.max():.2f}")
            
            stats_summary[col].update({
                "mean": float(col_data.mean()),
                "median": float(col_data.median()),
                "min": float(col_data.min()),
                "max": float(col_data.max()),
                "std": float(col_data.std())
            })
            
            # Create histogram
            fig = px.histogram(
                x=col_data,
                title=f"Distribuição - {col}",
                labels={'x': col, 'y': 'Frequência'},
                nbins=20
            )
            fig.update_layout(
                title_font_size=16,
                xaxis_title_font_size=14,
                yaxis_title_font_size=14
            )
            
            chart_file = charts_dir / f"chart_{col.replace('/', '_')}.html"
            fig.write_html(chart_file)
            chart_info.append({
                "column": col,
                "type": "numerical",
                "file": chart_file.name,
                "description": f"Histograma de {col}"
            })
            
        else:  # Text data
            print("   - Tipo: Textual")
            stats_summary[col]["chart_type"] = "textual"
            
            # Most common words/phrases
            value_counts = col_data.value_counts()
            print(f"   - Respostas mais comuns: {dict(value_counts.head(3))}")
            
            # Create word cloud style chart
            if len(value_counts) > 1:
                fig = px.bar(
                    x=value_counts.head(10).values,
                    y=value_counts.head(10).index,
                    orientation='h',
                    title=f"Top 10 Respostas - {col}",
                    labels={'x': 'Frequência', 'y': 'Resposta'}
                )
                fig.update_layout(
                    title_font_size=16,
                    xaxis_title_font_size=14,
                    yaxis_title_font_size=14,
                    height=500
                )
                
                chart_file = charts_dir / f"chart_{col.replace('/', '_')}.html"
                fig.write_html(chart_file)
                chart_info.append({
                    "column": col,
                    "type": "textual",
                    "file": chart_file.name,
                    "description": f"Respostas mais frequentes para {col}"
                })
    
    # Create overview dashboard
    print("\n📊 CRIANDO DASHBOARD...")
    
    # Summary statistics
    total_responses = len(df)
    total_survey_cols = len(survey_cols)
    avg_completion = survey_data.count().mean()
    
    # Create main dashboard
    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard de Análise de Pesquisa</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
            .chart-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
            .chart-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .chart-title {{ font-size: 1.2em; font-weight: bold; margin-bottom: 10px; color: #333; }}
            iframe {{ width: 100%; height: 400px; border: none; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Dashboard de Análise de Pesquisa</h1>
            <p>Análise automática gerada em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
            <p>Arquivo: {file_path}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_responses:,}</div>
                <div>Total de Respostas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_survey_cols}</div>
                <div>Perguntas da Pesquisa</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{avg_completion:.1f}</div>
                <div>Média de Respostas por Pergunta</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{(avg_completion/total_responses*100):.1f}%</div>
                <div>Taxa de Completude</div>
            </div>
        </div>
        
        <h2>📈 Visualizações por Pergunta</h2>
        <div class="chart-grid">
    """
    
    # Add charts to dashboard
    for chart in chart_info:
        dashboard_html += f"""
            <div class="chart-card">
                <div class="chart-title">{chart['description']}</div>
                <iframe src="charts/{chart['file']}"></iframe>
            </div>
        """
    
    dashboard_html += """
        </div>
        
        <div style="margin-top: 40px; text-align: center; color: #666;">
            <p>🤖 Dashboard gerado automaticamente pelo Automagik Hive Survey Analyzer</p>
        </div>
    </body>
    </html>
    """
    
    # Save dashboard
    dashboard_file = output_dir / "dashboard.html"
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    # Save analysis results as JSON
    analysis_results = {
        "metadata": {
            "file_path": file_path,
            "analysis_date": datetime.now().isoformat(),
            "total_rows": total_responses,
            "total_columns": len(df.columns),
            "survey_columns": len(survey_cols)
        },
        "survey_columns": survey_cols,
        "statistics": stats_summary,
        "charts": chart_info
    }
    
    results_file = output_dir / "analysis_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print("✅ Dashboard criado com sucesso!")
    print("=" * 50)
    print(f"📊 Dashboard: {dashboard_file}")
    print(f"📄 Resultados JSON: {results_file}")
    print(f"📈 Gráficos: {charts_dir}")
    print()
    print("🎯 PRÓXIMOS PASSOS:")
    print("1. Abra o dashboard.html no navegador")
    print("2. Revise os gráficos individuais em charts/")
    print("3. Use os dados JSON para análises adicionais")
    print()
    
    return str(dashboard_file)

if __name__ == "__main__":
    file_path = "data/surveys/raw/bruto.xlsx"
    analyze_survey_data(file_path)