# 📊 Endpoint: Contas Não Pagas Por Data de Corte

## 🎯 **O QUE ESTE ENDPOINT RETORNA**

O endpoint `contas-nao-pagas-por-data-corte` retorna uma **análise completa das contas a pagar e a receber não pagas**, divididas em dois períodos baseados em uma **data de corte** que você especifica.

---

## 📍 **URL DO ENDPOINT**
```
GET /contas/contas-nao-pagas-por-data-corte/
```

---

## 🔧 **PARÂMETROS OBRIGATÓRIOS E OPCIONAIS**

| Parâmetro | Tipo | Obrigatório | Descrição | Exemplo |
|-----------|------|-------------|-----------|---------|
| `data_corte` | String | ✅ **SIM** | Data de referência (YYYY-MM-DD) | `2024-06-01` |
| `tipo` | String | ❌ Não | Filtro: 'pagar', 'receber' ou 'ambos' | `ambos` (padrão) |
| `incluir_canceladas` | Boolean | ❌ Não | Incluir contas canceladas | `false` (padrão) |
| `filtrar_por_data_emissao` | Boolean | ❌ Não | Filtrar apenas contas com data de emissão anterior à data de corte | `false` (padrão) |

---

## 📊 **ESTRUTURA COMPLETA DA RESPOSTA**

### **🏷️ 1. Cabeçalho com Filtros Aplicados**
```json
{
  "data_corte": "2024-06-01",
  "filtros": {
    "tipo": "ambos",
    "incluir_canceladas": false,
    "filtrar_por_data_emissao": false
  }
}
```

### **📈 2. Resumo Geral por Período**
```json
{
  "resumo_geral": {
    "antes_data_corte": {
      "total_contas_pagar": 0,         // Quantidade de contas a pagar
      "valor_total_pagar": 0.0,        // Valor total a pagar
      "total_contas_receber": 12,      // Quantidade de contas a receber  
      "valor_total_receber": 10024.09, // Valor total a receber
      "total_fornecedores": 0,         // Fornecedores distintos
      "total_clientes": 7,             // Clientes distintos
      "saldo_liquido": 10024.09,       // Saldo líquido do período
      "custos_por_tipo": {             // 🆕 NOVO: Análise por tipo de custo
        "FIXO": {
          "total_contas": 0,
          "valor_total": 0.0
        },
        "VARIÁVEL": {
          "total_contas": 0,
          "valor_total": 0.0
        },
        "NÃO CLASSIFICADO": {
          "total_contas": 0,
          "valor_total": 0.0
        }
      }
    },
    "depois_data_corte": {
      "total_contas_pagar": 166,       // Quantidade de contas a pagar
      "valor_total_pagar": 143072.84,  // Valor total a pagar
      "total_contas_receber": 379,     // Quantidade de contas a receber
      "valor_total_receber": 194333.51, // Valor total a receber
      "total_fornecedores": 29,        // Fornecedores distintos
      "total_clientes": 40,            // Clientes distintos
      "saldo_liquido": 51260.67,       // Saldo líquido do período
      "custos_por_tipo": {             // 🆕 NOVO: Análise por tipo de custo
        "FIXO": {
          "total_contas": 148,
          "valor_total": 131519.0
        },
        "VARIÁVEL": {
          "total_contas": 76,
          "valor_total": 73622.82
        },
        "NÃO CLASSIFICADO": {
          "total_contas": 22,
          "valor_total": 4551.58
        }
      }
    },
    "saldo_total": 61284.76            // Saldo geral (antes + depois)
  }
}
```

### **📋 3. Detalhamento Por Fornecedor (Contas a Pagar)**
```json
{
  "detalhamento": {
    "contas_a_pagar": {
      "antes_data_corte": [], // Lista vazia (nenhuma conta antes de jun/2024)
      "depois_data_corte": [
        {
          "fornecedor": {
            "id": 43,
            "nome": "FOLHA FIXA",
            "cnpj_cpf": null,
            "especificacao": "SALARIOS",        // 🔑 AGRUPADO POR ESPECIFICAÇÃO
            "tipo_custo": "FIXO"                // 🆕 NOVO: Classificação do custo
          },
          "total_contas": 5,                 // Quantidade de títulos
          "valor_total": 41430.95,           // Valor total dos títulos
          "periodo_vencimento": {
            "menor_data": "2025-09-05",      // Vencimento mais próximo
            "maior_data": "2026-01-05"       // Vencimento mais distante
          }
        }
      ]
    }
  }
}
```

### **📋 4. Detalhamento Por Cliente (Contas a Receber)**
```json
{
  "contas_a_receber": {
    "antes_data_corte": [
      {
        "cliente": {
          "id": 5562,
          "nome": "CONAP - CONTAB.ASSESSORIA E PROCESSAMENTO S/S - ME",
          "cnpj_cpf": "63501860000129"
        },
        "total_contas": 1,               // Quantidade de títulos
        "valor_total": 5465.5,          // Valor total dos títulos
        "periodo_vencimento": {
          "menor_data": "2024-04-24",    // Vencimento mais próximo
          "maior_data": "2024-04-24"     // Vencimento mais distante
        }
      }
    ],
    "depois_data_corte": [
      {
        "cliente": {
          "id": 4771,
          "nome": "INSTITUTO CENTRO DE ENSINO TECNOLOGICO - CENTEC",
          "cnpj_cpf": "03021597000149"
        },
        "total_contas": 10,
        "valor_total": 102825.28,       // 💰 MAIOR VALOR A RECEBER
        "periodo_vencimento": {
          "menor_data": "2025-08-18",
          "maior_data": "2026-05-01"
        }
      }
    ]
  }
}
```

### **📊 5. Metadados da Consulta**
```json
{
  "metadados": {
    "data_consulta": "2025-09-10T05:48:32.445352",
    "total_registros_antes": 12,      // Total de registros antes da data
    "total_registros_depois": 545     // Total de registros depois da data
  }
}
```

---

## 💰 **DADOS REAIS DO SISTEMA (Exemplo com data_corte=2024-06-01)**

### **📊 Resumo Financeiro:**
- **💸 A Pagar (depois jun/2024):** R$ 143.072,84 (166 contas)
- **💰 A Receber (antes jun/2024):** R$ 10.024,09 (12 contas) 
- **💰 A Receber (depois jun/2024):** R$ 194.333,51 (379 contas)
- **💹 SALDO LÍQUIDO TOTAL:** R$ 61.284,76 (positivo = mais a receber)

### **🏆 Maiores Valores:**

#### **💸 Contas a Pagar:**
- **FOLHA FIXA:** R$ 41.430,95 (5 contas)
- **SIMPLES NACIONAL:** R$ 18.392,92 (5 contas)
- **PRO-LABORE LUINA:** R$ 13.627,23 (5 contas)

#### **💰 Contas a Receber:**
- **INSTITUTO CENTEC:** R$ 102.825,28 (10 contas)
- **SIND.TRAB.SERV.PUBLICO FEDERAL:** R$ 11.533,85 (14 contas)
- **SANTANENSE ENSINO:** R$ 10.105,00 (7 contas)

---

## � **NOVA FUNCIONALIDADE: CLASSIFICAÇÃO DE CUSTOS FIXOS E VARIÁVEIS**

### **🎯 O que foi adicionado:**
O endpoint agora classifica automaticamente todos os fornecedores como **CUSTOS FIXOS**, **CUSTOS VARIÁVEIS** ou **NÃO CLASSIFICADO** baseado na especificação.

### **📊 Classificação Automática:**

#### **💰 CUSTOS FIXOS:**
- **SALARIOS** - Folha de pagamento
- **PRO-LABORE** - Remuneração de sócios
- **HONOR. CONTABEIS** - Honorários contábeis
- **LUZ, AGUA, TELEFONE** - Utilidades básicas
- **IMPOSTOS, ENCARGOS** - Obrigações fiscais
- **REFEICAO, BENEFICIOS** - Benefícios de funcionários
- **OUTRAS DESPESAS** - Despesas administrativas gerais
- **MAT. DE ESCRITORIO** - Material de escritório
- **PAGTO SERVICOS** - Pagamento de serviços
- **EMPRESTIMO, DESP. FINANCEIRAS** - Custos financeiros

#### **📈 CUSTOS VARIÁVEIS:**
- **FORNECEDORES** - Compras de mercadorias/produtos
- **FRETE** - Transporte de mercadorias
- **COMISSOES** - Comissões sobre vendas
- **DESP. VEICULOS** - Despesas variáveis com veículos

### **📊 Exemplo Prático (dados reais - data_corte=2024-06-01):**
```json
{
  "custos_por_tipo": {
    "FIXO": {
      "total_contas": 148,
      "valor_total": 131519.0       // R$ 131.519,00 (63%)
    },
    "VARIÁVEL": {
      "total_contas": 76,
      "valor_total": 73622.82       // R$ 73.622,82 (35%)
    },
    "NÃO CLASSIFICADO": {
      "total_contas": 22,
      "valor_total": 4551.58        // R$ 4.551,58 (2%)
    }
  }
}
```

### **💡 Insights dos Dados Reais:**
- **📊 Distribuição:** 63% custos fixos, 35% custos variáveis, 2% não classificados
- **🔧 Fixos Dominantes:** Empresa tem estrutura de custos fixos alta
- **📈 Oportunidades:** Custos variáveis podem ser otimizados conforme demanda

### **🏢 Exemplos por Categoria:**

#### **💰 Custos Fixos Identificados:**
- CAGECE - Água (AGUA)
- FOLHA FIXA - Salários (SALARIOS)
- SIMPLES NACIONAL - Impostos (IMPOSTOS)
- COELCE - Energia (LUZ)

#### **📈 Custos Variáveis Identificados:**
- COGRA DISTRIBUIDORA - Mercadorias (FORNECEDORES)
- COMISSAO CONTRATOS/VENDAS (COMISSOES)
- MANUTENÇÃO VEICULOS (DESP. VEICULOS)

---

## �🎯 **CASOS DE USO PRÁTICOS (ATUALIZADOS)**

### **💼 1. Análise de Fluxo de Caixa**
```bash
GET /contas/contas-nao-pagas-por-data-corte/?data_corte=2024-12-31&tipo=ambos
```
**Para:** Ver posição financeira antes/depois do fim do ano

### **📅 2. Contas Vencidas vs Futuras**
```bash
GET /contas/contas-nao-pagas-por-data-corte/?data_corte=2025-09-10&tipo=ambos
```
**Para:** Separar contas vencidas (antes) das futuras (depois da data atual)

### **💸 3. Análise Apenas de Pagamentos**
```bash
GET /contas/contas-nao-pagas-por-data-corte/?data_corte=2024-06-01&tipo=pagar
```
**Para:** Focar apenas nas contas a pagar

### **💰 4. Análise Apenas de Recebimentos**
```bash
GET /contas/contas-nao-pagas-por-data-corte/?data_corte=2024-06-01&tipo=receber
```
**Para:** Focar apenas nas contas a receber

### **🆕 5. Filtro por Data de Emissão - Contas Antigas**
```bash
GET /contas/contas-nao-pagas-por-data-corte/?data_corte=2024-06-01&tipo=ambos&filtrar_por_data_emissao=true
```
**Para:** Analisar apenas contas emitidas antes da data de corte

### **🔍 6. Auditoria de Contas Antigas a Pagar**
```bash
GET /contas/contas-nao-pagas-por-data-corte/?data_corte=2024-01-01&tipo=pagar&filtrar_por_data_emissao=true
```
**Para:** Identificar contas a pagar emitidas antes de 2024 e ainda em aberto

### **🆕 7. Análise de Custos Fixos vs Variáveis**
```bash
GET /contas/contas-nao-pagas-por-data-corte/?data_corte=2024-06-01&tipo=pagar
```
**Para:** Analisar distribuição entre custos fixos (63%) e variáveis (35%)

### **💼 8. Planejamento de Fluxo de Caixa por Tipo de Custo**
```bash
GET /contas/contas-nao-pagas-por-data-corte/?data_corte=2025-12-31&tipo=pagar
```
**Para:** Projetar custos fixos obrigatórios vs custos variáveis controláveis

### **📊 9. Otimização de Custos Variáveis**
```bash
GET /contas/contas-nao-pagas-por-data-corte/?data_corte=2025-09-10&tipo=pagar
```
**Para:** Identificar fornecedores variáveis para negociação e otimização

---

## 🆕 **NOVO FILTRO: DATA DE EMISSÃO**

### **🎯 O que faz:**
O parâmetro `filtrar_por_data_emissao=true` filtra **apenas as contas que foram emitidas antes da data de corte**.

### **📊 Comportamento:**
- **Sem filtro:** Analisa todas as contas não pagas (independente da data de emissão)
- **Com filtro:** Analisa apenas contas emitidas antes da `data_corte` E que têm data de emissão preenchida

### **💡 Casos de Uso:**
- **Auditoria:** Ver apenas contas antigas já emitidas
- **Análise Temporal:** Focar em contas de determinado período de emissão
- **Limpeza:** Identificar contas emitidas há muito tempo e ainda em aberto

### **📈 Exemplo Prático (data_corte=2024-06-01):**
```bash
# Sem filtro: 246 contas a pagar
GET /contas/contas-nao-pagas-por-data-corte/?data_corte=2024-06-01&tipo=pagar

# Com filtro: apenas 10 contas a pagar emitidas antes de jun/2024
GET /contas/contas-nao-pagas-por-data-corte/?data_corte=2024-06-01&tipo=pagar&filtrar_por_data_emissao=true
```

**Resultados Reais:**
- **Contas a Pagar (sem filtro):** 11 antes + 246 depois = 257 total
- **Contas a Pagar (com filtro):** 10 antes + 0 depois = 10 total (apenas as antigas)
- **Contas a Receber (com filtro):** 12 antes + 0 depois = 12 total (apenas as antigas)

---

## 🔍 **PRINCIPAIS INSIGHTS QUE O ENDPOINT FORNECE**

### **📊 1. Análise Temporal**
- **Contas Vencidas:** Todas antes da data de corte
- **Contas Futuras:** Todas depois da data de corte
- **Distribuição no Tempo:** Menores e maiores datas de vencimento

### **🏢 2. Análise por Fornecedor/Cliente**
- **Agrupamento:** Contas consolidadas por fornecedor/cliente
- **Especificação:** Contas a pagar agrupadas por tipo de despesa
- **Concentração:** Identificação dos maiores devedores/credores

### **💰 3. Análise Financeira**
- **Saldo Líquido:** Diferença entre a receber e a pagar
- **Posição por Período:** Situação financeira antes/depois da data
- **Valores Totais:** Somatórios por categoria e período

### **📈 4. Análise Operacional**
- **Quantidade de Títulos:** Volume de contas por período
- **Diversificação:** Número de fornecedores/clientes únicos
- **Concentração de Riscos:** Identificação de grandes exposições

### **🆕 5. Análise de Custos por Tipo**
- **Custos Fixos:** Despesas obrigatórias e recorrentes (salários, impostos, utilidades)
- **Custos Variáveis:** Despesas controláveis conforme demanda (fornecedores, fretes, comissões)
- **Distribuição Percentual:** Proporção entre custos fixos e variáveis
- **Oportunidades de Otimização:** Identificação de custos variáveis para negociação

---

## ⚙️ **CARACTERÍSTICAS TÉCNICAS**

### **🔧 Filtros Aplicados:**
- **Status:** Apenas contas com status 'A' (Abertas/Não Pagas)
- **Canceladas:** Excluídas por padrão (incluir_canceladas=false)
- **Agrupamento:** Por fornecedor/cliente com agregações

### **📊 Agregações Calculadas:**
- **Contagem:** Total de contas por entidade
- **Soma:** Valor total por entidade
- **Mín/Máx:** Datas de vencimento extremas por entidade

### **🔗 Relacionamentos:**
- **Contas a Pagar ← Fornecedor** (com especificação)
- **Contas a Receber ← Cliente**
- **Select Related:** Otimização de consultas

---

## 🎉 **RESUMO EXECUTIVO**

✅ **Função Principal:** Análise temporal de contas não pagas  
✅ **Divisão Temporal:** Antes/depois de uma data de corte  
✅ **Agrupamento:** Por fornecedor (com especificação) e cliente  
✅ **Cálculos:** Saldos líquidos e totais agregados  
✅ **Filtros:** Por tipo (pagar/receber/ambos) e inclusão de canceladas  
✅ **Metadados:** Informações da consulta e totais de registros  

**Ideal para:** Gestão de fluxo de caixa, análise de inadimplência, planejamento financeiro e controle de posição por fornecedor/cliente.
