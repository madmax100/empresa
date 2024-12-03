# verify_financial.py
import psycopg2
from datetime import datetime

def verify_financial():
    pg_config = {
        'dbname': 'nova_empresa',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    try:
        print("Conectando ao PostgreSQL...")
        conn = psycopg2.connect(**pg_config)
        cur = conn.cursor()

        # Verifica estrutura da tabela
        print("\nVerificando estrutura da tabela...")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'movimentos_financeiros'
        """)
        print("\nEstrutura da tabela:")
        for col in cur.fetchall():
            print(f"{col[0]:<20} {col[1]}")

        # Total de registros
        cur.execute("SELECT COUNT(*) FROM movimentos_financeiros")
        total = cur.fetchone()[0]
        print(f"\nTotal de registros: {total}")

        # Verifica registros por ano com tratamento de nulos
        print("\nVerificando distribuição por ano...")
        cur.execute("""
            SELECT 
                COALESCE(EXTRACT(YEAR FROM data), 0) as ano,
                COUNT(*) as total,
                COALESCE(SUM(credito), 0) as total_credito,
                COALESCE(SUM(debito), 0) as total_debito,
                COUNT(CASE WHEN data IS NULL THEN 1 END) as registros_sem_data
            FROM movimentos_financeiros
            GROUP BY EXTRACT(YEAR FROM data)
            ORDER BY ano NULLS LAST
        """)
        
        print("\nDistribuição por ano:")
        print("Ano      | Registros | Créditos    | Débitos     | Saldo")
        print("-" * 65)
        
        resultados = cur.fetchall()
        for row in resultados:
            ano, qtd, creditos, debitos, sem_data = row
            if ano is not None:
                saldo = creditos - debitos
                print(f"{int(ano):<8} | {qtd:<9} | {creditos:>10.2f} | {debitos:>10.2f} | {saldo:>10.2f}")
            else:
                print(f"{'Sem Data':<8} | {qtd:<9} | {creditos:>10.2f} | {debitos:>10.2f} | {creditos-debitos:>10.2f}")

        # Verifica valores totais
        cur.execute("""
            SELECT 
                COUNT(*) as total_registros,
                COALESCE(SUM(credito), 0) as total_creditos,
                COALESCE(SUM(debito), 0) as total_debitos,
                COUNT(CASE WHEN credito > 0 THEN 1 END) as registros_credito,
                COUNT(CASE WHEN debito > 0 THEN 1 END) as registros_debito
            FROM movimentos_financeiros
        """)
        
        totais = cur.fetchone()
        print("\nTotais gerais:")
        print(f"Total de registros: {totais[0]}")
        print(f"Total de créditos: R$ {totais[1]:,.2f} ({totais[3]} registros)")
        print(f"Total de débitos:  R$ {totais[2]:,.2f} ({totais[4]} registros)")
        print(f"Saldo:            R$ {(totais[1] - totais[2]):,.2f}")

        # Verifica registros com problemas
        print("\nVerificando possíveis problemas...")
        cur.execute("""
            SELECT 
                COUNT(CASE WHEN data IS NULL THEN 1 END) as sem_data,
                COUNT(CASE WHEN credito = 0 AND debito = 0 THEN 1 END) as sem_valor,
                COUNT(CASE WHEN credito > 0 AND debito > 0 THEN 1 END) as cred_deb_simultaneo
            FROM movimentos_financeiros
        """)
        
        problemas = cur.fetchone()
        print(f"Registros sem data: {problemas[0]}")
        print(f"Registros sem valor (crédito ou débito): {problemas[1]}")
        print(f"Registros com crédito e débito simultâneos: {problemas[2]}")

        # Amostra dos últimos registros
        print("\nÚltimos 5 registros:")
        cur.execute("""
            SELECT data, hora, tipo, credito, debito, historico
            FROM movimentos_financeiros
            WHERE data IS NOT NULL
            ORDER BY data DESC, hora DESC NULLS LAST
            LIMIT 5
        """)
        
        for row in cur.fetchall():
            data = row[0].strftime('%d/%m/%Y') if row[0] else 'Sem data'
            hora = row[1].strftime('%H:%M:%S') if row[1] else 'Sem hora'
            print(f"Data: {data} {hora} | Tipo: {row[2] or 'N/A'} | " +
                  f"Créd: {row[3] or 0:.2f} | Déb: {row[4] or 0:.2f} | " +
                  f"Hist: {row[5] or 'Sem histórico'}")

    except Exception as e:
        print(f"Erro durante a verificação: {str(e)}")
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Iniciando verificação dos movimentos financeiros...")
    print("Data e hora:", datetime.now())
    verify_financial()