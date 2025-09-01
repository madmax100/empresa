import axios from 'axios';
import config from '@/config';
import { FluxoCaixaFiltros } from '@/types/financeiro';
import { DashboardEstrategico, DashboardGerencial, DashboardOperacional, FluxoCaixaResumo, Totalizadores } from '@/types/dashboard';
import { Movimento } from '@/types/movimento';
export const api = axios.create({
  baseURL: config.api.baseURL,
  headers: {
    'Content-Type': 'application/json',
  }
});

export class ServicoFinanceiro {
  // Dashboard Operacional
  async obterDashboardOperacional(filtros: Partial<FluxoCaixaFiltros>): Promise<DashboardOperacional> {
    // Convert filter params to backend format
    const params = this.convertFilters(filtros);
    const response = await api.get<DashboardOperacional>('/contas_receber/dashboard/', { params });
    return response.data;
  }

  async obterMovimentacoes(filtros: Partial<FluxoCaixaFiltros>): Promise<Movimento[]> {
    const params = this.convertFilters(filtros);
    const response = await api.get<Movimento[]>('/contas_receber/', { params });
    return response.data;
  }

  async obterTotalizadores(filtros: Partial<FluxoCaixaFiltros>): Promise<Totalizadores> {
    const params = this.convertFilters(filtros);
    const response = await api.get<Totalizadores>('/contas_receber/dashboard/', { params });
    return response.data;
  }

  async obterResumoFluxoCaixa(filtros: Partial<FluxoCaixaFiltros>): Promise<FluxoCaixaResumo> {
    const params = this.convertFilters(filtros);
    const response = await api.get<FluxoCaixaResumo>('/contas_receber/dashboard/', { params });
    return response.data;
  }

  async realizarMovimento(id: number): Promise<{ message: string; movimento: Movimento }> {
    const response = await api.patch<{ message: string; movimento: Movimento }>(`/contas_receber/${id}/atualizar_status/`, { status: 'P' });
    return response.data;
  }

  // Dashboard Estratégico
  async obterDashboardEstrategico(filtros: Partial<FluxoCaixaFiltros>): Promise<DashboardEstrategico> {
    const params = this.convertFilters(filtros);
    const response = await api.get<DashboardEstrategico>('/contas_receber/dashboard/', { params });
    return response.data;
  }

  async obterRelatorioDRE(filtros: Partial<FluxoCaixaFiltros>): Promise<DashboardEstrategico> {
    const params = this.convertFilters(filtros);
    const response = await api.get<DashboardEstrategico>('/contas_receber/dashboard/', { params });
    return response.data;
  }

  async obterAnaliseRentabilidade(filtros: Partial<FluxoCaixaFiltros>): Promise<DashboardEstrategico> {
    const params = this.convertFilters(filtros);
    const response = await api.get<DashboardEstrategico>('/contas_receber/dashboard/', { params });
    return response.data;
  }

  // Dashboard Gerencial
  async obterDashboardGerencial(filtros: Partial<FluxoCaixaFiltros>): Promise<DashboardGerencial> {
    const params = this.convertFilters(filtros);
    const response = await api.get<DashboardGerencial>('/contas_receber/dashboard/', { params });
    return response.data;
  }

  // Helper method to convert frontend filters to backend params
  private convertFilters(filtros: Partial<FluxoCaixaFiltros>) {
    const params: any = {};
    if (filtros.data_inicial) params.data_inicio = filtros.data_inicial;
    if (filtros.data_final) params.data_fim = filtros.data_final;
    if (filtros.status) params.status = filtros.status;
    return params;
  }

  async obterAnaliseContratos(filtros: Partial<FluxoCaixaFiltros>): Promise<{
    metricas_contratos: DashboardGerencial['metricas_contratos'];
    contratos_status: DashboardGerencial['contratos_status'];
    receita_por_tipo_contrato: DashboardGerencial['receita_por_tipo_contrato'];
  }> {
  const response = await api.get('/fluxo-caixa/analise_contratos/', { params: filtros });
    return response.data;
  }

  async obterAnaliseClientes(filtros: Partial<FluxoCaixaFiltros>): Promise<DashboardGerencial> {
  const response = await api.get<DashboardGerencial>('/fluxo-caixa/analise_clientes/', { params: filtros });
    return response.data;
  }

  // Operações Auxiliares
  async sincronizarDados(): Promise<{ message: string }> {
  const response = await api.post<{ message: string }>('/fluxo-caixa/sincronizar/');
    return response.data;
  }

  async conciliacaoBancaria(filtros: Partial<FluxoCaixaFiltros>): Promise<Totalizadores> {
  const response = await api.post<Totalizadores>('/fluxo-caixa/conciliacao_bancaria/', filtros);
    return response.data;
  }

  async importarLancamentos(movimentos: Omit<Movimento, 'id'>[]): Promise<{ message: string }> {
  const response = await api.post<{ message: string }>('/fluxo-caixa/importar_lancamentos/', { movimentos });
    return response.data;
  }

  async limparHistorico(dataLimite: string): Promise<{
    message: string;
    data_limite: string;
    saldo_inicial_atualizado: number;
  }> {
  const response = await api.post('/fluxo-caixa/limpar_historico/', { data_limite: dataLimite });
    return response.data;
  }
}

export const servicoFinanceiro = new ServicoFinanceiro();
export default servicoFinanceiro;