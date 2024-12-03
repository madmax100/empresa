# fix_financial.py
import psycopg2
from datetime import datetime

def fix_financial():
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

        # 1. Corrigir anos futuros (provavelmente erro de digitação)
        print("\n1. Corrigindo datas futuras...")
        
        # 2109 -> 2019
        cur.execute("""
            UPDATE movimentos_financeiros 
            SET data = data - interval '90 years'
            WHERE EXTRACT(YEAR FROM data) = 2109;
        """)
        
        # 2201 -> 2021
        cur.execute("""
            UPDATE movimentos_financeiros 
            SET data = data - interval '180 years'
            WHERE EXTRACT(YEAR FROM data) = 2201;
        """)
        
        # 2208 -> 2028
        cur.execute("""
            UPDATE movimentos_financeiros 
            SET data = data - interval '180 years'
            WHERE EXTRACT(YEAR FROM data) = 2208;
        """)
        
        # 2025 -> 2023 (provável erro)
        cur.execute("""
            UPDATE movimentos_financeiros 
            SET data = data - interval '2 years'
            WHERE EXTRACT(YEAR FROM data) = 2025;
        """)

        # 2. Identificar registros problemáticos para análise
        print("\n2. Identificando registros problemáticos...")
        
        cur.execute("""
            CREATE TEMP TABLE registros_problematicos AS
            SELECT 
                id,
                data,
                hora,
                tipo,
                credito,
                debito,
                historico,
                CASE 
                    WHEN data IS NULL THEN 'Sem data'
                    WHEN credito = 0 AND debito = 0 THEN 'Sem valor'
                    WHEN EXTRACT(YEAR FROM data) < 2006 THEN 'Data antiga suspeita'
                END as tipo_problema
            FROM movimentos_financeiros
            WHERE 
                data IS NULL OR
                (credito = 0 AND debito = 0) OR
                EXTRACT(YEAR FROM data) < 2006
        """)

        # Exporta registros problemáticos para análise
        cur.execute("SELECT * FROM registros_problematicos")
        problemas = cur.fetchall()
        
        with open('registros_problematicos.txt', 'w', encoding='utf-8') as f:
            f.write("Registros que precisam de verificação manual:\n\n")
            for reg in problemas:
                f.write(f"ID: {reg[0]}\n")
                f.write(f"Data: {reg[1]}\n")
                f.write(f"Hora: {reg[2]}\n")
                f.write(f"Tipo: {reg[3]}\n")
                f.write(f"Crédito: {reg[4]}\n")
                f.write(f"Débito: {reg[5]}\n")
                f.write(f"Histórico: {reg[6]}\n")
                f.write(f"Problema: {reg[7]}\n")
                f.write("-" * 50 + "\n")

        # 3. Verificação final
        print("\n3. Verificando resultados após correções...")
        cur.execute("""
            SELECT 
                EXTRACT(YEAR FROM data) as ano,
                COUNT(*) as total,
                SUM(credito) as creditos,
                SUM(debito) as debitos
            FROM movimentos_financeiros
            WHERE data IS NOT NULL
            GROUP BY EXTRACT(YEAR FROM data)
            ORDER BY ano
        """)
        
        print("\nDistribuição por ano após correções:")
        print("Ano      | Registros | Créditos    | Débitos     | Saldo")
        print("-" * 65)
        
        for row in cur.fetchall():
            ano, qtd, creditos, debitos = row
            saldo = creditos - debitos
            print(f"{int(ano):<8} | {qtd:<9} | {creditos:>10.2f} | {debitos:>10.2f} | {saldo:>10.2f}")

        conn.commit()
        print("\nCorreções aplicadas com sucesso!")
        print("\nRegistros problemáticos foram exportados para 'registros_problematicos.txt'")
        print("Por favor, revise o arquivo e faça as correções necessárias manualmente.")

    except Exception as e:
        print(f"Erro durante a correção: {str(e)}")
        conn.rollback()
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Iniciando correção dos movimentos financeiros...")
    fix_financial()