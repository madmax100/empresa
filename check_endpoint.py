import requests
import json

def check_endpoint(url):
    """Faz uma requisição a um endpoint e imprime a resposta."""
    try:
        print(f"Verificando endpoint: {url}")
        response = requests.get(url, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("Dados recebidos (JSON válido):")
                # Imprime de forma formatada
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                if isinstance(data, dict) and "estoque" in data:
                    print(f"\nEncontrados {len(data['estoque'])} produtos na chave 'estoque'.")
                elif isinstance(data, list):
                    print(f"\nEncontrados {len(data)} itens na lista.")

            except json.JSONDecodeError:
                print("Erro: A resposta não é um JSON válido.")
                print("Conteúdo da resposta:")
                print(response.text)
        else:
            print("Erro na requisição.")
            print("Conteúdo da resposta:")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro ao tentar acessar o endpoint: {e}")

if __name__ == "__main__":
    # Endpoint principal que o frontend está tentando acessar
    estoque_geral_url = "http://127.0.0.1:8000/contas/estoque-controle/estoque_atual/?limite=10"
    check_endpoint(estoque_geral_url)
