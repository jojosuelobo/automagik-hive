#!/usr/bin/env python3
"""
Execução direta do workflow de análise de pesquisa
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.insert(0, os.getcwd())

try:
    from ai.workflows.survey_data_visualization_workflow.workflow import get_survey_data_visualization_workflow
    print("✅ Workflow importado com sucesso!")
except ImportError as e:
    print(f"❌ Erro na importação: {e}")
    print("🔧 Tentando importação alternativa...")
    
    # Tentar importação direta dos módulos
    import importlib.util
    
    workflow_path = Path("ai/workflows/survey-data-visualization-workflow/workflow.py")
    if workflow_path.exists():
        spec = importlib.util.spec_from_file_location("workflow_module", workflow_path)
        workflow_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(workflow_module)
        get_survey_data_visualization_workflow = workflow_module.get_survey_data_visualization_workflow
        print("✅ Importação alternativa bem-sucedida!")
    else:
        print(f"❌ Arquivo não encontrado: {workflow_path}")
        sys.exit(1)


async def run_survey_analysis():
    """Executar análise de pesquisa"""
    
    file_path = "data/surveys/raw/bruto.xlsx"
    
    # Verificar se arquivo existe
    if not Path(file_path).exists():
        print(f"❌ Arquivo não encontrado: {file_path}")
        return
    
    print("🔬 INICIANDO ANÁLISE DE PESQUISA")
    print("=" * 50)
    print(f"📁 Arquivo: {file_path}")
    print(f"🕐 Início: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    try:
        # Criar workflow com SQLite para execução local
        print("🔧 Criando instância do workflow...")
        
        from agno.storage.sqlite import SqliteStorage
        
        workflow = get_survey_data_visualization_workflow(
            session_id=f"bruto-analysis-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            storage=SqliteStorage(
                table_name="survey_workflows",
                db_file="data/workflows.db"
            )
        )
        print("✅ Workflow criado com sucesso!")
        
        # Preparar mensagem de análise
        analysis_message = f"""
        Por favor, analise os dados de pesquisa do arquivo XLSX: {file_path}
        
        Instruções específicas:
        1. Extraia todas as colunas que contenham 'pesquisa' no nome
        2. Classifique automaticamente os tipos de dados (categórico, numérico, temporal, textual)
        3. Gere visualizações profissionais apropriadas para cada tipo
        4. Compile um dashboard interativo com insights executivos
        5. Crie relatório PDF com recomendações de negócio
        
        Estrutura esperada:
        - Colunas pesquisa300625_screen0 até pesquisa300625_screen9
        - Análise completa com estatísticas descritivas
        - Insights de negócio e recomendações acionáveis
        
        Gere análise abrangente para stakeholders.
        """
        
        print("🚀 Executando workflow...")
        print("   (Isso pode levar alguns minutos)")
        print()
        
        # Executar workflow
        result = await workflow.arun(message=analysis_message)
        
        print("🎉 ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("=" * 50)
        print(f"✅ Processamento finalizado às {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        # Mostrar resultado
        if hasattr(result, 'content'):
            print("📊 RESUMO DOS RESULTADOS:")
            print("-" * 30)
            content = str(result.content)
            if len(content) > 1000:
                print(content[:1000] + "...")
                print(f"\n[Resultado completo: {len(content)} caracteres]")
            else:
                print(content)
        else:
            print("📊 Resultado:", result)
        
        # Verificar arquivos de saída
        print("\n📁 ARQUIVOS GERADOS:")
        output_dir = Path("data/surveys/outputs")
        if output_dir.exists():
            for item in output_dir.iterdir():
                if item.is_dir() and "analysis_" in item.name:
                    print(f"   📂 {item.name}")
                    for file in item.iterdir():
                        if file.is_file():
                            print(f"      📄 {file.name} ({file.stat().st_size} bytes)")
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Abra o dashboard.html no navegador")
        print("2. Revise o relatório PDF gerado")
        print("3. Compartilhe os insights com stakeholders")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE A EXECUÇÃO:")
        print(f"   {str(e)}")
        print(f"\n🐛 Tipo do erro: {type(e).__name__}")
        
        # Stack trace para debug
        import traceback
        print("\n📋 Stack trace completo:")
        traceback.print_exc()


if __name__ == "__main__":
    print("🤖 Executando análise de pesquisa - bruto.xlsx")
    asyncio.run(run_survey_analysis())