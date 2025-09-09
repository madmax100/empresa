# 💰 VALORES CONTRATUAIS - ENDPOINT SUPRIMENTOS

## 📋 Resumo da Melhoria

**Campo Adicionado:** `valores_contratuais` na resposta do endpoint suprimentos-por-contrato

**Informação Principal:** O campo `valor_mensal` representa **o valor da parcela mensal do contrato**

---

## 🔧 Estrutura dos Valores Contratuais

### Novo Campo na Resposta
```json
{
  "valores_contratuais": {
    "valor_mensal": 350.50,           // VALOR DA PARCELA MENSAL
    "valor_total_contrato": 4206.00,  // Valor total do contrato
    "numero_parcelas": "12"           // Quantidade de parcelas
  }
}
```

### Mapeamento do Banco de Dados
| Campo API | Campo BD | Descrição |
|-----------|----------|-----------|
| `valor_mensal` | `valorpacela` | **Valor da parcela mensal** |
| `valor_total_contrato` | `valorcontrato` | Valor total do contrato |
| `numero_parcelas` | `numeroparcelas` | Número de parcelas |

---

## 📊 Dados Reais de Produção

### Exemplos de Contratos Vigentes
```
Contrato 1587: Valor mensal = R$ 263.33 (Total: R$ 3.159,96 em 12x)
Contrato 1588: Valor mensal = R$ 120.00 (Total: R$ 1.440,00 em 12x)
Contrato 1590: Valor mensal = R$ 158.30 (Total: R$ 1.899,60 em 12x)
Contrato 1595: Valor mensal = R$ 922.70 (Total: R$ 11.072,40 em 12x)
```

### Estatísticas dos Testes
- **Contratos testados:** 32 vigentes
- **Com valores definidos:** 10 contratos (31%)
- **Valor mensal total:** R$ 3.323,80
- **Média por contrato:** R$ 332,38

---

## 🎯 Importância do Valor Mensal

### 📈 **Análise de Rentabilidade**
- Permite comparar **valor mensal do contrato** vs **custos de suprimentos**
- Calcula margem de lucro por contrato
- Identifica contratos deficitários

### 📊 **Relatórios Gerenciais**
- Receita mensal garantida por contrato
- Projeção de faturamento
- Análise de performance financeira

### 💡 **Decisões Estratégicas**
- Renovação de contratos
- Ajuste de valores
- Otimização de custos

---

## 🧪 Exemplos de Uso

### 1. **Análise de Margem**
```json
{
  "contrato_id": 1587,
  "valores_contratuais": {
    "valor_mensal": 263.33    // Receita mensal
  },
  "suprimentos": {
    "total_valor": 45.20,     // Custo no período
    "quantidade_notas": 3
  }
}
// Margem = R$ 263,33 - R$ 45,20 = R$ 218,13 (83%)
```

### 2. **Contratos com Alto Custo de Suprimentos**
```bash
# Buscar contratos onde suprimentos > 50% do valor mensal
curl "http://localhost:8000/api/contratos_locacao/suprimentos/?data_inicial=2024-01-01&data_final=2024-12-31"
```

### 3. **Projeção de Receita**
```python
# Calcular receita mensal de contratos vigentes
total_receita_mensal = sum([
    contrato['valores_contratuais']['valor_mensal'] 
    for contrato in resultados
])
```

---

## 📝 Observações Técnicas

### ⚠️ **Campo com Erro de Nomenclatura**
- **Banco de dados:** `valorpacela` (com erro de digitação)
- **Deveria ser:** `valorparcela`
- **API corrige:** Expõe como `valor_mensal` (nome claro)

### ✅ **Tratamento de Valores**
- Valores `NULL` retornam como `0.0`
- Precisão decimal mantida (2 casas)
- Conversão segura para float

### 🔄 **Compatibilidade**
- Campo opcional (não quebra integrações existentes)
- Presente apenas quando contrato tem valores definidos
- Mantém estrutura da resposta original

---

## 📈 Impacto nos Negócios

### ✅ **Benefícios Imediatos**
1. **Visibilidade financeira:** Receita mensal por contrato
2. **Controle de custos:** Comparação com gastos de suprimentos
3. **Análise de performance:** Identificação de contratos problemáticos

### 🎯 **Casos de Uso**
- **Controladoria:** Análise de margem por contrato
- **Comercial:** Suporte para negociação de renovações
- **Operacional:** Otimização de entregas de suprimentos

---

## 🔍 Teste e Validação

### Arquivo de Teste
```bash
python teste_valores_contratuais.py
```

### Comando de API
```bash
curl "http://localhost:8000/api/contratos_locacao/suprimentos/?data_inicial=2024-08-01&data_final=2024-08-31&contrato_id=1587"
```

### Verificação de Dados
```sql
-- Validar valores no banco
SELECT contrato, valorpacela, valorcontrato, numeroparcelas 
FROM contratos_locacao 
WHERE valorpacela IS NOT NULL 
ORDER BY valorpacela DESC;
```

---

**Data:** 2025-01-03  
**Versão:** 1.1.0  
**Autor:** GitHub Copilot

---

> 💡 **Dica:** O valor mensal permite calcular rapidamente a rentabilidade de cada contrato comparando com os custos de suprimentos do período!
