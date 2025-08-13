#!/usr/bin/env python3
"""
Script de linha de comando para análise de dados de pesquisa
Uso: python scripts/analyze_survey.py caminho/para/planilha.xlsx
"""

import asyncio
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.workflows.survey_data_visualization_workflow.workflow import get_survey_data_visualization_workflow


def setup_args():
    """Configurar argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description="Análise automatizada de dados de pesquisa com visualizações profissionais",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python scripts/analyze_survey.py data/surveys/raw/pesquisa.xlsx
  python scripts/analyze_survey.py pesquisa.xlsx --output results/
  python scripts/analyze_survey.py survey.xlsx --session "analise-jan2024"
        """
    )
    
    parser.add_argument(
        "xlsx_file",
        help="Caminho para o arquivo XLSX de pesquisa"
    )
    
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Diretório de saída para os resultados (padrão: data/surveys/outputs/analysis_TIMESTAMP)"
    )
    
    parser.add_argument(
        "--session", "-s",
        default=None,
        help="ID da sessão para tracking (padrão: survey-analysis-TIMESTAMP)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Ativar modo debug com logs detalhados"
    )
    
    parser.add_argument(
        "--format",
        choices=["all", "dashboard", "pdf", "charts"],
        default="all",
        help="Formato de saída (padrão: all)"
    )
    
    return parser.parse_args()


async def analyze_survey_cli(args):
    """Executar análise via CLI"""
    
    # Validar arquivo de entrada
    xlsx_path = Path(args.xlsx_file)
    if not xlsx_path.exists():
        print(f"❌ Arquivo não encontrado: {xlsx_path}")
        return 1
    
    if not xlsx_path.suffix.lower() in ['.xlsx', '.xls']:
        print(f"❌ Formato de arquivo não suportado: {xlsx_path.suffix}")
        print("   Formatos aceitos: .xlsx, .xls")
        return 1
    
    # Configurar diretório de saída
    if args.output:
        output_dir = Path(args.output)
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path(f"data/surveys/outputs/analysis_{timestamp}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Configurar sessão
    if args.session:
        session_id = args.session
    else:
        session_id = f"survey-cli-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Informações iniciais
    print("🔬 ANÁLISE DE DADOS DE PESQUISA")
    print("=" * 50)
    print(f"📁 Arquivo: {xlsx_path}")
    print(f"📊 Output: {output_dir}")
    print(f"🆔 Sessão: {session_id}")
    print(f"🎯 Formato: {args.format}")
    if args.debug:
        print("🐛 Debug: Ativado")
    print()
    
    try:
        # Criar workflow
        workflow = get_survey_data_visualization_workflow(
            session_id=session_id
        )
        
        # Preparar mensagem de análise
        analysis_request = f"""
        Analise os dados de pesquisa do arquivo XLSX: {xlsx_path}
        
        Requisitos:
        1. Extrair colunas com padrão 'pesquisa*' (ex: pesquisa300625_screen0-9)
        2. Classificar automaticamente os tipos de dados
        3. Gerar visualizações profissionais apropriadas
        4. Compilar dashboard interativo com insights
        5. Criar relatório executivo com recomendações
        
        Configurações:
        - Formato de saída: {args.format}
        - Diretório de saída: {output_dir}
        - Modo debug: {args.debug}
        
        Gere análise completa com estatísticas descritivas e insights de negócio.
        """
        
        # Executar com streaming para mostrar progresso
        print("🚀 Iniciando processamento...")
        step_count = 0
        
        async for response in workflow.run(
            message=analysis_request,
            stream=True,
            stream_intermediate_steps=True
        ):
            step_count += 1
            if hasattr(response, 'step_name') and response.step_name:
                print(f"   📋 Etapa {step_count}: {response.step_name}")
                if args.debug:
                    print(f"      Detalhes: {response.content[:200]}...")
            else:
                print(f"   ⏳ Processando...")
        
        # Resultado final
        print("\n🎉 ANÁLISE CONCLUÍDA!")
        print("=" * 50)
        print(f"✅ Dados processados com sucesso")
        print(f"📊 Dashboard gerado: {output_dir}/dashboard.html")
        print(f"📄 Relatório PDF: {output_dir}/relatorio_executivo.pdf")
        print(f"📈 Gráficos: {output_dir}/charts/")
        print(f"💾 Dados JSON: {output_dir}/analysis_results.json")
        print()
        print("🎯 Próximos passos:")
        print("   1. Abrir dashboard.html no navegador")
        print("   2. Compartilhar relatorio_executivo.pdf com stakeholders") 
        print("   3. Usar gráficos individuais em apresentações")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE A EXECUÇÃO:")
        print(f"   {str(e)}")
        if args.debug:
            import traceback
            print("\n🐛 Stack trace completo:")
            traceback.print_exc()
        return 1


def main():
    """Função principal do CLI"""
    args = setup_args()
    
    # Executar análise
    return asyncio.run(analyze_survey_cli(args))


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)