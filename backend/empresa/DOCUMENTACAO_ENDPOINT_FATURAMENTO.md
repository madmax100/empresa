# Endpoint: Relatório de Faturamento

## **URL**
```
GET /contas/relatorios/faturamento/
```

## **Descrição**
Endpoint para relatórios completos de faturamento baseado em **Notas Fiscais de Entrada, Saída e Serviço** em um período específico.

Fornece análise abrangente de compras, vendas e serviços com rankings de fornecedores e clientes.

**🆕 NOVA FUNCIONALIDADE:** Inclui análise de margem de lucro calculada com preços de entrada dos produtos vendidos, permitindo análise de rentabilidade detalhada.

## **Parâmetros de Query (Obrigatórios)**

| Parâmetro | Tipo | Formato | Descrição |
|-----------|------|---------|-----------|
| `data_inicio` | string | YYYY-MM-DD | Data de início do período |
| `data_fim` | string | YYYY-MM-DD | Data de fim do período |

## **Filtros Aplicados**

1. **Notas Fiscais de Entrada:** Operações contendo 'COMPRA'
2. **Notas Fiscais de Saída:** Operações contendo 'VENDA'
3. **Notas Fiscais de Serviço:** Todas as notas de serviço
4. **Período:** Data da nota fiscal entre data_inicio e data_fim

## **Exemplo de Requisição**
```bash
GET /contas/relatorios/faturamento/?data_inicio=2024-08-01&data_fim=2025-01-09
```

## **Estrutura da Resposta**

```json
{
    "parametros": {
        "data_inicio": "2024-08-01",
        "data_fim": "2025-01-09",
        "filtros_aplicados": {
            "nf_entrada": "Operação contendo COMPRA",
            "nf_saida": "Operação contendo VENDA",
            "nf_servico": "Todas as notas de serviço"
        },
        "fonte_dados": "Notas Fiscais (Entrada, Saída e Serviço)"
    },
    "totais_gerais": {
        "total_quantidade_notas": 323,
        "total_valor_produtos": 404275.96,
        "total_valor_geral": 408931.5,
        "total_impostos": 3150.29,
        "analise_vendas": {
            "valor_vendas": 138580.7,
            "valor_preco_entrada": 87251.32,
            "margem_bruta": 51329.38,
            "percentual_margem": 37.04,
            "itens_analisados": 161,
            "produtos_sem_preco_entrada": 0
        }
    },
    "resumo_por_tipo": [
        {
            "tipo": "Compras (NF Entrada)",
            "quantidade_notas": 42,
            "valor_produtos": 105602.4,
            "valor_total": 110257.94,
            "impostos": 3150.29,
            "detalhes": {
                "valor_icms": 0.0,
                "valor_ipi": 3150.29
            }
        },
        {
            "tipo": "Vendas (NF Saída)",
            "quantidade_notas": 101,
            "valor_produtos": 138580.7,
            "valor_total": 138580.7,
            "impostos": 0.0,
            "valor_preco_entrada": 87251.32,
            "margem_bruta": 51329.38,
            "detalhes": {
                "valor_icms": 0.0,
                "valor_desconto": 0.0,
                "itens_calculados": 161,
                "produtos_sem_preco_entrada": 0
            }
        },
        {
            "tipo": "Serviços (NF Serviço)",
            "quantidade_notas": 180,
            "valor_produtos": 160092.86,
            "valor_total": 160092.86,
            "impostos": 0.0,
            "detalhes": {
                "valor_iss": 0.0
            }
        }
    ],
    "top_fornecedores": [
        {
            "fornecedor": "TINSEI COMERCIO IMPORTACAO E DISTRIBUICAO LTDA",
            "valor_total": 47286.93,
            "quantidade_notas": 11
        }
    ],
    "top_clientes": [
        {
            "cliente": "INSTITUTO CENTRO DE ENSINO TECNOLOGICO - CENTEC",
            "valor_total": 46990.0,
            "quantidade_notas": 7,
            "tipo": "vendas+serviços"
        }
    ],
    "notas_detalhadas": {
        "compras": [
            {
                "id": 7964,
                "numero_nota": "7881",
                "data_emissao": "2025-01-07T03:00:00Z",
                "fornecedor": "FM COM DE EQUIPAMENTOS P/ESCRITORIO LTDA-ME",
                "operacao": "COMPRA",
                "valor_produtos": 396.0,
                "valor_total": 436.0,
                "valor_icms": 0.0,
                "valor_ipi": 0.0
            }
        ],
        "vendas": [
            {
                "id": 581,
                "numero_nota": "41055",
                "data": "2025-01-08T03:00:00Z",
                "cliente": "MARINHO SOARES COMERCIO E SERVIÇOS LTDA",
                "operacao": "VENDA",
                "valor_produtos": 850.0,
                "valor_total": 850.0,
                "valor_icms": 0.0,
                "desconto": 0.0,
                "valor_preco_entrada": 425.50,
                "margem_bruta": 424.50
            }
        ],
        "servicos": [
            {
                "id": 389,
                "numero_nota": "15254",
                "data": "2025-01-09T03:00:00Z",
                "cliente": "IEPRO-INST DE ESTUDOS E PESQUISA PROJETOS DA UECE",
                "operacao": "SERVIÇO",
                "valor_produtos": 359.2,
                "valor_total": 359.2,
                "valor_iss": 0.0
            }
        ]
    }
}
```

## **Principais Funcionalidades**

### **1. Visão Geral Consolidada**
- Total de quantidade de notas fiscais
- Valor total de produtos e serviços
- Valor geral incluindo impostos
- Total de impostos pagos
- **🆕 Análise de Vendas com Margem:** 
  - Valor total das vendas
  - Valor calculado com preços de entrada
  - Margem bruta (vendas - custos)
  - Percentual de margem
  - Estatísticas de itens analisados

### **2. Resumo por Tipo de Operação**
Para cada tipo (Compras, Vendas, Serviços):
- Quantidade de notas
- Valor de produtos/serviços
- Valor total com impostos
- Detalhamento de impostos específicos
- **🆕 Para Vendas:** Análise de margem com valor de entrada e margem bruta

### **3. Rankings Estratégicos**
- **Top 10 Fornecedores:** Maiores valores de compra
- **Top 10 Clientes:** Maiores valores de vendas e serviços
- Indicação se cliente tem vendas, serviços ou ambos

### **4. Notas Detalhadas**
- **Últimas 50 notas** de cada tipo
- Informações completas: número, data, cliente/fornecedor
- Valores discriminados por tipo de imposto
- **🆕 Para Vendas:** Valor com preço de entrada e margem bruta individual

## **Códigos de Status**

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 400 | Parâmetros obrigatórios faltando ou formato inválido |

## **Campos por Tipo de Nota Fiscal**

### **Notas Fiscais de Entrada (Compras)**
- **Campos principais:** valor_produtos, valor_total, valor_icms, valor_ipi
- **Relacionamento:** Fornecedor
- **Filtro:** Operação contendo 'COMPRA'

### **Notas Fiscais de Saída (Vendas)**
- **Campos principais:** valor_produtos, valor_total_nota, valor_icms, desconto
- **🆕 Análise de Margem:** valor_preco_entrada, margem_bruta
- **Relacionamento:** Cliente
- **Filtro:** Operação contendo 'VENDA'
- **🆕 Cálculo de Preço de Entrada:** 
  - Busca último preço de entrada no MovimentacoesEstoque (tipos 1 e 3)
  - Fallback para custo médio no SaldosEstoque
  - Fallback final para 0 se não encontrar dados

### **Notas Fiscais de Serviço**
- **Campos principais:** valor_produtos, iss
- **Relacionamento:** Cliente
- **Filtro:** Todas as operações

## **Exemplo de Uso**

### **Relatório Mensal de Faturamento**
```bash
curl -X GET "http://localhost:8000/contas/relatorios/faturamento/?data_inicio=2025-01-01&data_fim=2025-01-31"
```

### **Análise Trimestral**
```bash
curl -X GET "http://localhost:8000/contas/relatorios/faturamento/?data_inicio=2024-10-01&data_fim=2024-12-31"
```

### **Comparativo Anual**
```bash
curl -X GET "http://localhost:8000/contas/relatorios/faturamento/?data_inicio=2024-01-01&data_fim=2024-12-31"
```

## **Aplicações Práticas**

1. **Análise de Performance de Vendas:** Identificar principais clientes e tendências
2. **Gestão de Fornecedores:** Monitorar maiores gastos com compras
3. **Controle Fiscal:** Acompanhar impostos pagos por tipo
4. **Planejamento Estratégico:** Analisar evolução do faturamento
5. **Auditoria:** Verificar movimentação detalhada por período
6. **🆕 Análise de Rentabilidade:** 
   - Calcular margem de lucro por produto/cliente
   - Identificar produtos com maior margem
   - Monitorar evolução da rentabilidade no tempo
   - Comparar margem entre diferentes períodos

## **Observações Técnicas**

- **Performance:** Otimizado para grandes volumes de dados
- **Ordenação:** Top fornecedores/clientes por valor decrescente
- **Tratamento de Nulos:** Valores automáticamente convertidos para 0.0
- **Timezone:** Todas as datas em UTC
- **Limite:** Últimas 50 notas detalhadas por tipo para performance
- **🆕 Cálculo de Preços de Entrada:**
  - Busca preços em MovimentacoesEstoque (tipo 1=Entrada, tipo 3=Estoque Inicial)
  - Ordenação por data decrescente para obter último preço
  - Fallback para custo_medio em SaldosEstoque
  - Tratamento de produtos sem histórico de entrada (valor 0)
  - Cálculo de margem: (valor_venda - custo_entrada)
  - Percentual de margem: ((margem / valor_venda) * 100)
