"""
Script independente para limpar todas as tabelas do PostgreSQL
Pode ser executado separadamente se necessário
"""
import os
import sys
import logging

# Adicionar o diretório migrations ao path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, 'migrations'))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('clean_database.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Função principal para limpeza independente"""
    logger.info("=== INICIANDO LIMPEZA INDEPENDENTE DO BANCO ===")
    
    try:
        from clean_all_tables import clean_all_tables
        
        if clean_all_tables():
            logger.info("Limpeza independente finalizada com sucesso!")
            return True
        else:
            logger.error("Falha na limpeza independente!")
            return False
            
    except ImportError as e:
        logger.error(f"Erro ao importar clean_all_tables: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erro durante a limpeza: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        if main():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        logger.error("Limpeza interrompida pelo usuário!")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}")
        sys.exit(1)
