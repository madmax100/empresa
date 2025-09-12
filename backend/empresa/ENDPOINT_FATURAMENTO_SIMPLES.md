# 📊 Endpoint Faturamento - Documentação Simples

## **URL**
```
GET /contas/relatorios/faturamento/
```

## **O que faz**
Gera relatório completo de faturamento com vendas, compras e serviços em um período, incluindo análise de margem de lucro.

## **Parâmetros**
| Campo | Obrigatório | Formato | Exemplo |
|-------|-------------|---------|---------|
| `data_inicio` | ✅ | YYYY-MM-DD | 2024-01-01 |
| `data_fim` | ✅ | YYYY-MM-DD | 2024-12-31 |

## **Exemplo de Uso**
```bash
GET /contas/relatorios/faturamento/?data_inicio=2024-01-01&data_fim=2024-12-31
```

## **Resposta Principal**

### **Totais Gerais**
```json
{
    "totais_gerais": {
        "total_quantidade_notas": 323,
        "total_valor_produtos": 404275.96,
        "total_valor_geral": 408931.5,
        "total_impostos": 3150.29,
        "analise_vendas": {
            "valor_vendas": 138580.7,
            "valor_preco_entrada": 87251.32,
            "margem_bruta": 51329.38,
            "percentual_margem": 37.04
        }
    }
}
```

### **Resumo por Tipo**
```json
{
    "resumo_por_tipo": [
        {
            "tipo": "Compras (NF Entrada)",
            "quantidade_notas": 42,
            "valor_produtos": 105602.4,
            "valor_total": 110257.94,
            "impostos": 3150.29
        },
        {
            "tipo": "Vendas (NF Saída)",
            "quantidade_notas": 101,
            "valor_produtos": 138580.7,
            "valor_total": 138580.7,
            "valor_preco_entrada": 87251.32,
            "margem_bruta": 51329.38
        },
        {
            "tipo": "Serviços (NF Serviço)",
            "quantidade_notas": 180,
            "valor_produtos": 160092.86,
            "valor_total": 160092.86
        }
    ]
}
```

### **Top Fornecedores/Clientes**
```json
{
    "top_fornecedores": [
        {
            "fornecedor": "TINSEI COMERCIO...",
            "valor_total": 47286.93,
            "quantidade_notas": 11
        }
    ],
    "top_clientes": [
        {
            "cliente": "INSTITUTO CENTRO...",
            "valor_total": 46990.0,
            "quantidade_notas": 7
        }
    ]
}
```

## **Análise de Margem** 🆕

### **Como Funciona**
- Calcula o custo real dos produtos vendidos usando preços de entrada
- Mostra margem bruta: `vendas - custos`
- Exibe percentual de margem: `(margem ÷ vendas) × 100`

### **Campos de Margem**
- `valor_preco_entrada`: Custo total dos produtos vendidos
- `margem_bruta`: Lucro bruto (vendas - custos)
- `percentual_margem`: % de margem sobre as vendas

## **Dados Incluídos**

| Tipo | Fonte | O que mostra |
|------|-------|--------------|
| **Compras** | Notas Fiscais de Entrada | Gastos com fornecedores |
| **Vendas** | Notas Fiscais de Saída | Receitas + Margem de lucro |
| **Serviços** | Notas Fiscais de Serviço | Receitas de serviços |

## **Para que serve**

✅ **Gestão Financeira:** Ver receitas vs gastos  
✅ **Análise de Margem:** Calcular rentabilidade real  
✅ **Controle de Fornecedores:** Maiores gastos  
✅ **Ranking de Clientes:** Maiores receitas  
✅ **Planejamento:** Tendências e metas  

## **Resposta de Erro**
```json
{
    "error": "Parâmetros data_inicio e data_fim são obrigatórios"
}
```

---

**💡 Dica:** Para análises rápidas, foque nos campos `totais_gerais` e `analise_vendas` que mostram o panorama completo do período.
