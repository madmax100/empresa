import os
import sys
import logging
from datetime import datetime
import importlib
import subprocess

# Obter o diretório dos scripts
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Adicionar o diretório migrations ao path para importar clean_all_tables
sys.path.append(os.path.join(SCRIPT_DIR, 'migrations'))

# Configurar logging geral
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_master.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Sequência de scripts a serem executados
SCRIPTS_SEQUENCE = [
    # 1. Tabelas Básicas (Cadastros)
    {
        'file': 'migrate_grupos.py',
        'desc': 'Grupos de Produtos',
        'deps': []
    },
    {
        'file': 'migrate_categorias.py',
        'desc': 'Categorias',
        'deps': []
    },
    {
        'file': 'migrate_marcas.py',
        'desc': 'Marcas',
        'deps': []
    },
    {
        'file': 'migrate_fornecedores.py',
        'desc': 'Fornecedores',
        'deps': []
    },
    {
        'file': 'migrate_transportadoras.py',
        'desc': 'Transportadoras',
        'deps': []
    },
    {
        'file': 'migrate_funcionarios.py',
        'desc': 'Funcionários',
        'deps': []
    },
    {
        'file': 'migrate_clientes.py',
        'desc': 'Clientes',
        'deps': []
    },
    {
        'file': 'migrate_produtos.py',
        'desc': 'Produtos',
        'deps': ['migrate_grupos.py', 'migrate_marcas.py']
    },
    
    # 2. Contratos de Locação
    {
        'file': 'migrate_contratos.py',
        'desc': 'Contratos de Locação',
        'deps': ['migrate_clientes.py']
    },
    {
        'file': 'migrate_itens_contrato.py',
        'desc': 'Itens de Contratos',
        'deps': ['migrate_contratos.py', 'migrate_categorias.py']
    },
    
    # 3. Notas Fiscais de Entrada
    {
        'file': 'migrate_nfe.py',
        'desc': 'Notas Fiscais de Entrada',
        'deps': ['migrate_fornecedores.py']
    },
    {
        'file': 'migrate_itens_nfe.py',
        'desc': 'Itens de NF Entrada',
        'deps': ['migrate_nfe.py', 'migrate_produtos.py']
    },
    
    # 4. Notas Fiscais de Saída
    {
        'file': 'migrate_nfs.py',
        'desc': 'Notas Fiscais de Saída',
        'deps': ['migrate_clientes.py', 'migrate_funcionarios.py', 'migrate_transportadoras.py']
    },
    {
        'file': 'migrate_itens_nfs.py',
        'desc': 'Itens de NF Saída',
        'deps': ['migrate_nfs.py', 'migrate_produtos.py']
    },
    
    # 5. Notas Fiscais de Serviço
    {
        'file': 'migrate_nfserv.py',
        'desc': 'Notas Fiscais de Serviço',
        'deps': ['migrate_clientes.py', 'migrate_funcionarios.py']
    },
    {
        'file': 'migrate_itens_nfserv.py',
        'desc': 'Itens de NF Serviço',
        'deps': ['migrate_nfserv.py']
    },
    
    # 6. Movimentações Financeiras
    {
        'file': 'migrate_contas_pagar.py',
        'desc': 'Contas a Pagar',
        'deps': ['migrate_fornecedores.py']
    },
    {
        'file': 'migrate_contas_receber.py',
        'desc': 'Contas a Receber',
        'deps': ['migrate_clientes.py']
    }
]

def verify_script_exists(script_path):
    """Verifica se o script existe no caminho especificado"""
    if not os.path.exists(script_path):
        logger.error(f"Script não encontrado: {script_path}")
        return False
    return True

def verify_dependencies(script_info, completed_scripts):
    """Verifica se todas as dependências foram concluídas"""
    for dep in script_info['deps']:
        if dep not in completed_scripts:
            return False
    return True

def execute_script(script_info):
    """Executa um script individual de migração"""
    script_path = os.path.join(SCRIPT_DIR+'\migrations', script_info['file'])
    
    # Verificar existência do script
    if not verify_script_exists(script_path):
        return False
    
    try:
        logger.info(f"\nIniciando migração de {script_info['desc']}...")
        logger.info(f"Executando {script_info['file']}...")
        
        # Executa o script como um processo separado usando o Python do venv
        python_path = r"C:\Users\Cirilo\Documents\c3mcopias\backend\venv\Scripts\python.exe"
        result = subprocess.run(
            [python_path, script_path],  # Usa o Python do ambiente virtual
            capture_output=True,
            text=True,
            check=True,
            cwd=SCRIPT_DIR  # Define o diretório de trabalho
        )
        
        # Log da saída do script
        if result.stdout:
            logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)
            
        logger.info(f"Migração de {script_info['desc']} concluída com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar {script_info['file']}")
        logger.error(f"Código de retorno: {e.returncode}")
        if e.stdout:
            logger.error(f"Saída padrão: {e.stdout}")
        if e.stderr:
            logger.error(f"Saída de erro: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado ao executar {script_info['file']}: {str(e)}")
        return False

def check_environment():
    """Verifica se o ambiente está configurado corretamente"""
    try:
        # Verificar se o arquivo de configuração existe
        config_path = os.path.join(SCRIPT_DIR, 'migrations\config.py')
        if not os.path.exists(config_path):
            logger.error(f"Arquivo de configuração não encontrado: {config_path}")
            return False
        
        # Verificar se todos os scripts existem
        for script_info in SCRIPTS_SEQUENCE:
            script_path = os.path.join(SCRIPT_DIR+'\migrations', script_info['file'])
            if not verify_script_exists(script_path):
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao verificar ambiente: {str(e)}")
        return False

def main():
    """Função principal que coordena a migração"""
    start_time = datetime.now()
    logger.info(f"=== INICIANDO PROCESSO DE MIGRAÇÃO ÀS {start_time} ===")
    
    # Verificar ambiente
    logger.info("Verificando ambiente...")
    if not check_environment():
        logger.error("Ambiente não está configurado corretamente.")
        return False
    
    # LIMPEZA COMPLETA DE TODAS AS TABELAS
    logger.info("\n=== EXECUTANDO LIMPEZA COMPLETA DAS TABELAS ===")
    try:
        from clean_all_tables import clean_all_tables
        if not clean_all_tables():
            logger.error("Falha na limpeza completa das tabelas.")
            return False
        logger.info("Limpeza completa das tabelas finalizada com sucesso!")
    except ImportError as e:
        logger.error(f"Erro ao importar clean_all_tables: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erro durante a limpeza completa: {str(e)}")
        return False
    
    # Lista de scripts já executados com sucesso
    completed_scripts = set()
    
    # Executar scripts na ordem definida
    for script_info in SCRIPTS_SEQUENCE:
        script_name = script_info['file']
        
        # Verifica dependências
        if not verify_dependencies(script_info, completed_scripts):
            logger.error(f"\nDependências não atendidas para {script_name}")
            logger.error(f"Dependências necessárias: {script_info['deps']}")
            logger.error(f"Scripts concluídos: {list(completed_scripts)}")
            logger.error("Abortando processo de migração...")
            return False
        
        # Executa o script
        if execute_script(script_info):
            completed_scripts.add(script_name)
        else:
            logger.error(f"\nErro na execução de {script_name}")
            logger.error("Abortando processo de migração...")
            return False
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info(f"""
    === PROCESSO DE MIGRAÇÃO CONCLUÍDO ===
    Início: {start_time}
    Fim: {end_time}
    Duração: {duration}
    Total de scripts executados: {len(completed_scripts)}
    """)
    
    return True

if __name__ == "__main__":
    try:
        if main():
            logger.info("Migração concluída com sucesso!")
            sys.exit(0)
        else:
            logger.error("Migração finalizada com erros!")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.error("\nMigração interrompida pelo usuário!")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nErro não tratado: {str(e)}")
        sys.exit(1)
