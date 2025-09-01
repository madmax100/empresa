import pyodbc
import psycopg2
from datetime import datetime
import hashlib
import json
from pathlib import Path
import importlib
from config import *

class DatabaseSync:
    def __init__(self, sync_state_file="sync_state.json"):
        self.sync_state_file = sync_state_file
        self.sync_state = self.load_sync_state()
        
    def load_sync_state(self):
        if Path(self.sync_state_file).exists():
            with open(self.sync_state_file, 'r') as f:
                return json.load(f)
        return {}

    def save_sync_state(self):
        with open(self.sync_state_file, 'w') as f:
            json.dump(self.sync_state, f, indent=2)

    def get_file_hash(self, filepath):
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def should_sync_file(self, filepath):
        current_hash = self.get_file_hash(filepath)
        last_hash = self.sync_state.get(str(filepath), None)
        
        if last_hash != current_hash:
            self.sync_state[str(filepath)] = current_hash
            return True
        return False

    def sync_cadastros(self):
        if self.should_sync_file(CADASTROS_DB):
            print("\nSincronizando Cadastros...")
            
            migrate_clientes = importlib.import_module('migrate_clientes')
            migrate_fornecedores = importlib.import_module('migrate_fornecedores')
            migrate_contratos = importlib.import_module('migrate_contratos')
            migrate_itens_contrato = importlib.import_module('migrate_itens_contrato')
            
            migrate_clientes.migrar_clientes()
            migrate_fornecedores.migrate_fornecedores()
            migrate_contratos.migrar_contratos()
            migrate_itens_contrato.migrar_itens_contrato()
            return True
        return False

    def sync_movimentos(self):
        if self.should_sync_file(MOVIMENTOS_DB):
            print("\nSincronizando Movimentos...")
            
            migrate_nfe = importlib.import_module('migrate_nfe')
            migrate_nfs = importlib.import_module('migrate_nfs')
            migrate_nfserv = importlib.import_module('migrate_nfserv')
            migrate_itens_nfe = importlib.import_module('migrate_itens_nfe')
            migrate_itens_nfs = importlib.import_module('migrate_itens_nfs')
            migrate_itens_nfserv = importlib.import_module('migrate_itens_nfserv')
            
            migrate_nfe.migrar_nfe()
            migrate_nfs.migrar_nfs()
            migrate_nfserv.migrar_nf_servico()
            migrate_itens_nfe.migrar_itens_nfe()
            migrate_itens_nfs.migrar_itens_nfs()
            migrate_itens_nfserv.migrar_itens_nf_servico()
            return True
        return False

    def sync_outros_movimentos(self):
        if self.should_sync_file(OUTROS_MOVIMENTOS_DB):
            print("\nSincronizando Outros Movimentos...")
            
            migrate_nfconsumo = importlib.import_module('migrate_nfconsumo')
            migrate_frete = importlib.import_module('migrate_frete')
            
            migrate_nfconsumo.migrar_nf_consumo()
            migrate_frete.migrar_fretes()
            return True
        return False

    def sync_contas(self):
        if self.should_sync_file(CONTAS_DB):
            print("\nSincronizando Contas...")
            
            migrate_contas_receber = importlib.import_module('migrate_contas_receber')
            migrate_pagar = importlib.import_module('migrate_contas_pagar')
            
            migrate_contas_receber.migrar_contas_receber()
            migrate_pagar.migrar_contas_pagar()
            return True
        return False

    def sync_all(self):
        print("=== INICIANDO SINCRONIZAÇÃO ===")
        print(f"Data/Hora: {datetime.now()}\n")
        
        changes = False
        
        try:
            if self.sync_cadastros():
                print("Cadastros sincronizados com sucesso!")
                changes = True
            
            if self.sync_movimentos():
                print("Movimentos sincronizados com sucesso!")
                changes = True
            
            if self.sync_outros_movimentos():
                print("Outros movimentos sincronizados com sucesso!")
                changes = True
            
            if self.sync_contas():
                print("Contas sincronizadas com sucesso!")
                changes = True
            
            if not changes:
                print("Nenhuma alteração detectada nos bancos de dados.")
            
            self.save_sync_state()
            print("\nSincronização finalizada com sucesso!")
            
        except Exception as e:
            print(f"\nErro durante a sincronização: {str(e)}")
            raise

def sync_databases():
    syncer = DatabaseSync()
    syncer.sync_all()

if __name__ == "__main__":
    sync_databases()