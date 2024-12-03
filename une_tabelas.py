import psycopg2
from psycopg2 import sql
from datetime import datetime
import re

def limpar_string(valor):
    """Limpa strings removendo caracteres especiais e espaços extras"""
    if valor is None:
        return None
    if isinstance(valor, str):
        valor = re.sub(r'\s+', ' ', valor)
        valor = ''.join(char for char in valor if ord(char) >= 32)
        return valor.strip()
    return str(valor)

def migrar_factoring():
    # Configurações de conexão
    conn_params = {
        'dbname': 'nova_empresa',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    try:
        # Conecta ao PostgreSQL
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()

        # 1. Migrar dados da tabela Factoring antiga
        print("Migrando dados do Factoring...")
        
        # Buscar dados da tabela antiga
        cur.execute("SELECT codigo, nome, fone, contato, fax FROM factoring")
        registros_antigos = cur.fetchall()

        # Preparar insert na nova tabela
        insert_sql = """
        INSERT INTO financeiro_factoring 
            (codigo, nome, telefone, contato, fax, created_at)
        VALUES 
            (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (codigo) DO UPDATE SET
            nome = EXCLUDED.nome,
            telefone = EXCLUDED.telefone,
            contato = EXCLUDED.contato,
            fax = EXCLUDED.fax;
        """

        # Processar cada registro
        for registro in registros_antigos:
            try:
                dados = [
                    limpar_string(registro[0]),  # codigo
                    limpar_string(registro[1]),  # nome
                    limpar_string(registro[2]),  # telefone
                    limpar_string(registro[3]),  # contato
                    limpar_string(registro[4])   # fax
                ]
                
                cur.execute(insert_sql, dados)
                print(f"Factoring migrado: {dados[1]}")
                
            except Exception as e:
                print(f"Erro ao migrar factoring {registro[1]}: {str(e)}")
                continue

        # Commit das alterações
        conn.commit()
        
        # Verificar resultados
        cur.execute("SELECT COUNT(*) FROM financeiro_factoring")
        total_migrado = cur.fetchone()[0]
        
        print(f"\nMigração de Factoring concluída!")
        print(f"Total de registros migrados: {total_migrado}")

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        conn.rollback()
        
    finally:
        # Fecha conexões
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrar_factoring()