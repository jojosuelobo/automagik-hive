"""
Exemplo de uso do Excel Processing Workflow
==========================================

Este exemplo demonstra como usar o workflow de processamento Excel
para ler, separar e validar dados de arquivos Excel.
"""

import asyncio
import json
from pathlib import Path
from workflow import get_excel_processing_workflow_workflow


async def exemplo_basico():
    """Exemplo básico de uso do workflow"""
    print("🚀 Iniciando exemplo básico do Excel Processing Workflow")
    
    # Criar instância do workflow
    workflow = get_excel_processing_workflow_workflow()
    
    # Caminho para arquivo de exemplo (substitua pelo seu arquivo)
    arquivo_excel = "/file/bruta.xlsx"
    
    try:
        # Executar o workflow
        print(f"📊 Processando arquivo: {arquivo_excel}")
        resultado = await workflow.arun(message=f"file_path: {arquivo_excel}")
        
        # Parsear resultado JSON
        dados_processados = json.loads(resultado.content)
        
        # Exibir informações básicas
        file_info = dados_processados.get("file_info", {})
        print(f"\n✅ Arquivo processado com sucesso!")
        print(f"   📁 Arquivo: {file_info.get('file_path', 'N/A')}")
        print(f"   📊 Linhas: {file_info.get('total_rows', 0)}")
        print(f"   📋 Colunas: {file_info.get('total_columns', 0)}")
        print(f"   💾 Tamanho: {file_info.get('file_size_mb', 0):.2f} MB")
        
        # Exibir informações de validação
        validation = dados_processados.get("validation_report", {})
        summary = validation.get("summary", {})
        print(f"\n🔍 Relatório de Validação:")
        print(f"   ✅ Válido: {'Sim' if validation.get('is_valid', False) else 'Não'}")
        print(f"   🔢 Colunas numéricas: {summary.get('numeric_columns', 0)}")
        print(f"   📝 Colunas de texto: {summary.get('text_columns', 0)}")
        print(f"   📅 Colunas de data: {summary.get('datetime_columns', 0)}")
        print(f"   ⚠️  Avisos: {summary.get('total_warnings', 0)}")
        print(f"   ❌ Problemas: {summary.get('total_issues', 0)}")
        
        return dados_processados
        
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo não encontrado: {arquivo_excel}")
        print("   💡 Dica: Verifique se o caminho está correto")
        
    except Exception as e:
        print(f"❌ Erro durante o processamento: {str(e)}")


async def exemplo_detalhado():
    """Exemplo detalhado mostrando informações de cada coluna"""
    print("\n🔬 Iniciando exemplo detalhado do Excel Processing Workflow")
    
    workflow = get_excel_processing_workflow_workflow()
    arquivo_excel = "/caminho/para/seu/arquivo.xlsx"
    
    try:
        resultado = await workflow.arun(message=arquivo_excel)  # Formato direto
        dados_processados = json.loads(resultado.content)
        
        separated_data = dados_processados.get("separated_data", {})
        columns = separated_data.get("columns", {})
        
        print(f"\n📋 Análise detalhada das colunas:")
        
        for nome_coluna, info_coluna in columns.items():
            print(f"\n   🏷️  Coluna: {nome_coluna}")
            print(f"      📊 Tipo: {info_coluna.get('type', 'unknown')}")
            print(f"      ✅ Valores válidos: {info_coluna.get('non_null_count', 0)}")
            print(f"      ❌ Valores nulos: {info_coluna.get('null_count', 0)}")
            print(f"      🔢 Valores únicos: {info_coluna.get('unique_values', 0)}")
            
            # Informações específicas por tipo
            if info_coluna.get('type') == 'numeric':
                print(f"      📈 Min: {info_coluna.get('min_value', 'N/A')}")
                print(f"      📈 Max: {info_coluna.get('max_value', 'N/A')}")
                print(f"      📈 Média: {info_coluna.get('mean_value', 'N/A'):.2f}")
                
            elif info_coluna.get('type') == 'text':
                print(f"      📏 Comprimento médio: {info_coluna.get('avg_length', 0):.1f}")
                print(f"      📏 Comprimento máximo: {info_coluna.get('max_length', 0)}")
            
            # Mostrar amostras de valores
            samples = info_coluna.get('sample_values', [])
            if samples:
                print(f"      🔍 Amostras: {samples[:3]}...")
        
        return dados_processados
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")


async def exemplo_com_validacao():
    """Exemplo focado na validação de dados"""
    print("\n🛡️  Iniciando exemplo com foco em validação")
    
    workflow = get_excel_processing_workflow_workflow()
    arquivo_excel = "/caminho/para/seu/arquivo.xlsx"
    
    try:
        resultado = await workflow.arun(message=f"file_path: {arquivo_excel}")
        dados_processados = json.loads(resultado.content)
        
        validation = dados_processados.get("validation_report", {})
        
        print(f"\n🔍 Relatório de Validação Completo:")
        print(f"   Status: {'✅ VÁLIDO' if validation.get('is_valid', False) else '❌ INVÁLIDO'}")
        
        # Mostrar problemas encontrados
        issues = validation.get("issues", [])
        if issues:
            print(f"\n   ❌ Problemas encontrados ({len(issues)}):")
            for i, issue in enumerate(issues, 1):
                print(f"      {i}. {issue}")
        
        # Mostrar avisos
        warnings = validation.get("warnings", [])
        if warnings:
            print(f"\n   ⚠️  Avisos ({len(warnings)}):")
            for i, warning in enumerate(warnings, 1):
                print(f"      {i}. {warning}")
        
        if not issues and not warnings:
            print("   🎉 Nenhum problema ou aviso encontrado!")
        
        return validation
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")


def criar_arquivo_teste():
    """Cria um arquivo Excel de exemplo para teste"""
    try:
        import pandas as pd
        
        # Dados de exemplo
        dados_exemplo = {
            'Nome': ['João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Oliveira', 'Carlos Lima'],
            'Idade': [25, 30, 35, 28, 42],
            'Email': ['joao@email.com', 'maria@email.com', 'pedro@email.com', 'ana@email.com', 'carlos@email.com'],
            'Salário': [3500.50, 4200.00, 5100.75, 3800.25, 6200.00],
            'Departamento': ['TI', 'RH', 'Vendas', 'TI', 'Financeiro']
        }
        
        df = pd.DataFrame(dados_exemplo)
        arquivo_teste = "exemplo_teste.xlsx"
        df.to_excel(arquivo_teste, index=False)
        
        print(f"📄 Arquivo de teste criado: {arquivo_teste}")
        print("   Use este arquivo para testar o workflow!")
        
        return arquivo_teste
        
    except ImportError:
        print("❌ Pandas não encontrado. Instale com: pip install pandas")
        return None


async def main():
    """Função principal - executa todos os exemplos"""
    print("🎯 Excel Processing Workflow - Exemplos de Uso")
    print("=" * 50)
    
    # Perguntar se deve criar arquivo de teste
    resposta = input("\n❓ Deseja criar um arquivo Excel de teste? (s/n): ").lower()
    if resposta in ['s', 'sim', 'y', 'yes']:
        arquivo_criado = criar_arquivo_teste()
        if arquivo_criado:
            print(f"\n💡 Edite os exemplos acima para usar: {arquivo_criado}")
    
    print("\n💡 Para usar os exemplos:")
    print("   1. Edite a variável 'arquivo_excel' nos exemplos acima")
    print("   2. Substitua pelo caminho do seu arquivo Excel")
    print("   3. Execute os exemplos individualmente")
    
    print("\n🚀 Exemplo de execução:")
    print("   # await exemplo_basico()")
    print("   # await exemplo_detalhado()")
    print("   # await exemplo_com_validacao()")


if __name__ == "__main__":
    asyncio.run(main()) 