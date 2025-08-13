#!/usr/bin/env python3
"""
Teste do HTML Report Generator Agent
==================================

Teste específico para validar o agente de geração de relatórios HTML
"""

import json
import os
import sys
from pathlib import Path
import webbrowser

def load_survey_analysis_data():
    """Carrega os dados da análise de pesquisa"""
    if os.path.exists("resultado_survey_analysis.json"):
        with open("resultado_survey_analysis.json", "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print("❌ Arquivo resultado_survey_analysis.json não encontrado")
        print("   Execute primeiro: python test_survey_analysis.py")
        return None

def load_excel_data():
    """Carrega os dados originais do Excel"""
    if os.path.exists("resultado_teste_simples.json"):
        with open("resultado_teste_simples.json", "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return None

def test_html_report_generator():
    """Testa o agente gerador de relatórios HTML"""
    
    print("📄 Iniciando teste do HTML Report Generator Agent")
    
    # Carregar dados da análise de pesquisa
    survey_analysis = load_survey_analysis_data()
    if not survey_analysis:
        return
    
    # Carregar dados originais do Excel
    excel_data = load_excel_data()
    
    print("✅ Dados de análise de pesquisa carregados com sucesso")
    
    try:
        # Importar funções do agente usando importlib
        import importlib.util
        
        current_dir = Path(__file__).parent
        agent_path = current_dir / "ai" / "agents" / "html-report-generator-agent" / "agent.py"
        
        spec = importlib.util.spec_from_file_location("html_agent", agent_path)
        html_agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(html_agent)
        
        # Usar as funções do módulo carregado
        generate_html_report = html_agent.generate_html_report
        save_html_report = html_agent.save_html_report
        
        # Extrair dados necessários
        survey_data = survey_analysis.get("survey_data", {})
        file_info = excel_data.get("file_info", {}) if excel_data else {}
        
        print(f"📊 Dados da pesquisa: {len(survey_data.get('survey_questions', {}))} perguntas")
        
        # Passo 1: Gerar HTML
        print("\n🔧 Passo 1: Gerando relatório HTML...")
        html_content = generate_html_report(survey_data, file_info)
        
        html_size_kb = len(html_content) / 1024
        print(f"   ✅ HTML gerado: {html_size_kb:.1f} KB")
        
        # Passo 2: Salvar arquivo
        print("\n💾 Passo 2: Salvando arquivo HTML...")
        report_filename = save_html_report(html_content, "relatorio_teste.html")
        
        file_size = os.path.getsize(report_filename) / 1024
        print(f"   ✅ Arquivo salvo: {report_filename} ({file_size:.1f} KB)")
        
        # Passo 3: Validar conteúdo
        print("\n🔍 Passo 3: Validando conteúdo HTML...")
        
        # Verificar se contém elementos esperados
        validations = {
            "HTML structure": "<!DOCTYPE html>" in html_content,
            "Chart.js library": "chart.js" in html_content,
            "CSS styling": "<style>" in html_content,
            "Survey data": "pesquisa" in html_content.lower(),
            "Interactive charts": "new Chart(" in html_content,
            "Responsive design": "viewport" in html_content,
            "Portuguese content": "Relatório de Pesquisa" in html_content
        }
        
        for check, passed in validations.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
        
        all_valid = all(validations.values())
        
        # Exibir estatísticas do relatório
        print("\n" + "="*60)
        print("📋 ESTATÍSTICAS DO RELATÓRIO HTML")
        print("="*60)
        
        print(f"\n📄 Arquivo Gerado:")
        print(f"   Nome: {report_filename}")
        print(f"   Tamanho: {file_size:.1f} KB")
        print(f"   Linhas de código: {html_content.count(chr(10))}")
        
        print(f"\n📊 Conteúdo:")
        questions_count = len(survey_data.get("survey_questions", {}))
        charts_count = html_content.count("new Chart(")
        print(f"   Perguntas processadas: {questions_count}")
        print(f"   Gráficos gerados: {charts_count}")
        print(f"   Seções incluídas: Header, Executive Summary, Overview, Charts, Insights")
        
        print(f"\n✅ Validação:")
        passed_checks = sum(validations.values())
        total_checks = len(validations)
        print(f"   Verificações passou: {passed_checks}/{total_checks}")
        print(f"   Status: {'✅ VÁLIDO' if all_valid else '⚠️ PROBLEMAS ENCONTRADOS'}")
        
        # Tentar abrir no navegador
        if all_valid:
            print(f"\n🌐 Tentando abrir relatório no navegador...")
            try:
                # Obter caminho absoluto
                abs_path = os.path.abspath(report_filename)
                file_url = f"file://{abs_path}"
                
                # Abrir no navegador padrão
                webbrowser.open(file_url)
                print(f"   ✅ Relatório aberto no navegador")
                print(f"   🔗 URL: {file_url}")
                
            except Exception as e:
                print(f"   ⚠️ Não foi possível abrir automaticamente: {str(e)}")
                print(f"   💡 Abra manualmente: {os.path.abspath(report_filename)}")
        
        print(f"\n🎉 Teste do HTML Report Generator concluído!")
        
        # Retornar informações do teste
        return {
            "html_generated": True,
            "filename": report_filename,
            "size_kb": file_size,
            "validations_passed": passed_checks,
            "total_validations": total_checks,
            "all_valid": all_valid,
            "questions_processed": questions_count,
            "charts_generated": charts_count
        }
        
    except Exception as e:
        print(f"\n❌ Erro durante geração do relatório HTML:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_workflow_integration():
    """Testa a integração completa do workflow"""
    print("\n" + "="*60)
    print("🔄 TESTE DE INTEGRAÇÃO DO WORKFLOW COMPLETO")
    print("="*60)
    
    print("\n1. ✅ Excel Processing - Separação de dados")
    print("2. ✅ Survey Analysis - Análise de pesquisa") 
    print("3. 🔄 HTML Report Generation - Geração de relatório")
    
    result = test_html_report_generator()
    
    if result and result.get("all_valid"):
        print("\n🎉 WORKFLOW COMPLETO EXECUTADO COM SUCESSO!")
        print("✅ Todas as etapas concluídas:")
        print("   📊 Dados do Excel separados e validados")
        print("   📋 Dados de pesquisa analisados")
        print("   📄 Relatório HTML profissional gerado")
        print("   🌐 Pronto para apresentação aos stakeholders")
    else:
        print("\n⚠️ Workflow parcialmente concluído")
        print("   Verifique os logs acima para detalhes")

if __name__ == "__main__":
    print("=" * 60)
    print("🎯 TESTE DO HTML REPORT GENERATOR AGENT")
    print("=" * 60)
    
    test_workflow_integration() 