
import psycopg2
from config import PG_CONFIG

def check_fluxo_caixa():
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()

        # Count total
        cursor.execute("SELECT COUNT(*) FROM fluxo_caixa_lancamentos")
        total = cursor.fetchone()[0]
        print(f"Total FluxoCaixaLancamentos: {total}")

        if total > 0:
            # Group by fonte_tipo
            cursor.execute("SELECT fonte_tipo, COUNT(*) FROM fluxo_caixa_lancamentos GROUP BY fonte_tipo")
            print("\nDistribuição por Fonte:")
            for fonte, count in cursor.fetchall():
                print(f"- {fonte}: {count}")
            
            # Check realized vs pending
            cursor.execute("SELECT realizado, COUNT(*) FROM fluxo_caixa_lancamentos GROUP BY realizado")
            print("\nRealizado vs Pendente:")
            for realizado, count in cursor.fetchall():
                print(f"- {'Realizado' if realizado else 'Pendente'}: {count}")

        conn.close()

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    check_fluxo_caixa()
