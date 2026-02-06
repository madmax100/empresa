# contas/views/relatorios_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Q
from datetime import datetime

from ..models.access import Fornecedores, ContasPagar, NotasFiscaisEntrada, NotasFiscaisSaida, NotasFiscaisServico, ItensNfSaida, MovimentacoesEstoque, SaldosEstoque

class RelatorioCustosFixosView(APIView):
    """
    Endpoint para relatórios de contas pagas de fornecedores 
    com tipos DESPESA FIXA ou CUSTO FIXO em um período.
    
    Utiliza a tabela ContasPagar filtrada por:
    - Status: 'P' (Pago)
    - Fornecedores com tipo 'DESPESA FIXA' ou 'CUSTO FIXO'
    - Período de pagamento especificado
    """
    
    def get(self, request, *args, **kwargs):
        # 1. Validação de Parâmetros
        data_inicio_str = request.query_params.get('data_inicio')
        data_fim_str = request.query_params.get('data_fim')
        
        if not data_inicio_str or not data_fim_str:
            return Response(
                {'error': 'Parâmetros data_inicio e data_fim são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de data inválido. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if data_inicio > data_fim:
            return Response(
                {'error': 'A data de início não pode ser maior que a data de fim.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Parâmetro opcional para categorias
        categorias_param = request.query_params.get('categorias')
        if categorias_param:
            categorias_filtro = [cat.strip() for cat in categorias_param.split(',')]
        else:
            # Categorias padrão para custos e despesas fixas
            categorias_filtro = ['despesas_operacionais', 'despesas_administrativas', 'impostos', 'aluguel']

        # 2. Lógica de Negócio - Filtrar por nome do fornecedor contendo palavras-chave de custos fixos
        
        # Palavras-chave para identificar custos fixos no nome do fornecedor
        # (alinhado com a classificação do fluxo de caixa)
        KEYWORDS_FIXOS = ['FOLHA', 'PROLABORE', 'PRO-LABORE', 'ALUGUEL', 'SALARIO', 'SALÁRIO', 
                         'INSS', 'FGTS', 'CONTADOR', 'CONTABILIDADE', 'LUZ', 'ENERGIA', 
                         'ÁGUA', 'AGUA', 'TELEFONE', 'INTERNET', 'SEGURO']
        
        # Construir query para buscar fornecedores com nomes contendo palavras-chave
        nome_query = Q()
        for keyword in KEYWORDS_FIXOS:
            nome_query |= Q(nome__icontains=keyword)
        
        fornecedores_fixos = Fornecedores.objects.filter(nome_query).values_list('id', flat=True)
        
        # Filtrar contas pagas por esses fornecedores no período
        queryset = ContasPagar.objects.filter(
            status='P',  # Apenas contas pagas
            data_pagamento__date__range=(data_inicio, data_fim),
            fornecedor_id__in=fornecedores_fixos
        ).select_related('fornecedor', 'conta').order_by('-data_pagamento')
        
        # 3. Estrutura da Resposta
        
        # 3. Estrutura da Resposta - Agregação via Python para permitir categorização inteligente
        
        pagamentos_detalhados = []
        resumo_por_tipo = {} # Dicionário para acumular totais por categoria
        resumo_por_fornecedor = {} # Dicionário para acumular totais por fornecedor

        def definir_categoria_fixa(nome, tipo_original):
            # Se já tiver um tipo definido no banco, respeita (opcional, pode-se forçar a regra também)
            # Mas dada a queixa do usuário, vamos priorizar a regra de palavras-chave se o tipo for nulo ou genérico
            
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

        for conta in queryset:
            # Função auxiliar para tratar valores numéricos None
            val_original = float(conta.valor or 0)
            val_pago = float(conta.valor_total_pago or 0)
            val_juros = float(conta.juros or 0)
            val_tarifas = float(conta.tarifas or 0)
            
            nome_fornecedor = conta.fornecedor.nome if conta.fornecedor else 'N/A'
            tipo_fornecedor_db = conta.fornecedor.tipo if conta.fornecedor else None
            
            # Categoria Inteligente
            categoria = definir_categoria_fixa(nome_fornecedor, tipo_fornecedor_db)
            
            # 1. Adicionar aos Detalhes
            pagamentos_detalhados.append({
                'id': conta.id,
                'data_pagamento': conta.data_pagamento.strftime('%Y-%m-%d') if conta.data_pagamento else 'N/A',
                'data_vencimento': conta.vencimento.strftime('%Y-%m-%d') if conta.vencimento else 'N/A',
                'valor_original': val_original,
                'valor_pago': val_pago,
                'juros': val_juros,
                'tarifas': val_tarifas,
                'valor_total_pago': val_pago,
                'historico': conta.historico or 'N/A',
                'fornecedor_nome': nome_fornecedor,
                'fornecedor_tipo': categoria, # Usamos a categoria calculada aqui também
                'conta_bancaria': str(conta.conta) if conta.conta else 'N/A',
                'forma_pagamento': conta.forma_pagamento or 'N/A',
                'numero_duplicata': conta.numero_duplicata or 'N/A',
            })
            
            # 2. Agregação por Categoria (Tipo)
            if categoria not in resumo_por_tipo:
                resumo_por_tipo[categoria] = {
                    'fornecedor__tipo': categoria,
                    'total_pago': 0.0,
                    'quantidade_contas': 0,
                    'total_valor_original': 0.0,
                    'total_juros': 0.0,
                    'total_tarifas': 0.0
                }
            resumo_por_tipo[categoria]['total_pago'] += val_pago
            resumo_por_tipo[categoria]['quantidade_contas'] += 1
            resumo_por_tipo[categoria]['total_valor_original'] += val_original
            resumo_por_tipo[categoria]['total_juros'] += val_juros
            resumo_por_tipo[categoria]['total_tarifas'] += val_tarifas
            
            # 3. Agregação por Fornecedor (Nome)
            if nome_fornecedor not in resumo_por_fornecedor:
                resumo_por_fornecedor[nome_fornecedor] = {
                    'fornecedor__nome': nome_fornecedor,
                    'fornecedor__tipo': categoria,
                    'total_pago': 0.0,
                    'quantidade_contas': 0,
                    'total_valor_original': 0.0,
                    'total_juros': 0.0,
                    'total_tarifas': 0.0
                }
            resumo_por_fornecedor[nome_fornecedor]['total_pago'] += val_pago
            resumo_por_fornecedor[nome_fornecedor]['quantidade_contas'] += 1
            resumo_por_fornecedor[nome_fornecedor]['total_valor_original'] += val_original
            resumo_por_fornecedor[nome_fornecedor]['total_juros'] += val_juros
            resumo_por_fornecedor[nome_fornecedor]['total_tarifas'] += val_tarifas

        # Converter dicionários de resumo para listas
        resumo_por_tipo_limpo = list(resumo_por_tipo.values())
        resumo_por_tipo_limpo.sort(key=lambda x: x['total_pago'], reverse=True)
        
        resumo_por_fornecedor_limpo = list(resumo_por_fornecedor.values())
        resumo_por_fornecedor_limpo.sort(key=lambda x: x['total_pago'], reverse=True)
        
        # Helper não é mais necessário dentro do loop pois fizemos conversão direta
        def safe_aggregate_value(value):
             return float(value) if value is not None else 0.0
        
        # Totais gerais
        totais_gerais = queryset.aggregate(
            soma_total_pago=Sum('valor_total_pago'),
            soma_valor_original=Sum('valor'),
            soma_juros=Sum('juros'),
            soma_tarifas=Sum('tarifas')
        )
        
        # Estatísticas dos fornecedores
        total_fornecedores_fixos = len(fornecedores_fixos)
        fornecedores_com_pagamentos = queryset.values('fornecedor_id').distinct().count()
        
        return Response({
            'parametros': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'filtro_aplicado': 'Fornecedores com nome contendo: FOLHA, PROLABORE, ALUGUEL, SALARIO, INSS, FGTS, CONTADOR, LUZ, ENERGIA, ÁGUA, TELEFONE, INTERNET, SEGURO',
                'fonte_dados': 'Contas a Pagar (status: Pago)',
            },
            'estatisticas_fornecedores': {
                'total_fornecedores_fixos_cadastrados': total_fornecedores_fixos,
                'fornecedores_com_pagamentos_no_periodo': fornecedores_com_pagamentos,
            },
            'totais_gerais': {
                'total_valor_original': safe_aggregate_value(totais_gerais['soma_valor_original']),
                'total_valor_pago': safe_aggregate_value(totais_gerais['soma_total_pago']),
                'total_juros': safe_aggregate_value(totais_gerais['soma_juros']),
                'total_tarifas': safe_aggregate_value(totais_gerais['soma_tarifas']),
            },
            'resumo_por_tipo_fornecedor': resumo_por_tipo_limpo,
            'resumo_por_fornecedor': resumo_por_fornecedor_limpo,
            'total_contas_pagas': queryset.count(),
            'contas_pagas': pagamentos_detalhados
        })


class RelatorioCustosVariaveisView(APIView):
    """
    Endpoint para relatórios de contas pagas de fornecedores 
    com tipos relacionados a DESPESAS VARIÁVEIS ou CUSTOS VARIÁVEIS em um período.
    
    Agrupa os valores pelo campo 'especificacao' da tabela de fornecedores.
    
    Utiliza a tabela ContasPagar filtrada por:
    - Status: 'P' (Pago)
    - Fornecedores com tipo contendo 'VARIAVEL', 'DESPESA VARIAVEL' ou 'CUSTO VARIAVEL'
    - Período de pagamento especificado
    """
    
    def safe_aggregate_value(self, value):
        """Helper para tratar valores None em agregações"""
        if value is None:
            return 0.0
        return float(value)
    
    def get(self, request, *args, **kwargs):
        # 1. Validação de Parâmetros
        data_inicio_str = request.query_params.get('data_inicio')
        data_fim_str = request.query_params.get('data_fim')
        
        if not data_inicio_str or not data_fim_str:
            return Response(
                {'error': 'Parâmetros data_inicio e data_fim são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de data inválido. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if data_inicio > data_fim:
            return Response(
                {'error': 'A data de início não pode ser maior que a data de fim.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 2. Lógica: Custos Variáveis = tudo que NÃO é custo fixo
        # Palavras-chave para identificar custos fixos (a serem EXCLUÍDOS)
        KEYWORDS_FIXOS = ['FOLHA', 'PROLABORE', 'PRO-LABORE', 'ALUGUEL', 'SALARIO', 'SALÁRIO', 
                         'INSS', 'FGTS', 'CONTADOR', 'CONTABILIDADE', 'LUZ', 'ENERGIA', 
                         'ÁGUA', 'AGUA', 'TELEFONE', 'INTERNET', 'SEGURO']
        
        # Construir query para EXCLUIR fornecedores com nomes contendo palavras-chave de custos fixos
        exclude_query = Q()
        for keyword in KEYWORDS_FIXOS:
            exclude_query |= Q(nome__icontains=keyword)
        
        # Fornecedores variáveis = todos EXCETO os fixos
        fornecedores_variaveis = Fornecedores.objects.exclude(exclude_query).values_list('id', flat=True)
        
        if not fornecedores_variaveis.exists():
            return Response({
                'parametros': {
                    'data_inicio': data_inicio,
                    'data_fim': data_fim,
                    'filtro_aplicado': 'Fornecedores que NÃO são custos fixos (excluindo: FOLHA, PROLABORE, ALUGUEL, etc)',
                    'fonte_dados': 'Contas a Pagar (status: Pago)',
                },
                'message': 'Nenhum fornecedor encontrado com tipo relacionado a custos variáveis.',
                'totais_gerais': {
                    'total_valor_original': 0.0,
                    'total_valor_pago': 0.0,
                    'total_juros': 0.0,
                    'total_tarifas': 0.0,
                },
                'resumo_por_especificacao': [],
                'total_contas_pagas': 0,
                'contas_pagas': []
            })
        
        # 3. Consultar contas pagas no período para fornecedores variáveis
        queryset = ContasPagar.objects.filter(
            status='P',  # Apenas contas pagas
            fornecedor_id__in=fornecedores_variaveis,
            data_pagamento__date__gte=data_inicio,
            data_pagamento__date__lte=data_fim
        ).select_related('fornecedor')
        
        # 4. Calcular totais gerais
        totais_gerais = queryset.aggregate(
            soma_valor_original=Sum('valor'),
            soma_total_pago=Sum('valor_total_pago'),
            soma_juros=Sum('juros'),
            soma_tarifas=Sum('tarifas')
        )
        
        # 5. Agrupar por especificação do fornecedor
        # 5. Agrupar por especificação do fornecedor e Detalhar Contas (Single Loop)
        resumo_por_especificacao = {}
        pagamentos_detalhados = []
        
        # Determinar categoria (Helper function) - Categorização Expandida
        def definir_categoria(nome_fornecedor, historico, especificacao_original):
            # Garantir strings seguras
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
            
            # --- Fallback: Verificar se o nome do fornecedor parece ser de uma empresa (contém LTDA, ME, EIRELI, etc.) ---
            if any(term in nome_safe.upper() for term in ['LTDA', 'ME', 'EIRELI', 'EPP', 'S/A', 'S.A.', 'COMERCIO', 'COMÉRCIO', 'DISTRIBUI', 'IMPORTA']):
                return 'Fornecedor'
            
            return 'Outros'

        for conta in queryset.order_by('-data_pagamento'):
            # Preparar dados
            nome_fornecedor = conta.fornecedor.nome if conta.fornecedor else 'N/A'
            tipo_fornecedor = conta.fornecedor.tipo if conta.fornecedor else 'N/A'
            espec_original = conta.fornecedor.especificacao if conta.fornecedor else None
            
            categoria = definir_categoria(nome_fornecedor, conta.historico, espec_original)
            
            val_original = float(conta.valor or 0)
            val_pago = float(conta.valor_total_pago or 0)
            val_juros = float(conta.juros or 0)
            val_tarifas = float(conta.tarifas or 0)
            
            # --- 1. Adicionar ao Resumo ---
            if categoria not in resumo_por_especificacao:
                resumo_por_especificacao[categoria] = {
                    'especificacao': categoria,
                    'valor_original_total': 0.0,
                    'valor_pago_total': 0.0,
                    'juros_total': 0.0,
                    'tarifas_total': 0.0,
                    'quantidade_contas': 0,
                    'fornecedores': set()
                }
            
            resumo_por_especificacao[categoria]['valor_original_total'] += val_original
            resumo_por_especificacao[categoria]['valor_pago_total'] += val_pago
            resumo_por_especificacao[categoria]['juros_total'] += val_juros
            resumo_por_especificacao[categoria]['tarifas_total'] += val_tarifas
            resumo_por_especificacao[categoria]['quantidade_contas'] += 1
            
            if conta.fornecedor:
                resumo_por_especificacao[categoria]['fornecedores'].add(conta.fornecedor.nome)
            
            # --- 2. Adicionar aos Detalhes ---
            pagamentos_detalhados.append({
                'id': conta.id,
                'data_pagamento': conta.data_pagamento.strftime('%Y-%m-%d') if conta.data_pagamento else 'N/A',
                'fornecedor_nome': nome_fornecedor,
                'fornecedor_tipo': tipo_fornecedor,
                'fornecedor_especificacao': categoria, 
                'valor_original': val_original,
                'valor_pago': val_pago,
                'juros': val_juros,
                'tarifas': val_tarifas,
                'historico': conta.historico or 'N/A',
                'forma_pagamento': conta.forma_pagamento or 'N/A',
            })
        
        # Converter sets para listas no resumo e ordenar
        resumo_por_especificacao_limpo = []
        for especificacao_data in resumo_por_especificacao.values():
            especificacao_data['fornecedores'] = list(especificacao_data['fornecedores'])
            especificacao_data['quantidade_fornecedores'] = len(especificacao_data['fornecedores'])
            resumo_por_especificacao_limpo.append(especificacao_data)
        
        resumo_por_especificacao_limpo.sort(key=lambda x: x['valor_pago_total'], reverse=True)
        
        # Detalhes já estão ordenados pela query loop

        
        # Estatísticas dos fornecedores
        total_fornecedores_variaveis = fornecedores_variaveis.count()
        fornecedores_com_pagamentos = queryset.values('fornecedor_id').distinct().count()
        
        return Response({
            'parametros': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'filtro_aplicado': 'Fornecedores que NÃO são custos fixos (excluindo: FOLHA, PROLABORE, ALUGUEL, SALARIO, INSS, FGTS, etc)',
                'fonte_dados': 'Contas a Pagar (status: Pago)',
            },
            'estatisticas_fornecedores': {
                'total_fornecedores_variaveis_cadastrados': total_fornecedores_variaveis,
                'fornecedores_com_pagamentos_no_periodo': fornecedores_com_pagamentos,
            },
            'totais_gerais': {
                'total_valor_original': self.safe_aggregate_value(totais_gerais['soma_valor_original']),
                'total_valor_pago': self.safe_aggregate_value(totais_gerais['soma_total_pago']),
                'total_juros': self.safe_aggregate_value(totais_gerais['soma_juros']),
                'total_tarifas': self.safe_aggregate_value(totais_gerais['soma_tarifas']),
            },
            'resumo_por_especificacao': resumo_por_especificacao_limpo,
            'total_contas_pagas': queryset.count(),
            'contas_pagas': pagamentos_detalhados
        })


class RelatorioFaturamentoView(APIView):
    """
    Endpoint para relatórios de faturamento baseado em notas fiscais em um período.
    
    Inclui:
    - Notas Fiscais de Entrada com operação relacionada a COMPRA
    - Notas Fiscais de Saída com operação relacionada a VENDA
    - Notas Fiscais de Serviço (todas, pois são prestação de serviços)
    
    Filtros aplicados:
    - NF Entrada: operação contendo 'COMPRA'
    - NF Saída: operação contendo 'VENDA'
    - NF Serviço: todas as notas de serviço
    - Período: data de emissão/data entre data_inicio e data_fim
    """
    
    def safe_aggregate_value(self, value):
        """Helper para tratar valores None em agregações"""
        if value is None:
            return 0.0
        return float(value)
    
    def _obter_ultimo_preco_entrada(self, produto_id, data_limite):
        """
        Busca o último preço de entrada do produto, mesmo anterior ao período
        """
        tipos_entrada = [1, 3]  # Entrada e Estoque Inicial
        
        # Busca última entrada com valor > 0 até a data limite
        ultima_entrada = MovimentacoesEstoque.objects.filter(
            produto_id=produto_id,
            tipo_movimentacao__id__in=tipos_entrada,
            quantidade__gt=0,
            custo_unitario__gt=0,
            data_movimentacao__date__lte=data_limite
        ).order_by('-data_movimentacao', '-id').first()
        
        if ultima_entrada:
            return {
                'preco': float(ultima_entrada.custo_unitario),
                'data': ultima_entrada.data_movimentacao.strftime('%Y-%m-%d %H:%M:%S'),
                'documento': ultima_entrada.documento_referencia or '',
                'encontrado': True
            }
        
        # Se não encontrou, tenta buscar no SaldosEstoque
        saldo = SaldosEstoque.objects.filter(produto_id=produto_id, custo_medio__gt=0).first()
        if saldo and saldo.custo_medio:
            return {
                'preco': float(saldo.custo_medio),
                'data': None,
                'documento': 'Custo médio atual',
                'encontrado': True
            }
        
        return {
            'preco': 0.0,
            'data': None,
            'documento': '',
            'encontrado': False
        }
    
    def _calcular_valores_preco_entrada(self, nf_saida_queryset, data_fim):
        """
        Calcula valores das vendas usando preços de entrada dos produtos
        """
        valor_total_preco_entrada = 0.0
        quantidade_itens_calculados = 0
        produtos_sem_preco_entrada = 0
        
        # Busca todos os itens das notas fiscais de saída no período
        itens_vendas = ItensNfSaida.objects.filter(
            nota_fiscal__in=nf_saida_queryset
        ).select_related('produto')
        
        for item in itens_vendas:
            if item.produto and item.quantidade:
                # Busca último preço de entrada do produto
                preco_info = self._obter_ultimo_preco_entrada(item.produto.id, data_fim)
                
                if preco_info['encontrado']:
                    valor_item_preco_entrada = float(item.quantidade) * preco_info['preco']
                    valor_total_preco_entrada += valor_item_preco_entrada
                    quantidade_itens_calculados += 1
                else:
                    produtos_sem_preco_entrada += 1
        
        return {
            'valor_total_preco_entrada': valor_total_preco_entrada,
            'quantidade_itens_calculados': quantidade_itens_calculados,
            'produtos_sem_preco_entrada': produtos_sem_preco_entrada
        }
    
    def get(self, request, *args, **kwargs):
        # 1. Validação de Parâmetros
        data_inicio_str = request.query_params.get('data_inicio')
        data_fim_str = request.query_params.get('data_fim')
        
        if not data_inicio_str or not data_fim_str:
            return Response(
                {'error': 'Parâmetros data_inicio e data_fim são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de data inválido. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if data_inicio > data_fim:
            return Response(
                {'error': 'A data de início não pode ser maior que a data de fim.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. Consultar Notas Fiscais de Entrada (Compras)
        nf_entrada = NotasFiscaisEntrada.objects.filter(
            Q(operacao__icontains='COMPRA'),
            data_emissao__date__gte=data_inicio,
            data_emissao__date__lte=data_fim
        ).select_related('fornecedor')
        
        # 3. Consultar Notas Fiscais de Saída (Vendas)
        nf_saida = NotasFiscaisSaida.objects.filter(
            Q(operacao__icontains='VENDA'),
            data__date__gte=data_inicio,
            data__date__lte=data_fim
        ).select_related('cliente')
        
        # 4. Consultar Notas Fiscais de Serviço
        nf_servico = NotasFiscaisServico.objects.filter(
            data__date__gte=data_inicio,
            data__date__lte=data_fim
        ).select_related('cliente')
        
        # 5. Calcular totais por tipo de nota
        totais_entrada = nf_entrada.aggregate(
            soma_valor_produtos=Sum('valor_produtos'),
            soma_valor_total=Sum('valor_total'),
            soma_valor_icms=Sum('valor_icms'),
            soma_valor_ipi=Sum('valor_ipi'),
            quantidade_notas=Count('id')
        )
        
        totais_saida = nf_saida.aggregate(
            soma_valor_produtos=Sum('valor_produtos'),
            soma_valor_total=Sum('valor_total_nota'),
            soma_valor_icms=Sum('valor_icms'),
            soma_desconto=Sum('desconto'),
            quantidade_notas=Count('id')
        )
        
        totais_servico = nf_servico.aggregate(
            soma_valor_produtos=Sum('valor_produtos'),
            soma_valor_total=Sum('valor_total'),
            soma_valor_iss=Sum('iss'),
            quantidade_notas=Count('id')
        )
        
        # 5.1. Calcular valores das vendas usando preços de entrada
        calculos_preco_entrada = self._calcular_valores_preco_entrada(nf_saida, data_fim)
        
        # 6. Resumo por tipo de operação
        resumo_por_tipo = [
            {
                'tipo': 'Compras (NF Entrada)',
                'quantidade_notas': totais_entrada['quantidade_notas'] or 0,
                'valor_produtos': self.safe_aggregate_value(totais_entrada['soma_valor_produtos']),
                'valor_total': self.safe_aggregate_value(totais_entrada['soma_valor_total']),
                'impostos': self.safe_aggregate_value(totais_entrada['soma_valor_icms']) + self.safe_aggregate_value(totais_entrada['soma_valor_ipi']),
                'detalhes': {
                    'valor_icms': self.safe_aggregate_value(totais_entrada['soma_valor_icms']),
                    'valor_ipi': self.safe_aggregate_value(totais_entrada['soma_valor_ipi'])
                }
            },
            {
                'tipo': 'Vendas (NF Saída)',
                'quantidade_notas': totais_saida['quantidade_notas'] or 0,
                'valor_produtos': self.safe_aggregate_value(totais_saida['soma_valor_produtos']),
                'valor_total': self.safe_aggregate_value(totais_saida['soma_valor_total']),
                'impostos': self.safe_aggregate_value(totais_saida['soma_valor_icms']),
                'valor_preco_entrada': calculos_preco_entrada['valor_total_preco_entrada'],
                'margem_bruta': self.safe_aggregate_value(totais_saida['soma_valor_total']) - calculos_preco_entrada['valor_total_preco_entrada'],
                'detalhes': {
                    'valor_icms': self.safe_aggregate_value(totais_saida['soma_valor_icms']),
                    'valor_desconto': self.safe_aggregate_value(totais_saida['soma_desconto']),
                    'itens_calculados': calculos_preco_entrada['quantidade_itens_calculados'],
                    'produtos_sem_preco_entrada': calculos_preco_entrada['produtos_sem_preco_entrada']
                }
            },
            {
                'tipo': 'Serviços (NF Serviço)',
                'quantidade_notas': totais_servico['quantidade_notas'] or 0,
                'valor_produtos': self.safe_aggregate_value(totais_servico['soma_valor_produtos']),
                'valor_total': self.safe_aggregate_value(totais_servico['soma_valor_total']),
                'impostos': self.safe_aggregate_value(totais_servico['soma_valor_iss']),
                'detalhes': {
                    'valor_iss': self.safe_aggregate_value(totais_servico['soma_valor_iss'])
                }
            }
        ]
        
        # 7. Totais gerais do faturamento
        total_quantidade_notas = (
            (totais_entrada['quantidade_notas'] or 0) +
            (totais_saida['quantidade_notas'] or 0) +
            (totais_servico['quantidade_notas'] or 0)
        )
        
        total_valor_produtos = (
            self.safe_aggregate_value(totais_entrada['soma_valor_produtos']) +
            self.safe_aggregate_value(totais_saida['soma_valor_produtos']) +
            self.safe_aggregate_value(totais_servico['soma_valor_produtos'])
        )
        
        total_valor_geral = (
            self.safe_aggregate_value(totais_entrada['soma_valor_total']) +
            self.safe_aggregate_value(totais_saida['soma_valor_total']) +
            self.safe_aggregate_value(totais_servico['soma_valor_total'])
        )
        
        total_impostos = (
            self.safe_aggregate_value(totais_entrada['soma_valor_icms']) +
            self.safe_aggregate_value(totais_entrada['soma_valor_ipi']) +
            self.safe_aggregate_value(totais_saida['soma_valor_icms']) +
            self.safe_aggregate_value(totais_servico['soma_valor_iss'])
        )
        
        # 8. Top fornecedores (compras)
        top_fornecedores = []
        if nf_entrada.exists():
            fornecedores_resumo = nf_entrada.values('fornecedor__nome').annotate(
                valor_total=Sum('valor_total'),
                quantidade_notas=Count('id')
            ).order_by('-valor_total')[:10]
            
            for fornecedor in fornecedores_resumo:
                top_fornecedores.append({
                    'fornecedor': fornecedor['fornecedor__nome'] or 'Sem Fornecedor',
                    'valor_total': float(fornecedor['valor_total'] or 0),
                    'quantidade_notas': fornecedor['quantidade_notas']
                })
        
        # 9. Top clientes (vendas + serviços)
        top_clientes = []
        
        # Vendas
        if nf_saida.exists():
            clientes_vendas = nf_saida.values('cliente__nome').annotate(
                valor_total=Sum('valor_total_nota'),
                quantidade_notas=Count('id')
            )
        else:
            clientes_vendas = []
        
        # Serviços
        if nf_servico.exists():
            clientes_servicos = nf_servico.values('cliente__nome').annotate(
                valor_total=Sum('valor_total'),
                quantidade_notas=Count('id')
            )
        else:
            clientes_servicos = []
        
        # Combinar vendas e serviços por cliente
        clientes_combinados = {}
        
        for venda in clientes_vendas:
            nome = venda['cliente__nome'] or 'Sem Cliente'
            clientes_combinados[nome] = {
                'cliente': nome,
                'valor_total': float(venda['valor_total'] or 0),
                'quantidade_notas': venda['quantidade_notas'],
                'tipo': 'vendas'
            }
        
        for servico in clientes_servicos:
            nome = servico['cliente__nome'] or 'Sem Cliente'
            if nome in clientes_combinados:
                clientes_combinados[nome]['valor_total'] += float(servico['valor_total'] or 0)
                clientes_combinados[nome]['quantidade_notas'] += servico['quantidade_notas']
                clientes_combinados[nome]['tipo'] = 'vendas+serviços'
            else:
                clientes_combinados[nome] = {
                    'cliente': nome,
                    'valor_total': float(servico['valor_total'] or 0),
                    'quantidade_notas': servico['quantidade_notas'],
                    'tipo': 'serviços'
                }
        
        # Ordenar clientes por valor total
        top_clientes = sorted(clientes_combinados.values(), key=lambda x: x['valor_total'], reverse=True)[:10]
        
        # 10. Detalhes das notas (primeiras 50 de cada tipo)
        notas_detalhadas = {
            'compras': [],
            'vendas': [],
            'servicos': []
        }
        
        # Compras
        for nf in nf_entrada.order_by('-data_emissao'):
            notas_detalhadas['compras'].append({
                'id': nf.id,
                'numero_nota': nf.numero_nota,
                'data_emissao': nf.data_emissao,
                'fornecedor': nf.fornecedor.nome if nf.fornecedor else 'N/A',
                'operacao': nf.operacao,
                'valor_produtos': float(nf.valor_produtos or 0),
                'valor_total': float(nf.valor_total or 0),
                'valor_icms': float(nf.valor_icms or 0),
                'valor_ipi': float(nf.valor_ipi or 0)
            })
        
        # Vendas
        for nf in nf_saida.order_by('-data'):
            # Calcular custo estimado desta nota
            custo_estimado_nota = 0.0
            itens_nota = []
            for item in nf.itens.all():
                if item.produto and item.quantidade:
                    preco_info = self._obter_ultimo_preco_entrada(item.produto.id, data_fim)
                    custo_item = 0.0
                    if preco_info['encontrado']:
                        custo_item = float(item.quantidade) * preco_info['preco']
                        custo_estimado_nota += custo_item
                    
                    itens_nota.append({
                        'produto_nome': item.produto.nome,
                        'quantidade': float(item.quantidade),
                        'custo_unitario': preco_info['preco'] if preco_info['encontrado'] else 0.0,
                        'custo_total': custo_item,
                        'valor_unitario_venda': float(item.valor_unitario or 0),
                        'valor_total_venda': float(item.quantidade) * float(item.valor_unitario or 0)
                    })

            notas_detalhadas['vendas'].append({
                'id': nf.id,
                'numero_nota': nf.numero_nota,
                'data': nf.data,
                'cliente': nf.cliente.nome if nf.cliente else 'N/A',
                'operacao': nf.operacao,
                'valor_produtos': float(nf.valor_produtos or 0),
                'valor_total': float(nf.valor_total_nota or 0),
                'valor_icms': float(nf.valor_icms or 0),
                'desconto': float(nf.desconto or 0),
                'valor_custo_estimado': custo_estimado_nota,
                'itens': itens_nota
            })
        
        # Serviços
        for nf in nf_servico.order_by('-data')[:50]:
            notas_detalhadas['servicos'].append({
                'id': nf.id,
                'numero_nota': nf.numero_nota,
                'data': nf.data,
                'cliente': nf.cliente.nome if nf.cliente else 'N/A',
                'operacao': nf.operacao,
                'valor_produtos': float(nf.valor_produtos or 0),
                'valor_total': float(nf.valor_produtos or 0),  # NotasFiscaisServico usa valor_produtos como total
                'valor_iss': float(nf.iss or 0)
            })
        
        return Response({
            'parametros': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'filtros_aplicados': {
                    'nf_entrada': 'Operação contendo COMPRA',
                    'nf_saida': 'Operação contendo VENDA',
                    'nf_servico': 'Todas as notas de serviço'
                },
                'fonte_dados': 'Notas Fiscais (Entrada, Saída e Serviço)'
            },
            'totais_gerais': {
                'total_quantidade_notas': total_quantidade_notas,
                'total_valor_produtos': total_valor_produtos,
                'total_valor_geral': total_valor_geral,
                'total_impostos': total_impostos,
                'analise_vendas': {
                    'valor_vendas': self.safe_aggregate_value(totais_saida['soma_valor_total']),
                    'valor_preco_entrada': calculos_preco_entrada['valor_total_preco_entrada'],
                    'margem_bruta': self.safe_aggregate_value(totais_saida['soma_valor_total']) - calculos_preco_entrada['valor_total_preco_entrada'],
                    'percentual_margem': round(
                        ((self.safe_aggregate_value(totais_saida['soma_valor_total']) - calculos_preco_entrada['valor_total_preco_entrada']) / 
                         self.safe_aggregate_value(totais_saida['soma_valor_total']) * 100) if self.safe_aggregate_value(totais_saida['soma_valor_total']) > 0 else 0, 2
                    ),
                    'itens_analisados': calculos_preco_entrada['quantidade_itens_calculados'],
                    'produtos_sem_preco_entrada': calculos_preco_entrada['produtos_sem_preco_entrada']
                }
            },
            'resumo_por_tipo': resumo_por_tipo,
            'top_fornecedores': top_fornecedores,
            'top_clientes': top_clientes,
            'notas_detalhadas': notas_detalhadas
        })
