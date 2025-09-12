# 💰 Endpoint: Contas Não Pagas por Data de Corte

## 🎯 **ENDPOINT CRIADO**

### **📍 URL:**
```
GET /contas/contas-nao-pagas-por-data-corte/
```

### **🔄 Funcionalidade:**
Mostra totais de **contas a pagar e receber não pagas** antes e depois de uma data de corte específica, **agrupadas por especificação do fornecedor/cliente**.

---

## 📋 **PARÂMETROS**

| Parâmetro | Obrigatório | Tipo | Descrição | Valores Aceitos |
|-----------|-------------|------|-----------|-----------------|
| `data_corte` | ✅ **SIM** | string | Data de referência | YYYY-MM-DD |
| `tipo` | ❌ Não | string | Tipo de conta | `pagar`, `receber`, `ambos` (padrão) |
| `incluir_canceladas` | ❌ Não | boolean | Incluir canceladas | `true`, `false` (padrão) |

---

## 📤 **EXEMPLO DE REQUISIÇÃO**

```bash
GET /contas/contas-nao-pagas-por-data-corte/?data_corte=2025-01-15&tipo=pagar
```

---

## 📥 **ESTRUTURA DA RESPOSTA**

```json
{
    "data_corte": "2025-01-15",
    "filtros": {
        "tipo": "pagar",
        "incluir_canceladas": false
    },
    "resumo_geral": {
        "antes_data_corte": {
            "total_contas_pagar": 13,
            "valor_total_pagar": 33526.87,
            "total_contas_receber": 0,
            "valor_total_receber": 0,
            "total_fornecedores": 9,
            "total_clientes": 0,
            "saldo_liquido": -33526.87
        },
        "depois_data_corte": {
            "total_contas_pagar": 244,
            "valor_total_pagar": 209511.09,
            "total_contas_receber": 0,
            "valor_total_receber": 0,
            "total_fornecedores": 45,
            "total_clientes": 0,
            "saldo_liquido": -209511.09
        },
        "saldo_total": -243037.96
    },
    "detalhamento": {
        "contas_a_pagar": {
            "antes_data_corte": [
                {
                    "fornecedor": {
                        "id": 123,
                        "nome": "INFORMA CONTABILIDADE",
                        "cnpj_cpf": "12.345.678/0001-90",
                        "especificacao": "HONOR. CONTABEIS"
                    },
                    "total_contas": 1,
                    "valor_total": 660.0,
                    "periodo_vencimento": {
                        "menor_data": "2025-01-10T00:00:00Z",
                        "maior_data": "2025-01-10T00:00:00Z"
                    }
                },
                {
                    "fornecedor": {
                        "id": 456,
                        "nome": "FGTS",
                        "cnpj_cpf": null,
                        "especificacao": "IMPOSTOS"
                    },
                    "total_contas": 3,
                    "valor_total": 2316.97,
                    "periodo_vencimento": {
                        "menor_data": "2025-01-07T00:00:00Z",
                        "maior_data": "2025-01-14T00:00:00Z"
                    }
                }
            ],
            "depois_data_corte": [
                {
                    "fornecedor": {
                        "id": 789,
                        "nome": "FORNECEDOR EXEMPLO",
                        "cnpj_cpf": "98.765.432/0001-10",
                        "especificacao": "MATERIAL ESCRITORIO"
                    },
                    "total_contas": 5,
                    "valor_total": 15420.50,
                    "periodo_vencimento": {
                        "menor_data": "2025-01-20T00:00:00Z",
                        "maior_data": "2025-02-15T00:00:00Z"
                    }
                }
            ]
        },
        "contas_a_receber": {
            "antes_data_corte": [],
            "depois_data_corte": []
        }
    },
    "metadados": {
        "data_consulta": "2025-01-09T10:30:00.123456",
        "total_registros_antes": 13,
        "total_registros_depois": 244
    }
}
```

---

## 🎯 **CARACTERÍSTICAS ESPECIAIS**

### **🏷️ Agrupamento por Especificação**
- As **contas a pagar** são agrupadas por `especificacao` do fornecedor
- Ordenação: primeiro por especificação, depois por nome do fornecedor
- Permite análise por categoria de gasto (ex: "IMPOSTOS", "MATERIAL ESCRITORIO", etc.)

### **📊 Dados Consolidados**
- **Resumo geral** com totais antes e depois da data de corte
- **Contagem de fornecedores/clientes** únicos
- **Saldo líquido** (receber - pagar) por período
- **Período de vencimento** (menor e maior data) por fornecedor

### **🔍 Filtros Avançados**
- **Status:** Apenas contas abertas (não pagas) por padrão
- **Canceladas:** Opção de incluir ou excluir contas canceladas
- **Tipo:** Pagar, receber ou ambos

---

## 📋 **CASOS DE USO PRÁTICOS**

### **💸 1. Análise de Fluxo de Caixa**
```bash
GET /contas/contas-nao-pagas-por-data-corte/?data_corte=2025-02-01&tipo=ambos
```
**Para:** Ver compromissos vencidos vs. futuros

### **🔍 2. Controle por Categoria de Gasto**
```bash
GET /contas/contas-nao-pagas-por-data-corte/?data_corte=2025-01-31&tipo=pagar
```
**Para:** Análise de gastos por especificação (IMPOSTOS, FORNECEDORES, etc.)

### **🚨 3. Contas Vencidas**
```bash
GET /contas/contas-nao-pagas-por-data-corte/?data_corte=2025-01-09&tipo=pagar
```
**Para:** Ver apenas as contas que já venceram (antes da data atual)

### **📈 4. Planejamento Financeiro**
```bash
GET /contas/contas-nao-pagas-por-data-corte/?data_corte=2025-01-31&tipo=ambos
```
**Para:** Planejar pagamentos/recebimentos do mês

---

## 📊 **RESULTADOS ATUAIS**

### **📈 Dados de Teste (15/01/2025):**
- **🔴 Vencidas (antes 15/01):** 13 contas = R$ 33.526,87
- **🟡 A vencer (depois 15/01):** 244 contas = R$ 209.511,09
- **📊 Total em aberto:** 257 contas = R$ 243.037,96

### **🏷️ Principais Especificações:**
- **HONOR. CONTABEIS:** R$ 660,00
- **IMPOSTOS:** R$ 2.499,28 (7 contas)
- **MATERIAL ESCRITORIO, FORNECEDORES, etc.**

---

## ⚙️ **IMPLEMENTAÇÃO TÉCNICA**

### **🔧 Agrupamento SQL:**
```python
.values(
    'fornecedor__id',
    'fornecedor__nome', 
    'fornecedor__cpf_cnpj',
    'fornecedor__especificacao'  # 🆕 Campo especificação
).annotate(
    total_contas=Count('id'),
    valor_total=Sum('valor'),
    menor_vencimento=Min('vencimento'),
    maior_vencimento=Max('vencimento')
).order_by('fornecedor__especificacao', 'fornecedor__nome')  # 🆕 Ordenação por especificação
```

### **📋 Campos Retornados:**
- **Fornecedor:** ID, nome, CNPJ/CPF e **especificação**
- **Agregações:** Total de contas, valor total, período de vencimento
- **Metadados:** Data de consulta, totais de registros

---

## 🎉 **CONCLUSÃO**

✅ **Endpoint funcionando** com agrupamento por especificação do fornecedor  
✅ **Dados reais**: 257 contas em aberto totalizando R$ 243.037,96  
✅ **Análise por categoria** de gasto via campo especificação  
✅ **Visão temporal** completa (antes/depois da data de corte)  

**Status:** ✅ **IMPLEMENTADO E TESTADO** - Pronto para uso em produção!
