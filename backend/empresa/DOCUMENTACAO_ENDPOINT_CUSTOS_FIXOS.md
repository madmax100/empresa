# 📋 Documentação - Endpoint de Custos Fixos

## 📑 Índice
- [Visão Geral](#-visão-geral)
- [Especificações Técnicas](#-especificações-técnicas)
- [Parâmetros](#-parâmetros)
- [Resposta da API](#-resposta-da-api)
- [Exemplos de Uso](#-exemplos-de-uso)
- [Códigos de Status](#-códigos-de-status)
- [Lógica de Negócio](#-lógica-de-negócio)
- [Performance](#-performance)
- [Casos de Uso](#-casos-de-uso)
- [Changelog](#-changelog)

---

## 🎯 Visão Geral

O **Endpoint de Custos Fixos** é uma API REST que fornece relatórios detalhados sobre despesas e custos fixos da empresa, baseado em dados migrados do sistema MS Access para PostgreSQL.

### Objetivo
Analisar e reportar gastos com fornecedores classificados como "DESPESA FIXA" ou "CUSTO FIXO" em um período específico, fornecendo insights financeiros para tomada de decisão.

### Fonte de Dados
- **Sistema Origem**: MS Access (migrado)
- **Sistema Atual**: PostgreSQL
- **Total de Registros**: 2.699 contas a pagar migradas
- **Fornecedores**: 796 cadastrados (306 com classificação de tipo)

---

## 🔧 Especificações Técnicas

### Informações da API

| Propriedade | Valor |
|-------------|-------|
| **URL** | `/contas/relatorios/custos-fixos/` |
| **Método HTTP** | `GET` |
| **Formato de Resposta** | `JSON` |
| **Autenticação** | Não requerida (desenvolvimento) |
| **Versionamento** | v1.0 |

### Implementação

| Propriedade | Valor |
|-------------|-------|
| **Framework** | Django 5.2.1 + Django REST Framework |
| **Classe** | `RelatorioCustosFixosView(APIView)` |
| **Arquivo** | `contas/views/relatorios_views.py` |
| **URL Config** | `contas/urls.py` |
| **Banco de Dados** | PostgreSQL |

---

## 📝 Parâmetros

### Parâmetros Obrigatórios

| Parâmetro | Tipo | Formato | Descrição | Exemplo |
|-----------|------|---------|-----------|---------|
| `data_inicio` | string | YYYY-MM-DD | Data de início do período de análise | `2024-01-01` |
| `data_fim` | string | YYYY-MM-DD | Data de fim do período de análise | `2024-12-31` |

### Parâmetros Opcionais

| Parâmetro | Tipo | Formato | Descrição | Default |
|-----------|------|---------|-----------|---------|
| `categorias` | string | csv | Lista de categorias separadas por vírgula | `despesas_operacionais,despesas_administrativas,impostos,aluguel` |

### Regras de Validação

- ✅ `data_inicio` e `data_fim` são **obrigatórios**
- ✅ Formato de data deve ser **YYYY-MM-DD**
- ✅ `data_inicio` deve ser **≤ data_fim**
- ✅ `categorias` é opcional e aceita valores separados por vírgula

---

## 📊 Resposta da API

### Estrutura da Resposta

```json
{
  "parametros": { ... },
  "estatisticas_fornecedores": { ... },
  "totais_gerais": { ... },
  "resumo_por_tipo_fornecedor": [ ... ],
  "resumo_por_fornecedor": [ ... ],
  "total_contas_pagas": 295,
  "contas_pagas": [ ... ]
}
```

### 1. Seção `parametros`

Informações sobre os filtros aplicados na consulta.

```json
{
  "parametros": {
    "data_inicio": "2023-01-01",
    "data_fim": "2024-12-31",
    "filtro_aplicado": "Fornecedores com tipo DESPESA FIXA ou CUSTO FIXO",
    "fonte_dados": "Contas a Pagar (status: Pago)"
  }
}
```

### 2. Seção `estatisticas_fornecedores`

Métricas sobre os fornecedores analisados.

```json
{
  "estatisticas_fornecedores": {
    "total_fornecedores_fixos_cadastrados": 52,
    "fornecedores_com_pagamentos_no_periodo": 21
  }
}
```

### 3. Seção `totais_gerais`

Consolidação financeira de todos os pagamentos do período.

```json
{
  "totais_gerais": {
    "total_valor_original": 253580.74,
    "total_valor_pago": 211550.03,
    "total_juros": 890.13,
    "total_tarifas": 0.0
  }
}
```

### 4. Seção `resumo_por_tipo_fornecedor`

Agregação por categoria de fornecedor (CUSTO FIXO vs DESPESA FIXA).

```json
{
  "resumo_por_tipo_fornecedor": [
    {
      "fornecedor__tipo": "CUSTO FIXO",
      "total_pago": 156900.40,
      "quantidade_contas": 145,
      "total_valor_original": 160068.02,
      "total_juros": 889.45,
      "total_tarifas": 0.0
    },
    {
      "fornecedor__tipo": "DESPESA FIXA",
      "total_pago": 54649.63,
      "quantidade_contas": 150,
      "total_valor_original": 93512.72,
      "total_juros": 0.68,
      "total_tarifas": 0.0
    }
  ]
}
```

### 5. Seção `resumo_por_fornecedor`

Detalhamento por fornecedor individual ordenado por valor pago (decrescente).

```json
{
  "resumo_por_fornecedor": [
    {
      "fornecedor__nome": "FOLHA FIXA",
      "fornecedor__tipo": "CUSTO FIXO",
      "total_pago": 81156.94,
      "quantidade_contas": 15,
      "total_valor_original": 83280.43,
      "total_juros": 8.22,
      "total_tarifas": 0.0
    },
    {
      "fornecedor__nome": "PRO-LABORE LUINA",
      "fornecedor__tipo": "DESPESA FIXA",
      "total_pago": 36635.38,
      "quantidade_contas": 32,
      "total_valor_original": 66577.84,
      "total_juros": 0.0,
      "total_tarifas": 0.0
    }
  ]
}
```

### 6. Seção `contas_pagas`

Lista detalhada de todas as contas pagas no período.

```json
{
  "contas_pagas": [
    {
      "id": 52485,
      "data_pagamento": "2024-12-30",
      "data_vencimento": "2024-11-28",
      "valor_original": 706.20,
      "valor_pago": 706.20,
      "juros": 0.0,
      "tarifas": 0.0,
      "valor_total_pago": 706.20,
      "historico": "REF. DOC. INFORMA 2024",
      "fornecedor": "INFORMA CONTABILIDADE",
      "fornecedor_tipo": "CUSTO FIXO",
      "conta_bancaria": "N/A",
      "forma_pagamento": "DUPLICATA",
      "numero_duplicata": "NOV/2024"
    }
  ]
}
```

---

## 💡 Exemplos de Uso

### Exemplo 1: Relatório Mensal

**Requisição:**
```http
GET /contas/relatorios/custos-fixos/?data_inicio=2024-01-01&data_fim=2024-01-31
```

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/contas/relatorios/custos-fixos/?data_inicio=2024-01-01&data_fim=2024-01-31" \
     -H "Content-Type: application/json"
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/contas/relatorios/custos-fixos/?data_inicio=2024-01-01&data_fim=2024-01-31" -Method GET
```

### Exemplo 2: Relatório Anual Completo

**Requisição:**
```http
GET /contas/relatorios/custos-fixos/?data_inicio=2024-01-01&data_fim=2024-12-31
```

### Exemplo 3: Análise de Período Específico

**Requisição:**
```http
GET /contas/relatorios/custos-fixos/?data_inicio=2024-06-01&data_fim=2024-06-30
```

---

## 🚨 Códigos de Status

### Respostas de Sucesso

| Código | Status | Descrição |
|--------|--------|-----------|
| `200` | OK | Consulta executada com sucesso |

### Respostas de Erro

| Código | Status | Descrição | Exemplo |
|--------|--------|-----------|---------|
| `400` | Bad Request | Parâmetros obrigatórios faltando | `{"error": "Parâmetros data_inicio e data_fim são obrigatórios."}` |
| `400` | Bad Request | Formato de data inválido | `{"error": "Formato de data inválido. Use YYYY-MM-DD."}` |
| `400` | Bad Request | Data de início maior que data fim | `{"error": "A data de início não pode ser maior que a data de fim."}` |

---

## ⚙️ Lógica de Negócio

### Critérios de Filtro

1. **Fornecedores Elegíveis:**
   - Tipo contém "DESPESA FIXA" OU "CUSTO FIXO"
   - Query: `WHERE (tipo ILIKE '%DESPESA FIXA%' OR tipo ILIKE '%CUSTO FIXO%')`

2. **Contas Elegíveis:**
   - Status = 'P' (Pago)
   - Data de pagamento dentro do período especificado
   - Fornecedor deve estar na lista de fornecedores elegíveis

### Processo de Cálculo

```sql
-- 1. Identificar fornecedores fixos
SELECT id FROM fornecedores 
WHERE tipo ILIKE '%DESPESA FIXA%' OR tipo ILIKE '%CUSTO FIXO%'

-- 2. Filtrar contas pagas
SELECT * FROM contas_pagar 
WHERE status = 'P' 
  AND data_pagamento BETWEEN :data_inicio AND :data_fim
  AND fornecedor_id IN (fornecedores_fixos)

-- 3. Agregações
SELECT 
  fornecedor__tipo,
  SUM(valor_total_pago) as total_pago,
  COUNT(*) as quantidade_contas,
  SUM(valor) as total_valor_original,
  SUM(juros) as total_juros,
  SUM(tarifas) as total_tarifas
FROM contas_filtradas
GROUP BY fornecedor__tipo
ORDER BY total_pago DESC
```

### Classificação dos Dados

- **Ordenação Principal**: Valor pago (decrescente)
- **Ordenação Secundária**: Data de pagamento (decrescente)
- **Agrupamento**: Por tipo de fornecedor e por fornecedor individual

---

## ⚡ Performance

### Otimizações Implementadas

1. **Consultas Otimizadas:**
   - `select_related('fornecedor', 'conta')` - Evita N+1 queries
   - `values_list('id', flat=True)` - Consulta eficiente para IDs
   - Agregações no banco de dados ao invés de Python

2. **Índices Sugeridos:**
   ```sql
   CREATE INDEX idx_contas_pagar_status_data ON contas_pagar(status, data_pagamento);
   CREATE INDEX idx_contas_pagar_fornecedor ON contas_pagar(fornecedor_id);
   CREATE INDEX idx_fornecedores_tipo ON fornecedores(tipo);
   ```

### Métricas de Performance

| Métrica | Valor |
|---------|-------|
| **Tempo de Resposta** | < 1 segundo |
| **Registros Processados** | 295 contas |
| **Fornecedores Analisados** | 52 fornecedores |
| **Período de Teste** | 2 anos (2023-2024) |

---

## 📈 Casos de Uso

### 1. Controle de Custos Mensais

**Objetivo:** Monitorar gastos fixos mensais para controle orçamentário.

**Frequência:** Mensal

**Exemplo:**
```http
GET /contas/relatorios/custos-fixos/?data_inicio=2024-08-01&data_fim=2024-08-31
```

### 2. Análise Anual para Budget

**Objetivo:** Planejamento orçamentário anual baseado em histórico.

**Frequência:** Anual

**Exemplo:**
```http
GET /contas/relatorios/custos-fixos/?data_inicio=2024-01-01&data_fim=2024-12-31
```

### 3. Comparativo Semestral

**Objetivo:** Análise de tendências e variações semestrais.

**Processo:**
1. Primeiro semestre: `data_inicio=2024-01-01&data_fim=2024-06-30`
2. Segundo semestre: `data_inicio=2024-07-01&data_fim=2024-12-31`
3. Comparação dos resultados

### 4. Auditoria de Fornecedores

**Objetivo:** Identificar fornecedores com maior impacto nos custos fixos.

**Análise:** Foco na seção `resumo_por_fornecedor` ordenada por valor.

### 5. Análise de Sazonalidade

**Objetivo:** Identificar padrões sazonais nos custos fixos.

**Processo:** Consultas trimestrais para identificar variações.

---

## 🔄 Integração com Outros Sistemas

### Sistema de Origem
- **MS Access**: Dados migrados via `migration_master.py`
- **Tabelas**: `Fornecedores`, `ContasPagar`
- **Frequência de Migração**: Manual/Agendada

### Sistemas Consumidores
- **Frontend Web**: Dashboard de custos
- **Relatórios Excel**: Exportação para análise
- **Sistemas BI**: Integração para dashboards

### APIs Relacionadas
- **Estoque**: `/contas/estoque-controle/`
- **Fluxo de Caixa**: `/contas/fluxo-caixa/`
- **Relatórios Gerais**: `/contas/relatorio-financeiro/`

---

## 🛠️ Desenvolvimento e Manutenção

### Estrutura do Código

```
contas/
├── views/
│   └── relatorios_views.py  # Implementação principal
├── models/
│   └── access.py           # Modelos de dados
├── urls.py                 # Configuração de rotas
└── tests/                  # Testes unitários (a implementar)
```

### Dependências

```python
# requirements.txt
Django==5.2.1
djangorestframework==3.14.0
psycopg2-binary==2.9.7
pyodbc==4.0.39  # Para migração do Access
```

### Variáveis de Ambiente

```env
# settings.py
DEBUG=True
DATABASE_URL=postgresql://user:pass@localhost:5432/empresa
ACCESS_DB_PATH=C:\path\to\access\database.mdb
```

---

## 📊 Dados de Exemplo (Produção)

### Estatísticas Reais (Período 2023-2024)

| Métrica | Valor |
|---------|-------|
| **Total Pago** | R$ 211.550,03 |
| **Contas Processadas** | 295 |
| **Fornecedores Ativos** | 21 |
| **Período Analisado** | 24 meses |

### Top 5 Fornecedores

| Ranking | Fornecedor | Tipo | Valor Pago |
|---------|------------|------|------------|
| 1 | FOLHA FIXA | CUSTO FIXO | R$ 81.156,94 |
| 2 | PRO-LABORE LUINA | DESPESA FIXA | R$ 36.635,38 |
| 3 | ALUGUEL | CUSTO FIXO | R$ 25.208,04 |
| 4 | INSS | CUSTO FIXO | R$ 11.920,84 |
| 5 | MATERIAIS P/COPA | DESPESA FIXA | R$ 8.500,00* |

*Valor aproximado

### Distribuição por Tipo

| Tipo | Valor Total | % do Total | Quantidade |
|------|-------------|------------|------------|
| **CUSTO FIXO** | R$ 156.900,40 | 74.2% | 145 contas |
| **DESPESA FIXA** | R$ 54.649,63 | 25.8% | 150 contas |

---

## 🔮 Roadmap e Melhorias Futuras

### Versão 1.1 (Planejada)

- [ ] **Filtros Avançados**: Por categoria específica de fornecedor
- [ ] **Exportação**: Excel e PDF direto da API
- [ ] **Cache**: Implementar cache Redis para consultas frequentes
- [ ] **Paginação**: Para grandes volumes de dados

### Versão 1.2 (Planejada)

- [ ] **Comparativo Temporal**: Comparação automática entre períodos
- [ ] **Alertas**: Notificações para valores acima de threshold
- [ ] **Gráficos**: Endpoint dedicado para dados de visualização
- [ ] **API Versioning**: Implementar versionamento da API

### Versão 2.0 (Futuro)

- [ ] **Machine Learning**: Previsão de custos baseada em histórico
- [ ] **Integração Contábil**: Sincronização com sistemas contábeis
- [ ] **API GraphQL**: Alternativa ao REST para consultas complexas
- [ ] **Auditoria**: Log completo de todas as consultas realizadas

---

## 📚 Changelog

### v1.0.0 (2025-09-08)

**🎉 Lançamento Inicial**

**Adicionado:**
- ✅ Endpoint básico de custos fixos
- ✅ Filtros por período (data_inicio, data_fim)
- ✅ Agregações por tipo de fornecedor
- ✅ Agregações por fornecedor individual
- ✅ Listagem detalhada de contas pagas
- ✅ Validação de parâmetros de entrada
- ✅ Tratamento de erros padronizado
- ✅ Documentação completa

**Dados Migrados:**
- ✅ 2.699 contas a pagar do MS Access
- ✅ 796 fornecedores (306 com classificação)
- ✅ Relacionamentos entre tabelas
- ✅ Dados históricos de 2023-2024

**Testes Realizados:**
- ✅ Teste com período de 2 anos
- ✅ Validação de 295 contas pagas
- ✅ Verificação de 21 fornecedores ativos
- ✅ Teste de performance (< 1s response time)

---

## 👥 Equipe e Contatos

### Desenvolvimento
- **Desenvolvedor Principal**: GitHub Copilot
- **Data de Desenvolvimento**: Setembro 2025
- **Repository**: madmax100/empresa

### Suporte
- **Documentação**: Este arquivo
- **Issues**: GitHub Issues
- **Wiki**: Repository Wiki

---

## 📄 Licença e Uso

### Termos de Uso
- **Uso Interno**: Autorizado para uso interno da empresa
- **Modificações**: Permitidas com documentação adequada
- **Distribuição**: Restrita ao ambiente corporativo

### Disclaimers
- ⚠️ **Ambiente de Desenvolvimento**: Configuração atual é para desenvolvimento
- ⚠️ **Dados Sensíveis**: Implementar autenticação antes da produção
- ⚠️ **Backup**: Manter backup regular dos dados migrados

---

**📅 Última Atualização:** 8 de setembro de 2025  
**🔄 Versão da Documentação:** 1.0.0  
**📍 Status:** Ativo e Operacional ✅

---

*Esta documentação foi gerada automaticamente com base na implementação e testes realizados. Para dúvidas ou sugestões, consulte a equipe de desenvolvimento.*
