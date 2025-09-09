#!/usr/bin/env python
"""
Script Master para Migração Completa do Sistema
Executa todas as migrações em ordem lógica
"""
import os
import sys
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_master_completa.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class MigrationMaster:
    """Orquestrador de todas as migrações"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.scripts_executados = []
        self.scripts_com_erro = []
        self.inicio_execucao = datetime.now()
        
        # Ordem lógica de execução das migrações
        # Tabelas independentes primeiro, depois as que têm dependências
        self.ordem_execucao = [
            # 1. Tabelas básicas (sem dependências)
            'migrate_categorias.py',
            'migrate_grupos.py',
            'migrate_marcas.py',
            'migrate_tipos_movimentacao.py',
            'migrate_transportadoras.py',
            
            # 2. Tabelas de pessoas/entidades
            'migrate_fornecedores.py',
            'migrate_clientes.py',
            'migrate_funcionarios.py',
            
            # 3. Tabelas de produtos
            'migrate_produtos.py',
            
            # 4. Tabelas financeiras
            'migrate_contas_pagar.py',
            'migrate_contas_receber.py',
            
            # 5. Tabelas de contratos
            'migrate_contratos.py',
            'migrate_itens_contrato.py',
            
            # 6. Tabelas de notas fiscais
            'migrate_nfe.py',
            'migrate_nfs.py',
            'migrate_nfserv.py',
            
            # 7. Itens das notas fiscais
            'migrate_itens_nfe.py',
            'migrate_itens_nfs.py',
            'migrate_itens_nfserv.py',
            
            # 8. Tabelas de movimentações e extratos
            'migrate_movimentacoes_extratos.py',
            'migrate_notas_fiscais_extratos.py',
            'migrate_lancamentos.py',
        ]
    
    def verificar_ambiente(self):
        """Verifica se o ambiente está configurado corretamente"""
        logger.info("Verificando ambiente...")
        
        # Verificar se arquivo de configuração existe
        config_file = self.base_dir / 'config.py'
        if not config_file.exists():
            logger.error(f"Arquivo de configuração não encontrado: {config_file}")
            return False
        
        # Verificar se scripts existem
        scripts_faltando = []
        for script in self.ordem_execucao:
            script_path = self.base_dir / script
            if not script_path.exists():
                scripts_faltando.append(script)
        
        if scripts_faltando:
            logger.warning(f"Scripts não encontrados: {scripts_faltando}")
            # Remove scripts faltando da lista de execução
            self.ordem_execucao = [s for s in self.ordem_execucao if s not in scripts_faltando]
        
        logger.info(f"Scripts a serem executados: {len(self.ordem_execucao)}")
        return True
    
    def executar_script(self, script_name):
        """Executa um script de migração específico"""
        script_path = self.base_dir / script_name
        
        logger.info(f"{'='*60}")
        logger.info(f"EXECUTANDO: {script_name}")
        logger.info(f"{'='*60}")
        
        try:
            # Executar o script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutos timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {script_name} executado com SUCESSO!")
                self.scripts_executados.append(script_name)
                
                # Log da saída do script
                if result.stdout:
                    logger.info("Saída do script:")
                    for linha in result.stdout.split('\n'):
                        if linha.strip():
                            logger.info(f"  {linha}")
                
                return True
            else:
                logger.error(f"❌ {script_name} FALHOU com código: {result.returncode}")
                self.scripts_com_erro.append({
                    'script': script_name,
                    'codigo': result.returncode,
                    'erro': result.stderr
                })
                
                # Log do erro
                if result.stderr:
                    logger.error("Erro do script:")
                    for linha in result.stderr.split('\n'):
                        if linha.strip():
                            logger.error(f"  {linha}")
                
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ {script_name} TIMEOUT (mais de 30 minutos)")
            self.scripts_com_erro.append({
                'script': script_name,
                'codigo': 'TIMEOUT',
                'erro': 'Script executou por mais de 30 minutos'
            })
            return False
            
        except Exception as e:
            logger.error(f"❌ {script_name} ERRO DE EXECUÇÃO: {str(e)}")
            self.scripts_com_erro.append({
                'script': script_name,
                'codigo': 'EXCEPTION',
                'erro': str(e)
            })
            return False
    
    def gerar_relatorio_final(self):
        """Gera relatório final da migração"""
        fim_execucao = datetime.now()
        tempo_total = fim_execucao - self.inicio_execucao
        
        logger.info(f"\n{'='*60}")
        logger.info(f"RELATÓRIO FINAL DA MIGRAÇÃO COMPLETA")
        logger.info(f"{'='*60}")
        logger.info(f"Início: {self.inicio_execucao}")
        logger.info(f"Fim: {fim_execucao}")
        logger.info(f"Tempo total: {tempo_total}")
        logger.info(f"")
        logger.info(f"📊 ESTATÍSTICAS:")
        logger.info(f"  - Scripts planejados: {len(self.ordem_execucao)}")
        logger.info(f"  - Scripts executados com sucesso: {len(self.scripts_executados)}")
        logger.info(f"  - Scripts com erro: {len(self.scripts_com_erro)}")
        logger.info(f"  - Taxa de sucesso: {(len(self.scripts_executados)/len(self.ordem_execucao)*100):.1f}%")
        
        if self.scripts_executados:
            logger.info(f"\n✅ SCRIPTS EXECUTADOS COM SUCESSO:")
            for i, script in enumerate(self.scripts_executados, 1):
                logger.info(f"  {i}. {script}")
        
        if self.scripts_com_erro:
            logger.info(f"\n❌ SCRIPTS COM ERRO:")
            for i, item in enumerate(self.scripts_com_erro, 1):
                logger.info(f"  {i}. {item['script']} (Código: {item['codigo']})")
                if item['erro']:
                    # Mostrar apenas as primeiras linhas do erro
                    linhas_erro = item['erro'].split('\n')[:3]
                    for linha in linhas_erro:
                        if linha.strip():
                            logger.info(f"     {linha.strip()}")
        
        logger.info(f"\n{'='*60}")
        
        if self.scripts_com_erro:
            logger.error("❌ MIGRAÇÃO FINALIZADA COM ERROS!")
            return False
        else:
            logger.info("✅ MIGRAÇÃO COMPLETA FINALIZADA COM SUCESSO!")
            return True
    
    def executar_migracao_completa(self):
        """Executa a migração completa"""
        logger.info(f"{'='*60}")
        logger.info(f"INICIANDO MIGRAÇÃO COMPLETA DO SISTEMA")
        logger.info(f"Data/Hora: {self.inicio_execucao}")
        logger.info(f"{'='*60}")
        
        # Verificar ambiente
        if not self.verificar_ambiente():
            logger.error("❌ Ambiente não está configurado corretamente.")
            return False
        
        logger.info(f"✅ Ambiente verificado. Iniciando execução de {len(self.ordem_execucao)} scripts...")
        
        # Executar scripts em ordem
        for i, script in enumerate(self.ordem_execucao, 1):
            logger.info(f"\n🔄 PROGRESSO: {i}/{len(self.ordem_execucao)} ({(i/len(self.ordem_execucao)*100):.1f}%)")
            
            sucesso = self.executar_script(script)
            
            if not sucesso:
                logger.warning(f"⚠️ {script} falhou, mas continuando com próximo script...")
            
            # Pequena pausa entre scripts
            import time
            time.sleep(2)
        
        # Gerar relatório final
        return self.gerar_relatorio_final()

def main():
    """Função principal"""
    try:
        migrator = MigrationMaster()
        sucesso = migrator.executar_migracao_completa()
        
        if sucesso:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.error("❌ Migração interrompida pelo usuário!")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
