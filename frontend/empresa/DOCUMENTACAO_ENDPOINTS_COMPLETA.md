# 📖 DOCUMENTAÇÃO COMPLETA DOS ENDPOINTS

## 🌐 **URL BASE**
```
http://localhost:8000
```

---

## 📋 **ÍNDICE**

1. [🔧 Endpoints CRUD Básicos](#-endpoints-crud-básicos)
2. [📊 Endpoints de Relatórios](#-endpoints-de-relatórios)
3. [💰 Endpoints Financeiros](#-endpoints-financeiros)
4. [📦 Endpoints de Estoque](#-endpoints-de-estoque)
5. [📈 Endpoints de Fluxo de Caixa](#-endpoints-de-fluxo-de-caixa)
6. [🆕 Novos Endpoints Implementados](#-novos-endpoints-implementados)
7. [📝 Exemplos de Uso](#-exemplos-de-uso)

---

## 🔧 **ENDPOINTS CRUD BÁSICOS**

### **👥 Gestão de Pessoas**

#### **Clientes**
- **GET** `/contas/clientes/` - Lista todos os clientes
- **POST** `/contas/clientes/` - Cria novo cliente
- **GET** `/contas/clientes/{id}/` - Busca cliente específico
- **PUT** `/contas/clientes/{id}/` - Atualiza cliente
- **DELETE** `/contas/clientes/{id}/` - Remove cliente

#### **Fornecedores**
- **GET** `/contas/fornecedores/` - Lista todos os fornecedores
- **POST** `/contas/fornecedores/` - Cria novo fornecedor
- **GET** `/contas/fornecedores/{id}/` - Busca fornecedor específico
- **PUT** `/contas/fornecedores/{id}/` - Atualiza fornecedor
- **DELETE** `/contas/fornecedores/{id}/` - Remove fornecedor

#### **Funcionários**
- **GET** `/contas/funcionarios/` - Lista todos os funcionários
- **POST** `/contas/funcionarios/` - Cria novo funcionário
- **GET** `/contas/funcionarios/{id}/` - Busca funcionário específico
- **PUT** `/contas/funcionarios/{id}/` - Atualiza funcionário
- **DELETE** `/contas/funcionarios/{id}/` - Remove funcionário

#### **Empresas**
- **GET** `/contas/empresas/` - Lista todas as empresas
- **POST** `/contas/empresas/` - Cria nova empresa
- **GET** `/contas/empresas/{id}/` - Busca empresa específica
- **PUT** `/contas/empresas/{id}/` - Atualiza empresa
- **DELETE** `/contas/empresas/{id}/` - Remove empresa

#### **Transportadoras**
- **GET** `/contas/transportadoras/` - Lista todas as transportadoras
- **POST** `/contas/transportadoras/` - Cria nova transportadora
- **GET** `/contas/transportadoras/{id}/` - Busca transportadora específica
- **PUT** `/contas/transportadoras/{id}/` - Atualiza transportadora
- **DELETE** `/contas/transportadoras/{id}/` - Remove transportadora

---

### **📦 Gestão de Produtos**

#### **Produtos**
- **GET** `/contas/produtos/` - Lista todos os produtos
- **POST** `/contas/produtos/` - Cria novo produto
- **GET** `/contas/produtos/{id}/` - Busca produto específico
- **PUT** `/contas/produtos/{id}/` - Atualiza produto
- **DELETE** `/contas/produtos/{id}/` - Remove produto

**Filtros disponíveis:**
- `?disponivel_locacao=true` - Produtos disponíveis para locação
- `?categoria={categoria}` - Filtrar por categoria

#### **Categorias de Produtos**
- **GET** `/contas/categorias_produtos/` - Lista categorias de produtos
- **POST** `/contas/categorias_produtos/` - Cria nova categoria
- **GET** `/contas/categorias_produtos/{id}/` - Busca categoria específica
- **PUT** `/contas/categorias_produtos/{id}/` - Atualiza categoria
- **DELETE** `/contas/categorias_produtos/{id}/` - Remove categoria

#### **Marcas**
- **GET** `/contas/marcas/` - Lista todas as marcas
- **POST** `/contas/marcas/` - Cria nova marca
- **GET** `/contas/marcas/{id}/` - Busca marca específica
- **PUT** `/contas/marcas/{id}/` - Atualiza marca
- **DELETE** `/contas/marcas/{id}/` - Remove marca

#### **Grupos**
- **GET** `/contas/grupos/` - Lista todos os grupos
- **POST** `/contas/grupos/` - Cria novo grupo
- **GET** `/contas/grupos/{id}/` - Busca grupo específico
- **PUT** `/contas/grupos/{id}/` - Atualiza grupo
- **DELETE** `/contas/grupos/{id}/` - Remove grupo

---

### **📋 Gestão Financeira**

#### **Categorias**
- **GET** `/contas/categorias/` - Lista todas as categorias
- **POST** `/contas/categorias/` - Cria nova categoria
- **GET** `/contas/categorias/{id}/` - Busca categoria específica
- **PUT** `/contas/categorias/{id}/` - Atualiza categoria
- **DELETE** `/contas/categorias/{id}/` - Remove categoria

#### **Contas a Pagar**
- **GET** `/contas/contas_pagar/` - Lista contas a pagar
- **POST** `/contas/contas_pagar/` - Cria nova conta a pagar
- **GET** `/contas/contas_pagar/{id}/` - Busca conta específica
- **PUT** `/contas/contas_pagar/{id}/` - Atualiza conta
- **DELETE** `/contas/contas_pagar/{id}/` - Remove conta

#### **Contas a Receber**
- **GET** `/contas/contas_receber/` - Lista contas a receber
- **POST** `/contas/contas_receber/` - Cria nova conta a receber
- **GET** `/contas/contas_receber/{id}/` - Busca conta específica
- **PUT** `/contas/contas_receber/{id}/` - Atualiza conta
- **DELETE** `/contas/contas_receber/{id}/` - Remove conta

#### **Despesas**
- **GET** `/contas/despesas/` - Lista todas as despesas
- **POST** `/contas/despesas/` - Cria nova despesa
- **GET** `/contas/despesas/{id}/` - Busca despesa específica
- **PUT** `/contas/despesas/{id}/` - Atualiza despesa
- **DELETE** `/contas/despesas/{id}/` - Remove despesa

---

### **🏢 Contratos e Locação**

#### **Contratos de Locação**
- **GET** `/contas/contratos_locacao/` - Lista contratos de locação
- **POST** `/contas/contratos_locacao/` - Cria novo contrato
- **GET** `/contas/contratos_locacao/{id}/` - Busca contrato específico
- **PUT** `/contas/contratos_locacao/{id}/` - Atualiza contrato
- **DELETE** `/contas/contratos_locacao/{id}/` - Remove contrato

#### **Itens de Contrato de Locação**
- **GET** `/contas/itens_contrato_locacao/` - Lista itens de contratos
- **POST** `/contas/itens_contrato_locacao/` - Cria novo item
- **GET** `/contas/itens_contrato_locacao/{id}/` - Busca item específico
- **PUT** `/contas/itens_contrato_locacao/{id}/` - Atualiza item
- **DELETE** `/contas/itens_contrato_locacao/{id}/` - Remove item

---

### **📋 Notas Fiscais**

#### **Notas Fiscais de Compra**
- **GET** `/contas/notas_fiscais_compra/` - Lista NFs de compra
- **POST** `/contas/notas_fiscais_compra/` - Cria nova NF de compra
- **GET** `/contas/notas_fiscais_compra/{id}/` - Busca NF específica
- **PUT** `/contas/notas_fiscais_compra/{id}/` - Atualiza NF
- **DELETE** `/contas/notas_fiscais_compra/{id}/` - Remove NF

#### **Notas Fiscais de Venda**
- **GET** `/contas/notas_fiscais_venda/` - Lista NFs de venda
- **POST** `/contas/notas_fiscais_venda/` - Cria nova NF de venda
- **GET** `/contas/notas_fiscais_venda/{id}/` - Busca NF específica
- **PUT** `/contas/notas_fiscais_venda/{id}/` - Atualiza NF
- **DELETE** `/contas/notas_fiscais_venda/{id}/` - Remove NF

#### **Itens de NF Compra**
- **GET** `/contas/itens_nf_compra/` - Lista itens de NF compra
- **POST** `/contas/itens_nf_compra/` - Cria novo item
- **GET** `/contas/itens_nf_compra/{id}/` - Busca item específico
- **PUT** `/contas/itens_nf_compra/{id}/` - Atualiza item
- **DELETE** `/contas/itens_nf_compra/{id}/` - Remove item

#### **Itens de NF Venda**
- **GET** `/contas/itens_nf_venda/` - Lista itens de NF venda
- **POST** `/contas/itens_nf_venda/` - Cria novo item
- **GET** `/contas/itens_nf_venda/{id}/` - Busca item específico
- **PUT** `/contas/itens_nf_venda/{id}/` - Atualiza item
- **DELETE** `/contas/itens_nf_venda/{id}/` - Remove item

---

### **🚚 Gestão de Frete**

#### **Fretes**
- **GET** `/contas/fretes/` - Lista todos os fretes
- **POST** `/contas/fretes/` - Cria novo frete
- **GET** `/contas/fretes/{id}/` - Busca frete específico
- **PUT** `/contas/fretes/{id}/` - Atualiza frete
- **DELETE** `/contas/fretes/{id}/` - Remove frete

#### **Tabelas de Frete**
- **GET** `/contas/tabelas_frete/` - Lista tabelas de frete
- **POST** `/contas/tabelas_frete/` - Cria nova tabela
- **GET** `/contas/tabelas_frete/{id}/` - Busca tabela específica
- **PUT** `/contas/tabelas_frete/{id}/` - Atualiza tabela
- **DELETE** `/contas/tabelas_frete/{id}/` - Remove tabela

#### **Custos Adicionais de Frete**
- **GET** `/contas/custos_adicionais_frete/` - Lista custos adicionais
- **POST** `/contas/custos_adicionais_frete/` - Cria novo custo
- **GET** `/contas/custos_adicionais_frete/{id}/` - Busca custo específico
- **PUT** `/contas/custos_adicionais_frete/{id}/` - Atualiza custo
- **DELETE** `/contas/custos_adicionais_frete/{id}/` - Remove custo

#### **Ocorrências de Frete**
- **GET** `/contas/ocorrencias_frete/` - Lista ocorrências
- **POST** `/contas/ocorrencias_frete/` - Cria nova ocorrência
- **GET** `/contas/ocorrencias_frete/{id}/` - Busca ocorrência específica
- **PUT** `/contas/ocorrencias_frete/{id}/` - Atualiza ocorrência
- **DELETE** `/contas/ocorrencias_frete/{id}/` - Remove ocorrência

#### **Regiões de Entrega**
- **GET** `/contas/regioes_entrega/` - Lista regiões de entrega
- **POST** `/contas/regioes_entrega/` - Cria nova região
- **GET** `/contas/regioes_entrega/{id}/` - Busca região específica
- **PUT** `/contas/regioes_entrega/{id}/` - Atualiza região
- **DELETE** `/contas/regioes_entrega/{id}/` - Remove região

#### **Histórico de Rastreamento**
- **GET** `/contas/historico_rastreamento/` - Lista histórico
- **POST** `/contas/historico_rastreamento/` - Cria novo registro
- **GET** `/contas/historico_rastreamento/{id}/` - Busca registro específico
- **PUT** `/contas/historico_rastreamento/{id}/` - Atualiza registro
- **DELETE** `/contas/historico_rastreamento/{id}/` - Remove registro

---

## 📦 **ENDPOINTS DE ESTOQUE**

### **Saldos de Estoque**
- **GET** `/contas/saldos_estoque/` - Lista saldos de estoque
- **POST** `/contas/saldos_estoque/` - Cria novo saldo
- **GET** `/contas/saldos_estoque/{id}/` - Busca saldo específico
- **PUT** `/contas/saldos_estoque/{id}/` - Atualiza saldo
- **DELETE** `/contas/saldos_estoque/{id}/` - Remove saldo

**Filtros disponíveis:**
- `?quantidade__gt=0` - Produtos com estoque maior que zero
- `?produto={produto_id}` - Filtrar por produto específico

### **Movimentações de Estoque**
- **GET** `/contas/movimentacoes_estoque/` - Lista movimentações
- **POST** `/contas/movimentacoes_estoque/` - Cria nova movimentação
- **GET** `/contas/movimentacoes_estoque/{id}/` - Busca movimentação específica
- **PUT** `/contas/movimentacoes_estoque/{id}/` - Atualiza movimentação
- **DELETE** `/contas/movimentacoes_estoque/{id}/` - Remove movimentação

**Filtros disponíveis:**
- `?data_movimentacao__date=YYYY-MM-DD` - Filtrar por data
- `?tipo_movimentacao={tipo}` - Filtrar por tipo

### **Posições de Estoque**
- **GET** `/contas/posicoes_estoque/` - Lista posições de estoque
- **POST** `/contas/posicoes_estoque/` - Cria nova posição
- **GET** `/contas/posicoes_estoque/{id}/` - Busca posição específica
- **PUT** `/contas/posicoes_estoque/{id}/` - Atualiza posição
- **DELETE** `/contas/posicoes_estoque/{id}/` - Remove posição

### **Locais de Estoque**
- **GET** `/contas/locais_estoque/` - Lista locais de estoque
- **POST** `/contas/locais_estoque/` - Cria novo local
- **GET** `/contas/locais_estoque/{id}/` - Busca local específico
- **PUT** `/contas/locais_estoque/{id}/` - Atualiza local
- **DELETE** `/contas/locais_estoque/{id}/` - Remove local

### **Tipos de Movimentação de Estoque**
- **GET** `/contas/tipos_movimentacao_estoque/` - Lista tipos
- **POST** `/contas/tipos_movimentacao_estoque/` - Cria novo tipo
- **GET** `/contas/tipos_movimentacao_estoque/{id}/` - Busca tipo específico
- **PUT** `/contas/tipos_movimentacao_estoque/{id}/` - Atualiza tipo
- **DELETE** `/contas/tipos_movimentacao_estoque/{id}/` - Remove tipo

---

## 📊 **ENDPOINTS DE RELATÓRIOS**

### **📈 Relatório de Valor do Estoque**
- **GET** `/contas/relatorio-valor-estoque/`
- **GET** `/contas/relatorio-valor-estoque/?data=YYYY-MM-DD`

**Resposta:**
```json
{
    "data_posicao": "2025-09-05",
    "valor_total_estoque": 1380445.68,
    "total_produtos_em_estoque": 581,
    "detalhes_por_produto": [
        {
            "produto_id": 3528,
            "produto_descricao": "ADAPTADOR T15 P/UC5&UC5E-6123LCP-T10 5309",
            "categoria": "PEÇAS",
            "quantidade_em_estoque": 1.000,
            "custo_unitario": 133.74,
            "valor_total_produto": 133.74
        }
    ]
}
```

### **💰 Relatório Financeiro por Período**
- **GET** `/contas/relatorio-financeiro/?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD`

### **📦 Suprimentos por Contrato**
- **GET** `/contas/contratos_locacao/suprimentos/?contrato_id={id}`

---

## 💰 **ENDPOINTS FINANCEIROS**

### **📊 Inventário**

#### **Inventários**
- **GET** `/contas/inventarios/` - Lista inventários
- **POST** `/contas/inventarios/` - Cria novo inventário
- **GET** `/contas/inventarios/{id}/` - Busca inventário específico
- **PUT** `/contas/inventarios/{id}/` - Atualiza inventário
- **DELETE** `/contas/inventarios/{id}/` - Remove inventário

#### **Contagens de Inventário**
- **GET** `/contas/contagens_inventario/` - Lista contagens
- **POST** `/contas/contagens_inventario/` - Cria nova contagem
- **GET** `/contas/contagens_inventario/{id}/` - Busca contagem específica
- **PUT** `/contas/contagens_inventario/{id}/` - Atualiza contagem
- **DELETE** `/contas/contagens_inventario/{id}/` - Remove contagem

#### **Lotes**
- **GET** `/contas/lotes/` - Lista lotes
- **POST** `/contas/lotes/` - Cria novo lote
- **GET** `/contas/lotes/{id}/` - Busca lote específico
- **PUT** `/contas/lotes/{id}/` - Atualiza lote
- **DELETE** `/contas/lotes/{id}/` - Remove lote

#### **Pagamentos de Funcionários**
- **GET** `/contas/pagamentos_funcionarios/` - Lista pagamentos
- **POST** `/contas/pagamentos_funcionarios/` - Cria novo pagamento
- **GET** `/contas/pagamentos_funcionarios/{id}/` - Busca pagamento específico
- **PUT** `/contas/pagamentos_funcionarios/{id}/` - Atualiza pagamento
- **DELETE** `/contas/pagamentos_funcionarios/{id}/` - Remove pagamento

---

## 📈 **ENDPOINTS DE FLUXO DE CAIXA**

### **💡 FluxoCaixaViewSet (Básico)**
- **GET** `/contas/fluxo-caixa/` - Lista lançamentos de fluxo de caixa
- **POST** `/contas/fluxo-caixa/` - Cria novo lançamento
- **GET** `/contas/fluxo-caixa/{id}/` - Busca lançamento específico
- **PUT** `/contas/fluxo-caixa/{id}/` - Atualiza lançamento
- **DELETE** `/contas/fluxo-caixa/{id}/` - Remove lançamento

### **📊 Dashboards**
- **GET** `/contas/fluxo-caixa/dashboard_comercial/` - Dashboard comercial
- **GET** `/contas/fluxo-caixa/dashboard_estrategico/` - Dashboard estratégico

### **👥 Análises de Clientes**
- **GET** `/contas/fluxo-caixa/analise_clientes/` - Análise de clientes
- **GET** `/contas/fluxo-caixa/clientes_inadimplentes/` - Clientes inadimplentes
- **GET** `/contas/fluxo-caixa/perfil_cliente/` - Perfil do cliente

### **📋 Análises de Contratos**
- **GET** `/contas/fluxo-caixa/rentabilidade_contratos/` - Rentabilidade
- **GET** `/contas/fluxo-caixa/contratos_vencendo/` - Contratos vencendo

### **📈 Relatórios e DRE**
- **GET** `/contas/fluxo-caixa/dre/` - Demonstrativo de Resultado
- **GET** `/contas/fluxo-caixa/relatorio_receitas/` - Relatório de receitas
- **GET** `/contas/fluxo-caixa/relatorio_despesas/` - Relatório de despesas
- **GET** `/contas/fluxo-caixa/relatorio_comparativo/` - Relatório comparativo

### **🔄 Operações**
- **POST** `/contas/fluxo-caixa/transferir_saldo/` - Transferir saldo
- **POST** `/contas/fluxo-caixa/conciliar_movimento/` - Conciliar movimento
- **POST** `/contas/fluxo-caixa/estornar_movimento/` - Estornar movimento
- **GET** `/contas/fluxo-caixa/resumo_periodo/` - Resumo do período

### **📊 Vendas e Estoque**
- **GET** `/contas/fluxo-caixa/analise_vendas_estoque/` - Análise vendas/estoque

---

## 📈 **FLUXO DE CAIXA AVANÇADO (FluxoCaixaLucroViewSet)**

### **🔧 Operações Básicas**
- **GET** `/contas/fluxo-caixa-lucro/` - Lista lançamentos de lucro
- **POST** `/contas/fluxo-caixa-lucro/` - Cria novo lançamento
- **GET** `/contas/fluxo-caixa-lucro/{id}/` - Busca lançamento específico
- **PUT** `/contas/fluxo-caixa-lucro/{id}/` - Atualiza lançamento
- **DELETE** `/contas/fluxo-caixa-lucro/{id}/` - Remove lançamento

### **⚡ Ações Específicas**
- **PATCH** `/contas/fluxo-caixa-lucro/{id}/realizar_movimento/` - Realizar movimento
- **POST** `/contas/fluxo-caixa-lucro/{id}/recalcular_saldos/` - Recalcular saldos

### **📊 Relatórios Avançados**
- **GET** `/contas/fluxo-caixa-lucro/relatorio_dre/?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD` - DRE
- **GET** `/contas/fluxo-caixa-lucro/projecao_fluxo/?meses=6` - Projeção de fluxo

### **🗂️ Gestão de Histórico**
- **POST** `/contas/fluxo-caixa-lucro/limpar_historico/?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD` - Limpar histórico
- **POST** `/contas/fluxo-caixa-lucro/reverter_lancamento/` - Reverter lançamento

### **📈 Cenários**
- **POST** `/contas/fluxo-caixa-lucro/cenarios/` - Análise de cenários

---

## 🆕 **NOVOS ENDPOINTS IMPLEMENTADOS**

### **💰 Relatório de Lucro por Período**
- **GET** `/contas/fluxo-caixa-lucro/relatorio-lucro/?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD`

**Parâmetros:**
- `data_inicio` (obrigatório): Data inicial (YYYY-MM-DD)
- `data_fim` (obrigatório): Data final (YYYY-MM-DD)

**Resposta:**
```json
{
    "periodo": {
        "data_inicio": "2025-08-01",
        "data_fim": "2025-08-31"
    },
    "resumo_financeiro": {
        "total_receitas": 78991.69,
        "total_despesas": 35758.55,
        "lucro_liquido": 43233.14
    },
    "detalhamento_receitas": [
        { "categoria": "vendas", "total": 45000.00 },
        { "categoria": "aluguel", "total": 25000.00 },
        { "categoria": "servicos", "total": 8991.69 }
    ],
    "detalhamento_despesas": [
        { "categoria": "compra", "total": 20000.00 },
        { "categoria": "despesas_operacionais", "total": 10000.00 },
        { "categoria": "folha_pagamento", "total": 5758.55 }
    ]
}
```

### **📅 Contas por Data de Pagamento**
- **GET** `/contas/contas-por-data-pagamento/?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD`

**Parâmetros:**
- `data_inicio` (obrigatório): Data inicial (YYYY-MM-DD)
- `data_fim` (obrigatório): Data final (YYYY-MM-DD)
- `tipo` (opcional): `pagar`, `receber`, `ambos` (padrão: `ambos`)
- `status` (opcional): `P`, `A`, `C`, `TODOS` (padrão: `P`)

**Resposta:**
```json
{
    "periodo": {
        "data_inicio": "2025-08-01",
        "data_fim": "2025-08-31"
    },
    "filtros": {
        "tipo": "ambos",
        "status": "P"
    },
    "resumo": {
        "total_contas_pagar": 75,
        "valor_total_pagar": 63674.08,
        "total_contas_receber": 63,
        "valor_total_receber": 60903.54,
        "saldo_liquido": -2770.54
    },
    "contas_a_pagar": [...],
    "contas_a_receber": [...]
}
```

### **⏰ Contas por Data de Vencimento**
- **GET** `/contas/contas-por-data-vencimento/?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD`

**Parâmetros:**
- `data_inicio` (obrigatório): Data inicial (YYYY-MM-DD)
- `data_fim` (obrigatório): Data final (YYYY-MM-DD)
- `tipo` (opcional): `pagar`, `receber`, `ambos` (padrão: `ambos`)
- `status` (opcional): `P`, `A`, `C`, `TODOS` (padrão: `A`)
- `incluir_vencidas` (opcional): `true`, `false` (padrão: `true`)

**Resposta:**
```json
{
    "periodo": {
        "data_inicio": "2025-09-03",
        "data_fim": "2025-10-03"
    },
    "filtros": {
        "tipo": "ambos",
        "status": "A",
        "incluir_vencidas": true
    },
    "resumo": {
        "total_contas_pagar": 53,
        "valor_total_pagar": 53812.12,
        "total_contas_receber": 50,
        "valor_total_receber": 38565.09,
        "contas_vencidas_pagar": 0,
        "valor_vencidas_pagar": 0.0,
        "contas_vencidas_receber": 0,
        "valor_vencidas_receber": 0.0,
        "saldo_previsto": -15247.03,
        "saldo_vencidas": 0.0
    },
    "contas_a_pagar": [...],
    "contas_a_receber": [...]
}
```

---

## 📝 **EXEMPLOS DE USO**

### **🔍 Buscando Produtos com Estoque**
```bash
GET /contas/saldos_estoque/?quantidade__gt=0
```

### **📊 Relatório de Estoque em Data Específica**
```bash
GET /contas/relatorio-valor-estoque/?data=2025-09-01
```

### **💰 Calculando Lucro de Agosto**
```bash
GET /contas/fluxo-caixa-lucro/relatorio-lucro/?data_inicio=2025-08-01&data_fim=2025-08-31
```

### **📅 Contas que Vencem nos Próximos 30 Dias**
```bash
GET /contas/contas-por-data-vencimento/?data_inicio=2025-09-05&data_fim=2025-10-05&status=A
```

### **💸 Contas Pagas em Setembro**
```bash
GET /contas/contas-por-data-pagamento/?data_inicio=2025-09-01&data_fim=2025-09-30&status=P
```

### **📦 Movimentações de Estoque de Hoje**
```bash
GET /contas/movimentacoes_estoque/?data_movimentacao__date=2025-09-05
```

### **🏢 Produtos Disponíveis para Locação**
```bash
GET /contas/produtos/?disponivel_locacao=true
```

---

## 🚀 **CÓDIGOS DE STATUS HTTP**

### **✅ Sucessos**
- **200 OK** - Requisição bem-sucedida
- **201 Created** - Recurso criado com sucesso
- **204 No Content** - Recurso deletado com sucesso

### **⚠️ Erros do Cliente**
- **400 Bad Request** - Parâmetros inválidos
- **401 Unauthorized** - Não autenticado
- **403 Forbidden** - Sem permissão
- **404 Not Found** - Recurso não encontrado
- **405 Method Not Allowed** - Método HTTP não permitido

### **🔧 Erros do Servidor**
- **500 Internal Server Error** - Erro interno do servidor

---

## 📋 **FILTROS COMUNS**

### **🗓️ Filtros de Data**
- `?data=YYYY-MM-DD` - Data específica
- `?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD` - Período
- `?data_movimentacao__date=YYYY-MM-DD` - Data de movimentação

### **🔢 Filtros Numéricos**
- `?quantidade__gt=0` - Maior que zero
- `?valor__gte=100` - Maior ou igual a 100
- `?valor__lt=1000` - Menor que 1000

### **📝 Filtros de Texto**
- `?nome__icontains=texto` - Contém texto (case-insensitive)
- `?status=A` - Status específico

### **🔗 Filtros de Relacionamento**
- `?produto={produto_id}` - Por produto específico
- `?cliente={cliente_id}` - Por cliente específico
- `?fornecedor={fornecedor_id}` - Por fornecedor específico

---

## ⚡ **PAGINAÇÃO**

Todos os endpoints de listagem suportam paginação:

### **Parâmetros**
- `?page=2` - Página específica
- `?page_size=50` - Itens por página (padrão: 20)

### **Resposta Paginada**
```json
{
    "count": 1000,
    "next": "http://localhost:8000/contas/produtos/?page=3",
    "previous": "http://localhost:8000/contas/produtos/?page=1",
    "results": [...]
}
```

---

## 🔒 **AUTENTICAÇÃO**

### **Headers Necessários**
```bash
Authorization: Bearer {token}
Content-Type: application/json
```

### **Login**
```bash
POST /auth/login/
{
    "username": "usuario",
    "password": "senha"
}
```

---

## 📞 **INFORMAÇÕES DE SUPORTE**

### **🌐 Configuração**
- **URL Base**: `http://localhost:8000`
- **Formato**: JSON
- **Encoding**: UTF-8

### **✅ Status do Sistema**
- **Sistema**: 100% Operacional
- **Endpoints**: Todos funcionando
- **Dados**: Validados com dados reais
- **Performance**: Otimizada

### **📝 Documentação Adicional**
- **Guia Frontend**: `GUIA_FRONTEND_COMPLETO.md`
- **Testes**: Scripts de teste disponíveis na pasta raiz

---

**📋 DOCUMENTAÇÃO COMPLETA DOS ENDPOINTS**  
*Última atualização: 05/09/2025*  
*Versão: 1.0*  
*Status: ✅ Todos os endpoints funcionais e testados*
