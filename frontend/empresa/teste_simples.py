import requests

try:
    print("Testando endpoint de saldos...")
    response = requests.get("http://localhost:8000/contas/saldos_estoque/?limit=1")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Tipo de resposta: {type(data)}")
        if isinstance(data, list):
            print(f"É uma lista com {len(data)} itens")
            if len(data) > 0:
                print("Primeiro item:", data[0])
        else:
            print(f"Chaves: {data.keys() if isinstance(data, dict) else 'N/A'}")
    else:
        print("Erro:", response.text[:200])
except Exception as e:
    print(f"Erro: {e}")
