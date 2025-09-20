// src/services/gerencia-service.ts

const API_BASE_URL = 'http://localhost:8000/contas';

export interface EstoqueReportResponse {
  data_posicao: string;
  valor_total_estoque: number;
  total_produtos_em_estoque: number;
  detalhes_por_produto: Array<{
    produto_id: number;
    produto_descricao: string;
    categoria: string;
    quantidade_atual: number;
    custo_unitario: number;
    valor_total: number;
  }>;
}

export interface FaturamentoContratosResponse {
  parametros: {
    data_inicio: string;
    data_fim: string;
    filtros_aplicados: {
      nf_entrada: string;
      nf_saida: string;
      nf_servico: string;
    };
    fonte_dados: string;
  };
  totais_gerais: {
    total_quantidade_notas: number;
    total_valor_produtos: number;
    total_valor_geral: number;
    total_impostos: number;
    analise_vendas: {
      valor_vendas: number;
      valor_preco_entrada: number;
      margem_bruta: number;
      percentual_margem: number;
      itens_analisados: number;
      produtos_sem_preco_entrada: number;
    };
  };
}

export interface CustosFixosResponse {
  parametros: {
    data_inicio: string;
    data_fim: string;
    filtro_aplicado: string;
    fonte_dados: string;
  };
  totais_gerais: {
    valor_total: number;
    valor_custos_fixos: number;
    valor_despesas_fixas: number;
    quantidade_total_contas: number;
  };
}

export interface CustosVariaveisResponse {
  parametros: {
    data_inicio: string;
    data_fim: string;
    filtro_aplicado: string;
    fonte_dados: string;
  };
  totais_gerais: {
    valor_total: number;
    quantidade_total_contas: number;
  };
}

export interface ContasAbertas {
  total_contas_pagar: number;
  valor_total_pagar: number;
  total_contas_receber: number;
  valor_total_receber: number;
  // Totais por tipo de custo (quando disponível no backend)
  custos_por_tipo?: {
    FIXO?: { total_contas: number; valor_total: number };
    VARIÁVEL?: { total_contas: number; valor_total: number };
    VARIAVEL?: { total_contas: number; valor_total: number };
    [key: string]: { total_contas: number; valor_total: number } | undefined;
  };
}

export interface ContasNaoPagasResponse {
  data_corte: string;
  filtros: {
    tipo: string;
    incluir_canceladas: boolean;
    filtrar_por_data_emissao: boolean;
  };
  resumo_geral: {
    antes_data_corte: ContasAbertas;
    apos_data_corte: ContasAbertas;
  };
  // Backend retorna detalhamento por grupo em `detalhamento`
  detalhamento?: {
    contas_a_pagar?: {
      antes_data_corte?: Array<{
        fornecedor?: {
          id?: number;
          nome?: string;
          cnpj_cpf?: string | null;
          especificacao?: string | null;
          tipo_custo?: string | null;
        };
        total_contas?: number;
        valor_total?: number;
      }>;
      depois_data_corte?: Array<unknown>;
    };
    contas_a_receber?: {
      antes_data_corte?: ReceberResumoItem[];
      depois_data_corte?: ReceberResumoItem[];
    };
  };
  // Compatibilidade com versões antigas (caso viesse no topo)
  contas_a_receber?: {
    antes_data_corte?: ReceberResumoItem[];
    depois_data_corte?: ReceberResumoItem[];
  };
}

export interface ReceberResumoItem {
  cliente?: {
    id?: number;
    nome?: string;
    cnpj_cpf?: string | null;
  };
  total_contas?: number;
  valor_total?: number;
  periodo_vencimento?: {
    menor_data?: string;
    maior_data?: string;
  };
}

export interface GerenciaData {
  estoqueInicio: number;
  estoqueFim: number;
  faturamentoContratos: number;
  custosFixos: number;
  custosVariaveis: number;
  contasReceberInicio: number;
  // A Receber de clientes com contrato de locação (na data de corte inicial)
  contasReceberInicioContratos?: number;
  contasReceberInicioContratosCount?: number;
  contasPagarInicio: number;
  contasReceberFim: number;
  // A Receber de clientes com contrato de locação (na data de corte final)
  contasReceberFimContratos?: number;
  contasReceberFimContratosCount?: number;
  contasPagarFim: number;
  // Quantidades (contagens) de contas na data de corte
  contasReceberInicioCount?: number;
  contasPagarInicioCount?: number;
  contasReceberFimCount?: number;
  contasPagarFimCount?: number;
  // Discriminação de Pagar por tipo de custo
  contasPagarInicioFixos?: number;
  contasPagarInicioVariaveis?: number;
  contasPagarInicioFixosCount?: number;
  contasPagarInicioVariaveisCount?: number;
  contasPagarInicioOutros?: number;
  contasPagarInicioOutrosCount?: number;
  contasPagarFimFixos?: number;
  contasPagarFimVariaveis?: number;
  contasPagarFimFixosCount?: number;
  contasPagarFimVariaveisCount?: number;
  contasPagarFimOutros?: number;
  contasPagarFimOutrosCount?: number;
  // Novos campos para indicar fonte dos dados
  fonteDados: {
    estoque: 'atual' | 'historico';
    periodo: string;
    isToday: boolean;
  };
}

export interface ResultadoMensal {
  mes: string; // AAAA-MM
  periodo: {
    inicio: string; // AAAA-MM-DD
    fim: string;    // AAAA-MM-DD
  };
  saldo_sem_fixos_inicio: number;
  saldo_sem_fixos_fim: number;
  variacao_saldo_sem_fixos: number;
  estoque_inicio: number;
  estoque_fim: number;
  variacao_estoque: number;
  resultado_mensal: number; // variacao_saldo_sem_fixos + variacao_estoque
}

export class GerenciaService {
  
  private static isToday(date: string): boolean {
    const today = new Date().toISOString().split('T')[0];
    return date === today;
  }

  // Utilitário: último dia do mês para uma data
  private static lastDayOfMonth(date: Date): Date {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0);
  }

  // Utilitário: formata Date para AAAA-MM-DD
  private static toISODate(d: Date): string {
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  }

  // Utilitário: cria lista de meses dentro do período [dataInicio, dataFim]
  private static buildMonthsRange(dataInicio: string, dataFim: string): Array<{ inicio: string; fim: string; mes: string }> {
    const start = new Date(dataInicio + 'T00:00:00');
    const end = new Date(dataFim + 'T23:59:59');

    const months: Array<{ inicio: string; fim: string; mes: string }> = [];

    // Começa no primeiro dia do mês do início
    let cursor = new Date(start.getFullYear(), start.getMonth(), 1);
    while (cursor <= end) {
      const firstDay = new Date(cursor.getFullYear(), cursor.getMonth(), 1);
      const lastDay = this.lastDayOfMonth(cursor);

      // Ajusta limites para o intervalo global
      const rangeStart = new Date(Math.max(firstDay.getTime(), new Date(start.getFullYear(), start.getMonth(), start.getDate()).getTime()));
      const rangeEnd = new Date(Math.min(lastDay.getTime(), end.getTime()));

      const inicio = this.toISODate(rangeStart);
      const fim = this.toISODate(rangeEnd);
      const mes = `${cursor.getFullYear()}-${String(cursor.getMonth() + 1).padStart(2, '0')}`;

      // Garante que o início seja <= fim
      if (new Date(inicio) <= new Date(fim)) {
        months.push({ inicio, fim, mes });
      }

      // Avança para o próximo mês
      cursor = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1);
    }

    return months;
  }

  // Calcula resultados mensais: variação do saldo sem custos fixos + variação do estoque
  static async calcularResultadosMensais(dataInicio: string, dataFim: string): Promise<ResultadoMensal[]> {
    console.log('📅 GerenciaService.calcularResultadosMensais:', { dataInicio, dataFim });
    const meses = this.buildMonthsRange(dataInicio, dataFim);
    const resultados: ResultadoMensal[] = [];

    for (const m of meses) {
      try {
        // Buscar contas não pagas nos cortes início e fim
        const [contasIni, contasFim] = await Promise.all([
          this.buscarContasNaoPagas(m.inicio),
          this.buscarContasNaoPagas(m.fim)
        ]);

        const extrairSaldosSemFixos = (res: ContasNaoPagasResponse) => {
          const geral = res?.resumo_geral?.antes_data_corte;
          const receber = Number(geral?.valor_total_receber) || 0;
          const pagar = Number(geral?.valor_total_pagar) || 0;
          // Extrai valor de FIXO em custos_por_tipo para remover dos pagar
          const tipos = geral?.custos_por_tipo as ContasAbertas['custos_por_tipo'] | undefined;
          const fixoValor = Number(tipos?.FIXO?.valor_total) || 0;
          const pagarSemFixos = pagar - fixoValor;
          const saldoSemFixos = receber - pagarSemFixos;
          return { saldoSemFixos };
        };

        const sIni = extrairSaldosSemFixos(contasIni).saldoSemFixos;
        const sFim = extrairSaldosSemFixos(contasFim).saldoSemFixos;
        const variacaoSaldoSemFixos = sFim - sIni;

        // Buscar valor de estoque no início e fim do mês
        const [estoqueIni, estoqueFim] = await Promise.all([
          this.buscarEstoquePorData(m.inicio),
          this.buscarEstoquePorData(m.fim)
        ]);

        const eIni = Number(estoqueIni?.valor_total_estoque) || 0;
        const eFim = Number(estoqueFim?.valor_total_estoque) || 0;
        const variacaoEstoque = eFim - eIni;

        const resultado_mensal = variacaoSaldoSemFixos + variacaoEstoque;

        resultados.push({
          mes: m.mes,
          periodo: { inicio: m.inicio, fim: m.fim },
          saldo_sem_fixos_inicio: sIni,
          saldo_sem_fixos_fim: sFim,
          variacao_saldo_sem_fixos: variacaoSaldoSemFixos,
          estoque_inicio: eIni,
          estoque_fim: eFim,
          variacao_estoque: variacaoEstoque,
          resultado_mensal
        });
      } catch (err) {
        console.error('❌ Erro ao calcular resultado mensal para', m, err);
        // Em caso de erro, ainda adiciona item com zeros para manter continuidade visual
        resultados.push({
          mes: m.mes,
          periodo: { inicio: m.inicio, fim: m.fim },
          saldo_sem_fixos_inicio: 0,
          saldo_sem_fixos_fim: 0,
          variacao_saldo_sem_fixos: 0,
          estoque_inicio: 0,
          estoque_fim: 0,
          variacao_estoque: 0,
          resultado_mensal: 0
        });
      }
    }

    // Garante continuidade: saldo_fim(mês N) = saldo_inicio(mês N+1)
    // Se houver diferença (por arredondamentos/semântica do endpoint), ajustamos o saldo_inicio do mês seguinte
    for (let i = 1; i < resultados.length; i++) {
      const prev = resultados[i - 1];
      const curr = resultados[i];
      const prevFim = Number(prev.saldo_sem_fixos_fim) || 0;
      if (curr.saldo_sem_fixos_inicio !== prevFim) {
        curr.saldo_sem_fixos_inicio = prevFim;
        curr.variacao_saldo_sem_fixos = (Number(curr.saldo_sem_fixos_fim) || 0) - prevFim;
        // Recalcula o resultado mensal mantendo a variação de estoque original
        curr.resultado_mensal = curr.variacao_saldo_sem_fixos + (Number(curr.variacao_estoque) || 0);
      }
    }

    return resultados;
  }

  private static formatPeriod(dataInicio: string, dataFim: string): string {
    return `${dataInicio} a ${dataFim}`;
  }

  static async buscarDadosGerencia(dataInicio: string, dataFim: string): Promise<GerenciaData> {
    try {
      console.log('🔄 Iniciando busca de dados de gerência...');
      console.log('📅 Período:', { dataInicio, dataFim });

      // Implementar lógica inteligente de data como no controle de estoque
      const isCurrentPeriod = this.isToday(dataFim);
      const fonteDados = isCurrentPeriod ? 'atual' : 'historico';
      
      console.log(`📋 Fonte de dados: ${fonteDados} (fim do período é hoje: ${isCurrentPeriod})`);

      // Buscar dados de estoque no início e fim do período
      const [estoqueInicioResponse, estoqueFimResponse] = await Promise.all([
        this.buscarEstoquePorData(dataInicio),
        this.buscarEstoquePorData(dataFim)
      ]);

      // Buscar faturamento dos contratos
      const faturamento = await this.buscarFaturamento(dataInicio, dataFim);

      // Buscar custos fixos
      const custosFixos = await this.buscarCustosFixos(dataInicio, dataFim);

      // Buscar custos variáveis
      const custosVariaveis = await this.buscarCustosVariaveis(dataInicio, dataFim);

      // Buscar contas não pagas no início e fim do período e clientes com contrato
      const [contasInicio, contasFim, clientesContrato] = await Promise.all([
        this.buscarContasNaoPagas(dataInicio),
        this.buscarContasNaoPagas(dataFim),
        this.buscarClientesComContrato()
      ]);

      const clientesContratoSet = new Set<number>(clientesContrato);

      // Helper para somar A Receber de clientes com contrato para um snapshot (antes da data de corte)
      const somarReceberContratos = (resp: ContasNaoPagasResponse) => {
        const lista = resp?.detalhamento?.contas_a_receber?.antes_data_corte
          ?? resp?.contas_a_receber?.antes_data_corte
          ?? [];
        if (!Array.isArray(lista)) return { valor: 0, quantidade: 0 };
        let totalValor = 0;
        let totalQtde = 0;
        for (const item of lista as ReceberResumoItem[]) {
          const cliId = Number(item?.cliente?.id ?? 0);
          if (cliId && clientesContratoSet.has(cliId)) {
            totalValor += Number(item?.valor_total ?? 0) || 0;
            totalQtde += Number(item?.total_contas ?? 0) || 0;
          }
        }
        return { valor: totalValor, quantidade: totalQtde };
      };

      const inicioContratos = somarReceberContratos(contasInicio);
      const fimContratos = somarReceberContratos(contasFim);

      // Extrair totais por tipo (FIXO / VARIÁVEL) para contas a pagar e calcular 'Outros'
      const pegarTotaisTipos = (res: ContasNaoPagasResponse) => {
        const tipos = res?.resumo_geral?.antes_data_corte?.custos_por_tipo;
        // Alguns ambientes podem usar 'VARIAVEL' sem acento; cobrimos ambos
        const fixoValor = Number(tipos?.FIXO?.valor_total) || 0;
        const fixoCount = Number(tipos?.FIXO?.total_contas) || 0;
        const variavelValor = Number((tipos?.['VARIÁVEL']?.valor_total ?? tipos?.VARIAVEL?.valor_total) || 0);
        const variavelCount = Number((tipos?.['VARIÁVEL']?.total_contas ?? tipos?.VARIAVEL?.total_contas) || 0);
        let outrosValor = 0;
        let outrosCount = 0;
        if (tipos) {
          for (const [chave, info] of Object.entries(tipos)) {
            const k = chave.toUpperCase();
            if (k === 'FIXO' || k === 'VARIÁVEL' || k === 'VARIAVEL') continue;
            const v = info?.valor_total ?? 0;
            const c = info?.total_contas ?? 0;
            outrosValor += Number(v) || 0;
            outrosCount += Number(c) || 0;
          }
        }
        return { fixoValor, fixoCount, variavelValor, variavelCount, outrosValor, outrosCount };
      };

      const tiposInicio = pegarTotaisTipos(contasInicio);
      const tiposFim = pegarTotaisTipos(contasFim);

      const resultado: GerenciaData = {
        estoqueInicio: estoqueInicioResponse.valor_total_estoque,
        estoqueFim: estoqueFimResponse.valor_total_estoque,
        faturamentoContratos: faturamento.totais_gerais.total_valor_geral,
        custosFixos: custosFixos.totais_gerais.valor_total,
        custosVariaveis: custosVariaveis.totais_gerais.valor_total,
        contasReceberInicio: contasInicio.resumo_geral.antes_data_corte.valor_total_receber,
        contasReceberInicioContratos: inicioContratos.valor,
        contasReceberInicioContratosCount: inicioContratos.quantidade,
        contasPagarInicio: contasInicio.resumo_geral.antes_data_corte.valor_total_pagar,
        contasReceberFim: contasFim.resumo_geral.antes_data_corte.valor_total_receber,
        contasReceberFimContratos: fimContratos.valor,
        contasReceberFimContratosCount: fimContratos.quantidade,
        contasPagarFim: contasFim.resumo_geral.antes_data_corte.valor_total_pagar,
        // Preencher contagens quando disponíveis
        contasReceberInicioCount: contasInicio.resumo_geral.antes_data_corte.total_contas_receber,
        contasPagarInicioCount: contasInicio.resumo_geral.antes_data_corte.total_contas_pagar,
        contasReceberFimCount: contasFim.resumo_geral.antes_data_corte.total_contas_receber,
        contasPagarFimCount: contasFim.resumo_geral.antes_data_corte.total_contas_pagar,
        // Discriminação de pagar por tipo
        contasPagarInicioFixos: tiposInicio.fixoValor,
        contasPagarInicioVariaveis: tiposInicio.variavelValor,
        contasPagarInicioFixosCount: tiposInicio.fixoCount,
        contasPagarInicioVariaveisCount: tiposInicio.variavelCount,
        contasPagarInicioOutros: tiposInicio.outrosValor,
        contasPagarInicioOutrosCount: tiposInicio.outrosCount,
        contasPagarFimFixos: tiposFim.fixoValor,
        contasPagarFimVariaveis: tiposFim.variavelValor,
        contasPagarFimFixosCount: tiposFim.fixoCount,
        contasPagarFimVariaveisCount: tiposFim.variavelCount,
        contasPagarFimOutros: tiposFim.outrosValor,
        contasPagarFimOutrosCount: tiposFim.outrosCount,
        fonteDados: {
          estoque: fonteDados,
          periodo: this.formatPeriod(dataInicio, dataFim),
          isToday: isCurrentPeriod
        }
      };

      console.log('✅ Dados de gerência carregados com sucesso:', resultado);
      return resultado;

    } catch (error) {
      console.error('❌ Erro ao buscar dados de gerência:', error);
      throw error;
    }
  }

  static async buscarEstoquePorData(data: string): Promise<EstoqueReportResponse> {
    try {
      console.log(`📦 Buscando VALOR TOTAL do estoque para data: ${data}`);
      
      // Usar o MESMO endpoint do Controle de Estoque (sem prefixo /api)
      // Controle de Estoque chama: /contas/estoque-controle/valor_total_estoque/?data=YYYY-MM-DD
      const response = await fetch(`${API_BASE_URL}/estoque-controle/valor_total_estoque/?data=${data}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const estoqueData = await response.json();
      
      // O endpoint retorna um objeto com a chave 'valor_total_estoque'
      const resultado: EstoqueReportResponse = {
        data_posicao: data,
        valor_total_estoque: estoqueData.valor_total_estoque || 0,
        total_produtos_em_estoque: estoqueData.total_produtos_em_estoque || 0,
        detalhes_por_produto: [] // Este endpoint não retorna detalhes por produto
      };
      
      console.log(`✅ Valor total do estoque (controle): R$ ${resultado.valor_total_estoque}`);
      return resultado;
      
    } catch (error) {
      console.error('Erro ao buscar valor total do estoque:', error);
      throw error;
    }
  }

  static async buscarFaturamento(dataInicio: string, dataFim: string): Promise<FaturamentoContratosResponse> {
    try {
      // Alinha com a página de contratos: usa o endpoint de vigência/suprimentos
      // GET http://localhost:8000/api/contratos_locacao/suprimentos/?data_inicial=YYYY-MM-DD&data_final=YYYY-MM-DD
      const url = `http://localhost:8000/api/contratos_locacao/suprimentos/?data_inicial=${dataInicio}&data_final=${dataFim}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Erro ${response.status}: ${response.statusText}`);
      }

      // A resposta possui estrutura { periodo, resumo, resumo_financeiro, resultados }
      const dados = await response.json();

      // Para manter compatibilidade com o restante do código (que espera FaturamentoContratosResponse),
      // mapeamos os totais do endpoint de contratos para os campos esperados.
      const mapped: FaturamentoContratosResponse = {
        parametros: {
          data_inicio: dados?.periodo?.data_inicio ?? dataInicio,
          data_fim: dados?.periodo?.data_fim ?? dataFim,
          filtros_aplicados: {
            nf_entrada: 'todos',
            nf_saida: 'todos',
            nf_servico: 'todos'
          },
          fonte_dados: 'api/contratos_locacao/suprimentos'
        },
        totais_gerais: {
          total_quantidade_notas: Number(dados?.resumo?.total_contratos_vigentes) || 0,
          total_valor_produtos: 0,
          // Valor que o painel deve exibir como faturamento: mesmo total usado na página de contratos
          total_valor_geral: Number(dados?.resumo_financeiro?.faturamento_total_proporcional) || 0,
          total_impostos: 0,
          analise_vendas: {
            valor_vendas: Number(dados?.resumo_financeiro?.faturamento_total_proporcional) || 0,
            valor_preco_entrada: Number(dados?.resumo_financeiro?.custo_total_suprimentos) || 0,
            margem_bruta: Number(dados?.resumo_financeiro?.margem_bruta_total) || 0,
            percentual_margem: Number(dados?.resumo_financeiro?.percentual_margem_total) || 0,
            itens_analisados: Number(dados?.resumo?.total_contratos_vigentes) || 0,
            produtos_sem_preco_entrada: 0
          }
        }
      };

      return mapped;
    } catch (error) {
      console.error('❌ Erro ao buscar faturamento:', error);
      throw error;
    }
  }

  static async buscarCustosFixos(dataInicio: string, dataFim: string): Promise<CustosFixosResponse> {
    try {
      // Alinhar com o dashboard de Custos Fixos: usar o endpoint /api/relatorios/custos-fixos/
      const url = `http://127.0.0.1:8000/api/relatorios/custos-fixos/?data_inicio=${dataInicio}&data_fim=${dataFim}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Erro ${response.status}: ${response.statusText}`);
      }

      const apiData = await response.json();

      // Extrair totais pagos no período (gastos no período)
      const totalPago = Number(apiData?.totais_gerais?.total_valor_pago) || 0;
      const totalContas = Number(apiData?.total_contas_pagas) || 0;

      // Tentar separar custos fixos x despesas fixas quando disponível
      let valorCustosFixos = 0;
      let valorDespesasFixas = 0;
      if (Array.isArray(apiData?.resumo_por_tipo_fornecedor)) {
        for (const item of apiData.resumo_por_tipo_fornecedor as Array<Record<string, unknown>>) {
          const tipo = String((item['fornecedor__tipo'] ?? item['tipo_fornecedor'] ?? ''));
          const valor = Number((item['total_pago'] ?? item['valor_total'] ?? 0));
          if (tipo.toUpperCase() === 'CUSTO FIXO') valorCustosFixos += valor;
          else if (tipo.toUpperCase() === 'DESPESA FIXA') valorDespesasFixas += valor;
        }
      }

      const mapped: CustosFixosResponse = {
        parametros: {
          data_inicio: apiData?.parametros?.data_inicio ?? dataInicio,
          data_fim: apiData?.parametros?.data_fim ?? dataFim,
          filtro_aplicado: 'Pagos no período (Fornecedores tipo CUSTO FIXO/DESPESA FIXA)',
          fonte_dados: 'Contas a Pagar (status: Pago)'
        },
        totais_gerais: {
          valor_total: totalPago,
          valor_custos_fixos: valorCustosFixos,
          valor_despesas_fixas: valorDespesasFixas,
          quantidade_total_contas: totalContas
        }
      };

      return mapped;
    } catch (error) {
      console.error('❌ Erro ao buscar custos fixos:', error);
      throw error;
    }
  }

  static async buscarCustosVariaveis(dataInicio: string, dataFim: string): Promise<CustosVariaveisResponse> {
    try {
      // Preferir o endpoint usado nos relatórios: /api/relatorios/custos-variaveis/
      let response = await fetch(
        `http://127.0.0.1:8000/api/relatorios/custos-variaveis/?data_inicio=${dataInicio}&data_fim=${dataFim}`
      );

      // Fallback para rota alternativa caso necessário
      if (!response.ok) {
        response = await fetch(
          `http://localhost:8000/contas/relatorios/custos-variaveis/?data_inicio=${dataInicio}&data_fim=${dataFim}`
        );
      }

      if (!response.ok) {
        throw new Error(`Erro ${response.status}: ${response.statusText}`);
      }

      const apiData = await response.json();
      const totalPago = Number(apiData?.totais_gerais?.total_valor_pago) || 0;
      const totalContas = Number(apiData?.total_contas_pagas) || 0;

      const mapped: CustosVariaveisResponse = {
        parametros: {
          data_inicio: apiData?.parametros?.data_inicio ?? dataInicio,
          data_fim: apiData?.parametros?.data_fim ?? dataFim,
          filtro_aplicado: 'Fornecedores com tipo relacionado a CUSTOS VARIÁVEIS',
          fonte_dados: 'Contas a Pagar (status: Pago)'
        },
        totais_gerais: {
          valor_total: totalPago,
          quantidade_total_contas: totalContas
        }
      };

      return mapped;
    } catch (error) {
      console.error('❌ Erro ao buscar custos variáveis:', error);
      throw error;
    }
  }

  static async buscarContasNaoPagas(dataCorte: string): Promise<ContasNaoPagasResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/contas-nao-pagas-por-data-corte/?data_corte=${dataCorte}`);
      
      if (!response.ok) {
        throw new Error(`Erro ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('❌ Erro ao buscar contas não pagas:', error);
      throw error;
    }
  }

  // Retorna lista de IDs de clientes que possuem contratos de locação
  static async buscarClientesComContrato(): Promise<number[]> {
    try {
      let url = `http://localhost:8000/contas/contratos_locacao/`;
      const ids = new Set<number>();
      let safety = 0;
      type ContratoItem = { cliente_id?: number; cliente?: { id?: number } };
      type Paginated<T> = { results: T[]; next?: string | null };
      const isPaginated = (d: unknown): d is Paginated<ContratoItem> => {
        if (!d || typeof d !== 'object') return false;
        const obj = d as Record<string, unknown>;
        return Array.isArray(obj.results);
      };
      while (url && safety < 50) {
        const resp = await fetch(url);
        if (!resp.ok) break;
        const data: unknown = await resp.json();
        const items: ContratoItem[] = Array.isArray(data)
          ? (data as ContratoItem[])
          : (isPaginated(data) ? data.results : []);
        for (const it of items) {
          const cliId = Number(it?.cliente_id ?? it?.cliente?.id ?? 0);
          if (cliId) ids.add(cliId);
        }
        const next = isPaginated(data) ? data.next : '';
        url = typeof next === 'string' && next.length > 0 ? next : '';
        safety += 1;
        if (!Array.isArray(data) && !isPaginated(data)) break; // não paginado, encerra
      }
      return Array.from(ids);
    } catch (e) {
      console.warn('⚠️ Falha ao buscar clientes com contrato, seguindo sem filtro específico:', e);
      return [];
    }
  }
}