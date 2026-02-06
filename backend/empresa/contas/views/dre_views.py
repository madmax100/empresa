# contas/views/dre_views.py
"""
Endpoint para Demonstrativo de Resultados (DRE) e Saúde Financeira
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from decimal import Decimal

from ..models.access import (
    ContasPagar,
    ContasReceber,
    NotasFiscaisSaida,
    NotasFiscaisEntrada,
    NotasFiscaisServico,
    MovimentacoesEstoque,
    Produtos,
    ContratosLocacao,
    SaldosEstoque,
    Fornecedores,
    ItensNfSaida,
    ItensNfEntrada
)


class DREView(APIView):
    """
    Endpoint para cálculo do DRE (Demonstrativo de Resultados) e indicadores de Saúde Financeira.
    
    GET /api/contas/dre/?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD
    
    Retorna:
    - DRE: Faturamento, Impostos, CMV, Lucro Bruto, Despesas, Resultado Líquido
    - Saúde Financeira: Liquidez, Contas a Receber/Pagar, Capital de Giro
    - Ciclo de Caixa: Análise de necessidade de capital
    """
    
    # Percentual médio de impostos sobre vendas (Simples Nacional estimado)
    PERCENTUAL_IMPOSTOS = Decimal('0.08')  # 8%
    
    # Mapeamento de Categorias de Custos
    # --- Métodos de Categorização Padronizados (Portados de relatorios_views.py) ---
    
    def _definir_categoria_fixa(self, nome, tipo_original):
        """
        Define categoria para custos fixos baseado em palavras-chave.
        Mesma lógica de RelatorioCustosFixosView.
        """
        nome = str(nome or '').upper()
        tipo_original = str(tipo_original or '').upper()
        
        if 'FOLHA' in nome or 'SALARIO' in nome or 'SALÁRIO' in nome: return 'Pessoal'
        if 'PROLABORE' in nome or 'PRO-LABORE' in nome: return 'Pró-Labore'
        if 'INSS' in nome or 'FGTS' in nome or 'DARF' in nome: return 'Impostos'
        if 'ALUGUEL' in nome: return 'Aluguel'
        if 'LUZ' in nome or 'ENERGIA' in nome or 'AGUA' in nome or 'ÁGUA' in nome: return 'Utilidades'
        if 'TELEFONE' in nome or 'INTERNET' in nome: return 'Telecom'
        if 'CONTADOR' in nome or 'CONTABILIDADE' in nome: return 'Contabilidade'
        if 'SEGURO' in nome: return 'Seguros'
        
        return tipo_original if tipo_original and tipo_original != 'N/A' else 'Outros Fixos'

    def _definir_categoria_variavel(self, nome_fornecedor, historico, especificacao_original):
        """
        Define categoria para custos variáveis baseado em palavras-chave e especificação.
        Mesma lógica de RelatorioCustosVariaveisView.
        """
        nome_safe = str(nome_fornecedor) if nome_fornecedor is not None else ''
        hist_safe = str(historico) if historico is not None else ''
        texto = (nome_safe + ' ' + hist_safe).upper()
        
        # --- Categorias Financeiras ---
        if 'TARIFA' in texto and ('BANC' in texto or 'BOLETO' in texto or 'PIX' in texto or 'CHEQUE' in texto or 'MANUTENÇ' in texto or 'RELACION' in texto or 'BAIXA' in texto or 'REGISTRO' in texto or 'ALTERAÇ' in texto or 'CONCESS' in texto):
            return 'Tarifas Bancárias'
        elif 'JUROS' in texto:
            return 'Juros'
        elif 'EMPREST' in texto or 'EMPRÉSTIMO' in texto or 'CONSIGNAD' in texto:
            return 'Empréstimos'
        elif 'COMPRA DE TIT' in texto or 'DESCONTO' in texto and 'TARIFA' not in texto:
            return 'Operações Financeiras'
        
        # --- Categorias Operacionais / Logística ---
        elif 'FRETE' in texto or 'TRANSPORT' in texto:
            return 'Frete'
        elif 'COMBUSTIVEL' in texto or 'COMBUSTÍVEL' in texto:
            return 'Combustível'
        elif 'ESTACIONAMENTO' in texto:
            return 'Estacionamento'
        elif 'MANUTENÇÃ' in texto and 'VEIC' in texto or 'VIA MOTOS' in texto or 'ÓLEO' in texto or 'OLEO' in texto or 'REVISÃO' in texto:
            return 'Manutenção Veículos'
        elif 'VIAGEM' in texto or 'PASSAGEM' in texto:
            return 'Despesas de Viagem'
        elif 'RASTREAMENTO' in texto:
            return 'Rastreamento'
        
        # --- Categorias de Alimentação ---
        elif 'REFEIÇÃO' in texto or 'REFEICAO' in texto:
            return 'Alimentação'
        elif 'COPA' in texto or 'CAFÉ' in texto or 'CAFE' in texto or 'AGUA' in texto or 'ÁGUA' in texto:
            return 'Materiais Copa'
        
        # --- Categorias de Materiais ---
        elif 'ASSIST' in texto and 'TECN' in texto or 'ASSIST.TECN' in texto:
            return 'Materiais Assist. Técnica'
        elif 'ESCRITORIO' in texto or 'ESCRITÓRIO' in texto:
            return 'Materiais Escritório'
        
        # --- Categorias de Serviços ---
        elif 'DIARISTA' in texto or 'SERV.TERCEIROS' in texto or 'SERVIÇOS TERCEIROS' in texto:
            return 'Serviços Terceiros'
        elif 'CONTADOR' in texto or 'CONTABIL' in texto or 'CONTÁBIL' in texto:
            return 'Contabilidade'
        elif 'CERTIFICAÇ' in texto or 'CERTIFICADO DIGITAL' in texto:
            return 'Certificação Digital'
        elif 'TREINAMENTO' in texto or 'CURSO' in texto:
            return 'Treinamento'
        elif 'MARKETING' in texto or 'IMPULSIONAMENTO' in texto:
            return 'Marketing'
        elif 'INTERMAX' in texto or 'SISTEMA' in texto:
            return 'Software/Sistemas'
        
        # --- Categorias de Telecomunicações e Utilidades ---
        elif 'OI' in nome_safe.upper() and ('CONTA' in texto or 'NIO' in texto) or 'TELEFONE' in texto:
            return 'Telecomunicações'
        elif 'COELCE' in texto or 'ENERGIA' in texto or 'LUZ' in texto:
            return 'Energia Elétrica'
        
        # --- Categorias de Impostos e Taxas ---
        elif 'ICMS' in texto or 'IMPOSTO' in texto:
            return 'ICMS'
        elif 'SIMPLES' in texto or 'DARF' in texto:
            return 'Impostos'
        elif 'CDL' in texto or 'SINDICATO' in texto:
            return 'Associações/Sindicatos'
        
        # --- Categorias de Pessoal ---
        elif 'CONFRATERNIZAÇ' in texto or 'ANIVERSÁRIO' in texto:
            return 'Confraternização'
        elif 'AJUDA CUSTO' in texto:
            return 'Ajuda de Custo'
        
        # --- Categorias Comerciais ---
        elif 'COMISSAO' in texto or 'COMISSÃO' in texto or 'REPRESENTANTE' in texto:
            return 'Comissão'
        
        # --- Diversos ---
        elif 'DIVERSOS' in texto:
            return 'Diversos'
        
        # --- Se já tem especificação original útil, usa ela ---
        if especificacao_original and especificacao_original.strip() and especificacao_original != 'Sem Especificação':
            return especificacao_original
        
        # --- Fallback: Verificar se o nome do fornecedor parece ser de uma empresa ---
        if any(term in nome_safe.upper() for term in ['LTDA', 'ME', 'EIRELI', 'EPP', 'S/A', 'S.A.', 'COMERCIO', 'COMÉRCIO', 'DISTRIBUI', 'IMPORTA']):
            return 'Fornecedor'
        
        return 'Outros'
    
    def get(self, request):
        # Parâmetros de data
        data_inicio_str = request.query_params.get('data_inicio')
        data_fim_str = request.query_params.get('data_fim')
        
        if not data_inicio_str or not data_fim_str:
            # Default: mês atual
            hoje = datetime.now().date()
            data_inicio = hoje.replace(day=1)
            data_fim = hoje
        else:
            try:
                data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
                data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de data inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Calcular DRE
        dre = self._calcular_dre(data_inicio, data_fim)
        
        # Calcular Saúde Financeira
        saude_financeira = self._calcular_saude_financeira(data_fim)
        
        # Calcular Ciclo de Caixa
        ciclo_caixa = self._calcular_ciclo_caixa(data_inicio, data_fim, saude_financeira)
        
        return Response({
            'periodo': {
                'inicio': data_inicio.isoformat(),
                'fim': data_fim.isoformat()
            },
            'dre': dre,
            'saude_financeira': saude_financeira,
            'ciclo_caixa': ciclo_caixa
        })
    
    def _calcular_dre(self, data_inicio, data_fim):
        """Calcula o Demonstrativo de Resultados do período."""
        
        # 1. FATURAMENTO BRUTO - NFe de Saída (Vendas) + NF Serviço
        
        # 1.1 Vendas de Mercadorias (NF Saída)
        # Filtro: apenas operações que contêm "VENDA" (consistente com relatorios_views.py)
        nfs_vendas = NotasFiscaisSaida.objects.filter(
            operacao__icontains='VENDA',
            data__range=[data_inicio, data_fim]
        ).select_related('cliente')
        
        faturamento_vendas = sum(nf.valor_total_nota or Decimal('0') for nf in nfs_vendas)
        
        # Lista de vendas para modal
        lista_vendas = [{
            'numero': nf.numero_nota,
            'data': nf.data.strftime('%d/%m/%Y') if nf.data else '',
            'cliente': nf.cliente.nome if nf.cliente else 'N/A',
            'valor': float(nf.valor_total_nota or 0)
        } for nf in nfs_vendas.order_by('-data')[:100]]  # Limitar a 100 para performance
        
        # 1.2 Serviços (NF Serviço) - Separar Contratos vs Avulsos
        # Padrão para identificar referência a contrato: "C" seguido de números (ex: C372)
        import re
        contrato_pattern = re.compile(r'C\d+', re.IGNORECASE)
        
        nfs_servico = NotasFiscaisServico.objects.filter(
            data__date__gte=data_inicio,
            data__date__lte=data_fim
        ).select_related('cliente')
        
        faturamento_servicos_contratos = Decimal('0')
        faturamento_servicos_avulsos = Decimal('0')
        lista_servicos_contratos = []
        lista_servicos_avulsos = []
        
        for nf in nfs_servico.order_by('-data'):
            obs = nf.obs or ''
            valor = nf.valor_total or Decimal('0')
            
            item = {
                'numero': nf.numero_nota,
                'data': nf.data.strftime('%d/%m/%Y') if nf.data else '',
                'cliente': nf.cliente.nome if nf.cliente else 'N/A',
                'valor': float(valor),
                'obs': obs[:50] + '...' if len(obs) > 50 else obs
            }
            
            if contrato_pattern.search(obs):
                faturamento_servicos_contratos += valor
                if len(lista_servicos_contratos) < 100:
                    lista_servicos_contratos.append(item)
            else:
                faturamento_servicos_avulsos += valor
                if len(lista_servicos_avulsos) < 100:
                    lista_servicos_avulsos.append(item)
        
        faturamento_servicos = faturamento_servicos_contratos + faturamento_servicos_avulsos
        
        # 1.3 Total Faturamento Bruto
        faturamento_bruto = faturamento_vendas + faturamento_servicos

        
        # 2. IMPOSTOS SOBRE VENDAS (estimativa)
        impostos_vendas = faturamento_bruto * self.PERCENTUAL_IMPOSTOS
        
        
        # 3. CMV (Custo da Mercadoria Vendida)
        # Novo cálculo: Custo dos itens que saíram (baseado na última entrada)
        # Estoque e compras não são mais usados para CMV, definindo como 0 para manter compatibilidade do retorno
        estoque_inicio = Decimal('0')
        estoque_fim = Decimal('0')
        # 4. Cálculo do CMV (Custo da Mercadoria Vendida)
        itens_vendidos_result = self._calcular_cmv_real(data_inicio, data_fim)
        # Unpacking handled dynamically below to support old/new signature if needed, but here we expect the new one
        if len(itens_vendidos_result) == 8:
             cmv, cmv_vendas, cmv_contratos, cmv_outros, lista_cmv, lista_cmv_vendas, lista_cmv_contratos, lista_cmv_outros = itens_vendidos_result
        else:
             cmv, cmv_vendas, cmv_contratos, cmv_outros, lista_cmv = itens_vendidos_result
             lista_cmv_vendas, lista_cmv_contratos, lista_cmv_outros = [], [], []
        
        
        # 4. LUCRO BRUTO
        lucro_bruto = faturamento_bruto - impostos_vendas - cmv
        
        # 5. DESPESAS OPERACIONAIS (Custos Fixos + Variáveis)
        custos_fixos, custos_variaveis, detalhe_fixos, detalhe_variaveis = self._calcular_custos(data_inicio, data_fim)
        despesas_operacionais = custos_fixos + custos_variaveis
        despesas_operacionais = custos_fixos + custos_variaveis
        
        # 6. RESULTADO LÍQUIDO
        resultado_liquido = lucro_bruto - despesas_operacionais
        
        # 7. MARGENS
        margem_bruta_percent = (lucro_bruto / faturamento_bruto * 100) if faturamento_bruto > 0 else Decimal('0')
        margem_liquida_percent = (resultado_liquido / faturamento_bruto * 100) if faturamento_bruto > 0 else Decimal('0')
        
        compras_periodo = Decimal('0')

        return {
            'faturamento_bruto': float(faturamento_bruto),
            'faturamento_vendas': float(faturamento_vendas),
            'faturamento_servicos_contratos': float(faturamento_servicos_contratos),
            'faturamento_servicos_avulsos': float(faturamento_servicos_avulsos),
            'lista_vendas': lista_vendas,
            'lista_servicos_contratos': lista_servicos_contratos,
            'lista_servicos_avulsos': lista_servicos_avulsos,
            'impostos_vendas': float(impostos_vendas),
            'percentual_impostos': float(self.PERCENTUAL_IMPOSTOS * 100),
            'estoque_inicio': float(estoque_inicio),
            'compras_periodo': float(compras_periodo),
            'estoque_fim': float(estoque_fim),
            'cmv': float(cmv),
            'cmv_vendas': float(cmv_vendas),
            'cmv_contratos': float(cmv_contratos),
            'cmv_outros': float(cmv_outros),
            'lista_cmv': lista_cmv,
            'lista_cmv_vendas': lista_cmv_vendas,
            'lista_cmv_contratos': lista_cmv_contratos,
            'lista_cmv_outros': lista_cmv_outros,
            'lucro_bruto': float(lucro_bruto),
            'margem_bruta_percent': float(margem_bruta_percent),
            'custos_fixos': float(custos_fixos),
            'custos_variaveis': float(custos_variaveis),
            'detalhe_custos_fixos': detalhe_fixos,
            'detalhe_custos_variaveis': detalhe_variaveis,
            'despesas_operacionais': float(despesas_operacionais),
            'resultado_liquido': float(resultado_liquido),
            'margem_liquida_percent': float(margem_liquida_percent)
        }
    

    def _calcular_cmv_real(self, data_inicio, data_fim):
        """
        Calcula o CMV baseado no custo da última entrada dos itens vendidos.
        CMV = Soma(Quantidade Vendida * Custo Unitário da Última Entrada)
        """
        # 1. Identificar NFs de Saída no período
        # Obter todas as NFs de Saída no período
        all_nfs = NotasFiscaisSaida.objects.filter(
            data__range=[data_inicio, data_fim]
        ).select_related('cliente')
        
        # Obter IDs de todas as NFs
        valid_nf_ids = list(all_nfs.values_list('id', flat=True))
        
        # 2. Identificar contratos vigentes no período (mesma lógica da página Contratos de Locação)
        contratos_vigentes = ContratosLocacao.objects.filter(
            Q(inicio__lte=data_fim) & 
            (Q(fim__gte=data_inicio) | Q(fim__isnull=True))
        )
        clientes_contratos_vigentes = set(contratos_vigentes.values_list('cliente_id', flat=True).distinct())
        
        # 3. Obter itens vendidos/enviados
        try:
            itens_vendidos = ItensNfSaida.objects.filter(
                nota_fiscal_id__in=valid_nf_ids
            ).select_related('produto', 'nota_fiscal', 'nota_fiscal__cliente')
        except:
            return Decimal('0'), Decimal('0'), Decimal('0'), Decimal('0'), []
        
        cmv_total = Decimal('0')
        cmv_vendas = Decimal('0')
        cmv_contratos = Decimal('0')
        cmv_outros = Decimal('0')
        
        lista_itens = []
        lista_vendas = []
        lista_contratos = []
        lista_outros = []
        custos_cache = {}
        
        for item in itens_vendidos:
            produto_id = item.produto_id
            quantidade = item.quantidade or Decimal('0')
            valor_venda_total = item.valor_total or Decimal('0')
            valor_venda_unitario = item.valor_unitario or Decimal('0')
            
            # Classificação do Item usando mesmo critério da página Contratos de Locação
            operacao = (item.nota_fiscal.operacao or '').upper()
            cliente_id = item.nota_fiscal.cliente_id
            
            tipo_item = 'OUTROS'
            if 'VENDA' in operacao:
                tipo_item = 'VENDA'
            elif 'SIMPLES REMESSA' in operacao and cliente_id in clientes_contratos_vigentes:
                # Critério correto: SIMPLES REMESSA para cliente com contrato vigente
                tipo_item = 'CONTRATO'
            
            data_venda = item.nota_fiscal.data
            
            if produto_id in custos_cache:
                custo_unit = custos_cache[produto_id]
            else:
                custo_unit = Decimal('0')
                try:
                    ultima_entrada = ItensNfEntrada.objects.filter(
                        produto_id=produto_id,
                        nota_fiscal__data_entrada__lte=data_venda
                    ).order_by('-nota_fiscal__data_entrada', '-id').first()
                    
                    if ultima_entrada:
                        if ultima_entrada.valor_total and ultima_entrada.quantidade:
                             custo_unit = ultima_entrada.valor_total / ultima_entrada.quantidade
                        elif ultima_entrada.valor_unitario:
                             custo_unit = ultima_entrada.valor_unitario
                except:
                    pass
                
                if custo_unit == Decimal('0'):
                    try:
                        produto = Produtos.objects.get(id=produto_id)
                        custo_unit = getattr(produto, 'preco_custo', Decimal('0')) or Decimal('0')
                    except:
                        pass
                
                custos_cache[produto_id] = custo_unit
            
            custo_total_item = quantidade * custo_unit
            cmv_total += custo_total_item
            
            if tipo_item == 'VENDA':
                cmv_vendas += custo_total_item
            elif tipo_item == 'CONTRATO':
                cmv_contratos += custo_total_item
            else:
                cmv_outros += custo_total_item
            
            # if len(lista_itens) < 200: Removed limit to show all items
            try:
                cliente_nome = item.nota_fiscal.cliente.nome if item.nota_fiscal.cliente else 'Consumidor'
            except:
                cliente_nome = 'N/A'
                
            item_data = {
                'data': data_venda.strftime('%d/%m/%Y') if data_venda else '',
                'nota_fiscal': item.nota_fiscal.numero_nota,
                'cliente': cliente_nome,
                'produto': str(item.produto.codigo) if item.produto else 'Item',
                'quantidade': float(quantidade),
                'custo_unitario': float(custo_unit),
                'custo_total': float(custo_total_item),
                'preco_venda_unitario': float(valor_venda_unitario),
                'preco_venda_total': float(valor_venda_total),
                'tipo': tipo_item,
                'operacao': operacao
            }
            
            lista_itens.append(item_data)
            
            if tipo_item == 'VENDA':
                lista_vendas.append(item_data)
            elif tipo_item == 'CONTRATO':
                lista_contratos.append(item_data)
            else:
                lista_outros.append(item_data)
            
        # Recalcular CMV Total apenas com Vendas e Contratos (Excluindo Outros, conforme solicitado)
        cmv_total = cmv_vendas + cmv_contratos
            
        return cmv_total, cmv_vendas, cmv_contratos, cmv_outros, lista_itens, lista_vendas, lista_contratos, lista_outros

    def _obter_valor_estoque(self, data):
        """
        Obtém o valor total do estoque.
        Nota: SaldosEstoque é uma tabela de saldo atual, não histórica.
        Para um DRE preciso, seria necessário snapshots históricos.
        Usamos o saldo atual como aproximação.
        """
        from django.db.models import F
        
        # SaldosEstoque tem: quantidade, custo_medio, produto_id
        # Valor = soma(quantidade * custo_medio)
        total = SaldosEstoque.objects.aggregate(
            valor_total=Sum(F('quantidade') * F('custo_medio'))
        )['valor_total']
        
        if total:
            return Decimal(str(total))
        
        # Fallback: calcular direto dos produtos
        total = Decimal('0')
        produtos = Produtos.objects.filter(ativo=True)
        for produto in produtos:
            qtd = produto.estoque_atual or 0
            preco = produto.preco_custo or 0
            total += Decimal(str(qtd)) * Decimal(str(preco))
        
        return total
    
    def _calcular_custos(self, data_inicio, data_fim):
        """Calcula custos fixos e variáveis do período categorizados."""
        
        contas_pagas = ContasPagar.objects.filter(
            data_pagamento__range=[data_inicio, data_fim],
            status='P'
        ).select_related('fornecedor')
        
        # Estruturas para acumular valores
        # { 'Categoria': {'valor': Decimal, 'itens': []} }
        fixos_map = {}
        variaveis_map = {}
        
        total_fixo = Decimal('0')
        total_variavel = Decimal('0')
        
        # Palavras-chave para identificar custos fixos (mesma lista de RelatorioCustosVariaveisView)
        KEYWORDS_FIXOS = ['FOLHA', 'PROLABORE', 'PRO-LABORE', 'ALUGUEL', 'SALARIO', 'SALÁRIO', 
                         'INSS', 'FGTS', 'CONTADOR', 'CONTABILIDADE', 'LUZ', 'ENERGIA', 
                         'ÁGUA', 'AGUA', 'TELEFONE', 'INTERNET', 'SEGURO']
        
        for conta in contas_pagas:
            valor = Decimal(str(conta.valor_total_pago or conta.valor or 0))
            if valor <= 0: continue
            
            nome_fornecedor = conta.fornecedor.nome if conta.fornecedor and conta.fornecedor.nome else ''
            tipo_fornecedor_db = conta.fornecedor.tipo if conta.fornecedor else None
            especificacao_original = conta.fornecedor.especificacao if conta.fornecedor else None
            historico = conta.historico or ''
            
            # --- Lógica de Decisão: Fixo vs Variável ---
            # Segue a mesma lógica de exclusão/inclusão dos relatórios
            # 1. Verifica se contém Keywords de Fixos
            eh_fixo = False
            texto_busca = nome_fornecedor.upper()
            
            # Checa se é fixo baseado nas keywords
            for keyword in KEYWORDS_FIXOS:
                if keyword in texto_busca:
                     eh_fixo = True
                     break
            
            # 2. Definição da Categoria Específica
            if eh_fixo:
                categoria = self._definir_categoria_fixa(nome_fornecedor, tipo_fornecedor_db)
                tipo_custo = 'FIXO'
            else:
                categoria = self._definir_categoria_variavel(nome_fornecedor, historico, especificacao_original)
                tipo_custo = 'VARIAVEL'
            
            # Prepara dados do item
            item_data = {
                'data': conta.data_pagamento.strftime('%d/%m/%Y'),
                'descricao': f"{nome_fornecedor} - {historico}"[:60],
                'valor': float(valor)
            }
            
            # Acumula nos mapas
            if tipo_custo == 'FIXO':
                total_fixo += valor
                if categoria not in fixos_map:
                    fixos_map[categoria] = {'valor': Decimal('0'), 'itens': []}
                fixos_map[categoria]['valor'] += valor
                fixos_map[categoria]['itens'].append(item_data)
            else:
                total_variavel += valor
                if categoria not in variaveis_map:
                    variaveis_map[categoria] = {'valor': Decimal('0'), 'itens': []}
                variaveis_map[categoria]['valor'] += valor
                variaveis_map[categoria]['itens'].append(item_data)
        
        # Converter mapas para listas ordenadas
        def map_to_list(map_data):
            lista = []
            for cat, dados in map_data.items():
                lista.append({
                    'categoria': cat,
                    'valor': float(dados['valor']),
                    'itens': dados['itens'] # Já é uma lista de dicts
                })
            return sorted(lista, key=lambda x: x['valor'], reverse=True)
        
        detalhe_fixos = map_to_list(fixos_map)
        detalhe_variaveis = map_to_list(variaveis_map)
        
        return total_fixo, total_variavel, detalhe_fixos, detalhe_variaveis
        
        for conta in contas_pagas:
            valor = Decimal(str(conta.valor_total_pago or conta.valor or 0))
            if valor <= 0: continue
            
            nome_fornecedor = conta.fornecedor.nome.upper() if conta.fornecedor and conta.fornecedor.nome else ''
            historico = (conta.historico or '').upper()
            texto_busca = f"{nome_fornecedor} {historico}"
            
            # Identificar Categoria
            categoria_encontrada = 'Outros'
            tipo_custo = 'VARIAVEL' # Default
            
            # 1. Tenta Fixos
            found = False
            for cat, keywords in self.CATEGORIAS_MAPPING['FIXO'].items():
                if any(k in texto_busca for k in keywords):
                    categoria_encontrada = cat
                    tipo_custo = 'FIXO'
                    found = True
                    break
            
            # 2. Tenta Variáveis (se não achou fixo)
            if not found:
                for cat, keywords in self.CATEGORIAS_MAPPING['VARIAVEL'].items():
                    if any(k in texto_busca for k in keywords):
                        categoria_encontrada = cat
                        tipo_custo = 'VARIAVEL'
                        found = True
                        break
            
            # Se não achou nada, mantém default (Outros Variáveis)
            if not found:
                categoria_encontrada = 'Outros / Não Classificado'
                tipo_custo = 'VARIAVEL'

            # Adicionar ao mapa
            item_data = {
                'data': conta.data_pagamento.strftime('%d/%m/%Y'),
                'descricao': f"{nome_fornecedor} - {historico}"[:60],
                'valor': float(valor)
            }
            
            if tipo_custo == 'FIXO':
                total_fixo += valor
                if categoria_encontrada not in fixos_map:
                    fixos_map[categoria_encontrada] = {'valor': Decimal('0'), 'itens': []}
                fixos_map[categoria_encontrada]['valor'] += valor
                fixos_map[categoria_encontrada]['itens'].append(item_data)
            else:
                total_variavel += valor
                if categoria_encontrada not in variaveis_map:
                    variaveis_map[categoria_encontrada] = {'valor': Decimal('0'), 'itens': []}
                variaveis_map[categoria_encontrada]['valor'] += valor
                variaveis_map[categoria_encontrada]['itens'].append(item_data)
        
        # Converter mapas para listas ordenadas
        def map_to_list(map_data):
            lista = []
            for cat, dados in map_data.items():
                lista.append({
                    'categoria': cat,
                    'valor': float(dados['valor']),
                    'itens': dados['itens'] # Já é uma lista de dicts
                })
            return sorted(lista, key=lambda x: x['valor'], reverse=True)

        return total_fixo, total_variavel, map_to_list(fixos_map), map_to_list(variaveis_map)
    
    def _calcular_saude_financeira(self, data_corte):
        """Calcula indicadores de saúde financeira na data de corte."""
        
        # Liquidez Imediata (aproximação - seria saldo bancário)
        # Como não temos tabela de saldo bancário, usamos uma estimativa
        liquidez_imediata = Decimal('0')  # Placeholder
        
        # Contas a Receber em aberto
        contas_receber = ContasReceber.objects.filter(
            vencimento__lte=data_corte + timedelta(days=30),  # Próximos 30 dias
            status='A'
        ).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0')
        
        # Contas a Pagar em aberto
        contas_pagar = ContasPagar.objects.filter(
            vencimento__lte=data_corte + timedelta(days=30),
            status='A'
        ).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0')
        
        # Capital de Giro em Estoque
        capital_giro_estoque = self._obter_valor_estoque(data_corte)
        
        # Ponto de Equilíbrio = Custos Fixos / Margem de Contribuição %
        # Simplificado: PE = Custos Fixos Mensais / (1 - CMV/Faturamento)
        ponto_equilibrio = Decimal('0')  # Calculado com base no DRE
        
        return {
            'liquidez_imediata': float(liquidez_imediata),
            'contas_receber': float(contas_receber),
            'contas_receber_count': ContasReceber.objects.filter(
                vencimento__lte=data_corte + timedelta(days=30),
                status='A'
            ).count(),
            'contas_pagar': float(contas_pagar),
            'contas_pagar_count': ContasPagar.objects.filter(
                vencimento__lte=data_corte + timedelta(days=30),
                status='A'
            ).count(),
            'capital_giro_estoque': float(capital_giro_estoque),
            'saldo_liquido': float(contas_receber - contas_pagar)
        }
    
    def _calcular_ciclo_caixa(self, data_inicio, data_fim, saude_financeira):
        """Analisa o ciclo de caixa do período."""
        
        entradas_previstas = Decimal(str(saude_financeira['contas_receber']))
        saidas_previstas = Decimal(str(saude_financeira['contas_pagar']))
        saldo_liquido = Decimal(str(saude_financeira['saldo_liquido']))
        
        # Análise automática
        if saldo_liquido >= 0:
            analise = f"Você terá uma sobra de R$ {abs(saldo_liquido):,.2f} no período."
            situacao = 'POSITIVO'
        else:
            analise = f"Você precisará de R$ {abs(saldo_liquido):,.2f} adicional para cobrir as obrigações."
            situacao = 'NEGATIVO'
        
        return {
            'entradas_previstas': float(entradas_previstas),
            'saidas_previstas': float(saidas_previstas),
            'necessidade_capital': float(max(0, -saldo_liquido)),
            'sobra_caixa': float(max(0, saldo_liquido)),
            'situacao': situacao,
            'analise': analise
        }
