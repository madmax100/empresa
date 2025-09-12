# 📋 Endpoints de Contas a Pagar e Contas a Receber

## 🎯 **RESUMO EXECUTIVO**

O sistema possui **2 endpoints principais** para consultar contas a pagar e contas a receber:

### **📊 Endpoints Disponíveis:**

| Endpoint | Função | Status |
|----------|--------|--------|
| `/contas/contas-por-data-pagamento/` | **Contas por Data de Pagamento** | ✅ **ATIVO** |
| `/contas/contas-por-data-vencimento/` | **Contas por Data de Vencimento** | ✅ **ATIVO** |

### **📈 Dados Disponíveis:**
- **ContasPagar:** 2.699 registros
- **ContasReceber:** 1.909 registros  
- **Total:** 4.608 contas no sistema

---

## 🔍 **1. ENDPOINT: CONTAS POR DATA DE PAGAMENTO**

### **📍 URL:**
```
GET /contas/contas-por-data-pagamento/
```

### **🎯 Funcionalidade:**
Filtra contas a pagar e receber por **data de pagamento efetivo**

### **📋 Parâmetros:**

| Parâmetro | Obrigatório | Tipo | Descrição | Valores Aceitos |
|-----------|-------------|------|-----------|-----------------|
| `data_inicio` | ✅ **SIM** | string | Data inicial | YYYY-MM-DD |
| `data_fim` | ✅ **SIM** | string | Data final | YYYY-MM-DD |
| `tipo` | ❌ Não | string | Tipo de conta | `pagar`, `receber`, `ambos` (padrão) |
| `status` | ❌ Não | string | Status da conta | `P` (Pago), `A` (Aberto), `C` (Cancelado), `TODOS` (padrão: `P`) |

### **📤 Exemplo de Requisição:**
```bash
GET /contas/contas-por-data-pagamento/?data_inicio=2025-01-01&data_fim=2025-01-31&tipo=ambos&status=P
```

### **📥 Exemplo de Resposta:**
```json
{
    "periodo": {
        "data_inicio": "2025-01-01",
        "data_fim": "2025-01-31"
    },
    "filtros": {
        "tipo": "ambos",
        "status": "P"
    },
    "resumo": {
        "total_contas_pagar": 45,
        "valor_total_pagar": 125000.00,
        "total_contas_receber": 32,
        "valor_total_receber": 98000.00,
        "saldo_liquido": -27000.00
    },
    "contas_a_pagar": [
        {
            "id": 123,
            "fornecedor": {
                "id": 5,
                "nome": "Fornecedor Exemplo"
            },
            "valor_pago": 5000.00,
            "data_pagamento": "2025-01-15T09:30:00Z",
            "descricao": "Pagamento de serviços",
            "status": "P"
        }
    ],
    "contas_a_receber": [
        {
            "id": 456,
            "cliente": {
                "id": 12,
                "nome": "Cliente Exemplo"
            },
            "recebido": 3000.00,
            "data_pagamento": "2025-01-10T14:20:00Z",
            "descricao": "Recebimento de venda",
            "status": "P"
        }
    ]
}
```

---

## 🔍 **2. ENDPOINT: CONTAS POR DATA DE VENCIMENTO**

### **📍 URL:**
```
GET /contas/contas-por-data-vencimento/
```

### **🎯 Funcionalidade:**
Filtra contas a pagar e receber por **data de vencimento**

### **📋 Parâmetros:**

| Parâmetro | Obrigatório | Tipo | Descrição | Valores Aceitos |
|-----------|-------------|------|-----------|-----------------|
| `data_inicio` | ✅ **SIM** | string | Data inicial | YYYY-MM-DD |
| `data_fim` | ✅ **SIM** | string | Data final | YYYY-MM-DD |
| `tipo` | ❌ Não | string | Tipo de conta | `pagar`, `receber`, `ambos` (padrão) |
| `status` | ❌ Não | string | Status da conta | `P` (Pago), `A` (Aberto), `C` (Cancelado), `TODOS` (padrão: `A`) |
| `incluir_vencidas` | ❌ Não | boolean | Incluir vencidas | `true` (padrão), `false` |

### **📤 Exemplo de Requisição:**
```bash
GET /contas/contas-por-data-vencimento/?data_inicio=2025-01-01&data_fim=2025-01-31&tipo=pagar&status=A&incluir_vencidas=true
```

### **📥 Exemplo de Resposta:**
```json
{
    "periodo": {
        "data_inicio": "2025-01-01",
        "data_fim": "2025-01-31"
    },
    "filtros": {
        "tipo": "pagar",
        "status": "A",
        "incluir_vencidas": true
    },
    "resumo": {
        "total_contas_pagar": 28,
        "valor_total_pagar": 87500.00,
        "contas_vencidas": 5,
        "valor_vencido": 15000.00,
        "contas_vencer": 23,
        "valor_a_vencer": 72500.00
    },
    "contas_a_pagar": [
        {
            "id": 789,
            "fornecedor": {
                "id": 8,
                "nome": "Fornecedor ABC"
            },
            "valor": 2500.00,
            "data_vencimento": "2025-01-20",
            "descricao": "Fatura mensal",
            "status": "A",
            "dias_vencimento": -5,
            "situacao": "vencida"
        }
    ]
}
```

---

## 📊 **CASOS DE USO PRÁTICOS**

### **💰 1. Controle de Fluxo de Caixa**
```bash
# Consultar pagamentos realizados no mês
GET /contas/contas-por-data-pagamento/?data_inicio=2025-01-01&data_fim=2025-01-31&status=P
```

### **⏰ 2. Contas a Vencer**
```bash
# Ver contas em aberto que vencem nos próximos 30 dias
GET /contas/contas-por-data-vencimento/?data_inicio=2025-01-09&data_fim=2025-02-08&status=A
```

### **🚨 3. Inadimplência**
```bash
# Contas vencidas e não pagas
GET /contas/contas-por-data-vencimento/?data_inicio=2024-01-01&data_fim=2025-01-08&status=A&incluir_vencidas=true
```

### **📈 4. Relatório Financeiro**
```bash
# Visão completa do período - entradas e saídas
GET /contas/contas-por-data-pagamento/?data_inicio=2025-01-01&data_fim=2025-01-31&tipo=ambos&status=TODOS
```

---

## ⚙️ **PARÂMETROS DE STATUS**

### **📋 Status das Contas:**
- **`P`** - **Pago/Recebido:** Conta quitada
- **`A`** - **Aberto:** Conta pendente de pagamento/recebimento
- **`C`** - **Cancelado:** Conta cancelada
- **`TODOS`** - **Todos os status:** Sem filtro de status

### **📋 Tipos de Conta:**
- **`pagar`** - Apenas contas a pagar
- **`receber`** - Apenas contas a receber  
- **`ambos`** - Contas a pagar e receber (padrão)

---

## 🔗 **ENDPOINTS RELACIONADOS**

### **📊 Outros Endpoints Financeiros:**
- `/contas/relatorio-financeiro/` - Relatório financeiro consolidado
- `/contas/fluxo-caixa/` - Fluxo de caixa completo
- `/contas/analise-fluxo-caixa/` - Análise avançada do fluxo de caixa

---

## ⚠️ **OBSERVAÇÕES IMPORTANTES**

### **🚫 ViewSets NÃO Registrados:**
- Os ViewSets `ContasPagarViewSet` e `ContasReceberViewSet` **EXISTEM** mas **NÃO estão registrados** no router
- Para acesso CRUD completo, seria necessário registrar:
```python
router.register(r'contas-pagar', ContasPagarViewSet)
router.register(r'contas-receber', ContasReceberViewSet)
```

### **✅ Funcionalidades Disponíveis Atualmente:**
- ✅ Consulta por data de pagamento
- ✅ Consulta por data de vencimento
- ✅ Filtros por tipo e status
- ✅ Totalizadores e resumos
- ✅ Dados relacionados (fornecedor/cliente)

### **❌ Funcionalidades NÃO Disponíveis:**
- ❌ CRUD individual de contas (criar, editar, excluir)
- ❌ Listagem completa sem filtros de data
- ❌ Endpoints de ações específicas (baixa, estorno, etc.)

---

## 🎯 **CONCLUSÃO**

**RESPOSTA DIRETA:** Os endpoints que mostram contas a pagar e contas a receber são:

1. **`/contas/contas-por-data-pagamento/`** - Para consultar por data de pagamento
2. **`/contas/contas-por-data-vencimento/`** - Para consultar por data de vencimento

Ambos endpoints estão **funcionais** e permitem filtrar por período, tipo de conta e status, fornecendo dados completos para controle financeiro e fluxo de caixa.
