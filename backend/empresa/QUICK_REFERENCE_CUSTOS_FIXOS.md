# 🚀 Quick Reference - Endpoint Custos Fixos

## 📍 URL e Método
```
GET /contas/relatorios/custos-fixos/
```

## 📋 Parâmetros Obrigatórios
```
data_inicio: YYYY-MM-DD
data_fim: YYYY-MM-DD
```

## 💡 Exemplo de Uso
```bash
# cURL
curl -X GET "http://127.0.0.1:8000/contas/relatorios/custos-fixos/?data_inicio=2024-01-01&data_fim=2024-12-31"

# PowerShell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/contas/relatorios/custos-fixos/?data_inicio=2024-01-01&data_fim=2024-12-31" -Method GET
```

## 📊 Estrutura da Resposta
```json
{
  "parametros": { /* filtros aplicados */ },
  "estatisticas_fornecedores": { /* contadores */ },
  "totais_gerais": { /* somas financeiras */ },
  "resumo_por_tipo_fornecedor": [ /* CUSTO FIXO vs DESPESA FIXA */ ],
  "resumo_por_fornecedor": [ /* detalhes por fornecedor */ ],
  "total_contas_pagas": 295,
  "contas_pagas": [ /* lista detalhada */ ]
}
```

## ⚡ Dados em Produção
- **Total Migrado**: 2.699 contas
- **Período Testado**: 2023-2025
- **Contas Processadas**: 295+
- **Valor Total**: R$ 211.550,03+
- **Fornecedores Ativos**: 21+
- **Tempo de Resposta**: < 1 segundo

## 🎯 Top Fornecedores
1. **FOLHA FIXA** (Custo): R$ 81.156,94
2. **PRO-LABORE LUINA** (Despesa): R$ 36.635,38
3. **ALUGUEL** (Custo): R$ 25.208,04
4. **INSS** (Custo): R$ 11.920,84

## 🚨 Códigos de Erro
- `400`: Parâmetros faltando ou inválidos
- `200`: Sucesso

## 📂 Arquivos
- **View**: `contas/views/relatorios_views.py`
- **URL**: `contas/urls.py`
- **Doc Completa**: `DOCUMENTACAO_ENDPOINT_CUSTOS_FIXOS.md`

## 🔍 Filtros Aplicados
- Status: Apenas contas **PAGAS** ('P')
- Fornecedores: Tipo **"DESPESA FIXA"** ou **"CUSTO FIXO"**
- Período: Entre `data_inicio` e `data_fim`

## ✅ Melhorias v1.0.1
- **Tratamento de NaN**: Valores None/NULL são convertidos para 0.0
- **Validação robusta**: Todos os campos numéricos são tratados
- **Dados limpos**: Respostas consistentes sem valores undefined

---
*Versão: 1.0.1 | Atualizado: 08/09/2025*
