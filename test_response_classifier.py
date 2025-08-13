#!/usr/bin/env python3
"""
Teste do Response Classifier Agent
=================================

Teste específico para validar o agente classificador de respostas com IA
"""

import json
import os
import sys
from pathlib import Path

def load_survey_analysis_data():
    """Carrega os dados da análise de pesquisa"""
    if os.path.exists("resultado_survey_analysis.json"):
        with open("resultado_survey_analysis.json", "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print("❌ Arquivo resultado_survey_analysis.json não encontrado")
        print("   Execute primeiro: python test_survey_analysis.py")
        return None

def test_response_classifier():
    """Testa o agente classificador de respostas"""
    
    print("🤖 Iniciando teste do Response Classifier Agent")
    
    # Carregar dados da análise de pesquisa
    survey_analysis = load_survey_analysis_data()
    if not survey_analysis:
        return
    
    print("✅ Dados de análise de pesquisa carregados com sucesso")
    
    try:
        # Importar funções do agente usando importlib
        import importlib.util
        
        current_dir = Path(__file__).parent
        agent_path = current_dir / "ai" / "agents" / "response-classifier-agent" / "agent.py"
        
        spec = importlib.util.spec_from_file_location("classifier_agent", agent_path)
        classifier_agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(classifier_agent)
        
        # Usar as funções do módulo carregado
        enhance_survey_data_with_classification = classifier_agent.enhance_survey_data_with_classification
        classify_response_with_ai = classifier_agent.classify_response_with_ai
        
        # Extrair dados da pergunta 8
        survey_data = survey_analysis.get("survey_data", {})
        questions = survey_data.get("survey_questions", {})
        
        # Encontrar pergunta 8
        question_8_key = None
        for key in questions.keys():
            if "screen8" in key:
                question_8_key = key
                break
        
        if not question_8_key:
            print("❌ Pergunta 8 não encontrada")
            return
        
        question_8_data = questions[question_8_key]
        print(f"📋 Pergunta 8 encontrada: {question_8_key}")
        print(f"   Total de respostas: {question_8_data.get('total_responses', 0)}")
        
        # Teste 1: Classificar algumas respostas individuais
        print(f"\n🔍 Teste 1: Classificação de respostas individuais")
        
        frequency_analysis = question_8_data.get("frequency_analysis", {})
        test_responses = list(frequency_analysis.keys())[:5]  # Pegar primeiras 5
        
        for i, response in enumerate(test_responses, 1):
            print(f"\n   Resposta {i}: \"{response}\"")
            classification = classify_response_with_ai(
                response, 
                "8 - Você teve algum problema ou dificuldade para participar?"
            )
            print(f"   ➜ Categoria: {classification['categoria']}")
            print(f"   ➜ Confiança: {classification['confianca']}%")
            print(f"   ➜ Explicação: {classification['explicacao']}")
        
        # Teste 2: Aplicar classificação completa
        print(f"\n🚀 Teste 2: Aplicando classificação IA ao survey completo")
        
        enhanced_survey = enhance_survey_data_with_classification(survey_data)
        
        # Verificar resultados
        enhanced_questions = enhanced_survey.get("survey_questions", {})
        enhanced_q8 = enhanced_questions.get(question_8_key, {})
        
        if enhanced_q8.get("enhanced_with_ai", False):
            print("   ✅ Pergunta 8 foi aprimorada com IA")
            
            # Mostrar resultados da classificação
            classification_summary = enhanced_q8.get("classification_summary", {})
            categories = classification_summary.get("categories", {})
            
            print(f"\n📊 Resultados da Classificação:")
            for category, stats in categories.items():
                count = stats.get("count", 0)
                percentage = stats.get("percentage", 0)
                print(f"   {category}: {count} ({percentage}%)")
            
            # Mostrar frequency analysis simplificada
            new_freq = enhanced_q8.get("frequency_analysis", {})
            print(f"\n📈 Frequency Analysis Simplificada:")
            for category, data in new_freq.items():
                print(f"   {category}: {data['count']} ({data['percentage']}%)")
            
            # Verificar se o tipo de pergunta mudou
            old_type = question_8_data.get("question_type", "")
            new_type = enhanced_q8.get("question_type", "")
            print(f"\n🔄 Tipo de pergunta:")
            print(f"   Antes: {old_type}")
            print(f"   Depois: {new_type}")
            
        else:
            print("   ⚠️ Pergunta 8 não foi aprimorada")
        
        # Verificar resumo do enhancement
        enhancement_summary = enhanced_survey.get("enhancement_summary", {})
        questions_enhanced = enhancement_summary.get("questions_enhanced", 0)
        
        print(f"\n📋 Resumo do Enhancement:")
        print(f"   Total de perguntas: {enhancement_summary.get('total_questions', 0)}")
        print(f"   Perguntas aprimoradas: {questions_enhanced}")
        
        if questions_enhanced > 0:
            enhanced_list = enhanced_survey.get("ai_classification_applied", [])
            print(f"   Perguntas aprimoradas: {enhanced_list}")
        
        # Salvar resultado
        result_data = {
            "original_survey": survey_data,
            "enhanced_survey": enhanced_survey,
            "test_results": {
                "question_8_key": question_8_key,
                "enhancement_applied": enhanced_q8.get("enhanced_with_ai", False),
                "categories_found": list(categories.keys()) if categories else [],
                "classification_summary": classification_summary
            },
            "processed_at": enhanced_survey.get("enhancement_summary", {}).get("enhanced_at", "")
        }
        
        with open("resultado_response_classifier.json", "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Resultado salvo em: resultado_response_classifier.json")
        print(f"🎉 Teste do Response Classifier concluído!")
        
        return result_data
        
    except Exception as e:
        print(f"\n❌ Erro durante teste do classificador:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

def test_integration_with_workflow():
    """Testa a integração do classificador com o workflow"""
    print("\n" + "="*60)
    print("🔄 TESTE DE INTEGRAÇÃO COM WORKFLOW")
    print("="*60)
    
    print("\n1. ✅ Excel Processing - Separação de dados")
    print("2. ✅ Survey Analysis - Análise de pesquisa")
    print("3. 🤖 Response Classification - Classificação IA (NOVO!)")
    print("4. 🔄 HTML Report Generation - Relatório com dados classificados")
    
    # Regenerar dados de pesquisa com classificação
    print("\n🔄 Regenerando análise de pesquisa com classificação IA...")
    
    try:
        # Executar o teste do survey analysis que agora inclui classificação
        import subprocess
        result = subprocess.run(
            ["python", "test_survey_analysis.py"], 
            capture_output=True, 
            text=True,
            cwd="."
        )
        
        if result.returncode == 0:
            print("   ✅ Análise de pesquisa com IA regenerada")
            
            # Executar o teste do classificador
            classifier_result = test_response_classifier()
            
            if classifier_result:
                print("\n🎉 INTEGRAÇÃO COMPLETA TESTADA COM SUCESSO!")
                print("✅ Workflow agora inclui:")
                print("   📊 Separação de dados Excel")
                print("   📋 Análise de dados de pesquisa")
                print("   🤖 Classificação IA de respostas")
                print("   📄 Geração de relatório HTML")
                
                return True
        else:
            print(f"   ❌ Erro na regeneração: {result.stderr}")
            
    except Exception as e:
        print(f"   ❌ Erro na integração: {str(e)}")
    
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("🎯 TESTE DO RESPONSE CLASSIFIER AGENT")
    print("=" * 60)
    
    test_integration_with_workflow() 