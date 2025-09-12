# Endpoint: Relatório de Custos Variáveis

## **URL**
```
GET /contas/relatorios/custos-variaveis/
```

## **Descrição**
Endpoint para relatórios de contas pagas de fornecedores com tipos relacionados a **DESPESAS VARIÁVEIS** ou **CUSTOS VARIÁVEIS** em um período específico.

Os valores são agrupados pelo campo **'especificacao'** da tabela de fornecedores.

## **Parâmetros de Query (Obrigatórios)**

| Parâmetro | Tipo | Formato | Descrição |
|-----------|------|---------|-----------|
| `data_inicio` | string | YYYY-MM-DD | Data de início do período |
| `data_fim` | string | YYYY-MM-DD | Data de fim do período |

## **Filtros Aplicados**

1. **Status da Conta:** Apenas contas com status 'P' (Pago)
2. **Tipo de Fornecedor:** Fornecedores com campo 'tipo' contendo:
   - 'VARIAVEL'
   - 'DESPESA VARIAVEL' 
   - 'CUSTO VARIAVEL'
3. **Período:** Data de pagamento entre data_inicio e data_fim

## **Exemplo de Requisição**
```bash
GET /contas/relatorios/custos-variaveis/?data_inicio=2025-08-10&data_fim=2025-09-09
```

## **Estrutura da Resposta**

```json
{
    "parametros": {
        "data_inicio": "2025-08-10",
        "data_fim": "2025-09-09",
        "filtro_aplicado": "Fornecedores com tipo relacionado a CUSTOS VARIÁVEIS",
        "fonte_dados": "Contas a Pagar (status: Pago)"
    },
    "estatisticas_fornecedores": {
        "total_fornecedores_variaveis_cadastrados": 254,
        "fornecedores_com_pagamentos_no_periodo": 24
    },
    "totais_gerais": {
        "total_valor_original": 26134.28,
        "total_valor_pago": 26134.28,
        "total_juros": 0.0,
        "total_tarifas": 0.0
    },
    "resumo_por_especificacao": [
        {
            "especificacao": "FORNECEDORES",
            "valor_original_total": 14826.56,
            "valor_pago_total": 14826.56,
            "juros_total": 0.0,
            "tarifas_total": 0.0,
            "quantidade_contas": 18,
            "quantidade_fornecedores": 10,
            "fornecedores": ["CONECTA EQUIPAMENTOS E SERVICOS LTDA", "..."]
        },
        {
            "especificacao": "IMPOSTOS",
            "valor_original_total": 6509.42,
            "valor_pago_total": 6509.42,
            "juros_total": 0.0,
            "tarifas_total": 0.0,
            "quantidade_contas": 10,
            "quantidade_fornecedores": 4,
            "fornecedores": ["RECEITA FEDERAL", "SECRETARIA DA FAZENDA", "..."]
        }
    ],
    "total_contas_pagas": 43,
    "contas_pagas": [
        {
            "id": 1234,
            "data_pagamento": "2025-08-29T03:00:00Z",
            "fornecedor_nome": "CONECTA EQUIPAMENTOS E SERVICOS LTDA",
            "fornecedor_tipo": "DESPESA VARIAVEL",
            "fornecedor_especificacao": "FORNECEDORES",
            "valor_original": 1274.0,
            "valor_pago": 1274.0,
            "juros": 0.0,
            "tarifas": 0.0,
            "historico": "Pagamento de equipamentos",
            "forma_pagamento": "PIX"
        }
    ]
}
```

## **Principais Funcionalidades**

### **1. Agrupamento por Especificação**
- Os valores são agrupados pelo campo 'especificacao' dos fornecedores
- Fornecedores sem especificação aparecem como "Sem Especificação"
- Ordenação por valor pago (maior para menor)

### **2. Estatísticas Detalhadas**
- Total de fornecedores variáveis cadastrados
- Fornecedores com pagamentos no período
- Soma de valores originais, pagos, juros e tarifas

### **3. Detalhamento por Especificação**
Para cada especificação:
- Valor total original e pago
- Quantidade de contas e fornecedores
- Lista de fornecedores envolvidos
- Total de juros e tarifas

### **4. Contas Detalhadas**
Lista completa de todas as contas pagas com:
- Dados do fornecedor e especificação
- Valores detalhados
- Forma de pagamento
- Histórico da conta

## **Códigos de Status**

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 400 | Parâmetros obrigatórios faltando ou formato inválido |

## **Tratamento de Casos Especiais**

1. **Nenhum fornecedor variável encontrado:**
   - Retorna estrutura padrão com valores zerados
   - Mensagem explicativa

2. **Fornecedores sem especificação:**
   - Agrupados como "Sem Especificação"

3. **Valores nulos:**
   - Tratados como 0.0 automaticamente

## **Exemplo de Uso**

### **Relatório Mensal de Custos Variáveis**
```bash
curl -X GET "http://localhost:8000/contas/relatorios/custos-variaveis/?data_inicio=2025-08-01&data_fim=2025-08-31"
```

### **Análise Trimestral**
```bash
curl -X GET "http://localhost:8000/contas/relatorios/custos-variaveis/?data_inicio=2025-07-01&data_fim=2025-09-30"
```

## **Diferenças do Endpoint de Custos Fixos**

| Aspecto | Custos Fixos | Custos Variáveis |
|---------|--------------|------------------|
| **Filtro de Tipo** | 'DESPESA FIXA', 'CUSTO FIXO' | 'VARIAVEL', 'DESPESA VARIAVEL', 'CUSTO VARIAVEL' |
| **Agrupamento** | Por tipo de fornecedor | Por especificação do fornecedor |
| **Objetivo** | Custos recorrentes/fixos | Custos que variam conforme atividade |
