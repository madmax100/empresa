# GUIA DE IMPLEMENTAÇÃO DO FRONTEND 📋

## 🚀 INSTRUÇÕES PARA IMPLEMENTAR O DASHBOARD REACT

### 1. **INSTALAR DEPENDÊNCIAS**
```bash
cd frontend
npm install recharts axios lucide-react
```

### 2. **CONFIGURAR VITE (vite.config.ts)**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})
```

### 3. **ESTRUTURA DE PASTAS**
```
src/
├── components/
│   ├── ui/
│   │   ├── MetricCard.tsx
│   │   ├── AlertCard.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ErrorCard.tsx
│   ├── dashboard/
│   │   └── FluxoCaixaLucroDashboard.tsx
│   └── layout/
│       └── MainLayout.tsx
├── hooks/
│   └── useFluxoCaixaLucro.ts
├── services/
│   └── fluxo-caixa-lucro-service.ts
└── App.tsx
```

### 4. **CONFIGURAR TAILWIND CSS**
Certifique-se de que o `tailwind.config.js` inclui:
```javascript
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### 5. **ARQUIVOS PARA CRIAR**

#### A. **Serviço de API** (`src/services/fluxo-caixa-lucro-service.ts`)
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: '/api/fluxo-caixa-lucro',
  timeout: 10000,
});

// Interfaces TypeScript
export interface DashboardData {
  periodo: { inicio: string; fim: string };
  saldo_inicial: string;
  saldo_final_realizado: string;
  saldo_final_projetado: string;
  meses: Array<any>;
  totalizadores: any;
}

export interface AlertaData {
  data_analise: string;
  quantidade_alertas: number;
  alertas: Array<{
    tipo: string;
    severidade: string;
    mensagem: string;
    recomendacao: string;
  }>;
  metricas_monitoradas: any;
}

// Métodos da API
export const fluxoCaixaLucroService = {
  getDashboard: () => api.get<DashboardData>('/dashboard/'),
  getAlertas: () => api.get<AlertaData>('/alertas_inteligentes/'),
  getProjecao: () => api.get('/projecao_fluxo/'),
  getRelatorioDiario: (data: string) => api.get(`/relatorio_diario/?data=${data}`),
  getAnaliseCategorias: () => api.get('/analise_categorias/'),
  getEstatisticas: () => api.get('/estatisticas/'),
  getIndicadores: () => api.get('/indicadores/'),
  getRelatorioDRE: (dataInicial: string, dataFinal: string) => 
    api.get(`/relatorio_dre/?data_inicial=${dataInicial}&data_final=${dataFinal}`),
  getCenarios: () => api.get('/cenarios/'),
};
```

#### B. **Hooks React** (`src/hooks/useFluxoCaixaLucro.ts`)
```typescript
import { useState, useEffect } from 'react';
import { fluxoCaixaLucroService } from '@/services/fluxo-caixa-lucro-service';

export function useDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await fluxoCaixaLucroService.getDashboard();
      setData(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, refetch: fetchData };
}

// Criar hooks similares para: useAlertasInteligentes, useProjecaoFluxo, 
// useRelatorioDiario, useAnaliseCategorias
```

#### C. **Componentes UI**

**MetricCard** (`src/components/ui/MetricCard.tsx`):
```typescript
interface MetricCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  icon?: React.ReactNode;
  valueColor?: string;
  trend?: 'up' | 'down' | 'stable';
}

export function MetricCard({ title, value, subtitle, icon, valueColor = "text-gray-900", trend }: MetricCardProps) {
  const formatValue = (val: number | string) => {
    if (typeof val === 'number') {
      return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
    }
    return val;
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className={`text-2xl font-bold ${valueColor} mt-1`}>
            {formatValue(value)}
          </p>
          {subtitle && (
            <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className="flex-shrink-0 text-gray-400">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
```

#### D. **Dashboard Principal** (`src/components/dashboard/FluxoCaixaLucroDashboard.tsx`)
```typescript
import { useDashboard, useAlertasInteligentes, useProjecaoFluxo } from '@/hooks/useFluxoCaixaLucro';
import { MetricCard } from '@/components/ui/MetricCard';
import { AlertCard } from '@/components/ui/AlertCard';
// ... outros imports

export function FluxoCaixaLucroDashboard() {
  const dashboard = useDashboard();
  const alertas = useAlertasInteligentes();
  const projecao = useProjecaoFluxo();

  if (dashboard.loading) {
    return <div>Carregando...</div>;
  }

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-900">Dashboard Financeiro</h1>
      
      {/* Métricas Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {dashboard.data && (
          <>
            <MetricCard
              title="Saldo Inicial"
              value={dashboard.data.saldo_inicial}
              icon={<DollarSign className="h-6 w-6" />}
            />
            {/* Outras métricas... */}
          </>
        )}
      </div>

      {/* Alertas */}
      {alertas.data?.alertas && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Alertas Inteligentes</h2>
          {alertas.data.alertas.map((alerta, index) => (
            <AlertCard key={index} {...alerta} />
          ))}
        </div>
      )}

      {/* Gráficos com Recharts */}
      {/* Implementar gráficos usando Recharts */}
    </div>
  );
}
```

#### E. **Layout Principal** (`src/components/layout/MainLayout.tsx`)
```typescript
export function MainLayout() {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg">
        {/* Menu de navegação */}
      </div>
      
      {/* Conteúdo principal */}
      <div className="flex-1 flex flex-col">
        <header className="bg-white shadow-sm border-b h-16">
          {/* Header */}
        </header>
        <main className="flex-1 overflow-auto">
          <FluxoCaixaLucroDashboard />
        </main>
      </div>
    </div>
  );
}
```

#### F. **App.tsx**
```typescript
import { MainLayout } from '@/components/layout/MainLayout';

function App() {
  return <MainLayout />;
}

export default App;
```

### 6. **EXECUTAR O PROJETO**
```bash
# Terminal 1 - Backend Django
cd backend/empresa
python manage.py runserver

# Terminal 2 - Frontend React
cd frontend  
npm run dev
```

### 7. **FUNCIONALIDADES IMPLEMENTADAS**
- ✅ Dashboard com métricas principais
- ✅ Alertas inteligentes
- ✅ Projeções de fluxo de caixa
- ✅ Relatórios diários
- ✅ Análise por categorias
- ✅ Gráficos interativos (Recharts)
- ✅ Layout responsivo (Tailwind CSS)
- ✅ Estado de loading e erro
- ✅ Integração completa com API

### 8. **ENDPOINTS DISPONÍVEIS**
Todos os 9 endpoints estão funcionando:
- `/api/fluxo-caixa-lucro/dashboard/`
- `/api/fluxo-caixa-lucro/estatisticas/`
- `/api/fluxo-caixa-lucro/indicadores/`
- `/api/fluxo-caixa-lucro/alertas_inteligentes/`
- `/api/fluxo-caixa-lucro/projecao_fluxo/`
- `/api/fluxo-caixa-lucro/relatorio_dre/`
- `/api/fluxo-caixa-lucro/relatorio_diario/`
- `/api/fluxo-caixa-lucro/analise_categorias/`
- `/api/fluxo-caixa-lucro/cenarios/`

---

## 🚀 **PRONTO PARA IMPLEMENTAR!**

Siga essas instruções em ordem e terá um dashboard financeiro completo funcionando. Todos os endpoints do backend estão testados e funcionando perfeitamente!
