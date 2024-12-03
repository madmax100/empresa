# verify_migration.py
import pyodbc
import psycopg2
from datetime import datetime
from decimal import Decimal

def verify_migration():
    """Verifica a migração comparando totais entre Origin e Destino"""
    # Configurações
    pg_config = {
        'dbname': 'nova_empresa',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }
    
    movimentos_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\movimentos\Movimentos.mdb"
    outros_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\movimentos\Outrosmovimentos.mdb"
    
    try:
        # Conexão PostgreSQL
        print("Conectando ao PostgreSQL...")
        pg_conn = psycopg2.connect(**pg_config)
        pg_cursor = pg_conn.cursor()

        # Conexão Access - Movimentos
        print("\nConectando ao Movimentos.mdb...")
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={movimentos_path};'
            'PWD=010182;'
        )
        mov_conn = pyodbc.connect(conn_str)
        mov_cursor = mov_conn.cursor()

        # Conexão Access - Outros Movimentos
        print("Conectando ao Outrosmovimentos.mdb...")
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={outros_path};'
            'PWD=010182;'
        )
        outros_conn = pyodbc.connect(conn_str)
        outros_cursor = outros_conn.cursor()

        print("\n=== Verificação da Migração ===")
        print("-" * 80)

        # 1. Notas Fiscais de Saída (NFS)
        mov_cursor.execute("SELECT COUNT(*) FROM NFS")
        nfs_origin = mov_cursor.fetchone()[0]
        
        mov_cursor.execute("SELECT SUM(Valortotalnota) FROM NFS")
        nfs_valor_origin = mov_cursor.fetchone()[0] or 0
        
        pg_cursor.execute("SELECT COUNT(*), COALESCE(SUM(valor_total), 0) FROM notas_fiscais WHERE tipo = 'NFS'")
        nfs_dest = pg_cursor.fetchone()
        
        print("\n1. Notas Fiscais de Saída (NFS):")
        print(f"Origin: {nfs_origin:,} registros - R$ {nfs_valor_origin:,.2f}")
        print(f"Destino: {nfs_dest[0]:,} registros - R$ {nfs_dest[1]:,.2f}")
        print(f"Diferença: {nfs_origin - nfs_dest[0]:,} registros")
        
        # 2. Notas Fiscais de Entrada (NFE)
        mov_cursor.execute("SELECT COUNT(*) FROM NFE")
        nfe_origin = mov_cursor.fetchone()[0]
        
        mov_cursor.execute("SELECT SUM(Valortotalnota) FROM NFE")
        nfe_valor_origin = mov_cursor.fetchone()[0] or 0
        
        pg_cursor.execute("SELECT COUNT(*), COALESCE(SUM(valor_total), 0) FROM notas_fiscais WHERE tipo = 'NFE'")
        nfe_dest = pg_cursor.fetchone()
        
        print("\n2. Notas Fiscais de Entrada (NFE):")
        print(f"Origin: {nfe_origin:,} registros - R$ {nfe_valor_origin:,.2f}")
        print(f"Destino: {nfe_dest[0]:,} registros - R$ {nfe_dest[1]:,.2f}")
        print(f"Diferença: {nfe_origin - nfe_dest[0]:,} registros")

        # 3. Notas Fiscais de Serviço (NFSERV)
        mov_cursor.execute("SELECT COUNT(*) FROM NFSERV")
        nfserv_origin = mov_cursor.fetchone()[0]
        
        mov_cursor.execute("SELECT SUM(Valortotalnota) FROM NFSERV")
        nfserv_valor_origin = mov_cursor.fetchone()[0] or 0
        
        pg_cursor.execute("SELECT COUNT(*), COALESCE(SUM(valor_total), 0) FROM notas_fiscais WHERE tipo = 'NFSERV'")
        nfserv_dest = pg_cursor.fetchone()
        
        print("\n3. Notas Fiscais de Serviço (NFSERV):")
        print(f"Origin: {nfserv_origin:,} registros - R$ {nfserv_valor_origin:,.2f}")
        print(f"Destino: {nfserv_dest[0]:,} registros - R$ {nfserv_dest[1]:,.2f}")
        print(f"Diferença: {nfserv_origin - nfserv_dest[0]:,} registros")

        # 4. Notas Fiscais de Consumo (NFConsumo)
        outros_cursor.execute("SELECT COUNT(*) FROM NFConsumo")
        nfconsumo_origin = outros_cursor.fetchone()[0]
        
        outros_cursor.execute("SELECT SUM(Valortotalnota) FROM NFConsumo")
        nfconsumo_valor_origin = outros_cursor.fetchone()[0] or 0
        
        pg_cursor.execute("SELECT COUNT(*), COALESCE(SUM(valor_total), 0) FROM notas_fiscais WHERE tipo = 'NFCONSUMO'")
        nfconsumo_dest = pg_cursor.fetchone()
        
        print("\n4. Notas Fiscais de Consumo (NFConsumo):")
        print(f"Origin: {nfconsumo_origin:,} registros - R$ {nfconsumo_valor_origin:,.2f}")
        print(f"Destino: {nfconsumo_dest[0]:,} registros - R$ {nfconsumo_dest[1]:,.2f}")
        print(f"Diferença: {nfconsumo_origin - nfconsumo_dest[0]:,} registros")

        # 5. Conhecimentos de Frete
        outros_cursor.execute("SELECT COUNT(*) FROM Fretes")
        fretes_origin = outros_cursor.fetchone()[0]
        
        outros_cursor.execute("SELECT COUNT(*) FROM [Cópia de Fretes]")
        fretes_copia_origin = outros_cursor.fetchone()[0]
        
        outros_cursor.execute("SELECT SUM(ValorTotal) FROM Fretes")
        fretes_valor_origin = outros_cursor.fetchone()[0] or 0
        
        outros_cursor.execute("SELECT SUM(ValorTotal) FROM [Cópia de Fretes]")
        fretes_copia_valor_origin = outros_cursor.fetchone()[0] or 0
        
        pg_cursor.execute("SELECT COUNT(*), COALESCE(SUM(valor_total), 0) FROM conhecimentos_frete")
        fretes_dest = pg_cursor.fetchone()
        
        print("\n5. Conhecimentos de Frete:")
        print(f"Origin (Fretes): {fretes_origin:,} registros - R$ {fretes_valor_origin:,.2f}")
        print(f"Origin (Cópia): {fretes_copia_origin:,} registros - R$ {fretes_copia_valor_origin:,.2f}")
        print(f"Origin (Total): {fretes_origin + fretes_copia_origin:,} registros - R$ {fretes_valor_origin + fretes_copia_valor_origin:,.2f}")
        print(f"Destino: {fretes_dest[0]:,} registros - R$ {fretes_dest[1]:,.2f}")
        print(f"Diferença: {(fretes_origin + fretes_copia_origin) - fretes_dest[0]:,} registros")

        # Resumo
        print("\n=== Resumo da Verificação ===")
        problemas = []
        
        if nfs_origin != nfs_dest[0]:
            problemas.append(f"NFS: {abs(nfs_origin - nfs_dest[0])} registros de diferença")
            
        if nfe_origin != nfe_dest[0]:
            problemas.append(f"NFE: {abs(nfe_origin - nfe_dest[0])} registros de diferença")
            
        if nfserv_origin != nfserv_dest[0]:
            problemas.append(f"NFSERV: {abs(nfserv_origin - nfserv_dest[0])} registros de diferença")
            
        if nfconsumo_origin != nfconsumo_dest[0]:
            problemas.append(f"NFConsumo: {abs(nfconsumo_origin - nfconsumo_dest[0])} registros de diferença")
            
        if (fretes_origin + fretes_copia_origin) != fretes_dest[0]:
            problemas.append(f"Fretes: {abs((fretes_origin + fretes_copia_origin) - fretes_dest[0])} registros de diferença")

        if problemas:
            print("\nProblemas encontrados:")
            for p in problemas:
                print(f"- {p}")
        else:
            print("\nTodos os registros foram migrados corretamente!")

    except Exception as e:
        print(f"Erro durante a verificação: {str(e)}")
    finally:
        if 'mov_cursor' in locals():
            mov_cursor.close()
        if 'mov_conn' in locals():
            mov_conn.close()
        if 'outros_cursor' in locals():
            outros_cursor.close()
        if 'outros_conn' in locals():
            outros_conn.close()
        if 'pg_cursor' in locals():
            pg_cursor.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    print("Iniciando verificação da migração...")
    verify_migration()
