$urls = @(
    "http://127.0.0.1:8000/contas/estoque-controle/estoque_atual/?limite=50&offset=0&data=2025-09-15",
    "http://127.0.0.1:8000/contas/estoque-controle/estoque_atual/?limite=100&ordem=valor_atual&reverso=true&data=2025-09-15",
    "http://127.0.0.1:8000/contas/estoque-controle/estoque_critico/?limite=10&data=2025-09-15",
    "http://127.0.0.1:8000/contas/estoque-controle/produtos_mais_movimentados/?limite=10&data=2025-09-15"
)

foreach ($url in $urls) {
    Write-Output "Testando endpoint: $url"
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing
        Write-Output "Status Code: $($response.StatusCode)"
        if ($response.StatusCode -eq 200) {
            Write-Output "Teste APROVADO"
        } else {
            Write-Output "Teste FALHOU com status: $($response.StatusCode)"
        }
    } catch {
        Write-Output "Ocorreu um erro: $_"
    }
    Write-Output "--------------------------------------------------"
}
