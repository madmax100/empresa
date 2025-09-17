import requests
import pyodbc
from decimal import Decimal

def compare_estoque():
    # URL do endpoint
    endpoint_url = "http://127.0.0.1:8000/contas/estoque-controle/valor_estoque_por_grupo/"

    # Caminho para o banco de dados MS Access
    access_db_path = r"C:\\Users\\Cirilo\\Documents\\Bancos\\Cadastros\\Cadastros.mdb"

    # Conexão com o endpoint
    try:
        response = requests.get(endpoint_url)
        response.raise_for_status()
        endpoint_data = response.json()

        # Ajustar para a chave correta 'estoque_por_grupo'
        if 'estoque_por_grupo' in endpoint_data:
            valor_total_endpoint = sum(grupo['valor_total_estoque'] for grupo in endpoint_data['estoque_por_grupo'])
            print(f"Valor total do estoque (endpoint): R$ {valor_total_endpoint:,.2f}")
        else:
            print("Erro: A resposta do endpoint não contém a chave 'estoque_por_grupo'.")
            return
    except requests.RequestException as e:
        print(f"Erro ao acessar o endpoint: {e}")
        # Exibir a resposta completa para depuração
        print("Resposta do endpoint:", response.json())
        return
    except Exception as e:
        print(f"Erro ao processar os dados do endpoint: {e}")
        # Exibir a resposta completa antes de acessar a chave 'grupos'
        print("Resposta completa do endpoint para depuração:", response.json())
        return

    # Conexão com o banco de dados MS Access
    try:
        conn_str = (
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
            f"DBQ={access_db_path};"
            "PWD=010182;"
        )
        access_conn = pyodbc.connect(conn_str)
        access_cursor = access_conn.cursor()

        # Verificar a estrutura da tabela 'produtos'
        access_cursor.execute("SELECT TOP 1 * FROM produtos")
        colunas = [column[0] for column in access_cursor.description]
        print("Colunas na tabela 'produtos':", colunas)

        # Garantir que os campos necessários existem
        if 'Custo' not in colunas or 'Estoque' not in colunas:
            print("Erro: A tabela 'produtos' não contém os campos necessários 'Custo' e/ou 'Estoque'.")
            return

        # Consulta para obter o valor total do estoque na tabela produtos
        access_cursor.execute("SELECT SUM(Custo * Estoque) AS ValorTotal FROM produtos")
        valor_total_access = access_cursor.fetchone()[0] or Decimal('0')
        print(f"Valor total do estoque (MS Access): R$ {valor_total_access:,.2f}")

        # Comparação
        diferenca = Decimal(valor_total_endpoint) - valor_total_access
        print(f"Diferença entre os valores: R$ {diferenca:,.2f}")

    except pyodbc.Error as e:
        print(f"Erro ao acessar o banco de dados MS Access: {e}")
        return

if __name__ == "__main__":
    compare_estoque()