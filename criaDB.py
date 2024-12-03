# -*- coding: utf-8 -*-
"""
Created on Sun Nov 10 07:20:30 2024

@author: Cirilo
"""

# create_database.py
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys


def create_database():
    # Configurações de conexão com PostgreSQL
    config = {
        'user': 'cirilomax',
        'password': '226cmm100',  # Altere para sua senha
        'host': 'localhost',
        'port': '5432'
    }


    try:
        # Define encoding padrão
        if sys.platform.startswith('win'):
            import locale
            locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
        
        # Conecta ao PostgreSQL
        print("Tentando conectar ao PostgreSQL...")
        conn = psycopg2.connect(
            database='postgres',  # Conecta primeiro ao banco postgres
            **config
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Nome do banco de dados
        dbname = "nova_empresa"
        
        try:
            # Verifica se o banco de dados já existe
            print("Verificando se o banco já existe...")
            cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (dbname,))
            exists = cur.fetchone()
            
            if not exists:
                # Cria o banco de dados com encoding específico
                print(f"Criando banco de dados '{dbname}'...")
                cur.execute(f"CREATE DATABASE {dbname} WITH ENCODING 'UTF8' LC_COLLATE='Portuguese_Brazil.1252' LC_CTYPE='Portuguese_Brazil.1252'")
                print(f"Banco de dados '{dbname}' criado com sucesso!")
            else:
                print(f"Banco de dados '{dbname}' já existe!")
                
        except Exception as e:
            print(f"Erro ao criar/verificar banco de dados: {e}")
            raise
        finally:
            cur.close()
            conn.close()
        
        print("\nPróximos passos:")
        print("1. Verifique se o PostgreSQL está rodando")
        print("2. Confirme se as credenciais estão corretas no script")
        print("3. Execute o script de migração principal")
        
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        raise
    except Exception as e:
        print(f"Erro não esperado: {e}")
        raise

if __name__ == "__main__":
    try:
        create_database()
    except Exception as e:
        print(f"\nErro durante a execução: {e}")
        print("\nVerifique se:")
        print("1. O PostgreSQL está instalado e rodando")
        print("2. As credenciais estão corretas")
        print("3. A porta 5432 está disponível")
        print("4. O usuário tem permissão para criar bancos de dados")