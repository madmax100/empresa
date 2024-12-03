import pyodbc
import psycopg2
from datetime import datetime
from decimal import Decimal
import re

def clean_string(value):
    if value is None:
        return None
    return str(value).strip()

def clean_decimal(value):
    if value is None:
        return Decimal('0.00')
    try:
        clean_value = re.sub(r'[^\d.,\-]', '', str(value))
        clean_value = clean_value.replace(',', '.')
        return Decimal(clean_value).quantize(Decimal('0.01'))
    except:
        return Decimal('0.00')

def limpar_tabelas(pg_conn):
    try:
        cursor = pg_conn.cursor()
        
        print("\nIniciando limpeza das tabelas...")
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas = [
            'custos_adicionais_frete',
            'ocorrencias_frete',
            'fretes'
        ]
        
        for tabela in tabelas:
            try:
                print(f"\nVerificando tabela {tabela}...")
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                qtd_antes = cursor.fetchone()[0]
                print(f"Registros encontrados em {tabela}: {qtd_antes}")
                
                if qtd_antes > 0:
                    print(f"Limpando tabela {tabela}...")
                    cursor.execute(f"TRUNCATE TABLE {tabela} CASCADE")
                    pg_conn.commit()
                    print(f"Tabela {tabela} limpa com sucesso!")
                
            except Exception as e:
                print(f"Erro ao limpar tabela {tabela}: {str(e)}")
                pg_conn.rollback()
                raise
        
        cursor.execute("SET session_replication_role = 'origin';")
        pg_conn.commit()
        
        print("\nLimpeza concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro durante a limpeza: {str(e)}")
        pg_conn.rollback()
        return False

def carregar_transportadoras(pg_cursor):
    """Carrega o mapeamento de transportadoras com seus IDs"""
    pg_cursor.execute("SELECT id FROM transportadoras")
    ids = {row[0] for row in pg_cursor.fetchall()}
    print(f"Transportadoras encontradas: {ids}")
    return ids

def migrar_fretes():
    pg_config = {
        'dbname': 'c3mcopiasdb2',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    db_path = r"C:\Users\Cirilo\Documents\c3mcopias\Bancos\Movimentos\Outrosmovimentos.mdb"
    
    try:
        # Conexões
        print("Conectando aos bancos de dados...")
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={db_path};'
            'PWD=010182;'
        )
        access_conn = pyodbc.connect(conn_str)
        pg_conn = psycopg2.connect(**pg_config)
        
        # Limpar tabelas
        if not limpar_tabelas(pg_conn):
            raise Exception("Falha na limpeza das tabelas. Abortando importação.")

        pg_cursor = pg_conn.cursor()

        # Carregar transportadoras existentes
        transportadoras = carregar_transportadoras(pg_cursor)
        
        # Busca dados do Access
        print("\nBuscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute("""
            SELECT Codigo, Numero, 
                   DataEmissão, DataEntrada, Frete, 
                   Transportadora, CFOP, ValorTotal, 
                   BaseCalculo, Aliquota, ICMS, 
                   UFColeta, 
                   MunicipioColeta, CodIbge, Tipo, 
                   Chave, Fatura, Formulario
            FROM Fretes 
            ORDER BY Codigo
        """)

       # SQL de inserção - Transportadora como nullable
        insert_sql = """
            INSERT INTO fretes (
                id, numero,
                data_emissao, data_entrada,
                transportadora_id, cfop, valor_total,
                base_calculo, aliquota, icms,
                ufcoleta,
                municipiocoleta, ibge, tipo_cte, tipo_fob_cif,
                chave, fatura, formulario
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        # Processo de migração
        contador = 0
        erros = 0
        
        print("\nIniciando migração dos fretes...")
        
        while True:
            rows = access_cursor.fetchmany(1000)
            if not rows:
                break
            
            for row in rows:
                try:
                    # Validar e tratar transportadora
                    transportadora_original = row[5]  # Transportadora
                    transportadora_id = None  # Valor padrão None
                    
                    # Só usa o ID se for válido e existir
                    if transportadora_original and int(transportadora_original) in transportadoras:
                        transportadora_id = int(transportadora_original)
                    else:
                        print(f"Aviso: Transportadora inválida ou não encontrada: {transportadora_original}")

                    dados = (
                        int(row[0]),                # id (Codigo)
                        clean_string(row[1]),       # numero
                        row[2],                     # data_emissao
                        row[3],                     # data_entrada
                        transportadora_id,          # transportadora_id (pode ser None)
                        clean_string(row[6]),       # cfop
                        clean_decimal(row[7]),      # valor_total
                        clean_decimal(row[8]),      # base_calculo
                        clean_decimal(row[9]),      # aliquota
                        clean_decimal(row[10]),     # icms
                        clean_string(row[11]),      # ufcoleta
                        clean_string(row[12]),      # municipiocoleta
                        clean_string(row[13]),      # ibge
                        clean_string(row[14]),      # tipo_cte
                        clean_string(row[4]),       # tipo_fob_cif
                        clean_string(row[15]),      # chave
                        clean_string(row[16]),      # fatura
                        clean_string(row[17])       # formulario
                    )
                    
                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()
                    contador += 1
                    
                    if contador % 50 == 0:
                        print(f"Migrados {contador} fretes...")
                
                except Exception as e:
                    erros += 1
                    print(f"Erro ao migrar frete {row[0]}: {str(e)}")
                    print(f"Dados: {row}")
                    pg_conn.rollback()
                    continue

        print("\nMigração concluída!")
        print(f"Total de fretes migrados: {contador}")
        print(f"Total de erros: {erros}")
        
        # Atualizar sequence
        pg_cursor.execute("""
            SELECT setval('fretes_id_seq', 
                         (SELECT MAX(id) FROM fretes));
        """)
        pg_conn.commit()
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        if 'pg_conn' in locals():
            pg_conn.rollback()
    finally:
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    print("=== MIGRAÇÃO DE FRETES ===")
    print("Início:", datetime.now())
    migrar_fretes()
    print("Fim:", datetime.now())
