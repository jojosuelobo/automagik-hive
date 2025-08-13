#!/usr/bin/env python3
"""
Teste do Survey Data Analyzer Agent
=================================

Teste específico para validar o agente de análise de dados de pesquisa
"""

import json
import os
import sys
from pathlib import Path

# Importar dependências
import pandas as pd
from datetime import datetime

# Carregar dados do resultado anterior
def load_previous_excel_data():
    """Carrega os dados do Excel processado anteriormente"""
    if os.path.exists("resultado_teste_simples.json"):
        with open("resultado_teste_simples.json", "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print("❌ Arquivo resultado_teste_simples.json não encontrado")
        print("   Execute primeiro: python test_excel_simple.py")
        return None


def test_survey_analyzer():
    """Testa o agente analisador de dados de pesquisa"""
    
    print("🔍 Iniciando teste do Survey Data Analyzer Agent")
    
    # Carregar dados do Excel processado
    excel_data = load_previous_excel_data()
    if not excel_data:
        return
    
    print("✅ Dados do Excel carregados com sucesso")
    
    try:
        # Importar funções do agente usando importlib
        import importlib.util
        
        current_dir = Path(__file__).parent
        agent_path = current_dir / "ai" / "agents" / "survey-data-analyzer-agent" / "agent.py"
        
        spec = importlib.util.spec_from_file_location("survey_agent", agent_path)
        survey_agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(survey_agent)
        
        # Usar as funções do módulo carregado
        identify_survey_columns = survey_agent.identify_survey_columns
        extract_survey_responses = survey_agent.extract_survey_responses
        generate_survey_summary = survey_agent.generate_survey_summary
        
        separated_data = excel_data.get("separated_data", {})
        
        # Passo 1: Identificar colunas de pesquisa
        print("\n🔍 Passo 1: Identificando colunas de pesquisa...")
        survey_columns = identify_survey_columns(separated_data)
        
        print(f"   📊 Colunas de pesquisa encontradas: {len(survey_columns)}")
        for i, col in enumerate(survey_columns, 1):
            print(f"   {i}. {col}")
        
        if not survey_columns:
            print("❌ Nenhuma coluna de pesquisa encontrada")
            return
        
        # Passo 2: Extrair respostas de pesquisa
        print(f"\n📋 Passo 2: Extraindo respostas das {len(survey_columns)} colunas...")
        survey_data = extract_survey_responses(separated_data, survey_columns)
        
        questions = survey_data.get("survey_questions", {})
        print(f"   ✅ Dados extraídos para {len(questions)} perguntas")
        
        # Passo 3: Gerar resumo
        print(f"\n📈 Passo 3: Gerando resumo da pesquisa...")
        survey_summary = generate_survey_summary(survey_data)
        
        # Exibir resultados detalhados
        print("\n" + "="*60)
        print("📊 RESULTADOS DA ANÁLISE DE PESQUISA")
        print("="*60)
        
        # Overview
        overview = survey_summary.get("overview", {})
        print(f"\n📈 Visão Geral:")
        print(f"   Total de perguntas: {overview.get('total_questions', 0)}")
        print(f"   Total de respondentes: {overview.get('total_possible_responses', 0)}")
        print(f"   Taxa média de resposta: {overview.get('avg_response_rate', 0):.1f}%")
        
        # Tipos de perguntas
        question_types = overview.get("question_types", {})
        print(f"\n📝 Tipos de Perguntas:")
        for q_type, count in question_types.items():
            print(f"   {q_type}: {count} pergunta(s)")
        
        # Detalhes por pergunta (primeiras 3)
        print(f"\n🔍 Detalhes das Perguntas (primeiras 3):")
        
        for i, (q_name, q_data) in enumerate(list(questions.items())[:3]):
            print(f"\n   📋 Pergunta {i+1}: {q_name}")
            print(f"      Tipo: {q_data.get('question_type', 'unknown')}")
            print(f"      Respostas válidas: {q_data.get('total_responses', 0)}")
            print(f"      Taxa de resposta: {q_data.get('response_rate', 0):.1f}%")
            print(f"      Respostas únicas: {q_data.get('unique_responses', 0)}")
            
            # Top 3 respostas mais frequentes
            freq_analysis = q_data.get('frequency_analysis', {})
            if freq_analysis:
                print(f"      📊 Top 3 respostas:")
                sorted_responses = sorted(freq_analysis.items(), 
                                       key=lambda x: x[1]['count'], reverse=True)
                
                for j, (response, stats) in enumerate(sorted_responses[:3]):
                    count = stats['count']
                    percentage = stats['percentage']
                    print(f"         {j+1}. '{response}': {count} ({percentage}%)")
            
            # Sugestões de gráficos
            chart_suggestions = q_data.get('chart_suggestions', [])
            if chart_suggestions:
                print(f"      📈 Gráfico recomendado: {chart_suggestions[0]['type']}")
                print(f"         Motivo: {chart_suggestions[0]['reason']}")
        
        # Recomendações de visualização
        viz_recommendations = survey_summary.get("visualization_recommendations", [])
        if viz_recommendations:
            print(f"\n🎨 Recomendações de Visualização:")
            for i, rec in enumerate(viz_recommendations[:5], 1):
                print(f"   {i}. {rec['question']}")
                print(f"      Gráfico: {rec['recommended_chart']}")
                print(f"      Motivo: {rec['reason']}")
        
        # Salvar resultado completo
        result_data = {
            "survey_columns": survey_columns,
            "survey_data": survey_data,
            "survey_summary": survey_summary,
            "processed_at": datetime.now().isoformat()
        }
        
        with open("resultado_survey_analysis.json", "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Resultado completo salvo em: resultado_survey_analysis.json")
        print(f"🎉 Análise de pesquisa concluída com sucesso!")
        
        # Preparar dados para próximo agente (geração de charts)
        chart_ready_data = prepare_chart_data(survey_data)
        
        with open("dados_para_charts.json", "w", encoding="utf-8") as f:
            json.dump(chart_ready_data, f, ensure_ascii=False, indent=2)
        
        print(f"📊 Dados preparados para geração de charts: dados_para_charts.json")
        
        return result_data
        
    except Exception as e:
        print(f"\n❌ Erro durante análise de pesquisa:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


def prepare_chart_data(survey_data):
    """Prepara dados específicos para geração de charts"""
    
    chart_data = {
        "charts_to_generate": [],
        "prepared_at": datetime.now().isoformat(),
        "total_charts": 0
    }
    
    questions = survey_data.get("survey_questions", {})
    
    for q_name, q_data in questions.items():
        if q_data.get("total_responses", 0) > 0:
            
            # Preparar dados para cada pergunta
            chart_info = {
                "question_id": q_name,
                "question_name": q_name,
                "question_type": q_data.get("question_type", "unknown"),
                "total_responses": q_data.get("total_responses", 0),
                "chart_type_recommended": q_data.get("chart_suggestions", [{}])[0].get("type", "bar_chart"),
                "data_for_chart": q_data.get("frequency_analysis", {}),
                "chart_title": f"Respostas: {q_name}",
                "ready_for_generation": True
            }
            
            chart_data["charts_to_generate"].append(chart_info)
    
    chart_data["total_charts"] = len(chart_data["charts_to_generate"])
    
    return chart_data


if __name__ == "__main__":
    print("=" * 60)
    print("🎯 TESTE DO SURVEY DATA ANALYZER AGENT")
    print("=" * 60)
    
    test_survey_analyzer() 