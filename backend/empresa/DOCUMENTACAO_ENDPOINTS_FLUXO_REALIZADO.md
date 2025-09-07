# Documentação dos Endpoints de Fluxo de Caixa Realizado

## Visão Geral

Foram criados 2 novos endpoints para análise do fluxo de caixa baseado em dados realizados (movimentações efetivamente pagas/recebidas):

1. **Fluxo de Caixa Realizado** (`/api/fluxo-caixa-realizado/`)
2. **Análise de Fluxo de Caixa** (`/api/analise-fluxo-caixa/`)

## 1. Fluxo de Caixa Realizado

### Base URL: `/api/fluxo-caixa-realizado/`

#### 1.1 Movimentações Realizadas
**Endpoint:** `GET /api/fluxo-caixa-realizado/movimentacoes_realizadas/`

**Descrição:** Retorna todas as movimentações de entrada e saída que foram efetivamente realizadas no período.

**Parâmetros:**
- `data_inicio` (obrigatório): Data inicial no formato YYYY-MM-DD
- `data_fim` (obrigatório): Data final no formato YYYY-MM-DD

**Exemplo de uso:**
```
GET /api/fluxo-caixa-realizado/movimentacoes_realizadas/?data_inicio=2025-01-01&data_fim=2025-01-31
```

**Resposta:**
```json
{
  "periodo": {
    "data_inicio": "2025-01-01",
    "data_fim": "2025-01-31"
  },
  "resumo": {
    "total_entradas": 150000.00,
    "total_saidas": 120000.00,
    "saldo_liquido": 30000.00,
    "total_movimentacoes": 45
  },
  "movimentacoes": [
    {
      "id": "cr_123",
      "tipo": "entrada",
      "data_pagamento": "2025-01-15T10:30:00Z",
      "valor": 5000.00,
      "contraparte": "Cliente ABC Ltda",
      "historico": "Pagamento da NF 001234",
      "forma_pagamento": "PIX",
      "origem": "contas_receber"
    },
    {
      "id": "cp_456",
      "tipo": "saida",
      "data_pagamento": "2025-01-15T14:20:00Z",
      "valor": 2500.00,
      "contraparte": "Fornecedor XYZ",
      "historico": "Pagamento de material",
      "forma_pagamento": "Transferência",
      "origem": "contas_pagar"
    }
  ]
}
```

#### 1.2 Resumo Mensal
**Endpoint:** `GET /api/fluxo-caixa-realizado/resumo_mensal/`

**Descrição:** Retorna resumo consolidado por mês das movimentações realizadas.

**Parâmetros:**
- `data_inicio` (obrigatório): Data inicial no formato YYYY-MM-DD
- `data_fim` (obrigatório): Data final no formato YYYY-MM-DD

**Exemplo de uso:**
```
GET /api/fluxo-caixa-realizado/resumo_mensal/?data_inicio=2025-01-01&data_fim=2025-06-30
```

**Resposta:**
```json
{
  "periodo": {
    "data_inicio": "2025-01-01",
    "data_fim": "2025-06-30"
  },
  "totais": {
    "total_entradas": 750000.00,
    "total_saidas": 650000.00,
    "saldo_liquido": 100000.00
  },
  "resumo_mensal": [
    {
      "mes": "2025-01",
      "entradas": 120000.00,
      "saidas": 100000.00,
      "saldo_liquido": 20000.00,
      "qtd_entradas": 15,
      "qtd_saidas": 12
    },
    {
      "mes": "2025-02",
      "entradas": 130000.00,
      "saidas": 110000.00,
      "saldo_liquido": 20000.00,
      "qtd_entradas": 18,
      "qtd_saidas": 14
    }
  ]
}
```

#### 1.3 Resumo Diário
**Endpoint:** `GET /api/fluxo-caixa-realizado/resumo_diario/`

**Descrição:** Retorna resumo consolidado por dia das movimentações realizadas.

**Parâmetros:**
- `data_inicio` (obrigatório): Data inicial no formato YYYY-MM-DD
- `data_fim` (obrigatório): Data final no formato YYYY-MM-DD

**Exemplo de uso:**
```
GET /api/fluxo-caixa-realizado/resumo_diario/?data_inicio=2025-01-01&data_fim=2025-01-31
```

#### 1.4 Movimentações com Vencimento em Aberto
**Endpoint:** `GET /api/fluxo-caixa-realizado/movimentacoes_vencimento_aberto/`

**Descrição:** Retorna movimentações com data de vencimento dentro do período que estão em aberto (ainda não pagas/recebidas).

**Parâmetros:**
- `data_inicio` (obrigatório): Data inicial no formato YYYY-MM-DD
- `data_fim` (obrigatório): Data final no formato YYYY-MM-DD

**Exemplo de uso:**
```
GET /api/fluxo-caixa-realizado/movimentacoes_vencimento_aberto/?data_inicio=2025-01-01&data_fim=2025-01-31
```

**Resposta:**
```json
{
  "periodo": {
    "data_inicio": "2025-01-01",
    "data_fim": "2025-01-31"
  },
  "resumo": {
    "total_entradas_pendentes": 85000.00,
    "total_saidas_pendentes": 45000.00,
    "saldo_liquido_pendente": 40000.00,
    "total_movimentacoes": 23
  },
  "estatisticas_vencimento": {
    "no_prazo": {
      "entradas": 50000.00,
      "saidas": 25000.00,
      "qtd_entradas": 8,
      "qtd_saidas": 5
    },
    "vence_em_breve": {
      "entradas": 20000.00,
      "saidas": 10000.00,
      "qtd_entradas": 3,
      "qtd_saidas": 2
    },
    "vencido": {
      "entradas": 15000.00,
      "saidas": 10000.00,
      "qtd_entradas": 4,
      "qtd_saidas": 1
    }
  },
  "movimentacoes_abertas": [
    {
      "id": "cr_789",
      "tipo": "entrada_pendente",
      "data_emissao": "2025-01-10T00:00:00Z",
      "data_vencimento": "2025-01-25T00:00:00Z",
      "valor": 12000.00,
      "contraparte": "Cliente XYZ",
      "historico": "Fatura mensal",
      "forma_pagamento": "Boleto",
      "origem": "contas_receber",
      "dias_vencimento": -5,
      "status_vencimento": "vencido"
    },
    {
      "id": "cp_321",
      "tipo": "saida_pendente",
      "data_emissao": "2025-01-15T00:00:00Z",
      "data_vencimento": "2025-01-30T00:00:00Z",
      "valor": 8000.00,
      "contraparte": "Fornecedor ABC",
      "historico": "Material de construção",
      "forma_pagamento": "Transferência",
      "origem": "contas_pagar",
      "dias_vencimento": 2,
      "status_vencimento": "vence_em_breve"
    }
  ]
}
```

**Status de Vencimento:**
- `no_prazo`: Contas que vencem em mais de 3 dias
- `vence_em_breve`: Contas que vencem em até 3 dias
- `vencido`: Contas que já passaram da data de vencimento

## 2. Análise de Fluxo de Caixa

### Base URL: `/api/analise-fluxo-caixa/`

#### 2.1 Comparativo Realizado vs Previsto
**Endpoint:** `GET /api/analise-fluxo-caixa/comparativo_realizado_vs_previsto/`

**Descrição:** Compara o que foi efetivamente realizado vs o que estava previsto no período.

**Parâmetros:**
- `data_inicio` (obrigatório): Data inicial no formato YYYY-MM-DD
- `data_fim` (obrigatório): Data final no formato YYYY-MM-DD

**Exemplo de uso:**
```
GET /api/analise-fluxo-caixa/comparativo_realizado_vs_previsto/?data_inicio=2025-01-01&data_fim=2025-01-31
```

**Resposta:**
```json
{
  "periodo": {
    "data_inicio": "2025-01-01",
    "data_fim": "2025-01-31"
  },
  "realizado": {
    "entradas": 150000.00,
    "saidas": 120000.00,
    "saldo_liquido": 30000.00,
    "qtd_contas_recebidas": 25,
    "qtd_contas_pagas": 20
  },
  "previsto": {
    "entradas": 180000.00,
    "saidas": 140000.00,
    "saldo_liquido": 40000.00,
    "qtd_contas_a_receber": 35,
    "qtd_contas_a_pagar": 28
  },
  "analise": {
    "diferenca_entradas": -30000.00,
    "diferenca_saidas": -20000.00,
    "diferenca_saldo": -10000.00,
    "percentual_realizacao_entradas": 83.33,
    "percentual_realizacao_saidas": 85.71
  }
}
```

#### 2.2 Análise de Inadimplência
**Endpoint:** `GET /api/analise-fluxo-caixa/inadimplencia/`

**Descrição:** Analisa contas vencidas e não pagas/recebidas (inadimplência).

**Parâmetros:**
- `data_limite` (opcional): Data limite para considerar inadimplência (default: hoje)

**Exemplo de uso:**
```
GET /api/analise-fluxo-caixa/inadimplencia/?data_limite=2025-01-31
```

**Resposta:**
```json
{
  "data_referencia": "2025-01-31",
  "resumo": {
    "total_contas_pagar_atraso": 45000.00,
    "qtd_contas_pagar_atraso": 8,
    "total_contas_receber_atraso": 85000.00,
    "qtd_contas_receber_atraso": 12,
    "impacto_saldo": 40000.00
  },
  "analise_por_faixas": [
    {
      "faixa": "1-30 dias",
      "contas_pagar": {
        "total": 15000.00,
        "quantidade": 3
      },
      "contas_receber": {
        "total": 25000.00,
        "quantidade": 4
      }
    },
    {
      "faixa": "31-60 dias",
      "contas_pagar": {
        "total": 20000.00,
        "quantidade": 3
      },
      "contas_receber": {
        "total": 35000.00,
        "quantidade": 5
      }
    }
  ],
  "detalhes": {
    "contas_pagar_atraso": [...],
    "contas_receber_atraso": [...]
  }
}
```

#### 2.3 Projeção Semanal
**Endpoint:** `GET /api/analise-fluxo-caixa/projecao_semanal/`

**Descrição:** Projeta o fluxo de caixa para as próximas semanas baseado nas contas em aberto.

**Parâmetros:**
- `semanas` (opcional): Número de semanas para projetar (default: 4)

**Exemplo de uso:**
```
GET /api/analise-fluxo-caixa/projecao_semanal/?semanas=6
```

**Resposta:**
```json
{
  "periodo_projecao": "6 semanas",
  "resumo_geral": {
    "total_entradas_projetadas": 420000.00,
    "total_saidas_projetadas": 380000.00,
    "saldo_total_projetado": 40000.00
  },
  "projecoes_semanais": [
    {
      "semana": 1,
      "periodo": {
        "inicio": "2025-02-01",
        "fim": "2025-02-07"
      },
      "entradas_previstas": 75000.00,
      "saidas_previstas": 65000.00,
      "saldo_previsto": 10000.00,
      "qtd_contas_receber": 12,
      "qtd_contas_pagar": 8
    }
  ]
}
```

## Características dos Endpoints

### Diferencial dos Novos Endpoints

1. **Foco em Dados Realizados**: Diferente dos endpoints existentes, estes focam apenas em movimentações que realmente aconteceram (com `data_pagamento` preenchida e status 'P').

2. **Análise Comparativa**: Permite comparar o que foi planejado vs o que foi executado.

3. **Gestão de Inadimplência**: Oferece visão detalhada de atrasos por faixas de tempo.

4. **Projeções**: Baseado em contas em aberto, projeta cenários futuros.

### Parâmetros Comuns

- **Datas**: Sempre no formato `YYYY-MM-DD`
- **Status**: 
  - 'P' = Pago/Recebido (para dados realizados)
  - 'A' = Aberto (para dados previstos)
- **Valores**: Sempre em formato decimal com 2 casas

### Filtros Aplicados

1. **Contas Realizadas**: `data_pagamento IS NOT NULL` e `status = 'P'`
2. **Contas Previstas**: `status = 'A'` e baseado na data de vencimento
3. **Inadimplência**: `vencimento < data_limite` e `status = 'A'`

## Exemplos de Uso Prático

### Dashboard Financeiro
Combinar os endpoints para criar um dashboard completo:

1. Usar `movimentacoes_realizadas` para mostrar o que aconteceu
2. Usar `comparativo_realizado_vs_previsto` para mostrar eficiência
3. Usar `inadimplencia` para alertas de cobrança
4. Usar `projecao_semanal` para planejamento

### Relatórios Gerenciais
- Relatório mensal de performance financeira
- Análise de efetividade do planejamento
- Gestão de cobrança e pagamentos
- Projeções de caixa para tomada de decisão

### Integração com Frontend
Os endpoints retornam dados estruturados ideais para:
- Gráficos de linha (evolução temporal)
- Gráficos de barras (comparativos)
- Tabelas detalhadas (listagens)
- Cards de resumo (KPIs)
