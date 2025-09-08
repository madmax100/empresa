# Dashboard de Resultados do Período

## Visão Geral

O dashboard de resultados do período oferece uma análise completa dos resultados financeiros da empresa, incluindo:
- **Variação de estoque**: Comparação entre valor anterior e atual do estoque
- **Lucro operacional**: Diferença entre valores de saída e entrada (a preços de entrada)
- **Contratos recebidos**: Valores recebidos dos contratos de locação
- **Resultado líquido**: Consolidação de todos os componentes

## Arquitetura

### Componentes

```
src/
├── components/
│   └── dashboard/
│       └── ResultadosPeriodoDashboard.tsx    # Dashboard principal
├── pages/
│   └── ResultadosPage.tsx                    # Página wrapper
├── services/
│   └── resultados-service.ts                 # Service para APIs
└── hooks/
    └── useResultados.ts                      # Hook personalizado
```

### Service (`resultados-service.ts`)

O service gerencia todas as chamadas para as APIs do backend:

```typescript
// Endpoints disponíveis:
- GET /api/estoque/variacao/           # Variação de estoque
- GET /api/operacoes/lucro/           # Lucro operacional
- GET /api/contratos_locacao/recebimentos/  # Recebimentos de contratos
- GET /api/resultados/historico/      # Histórico de resultados
```

#### Métodos principais:

- `buscarVariacaoEstoque(filtros)` - Busca dados de variação de estoque
- `buscarLucroOperacional(filtros)` - Busca dados de lucro operacional
- `buscarContratosRecebidos(filtros)` - Busca valores recebidos de contratos
- `buscarResultadosPeriodo(filtros)` - Busca todos os dados consolidados
- `buscarHistoricoResultados(meses)` - Busca histórico para comparação

#### Fallback para dados mockados:

Quando as APIs não estão disponíveis, o service automaticamente retorna dados mockados para demonstração.

### Hook (`useResultados.ts`)

Hook personalizado que simplifica o uso dos dados de resultados:

```typescript
const {
  resultados,     // Dados dos resultados
  loading,        // Estado de carregamento
  error,          // Mensagem de erro
  carregarResultados, // Função para recarregar dados
  setFiltros,     // Atualizar filtros
  filtros         // Filtros atuais
} = useResultados();
```

### Componente Principal (`ResultadosPeriodoDashboard.tsx`)

Dashboard completo com:
- **Filtros de período**: Botões preset (Mês Atual, Último Mês, Ano Atual) + seleção manual
- **Cards de métricas**: 4 cards principais com indicadores visuais
- **Detalhamento**: Breakdown detalhado de estoque e lucro operacional
- **Resumo consolidado**: Visão geral dos resultados do período
- **Exportação CSV**: Funcionalidade de export dos dados

## Uso

### Integração em uma página:

```tsx
import ResultadosPeriodoDashboard from '@/components/dashboard/ResultadosPeriodoDashboard';

export default function ResultadosPage() {
  return (
    <div>
      <ResultadosPeriodoDashboard />
    </div>
  );
}
```

### Usando o hook em componentes customizados:

```tsx
import { useResultados } from '@/hooks/useResultados';

function MeuComponente() {
  const { resultados, loading, setFiltros } = useResultados({
    data_inicio: '2024-01-01',
    data_fim: '2024-01-31'
  });

  if (loading) return <div>Carregando...</div>;

  return (
    <div>
      <h2>Resultado: {resultados?.resumoGeral.resultadoLiquido}</h2>
      <button onClick={() => setFiltros({ 
        data_inicio: '2024-02-01', 
        data_fim: '2024-02-29' 
      })}>
        Fevereiro
      </button>
    </div>
  );
}
```

## APIs Backend

### Endpoints esperados:

#### 1. Variação de Estoque
```
GET /api/estoque/variacao/?data_inicio=2024-01-01&data_fim=2024-01-31

Response:
{
  "valorAnterior": 150000,
  "valorAtual": 165000,
  "diferenca": 15000,
  "percentual": 10.0
}
```

#### 2. Lucro Operacional
```
GET /api/operacoes/lucro/?data_inicio=2024-01-01&data_fim=2024-01-31

Response:
{
  "valorSaida": 200000,
  "valorEntrada": 140000,
  "lucro": 60000,
  "margem": 30.0
}
```

#### 3. Contratos Recebidos
```
GET /api/contratos_locacao/recebimentos/?data_inicio=2024-01-01&data_fim=2024-01-31

Response:
{
  "valorTotal": 180000,
  "quantidadeContratos": 25,
  "valorMedio": 7200
}
```

#### 4. Histórico de Resultados
```
GET /api/resultados/historico/?meses=6

Response:
[
  { "periodo": "jan 2024", "resultado": 255000 },
  { "periodo": "fev 2024", "resultado": 280000 },
  ...
]
```

## Funcionalidades

### 1. Filtros de Período
- **Botões preset**: Mês Atual, Último Mês, Ano Atual
- **Seleção manual**: Data início e fim personalizadas
- **Aplicação**: Botão "Aplicar" para executar a busca

### 2. Métricas Principais
- **Variação de Estoque**: Mostra diferença e percentual com indicador visual (verde/vermelho)
- **Lucro Operacional**: Exibe lucro e margem percentual
- **Contratos Recebidos**: Valor total, quantidade e média por contrato
- **Resultado Líquido**: Soma consolidada com margem total

### 3. Detalhamento
- **Estoque**: Valor anterior vs atual com cálculo da variação
- **Operacional**: Valor de saída vs entrada com cálculo do lucro

### 4. Resumo Consolidado
- **Três pilares**: Patrimônio (estoque), Operacional (lucro), Recebimentos (contratos)
- **Total do período**: Resultado líquido final com margem

### 5. Exportação
- **Formato CSV**: Exporta métricas principais com observações
- **Nome do arquivo**: Inclui período selecionado
- **Codificação**: UTF-8 com separador `;`

## Estados de Loading e Erro

### Loading
- **Spinner centralizado**: Durante carregamento inicial
- **Estado reativo**: Atualizado automaticamente pelo hook

### Erro
- **Alert visual**: Exibição de mensagens de erro
- **Fallback automático**: Dados mockados quando API falha
- **Log no console**: Detalhes técnicos para debugging

## Estilização

### Design System
- **Shadcn UI**: Componentes base (Card, Button, Input, Alert)
- **Tailwind CSS**: Estilização utilitária
- **Lucide React**: Ícones consistentes

### Cores e Bordas
- **Azul**: Variação de estoque
- **Verde**: Lucro operacional
- **Âmbar**: Contratos recebidos
- **Esmeralda**: Resultado líquido
- **Bordas coloridas**: `border-l-4` para identificação visual

### Responsividade
- **Grid adaptável**: `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`
- **Mobile-first**: Layout otimizado para dispositivos móveis
- **Espaçamento consistente**: Sistema de spacing do Tailwind

## Próximos Passos

1. **Integração com APIs reais**: Substituir dados mockados por endpoints funcionais
2. **Roteamento**: Adicionar a página ao sistema de navegação
3. **Testes**: Implementar testes unitários e de integração
4. **Otimizações**: Cache de dados e otimizações de performance
5. **Filtros avançados**: Filtros por cliente, tipo de operação, etc.
6. **Gráficos**: Adicionar visualizações gráficas (Recharts)
7. **Comparações**: Comparar períodos diferentes
8. **Alertas**: Notificações para mudanças significativas
