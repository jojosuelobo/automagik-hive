#!/usr/bin/env python3
"""
Teste do Excel Processing Workflow
================================

Script para testar o workflow com o arquivo bruta.xlsx
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Adicionar o diretório atual ao Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Importar os módulos diretamente
try:
    # Tentar importar o workflow diretamente
    sys.path.append(str(current_dir / "ai" / "workflows" / "excel-processing-workflow"))
    from workflow import get_excel_processing_workflow_workflow
    print("✅ Importação do workflow realizada com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar workflow: {e}")
    print("🔧 Tentando importação alternativa...")
    
    # Importar usando importlib
    import importlib.util
    workflow_path = current_dir / "ai" / "workflows" / "excel-processing-workflow" / "workflow.py"
    
    spec = importlib.util.spec_from_file_location("workflow", workflow_path)
    workflow_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(workflow_module)
    get_excel_processing_workflow_workflow = workflow_module.get_excel_processing_workflow_workflow
    print("✅ Importação alternativa realizada com sucesso")


async def testar_workflow():
    """Testa o workflow com o arquivo bruta.xlsx"""
    
    # Caminho para o arquivo Excel
    arquivo_excel = "ai/workflows/excel-processing-workflow/file/bruta.xlsx"
    arquivo_absoluto = os.path.abspath(arquivo_excel)
    
    print("🚀 Iniciando teste do Excel Processing Workflow")
    print(f"📁 Arquivo: {arquivo_absoluto}")
    
    # Verificar se arquivo existe
    if not os.path.exists(arquivo_absoluto):
        print(f"❌ Erro: Arquivo não encontrado: {arquivo_absoluto}")
        return
    
    # Obter informações básicas do arquivo
    file_size = os.path.getsize(arquivo_absoluto) / (1024 * 1024)  # MB
    print(f"💾 Tamanho do arquivo: {file_size:.2f} MB")
    
    try:
        # Criar instância do workflow
        print("\n🔧 Criando workflow...")
        workflow = get_excel_processing_workflow_workflow()
        
        # Executar o workflow
        print("⚡ Executando workflow...")
        resultado = await workflow.arun(message=f"file_path: {arquivo_absoluto}")
        
        # Parsear resultado
        dados_resultado = json.loads(resultado.content)
        
        # Exibir informações do primeiro passo (separação)
        if "file_info" in dados_resultado:
            file_info = dados_resultado["file_info"]
            print("\n✅ Passo 1 - Separação Excel:")
            print(f"   📊 Total de linhas: {file_info.get('total_rows', 'N/A')}")
            print(f"   📋 Total de colunas: {file_info.get('total_columns', 'N/A')}")
            print(f"   📝 Nome das colunas: {file_info.get('column_names', [])}")
        
        # Exibir informações de validação
        if "validation_report" in dados_resultado:
            validation = dados_resultado["validation_report"]
            summary = validation.get("summary", {})
            print(f"\n🔍 Relatório de Validação:")
            print(f"   ✅ Status: {'VÁLIDO' if validation.get('is_valid', False) else 'INVÁLIDO'}")
            print(f"   🔢 Colunas numéricas: {summary.get('numeric_columns', 0)}")
            print(f"   📝 Colunas de texto: {summary.get('text_columns', 0)}")
            print(f"   📅 Colunas de data: {summary.get('datetime_columns', 0)}")
            print(f"   ❌ Problemas: {summary.get('total_issues', 0)}")
            print(f"   ⚠️  Avisos: {summary.get('total_warnings', 0)}")
            
            # Mostrar problemas se houver
            if validation.get("issues"):
                print(f"\n❌ Problemas encontrados:")
                for issue in validation["issues"]:
                    print(f"   - {issue}")
            
            # Mostrar avisos se houver
            if validation.get("warnings"):
                print(f"\n⚠️  Avisos:")
                for warning in validation["warnings"]:
                    print(f"   - {warning}")
        
        # Exibir algumas colunas como exemplo
        if "separated_data" in dados_resultado:
            columns = dados_resultado["separated_data"].get("columns", {})
            print(f"\n📋 Exemplo de colunas processadas (primeiras 3):")
            
            for i, (nome_coluna, info_coluna) in enumerate(list(columns.items())[:3]):
                print(f"\n   🏷️  Coluna {i+1}: {nome_coluna}")
                print(f"      📊 Tipo: {info_coluna.get('type', 'unknown')}")
                print(f"      ✅ Valores válidos: {info_coluna.get('non_null_count', 0)}")
                print(f"      ❌ Valores nulos: {info_coluna.get('null_count', 0)}")
                
                # Mostrar amostras
                samples = info_coluna.get('sample_values', [])
                if samples:
                    print(f"      🔍 Amostras: {samples[:3]}")
        
        print(f"\n🎉 Workflow executado com sucesso!")
        print(f"📊 Status final: {dados_resultado.get('status', 'unknown')}")
        
        # Salvar resultado completo em arquivo
        with open("resultado_teste_workflow.json", "w", encoding="utf-8") as f:
            json.dump(dados_resultado, f, ensure_ascii=False, indent=2)
        print(f"💾 Resultado completo salvo em: resultado_teste_workflow.json")
        
        return dados_resultado
        
    except Exception as e:
        print(f"\n❌ Erro durante execução do workflow:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        print(f"\n🔍 Traceback completo:")
        traceback.print_exc()


async def main():
    """Função principal"""
    print("=" * 60)
    print("🎯 TESTE DO EXCEL PROCESSING WORKFLOW")
    print("=" * 60)
    
    await testar_workflow()


if __name__ == "__main__":
    asyncio.run(main()) 