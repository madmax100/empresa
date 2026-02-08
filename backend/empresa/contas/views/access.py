from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q, Count, Case, When, F, DecimalField, Min, Max
from django.db.models.functions import Coalesce, TruncMonth
from decimal import Decimal
from datetime import date, timedelta, datetime
import time


from ..models.access import ApontamentosProducao, ApuracoesFiscais, AtividadesCRM, Categorias, CategoriasProdutos, Clientes, ComissoesVenda, ConsumosProducao, ContagensInventario, ContasPagar, ContasReceber, ContratosLocacao, CotacoesCompra, CustosAdicionaisFrete, Despesas, Empresas, EtapasFunil, Fornecedores, Fretes, Funcionarios, Grupos, HistoricoRastreamento, ImpostosFiscais, Inventarios, ItensApuracaoFiscal, ItensContratoLocacao, ItensCotacaoCompra, ItensNfEntrada, ItensNfSaida, ItensOrcamentoVenda, ItensOrdemProducao, ItensPedidoCompra, ItensPedidoVenda, ItensPropostaVenda, ItensRequisicaoCompra, Leads, LocaisEstoque, Lotes, Marcas, MovimentacoesEstoque, NotasFiscaisEntrada, NotasFiscaisSaida, Oportunidades, OcorrenciasFrete, OrdensProducao, OrcamentosVenda, PagamentosFuncionarios, PedidosCompra, PedidosVenda, PosicoesEstoque, Produtos, PropostasVenda, RegioesEntrega, RequisicoesCompra, SaldosEstoque, TabelasFrete, TiposMovimentacaoEstoque, Transportadoras

from ..serializers.access import ApontamentosProducaoSerializer, ApuracoesFiscaisSerializer, AtividadesCRMSerializer, ComissoesVendaSerializer, ConsumosProducaoSerializer, CotacoesCompraSerializer, EtapasFunilSerializer, ImpostosFiscaisSerializer, ItemContratoLocacaoSerializer, ProdutoSerializer, CategoriaSerializer, CategoriasProdutosSerializer, ClienteSerializer, ContagensInventarioSerializer, ContasPagarSerializer, ContasReceberSerializer, ContratoLocacaoSerializer, CustosAdicionaisFreteSerializer, DespesasSerializer, EmpresasSerializer, FornecedoresSerializer, FretesSerializer, FuncionariosSerializer, GruposSerializer, HistoricoRastreamentoSerializer, InventariosSerializer, ItensApuracaoFiscalSerializer, ItensCotacaoCompraSerializer, ItensNfEntradaSerializer, ItensNfSaidaSerializer, ItensOrcamentoVendaSerializer, ItensOrdemProducaoSerializer, ItensPedidoCompraSerializer, ItensPedidoVendaSerializer, ItensPropostaVendaSerializer, ItensRequisicaoCompraSerializer, LeadsSerializer, LocaisEstoqueSerializer, LotesSerializer, MarcasSerializer, MovimentacoesEstoqueSerializer, NotasFiscaisEntradaSerializer, NotasFiscaisSaidaSerializer, OcorrenciasFreteSerializer, OportunidadesSerializer, OrdensProducaoSerializer, OrcamentosVendaSerializer, PagamentosFuncionariosSerializer, PedidosCompraSerializer, PedidosVendaSerializer, PosicoesEstoqueSerializer, PropostasVendaSerializer, RegioesEntregaSerializer, RequisicoesCompraSerializer, SaldosEstoqueSerializer, TabelasFreteSerializer, TiposMovimentacaoEstoqueSerializer, TransportadorasSerializer

class CategoriasViewSet(viewsets.ModelViewSet):
    queryset = Categorias.objects.all()
    serializer_class = CategoriaSerializer
    
class CategoriasProdutosViewSet(viewsets.ModelViewSet):
    queryset = CategoriasProdutos.objects.all()
    serializer_class = CategoriasProdutosSerializer
    
class ClientesViewSet(viewsets.ModelViewSet):
    queryset = Clientes.objects.all()
    serializer_class = ClienteSerializer
    
class ContagensInventarioViewSet(viewsets.ModelViewSet):
    queryset = ContagensInventario.objects.all()
    serializer_class = ContagensInventarioSerializer
    

class ContasPagarViewSet(viewsets.ModelViewSet):
    queryset = ContasPagar.objects.all()
    serializer_class = ContasPagarSerializer

    def parse_date(self, date_str):
        """
        Converte string de data ISO para objeto date
        """
        if not date_str:
            return None
        try:
            date_str = date_str.split('T')[0]
            return date(*time.strptime(date_str, '%Y-%m-%d')[:3])
        except (ValueError, IndexError):
            return None

    def get_contas_status(self, queryset, status_filtro='all'):
        """
        Filtra contas baseado no status
        """
        if status_filtro == 'all' or not status_filtro:
            return queryset  # Retorna todos os registros sem filtrar
            
        return queryset.filter(status=status_filtro)

    @action(detail=True, methods=['PATCH'])
    def atualizar_status(self, request, pk=None):
        try:
            print("1. Iniciando atualização")
            conta = self.get_object()
            print("2. Conta encontrada:", conta.id)
            
            novo_status = request.data.get('status')
            data_pagamento = request.data.get('data_pagamento')
            valor_pago = request.data.get('valor_pago')
            
            print(f"3. Status: {novo_status}, Data: {data_pagamento}, Valor: {valor_pago}")
            
            # Validações
            if novo_status not in ['A', 'P', 'C']:
                print("4. Status inválido")
                return Response(
                    {'error': 'Status inválido. Use A, P ou C.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if novo_status == 'P':
                if not data_pagamento:
                    print("5. Data de pagamento faltando")
                    return Response(
                        {'error': 'Data de pagamento obrigatória para baixa'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if not valor_pago:
                    print("6. Valor pago faltando")
                    return Response(
                        {'error': 'Valor pago obrigatório para baixa'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            print("7. Iniciando atualização da conta")
            # Atualiza o título
            try:
                conta.status = novo_status
                if novo_status == 'P':
                    conta.data_pagamento = data_pagamento
                    conta.valor_pago = Decimal(valor_pago)  # Convertendo para Decimal
                print("8. Salvando conta")
                conta.save()
                print("9. Conta salva com sucesso")
            except Exception as e:
                print(f"Erro ao salvar conta: {str(e)}")
                raise
            
            print("10. Serializando resposta")
            serializer = self.get_serializer(conta)
            return Response({
                'message': 'Status atualizado com sucesso',
                'titulo': serializer.data
            })
        except Exception as e:
            print(f"Erro geral: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False)
    def dashboard(self, request):
        try:
            data_inicial = self.parse_date(request.query_params.get('data_inicial'))
            data_final = self.parse_date(request.query_params.get('data_final'))
            status_filtro = request.query_params.get('status', 'all')
            search_term = request.query_params.get('searchTerm', '').strip()
            
            hoje = date.today()
            
            # Use o model diretamente
            contas = ContasPagar.objects.all()  # ou ContasReceber.objects.all()
            
            # Filtro de período
            if data_inicial:
                contas_anteriores = contas.filter(vencimento__lte=data_inicial)
                contas = contas.filter(vencimento__gte=data_inicial)
                contas_anteriores = contas_anteriores.filter(vencimento__gte='2023-01-01')
                contas_anteriores_abertas = contas_anteriores.filter(status='A')
                total_anteriores = contas_anteriores_abertas.aggregate(
                    total=Coalesce(Sum('valor'), Decimal('0.00'))
                )['total']
            else:
                total_anteriores = Decimal('0.00')
                contas_anteriores_abertas = ContasPagar.objects.none()  # ou ContasReceber.objects.none()

            if data_final:
                contas = contas.filter(vencimento__lte=data_final)

            # Filtro de busca
            if search_term:
                contas = contas.filter(
                    Q(fornecedor__nome__icontains=search_term) |
                    Q(historico__icontains=search_term)
                )

            # Sempre aplica os filtros de status em cópias separadas do queryset
            contas_filtradas_pagas = contas.filter(status='P')
            contas_filtradas_canceladas = contas.filter(status='C')
            contas_filtradas_abertas = contas.filter(status='A')

            # Se um status específico foi selecionado, zera os outros
            if status_filtro != 'all':
                if status_filtro == 'P':
                    contas_filtradas_canceladas = ContasPagar.objects.none()
                    contas_filtradas_abertas = ContasPagar.objects.none()
                elif status_filtro == 'C':
                    contas_filtradas_pagas = ContasPagar.objects.none()
                    contas_filtradas_abertas = ContasPagar.objects.none()
                elif status_filtro == 'A':
                    contas_filtradas_pagas = ContasPagar.objects.none()
                    contas_filtradas_canceladas = ContasPagar.objects.none()

            # Cálculos para o resumo
            total_filtrado_pago = contas_filtradas_pagas.aggregate(
                total=Coalesce(Sum('valor'), Decimal('0.00'))
            )['total']
            total_filtrado_cancelado = contas_filtradas_canceladas.aggregate(
                total=Coalesce(Sum('valor'), Decimal('0.00'))
            )['total']
            total_filtrado_aberto = contas_filtradas_abertas.aggregate(
                total=Coalesce(Sum('valor'), Decimal('0.00'))
            )['total']

            print(f"Total pago: {total_filtrado_pago}")
            print(f"Total cancelado: {total_filtrado_cancelado}")
            print(f"Total aberto: {total_filtrado_aberto}")
                    
            return Response({
                'resumo': {
                    'total_atrasado': float(total_anteriores),
                    'total_pago_periodo': float(total_filtrado_pago),
                    'total_cancelado_periodo': float(total_filtrado_cancelado),
                    'total_aberto_periodo': float(total_filtrado_aberto),
                    'quantidade_titulos': contas.count(),
                    'quantidade_atrasados_periodo': contas_filtradas_abertas.count()
                },
                'titulos_atrasados': self.get_serializer(
                    contas_anteriores_abertas.select_related('fornecedor').order_by('vencimento'), 
                    many=True
                ).data,
                'titulos_pagos_periodo': self.get_serializer(
                    contas_filtradas_pagas.select_related('fornecedor').order_by('vencimento'), 
                    many=True
                ).data,
                'titulos_abertos_periodo': self.get_serializer(
                    contas_filtradas_abertas.select_related('fornecedor').order_by('vencimento'), 
                    many=True
                ).data
            })
        except Exception as e:
            print(f"Erro: {str(e)}")  # Debug do erro
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    @action(detail=False, url_path='por-fornecedor/(?P<fornecedor_id>[^/.]+)')
    def por_fornecedor(self, request, fornecedor_id=None):
        """
        Retorna as contas a pagar de um fornecedor específico
        """
        hoje = date.today()
        contas = self.get_queryset().filter(fornecedor_id=fornecedor_id)
        
        em_aberto = contas.filter(
            status='A'
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('0.00'))
        )['total']
        
        atrasado = contas.filter(
            status='A',
            vencimento__lt=hoje
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('0.00'))
        )['total']
        
        quantidade_atrasados = contas.filter(
            status='A',
            vencimento__lt=hoje
        ).count()
        
        return Response({
            'resumo': {
                'total_em_aberto': float(em_aberto),
                'total_atrasado': float(atrasado),
                'quantidade_titulos': contas.filter(status='A').count(),
                'quantidade_atrasados': quantidade_atrasados
            },
            'titulos': self.get_serializer(
                contas.order_by('vencimento'), 
                many=True
            ).data
        })
    
    @action(detail=False, methods=['POST'])
    def baixa_em_lote(self, request):
        """
        Realiza baixa em lote de títulos
        """
        try:
            titulos_ids = request.data.get('titulos', [])
            data_pagamento = request.data.get('data_pagamento')
            forma_pagamento = request.data.get('forma_pagamento')
            valor_pago = request.data.get('valor_pago')
            
            if not all([titulos_ids, data_pagamento, forma_pagamento, valor_pago]):
                return Response(
                    {'error': 'Dados incompletos para baixa'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            titulos = self.get_queryset().filter(id__in=titulos_ids, status='A')
            
            for titulo in titulos:
                titulo.status = 'P'
                titulo.data_pagamento = data_pagamento
                titulo.forma_pagamento = forma_pagamento
                titulo.valor_pago = valor_pago
                titulo.save()
                
            return Response({
                'message': f'{len(titulos)} títulos baixados com sucesso',
                'titulos': self.get_serializer(titulos, many=True).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    def get_queryset(self):
        queryset = super().get_queryset()
        
        vencimento_inicial = self.request.query_params.get('vencimento_inicial')
        vencimento_final = self.request.query_params.get('vencimento_final')
        status = self.request.query_params.get('status')
        busca = self.request.query_params.get('busca')
        
        if vencimento_inicial:
            queryset = queryset.filter(vencimento__gte=vencimento_inicial)
        if vencimento_final:
            queryset = queryset.filter(vencimento__lte=vencimento_final)
        if status:
            queryset = queryset.filter(status=status)
        if busca:
            queryset = queryset.filter(
                Q(historico__icontains=busca) |
                Q(fornecedor__nome__icontains=busca) |
                Q(forma_pagamento__icontains=busca)
            )
        
        return queryset
    
    @action(detail=True, methods=['POST'])
    def estornar_baixa(self, request, pk=None):
        """
        Estorna a baixa de um título
        """
        try:
            titulo = self.get_object()
            
            if titulo.status != 'P':
                return Response(
                    {'error': 'Título não está baixado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            titulo.status = 'A'
            titulo.data_pagamento = None
            titulo.valor_pago = Decimal('0.00')
            titulo.save()
            
            return Response({
                'message': 'Baixa estornada com sucesso',
                'titulo': self.get_serializer(titulo).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    @action(detail=False)
    def dashboard_agrupado(self, request):
        """
        Dashboard com dados agrupados por período e forma de pagamento
        """
        try:
            hoje = date.today()
            contas = self.get_queryset()
            
            # Agrupa por forma de pagamento
            por_forma_pagamento = contas.values('forma_pagamento').annotate(
                total=Sum('valor'),
                quantidade=Count('id')
            ).order_by('-total')
            
            # Agrupa por mês de vencimento
            por_mes = contas.annotate(
                mes=TruncMonth('vencimento')
            ).values('mes').annotate(
                total=Sum('valor'),
                quantidade=Count('id')
            ).order_by('mes')
            
            # Títulos próximos ao vencimento (7 dias)
            proximos_vencer = contas.filter(
                status='A',
                vencimento__range=[hoje, hoje + timedelta(days=7)]
            ).order_by('vencimento')
            
            return Response({
                'por_forma_pagamento': por_forma_pagamento,
                'por_mes': por_mes,
                'proximos_vencer': self.get_serializer(proximos_vencer, many=True).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ContasReceberViewSet(viewsets.ModelViewSet):
    queryset = ContasReceber.objects.all()
    serializer_class = ContasReceberSerializer

    def parse_date(self, date_str):
        """
        Converte string de data ISO para objeto date
        """
        if not date_str:
            return None
        try:
            date_str = date_str.split('T')[0]
            return date(*time.strptime(date_str, '%Y-%m-%d')[:3])
        except (ValueError, IndexError):
            return None

    def get_contas_status(self, queryset, status_filtro='all'):
        """
        Filtra contas baseado no status
        """
        if status_filtro == 'all':
            return queryset
        status_map = {
            'A': 'A',
            'P': 'P',
            'C': 'C'
        }
        return queryset.filter(status=status_map.get(status_filtro))

    @action(detail=True, methods=['PATCH'])
    def atualizar_status(self, request, pk=None):
        try:
            conta = self.get_object()
            novo_status = request.data.get('status')
            data_pagamento = request.data.get('data_pagamento')
            valor_pago = request.data.get('valor_pago')
            
            # Validações
            if novo_status not in ['A', 'P', 'C']:
                return Response(
                    {'error': 'Status inválido. Use A, P ou C.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if novo_status == 'P':
                if not data_pagamento:
                    return Response(
                        {'error': 'Data de pagamento obrigatória para baixa'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if not valor_pago:
                    return Response(
                        {'error': 'Valor pago obrigatório para baixa'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            # Atualiza o título
            conta.status = novo_status
            if novo_status == 'P':
                conta.data_pagamento = data_pagamento
                conta.valor_pago = valor_pago
            conta.save()
            
            serializer = self.get_serializer(conta)
            return Response({
                'message': 'Status atualizado com sucesso',
                'titulo': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False)
    def dashboard(self, request):
        """
        Dashboard com filtros de data, status e busca
        """
        try:
            data_inicial = self.parse_date(request.query_params.get('data_inicial'))
            data_final = self.parse_date(request.query_params.get('data_final'))
            status_filtro = request.query_params.get('status', 'all')
            search_term = request.query_params.get('searchTerm', '').strip()
            
            hoje = date.today()
            contas = self.get_queryset()
            
            # Filtro de período
            if data_inicial:
                contas_anteriores = contas.filter(vencimento__lte=data_inicial)
                contas = contas.filter(vencimento__gte=data_inicial)
                contas_anteriores = contas_anteriores.filter(vencimento__gte='2023-01-01')
                contas_anteriores_abertas = self.get_contas_status(contas_anteriores, 'A')
                total_anteriores = contas_anteriores_abertas.aggregate(
                    total=Coalesce(Sum('valor'), Decimal('0.00'))
                )['total']
            else:
                total_anteriores = Decimal('0.00')
                contas_anteriores_abertas = contas.none()

            if data_final:
                contas = contas.filter(vencimento__lte=data_final)

            # Filtro de busca
            if search_term:
                contas = contas.filter(
                    Q(cliente__nome__icontains=search_term) |
                    Q(historico__icontains=search_term)
                )

            # Aplicar filtros de status
            contas_filtradas_pagas = self.get_contas_status(contas, 'P')
            contas_filtradas_canceladas = self.get_contas_status(contas, 'C')
            contas_filtradas_abertas = self.get_contas_status(contas, 'A')

            # Cálculos para o resumo
            total_filtrado_pago = contas_filtradas_pagas.aggregate(
                total=Coalesce(Sum('valor'), Decimal('0.00'))
            )['total']
            total_filtrado_cancelado = contas_filtradas_canceladas.aggregate(
                total=Coalesce(Sum('valor'), Decimal('0.00'))
            )['total']
            total_filtrado_aberto = contas_filtradas_abertas.aggregate(
                total=Coalesce(Sum('valor'), Decimal('0.00'))
            )['total']

            return Response({
                'resumo': {
                    'total_atrasado': float(total_anteriores),
                    'total_pago_periodo': float(total_filtrado_pago),
                    'total_cancelado_periodo': float(total_filtrado_cancelado),
                    'total_aberto_periodo': float(total_filtrado_aberto),
                    'quantidade_titulos': contas.count(),
                    'quantidade_atrasados_periodo': contas_filtradas_abertas.count()
                },
                'titulos_atrasados': self.get_serializer(
                    contas_anteriores_abertas.select_related('cliente').order_by('vencimento'), 
                    many=True
                ).data,
                'titulos_pagos_periodo': self.get_serializer(
                    contas_filtradas_pagas.select_related('cliente').order_by('vencimento'), 
                    many=True
                ).data,
                'titulos_abertos_periodo': self.get_serializer(
                    contas_filtradas_abertas.select_related('cliente').order_by('vencimento'), 
                    many=True
                ).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    @action(detail=False, url_path='por-cliente/(?P<cliente_id>[^/.]+)')
    def por_cliente(self, request, cliente_id=None):
        """
        Retorna as contas a receber de um cliente específico com filtros de data
        """
        # Parâmetros de filtro
        data_inicial = self.parse_date(request.query_params.get('data_inicial'))
        data_final = self.parse_date(request.query_params.get('data_final'))
        
        hoje = date.today()
        
        # Query base
        contas = self.get_queryset().filter(cliente_id=cliente_id)
        
        # Filtro de período
        if data_inicial:
            contas_anteriores = contas.filter(vencimento__lte=data_inicial)
            contas = contas.filter(vencimento__gte=data_inicial)
            contas_anteriores = contas_anteriores.filter(vencimento__gte='2023-01-01')
            contas_anteriores_abertas = self.get_contas_status(contas_anteriores, 'A')
            total_anteriores = contas_anteriores_abertas.aggregate(
                total=Coalesce(Sum('valor'), Decimal('0.00'))
            )['total']
        else:
            total_anteriores = Decimal('0.00')
            contas_anteriores_abertas = contas.none()

        if data_final:
            contas = contas.filter(vencimento__lte=data_final)

        # Aplicar filtros de status
        contas_filtradas_pagas = self.get_contas_status(contas, 'P')
        contas_filtradas_canceladas = self.get_contas_status(contas, 'C')
        contas_filtradas_abertas = self.get_contas_status(contas, 'A')

        # Cálculos para o resumo baseado no status
        total_filtrado_pago = contas_filtradas_pagas.aggregate(
            total=Coalesce(Sum('valor'), Decimal('0.00'))
        )['total']
        total_filtrado_cancelado = contas_filtradas_canceladas.aggregate(
            total=Coalesce(Sum('valor'), Decimal('0.00'))
        )['total']
        total_filtrado_aberto = contas_filtradas_abertas.aggregate(
            total=Coalesce(Sum('valor'), Decimal('0.00'))
        )['total']

        return Response({
            'resumo': {
                'total_atrasado': float(total_anteriores),
                'total_pago_periodo': float(total_filtrado_pago),
                'total_cancelado_periodo': float(total_filtrado_cancelado),
                'total_aberto_periodo': float(total_filtrado_aberto),
                'quantidade_titulos': contas.count(),
                'quantidade_atrasados_periodo': contas_filtradas_abertas.count()
            },
            'titulos_atrasados': self.get_serializer(
                contas_anteriores_abertas.select_related('cliente').order_by('vencimento'), 
                many=True
            ).data,
            'titulos_pagos_periodo': self.get_serializer(
                contas_filtradas_pagas.select_related('cliente').order_by('vencimento'), 
                many=True
            ).data,
            'titulos_abertos_periodo': self.get_serializer(
                contas_filtradas_abertas.select_related('cliente').order_by('vencimento'), 
                many=True
            ).data
        })
    
    @action(detail=False, methods=['POST'])
    def baixa_em_lote(self, request):
        """
        Realiza baixa em lote de títulos
        """
        try:
            titulos_ids = request.data.get('titulos', [])
            data_pagamento = request.data.get('data_pagamento')
            forma_pagamento = request.data.get('forma_pagamento')
            valor_pago = request.data.get('valor_pago')
            
            if not all([titulos_ids, data_pagamento, forma_pagamento, valor_pago]):
                return Response(
                    {'error': 'Dados incompletos para baixa'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            titulos = self.get_queryset().filter(id__in=titulos_ids, status='A')
            
            for titulo in titulos:
                titulo.status = 'P'
                titulo.data_pagamento = data_pagamento
                titulo.forma_pagamento = forma_pagamento
                titulo.valor_pago = valor_pago
                titulo.save()
                
            return Response({
                'message': f'{len(titulos)} títulos baixados com sucesso',
                'titulos': self.get_serializer(titulos, many=True).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    def get_queryset(self):
        queryset = super().get_queryset()
        
        vencimento_inicial = self.request.query_params.get('vencimento_inicial')
        vencimento_final = self.request.query_params.get('vencimento_final')
        status = self.request.query_params.get('status')
        busca = self.request.query_params.get('busca')
        
        if vencimento_inicial:
            queryset = queryset.filter(vencimento__gte=vencimento_inicial)
        if vencimento_final:
            queryset = queryset.filter(vencimento__lte=vencimento_final)
        if status:
            queryset = queryset.filter(status=status)
        if busca:
            queryset = queryset.filter(
                Q(historico__icontains=busca) |
                Q(cliente__nome__icontains=busca) |
                Q(forma_pagamento__icontains=busca)
            )
        
        return queryset
    
    @action(detail=True, methods=['POST'])
    def estornar_baixa(self, request, pk=None):
        """
        Estorna a baixa de um título
        """
        try:
            titulo = self.get_object()
            
            if titulo.status != 'P':
                return Response(
                    {'error': 'Título não está baixado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            titulo.status = 'A'
            titulo.data_pagamento = None
            titulo.valor_pago = Decimal('0.00')
            titulo.save()
            
            return Response({
                'message': 'Baixa estornada com sucesso',
                'titulo': self.get_serializer(titulo).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    @action(detail=False)
    def dashboard_agrupado(self, request):
        """
        Dashboard com dados agrupados por período e forma de pagamento
        """
        try:
            hoje = date.today()
            contas = self.get_queryset()
            
            # Agrupa por forma de pagamento
            por_forma_pagamento = contas.values('forma_pagamento').annotate(
                total=Sum('valor'),
                quantidade=Count('id')
            ).order_by('-total')
            
            # Agrupa por mês de vencimento
            por_mes = contas.annotate(
                mes=TruncMonth('vencimento')
            ).values('mes').annotate(
                total=Sum('valor'),
                quantidade=Count('id')
            ).order_by('mes')
            
            # Títulos próximos ao vencimento (7 dias)
            proximos_vencer = contas.filter(
                status='A',
                vencimento__range=[hoje, hoje + timedelta(days=7)]
            ).order_by('vencimento')
            
            return Response({
                'por_forma_pagamento': por_forma_pagamento,
                'por_mes': por_mes,
                'proximos_vencer': self.get_serializer(proximos_vencer, many=True).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
class ContratosLocacaoViewSet(viewsets.ModelViewSet):
    queryset = ContratosLocacao.objects.all()
    serializer_class = ContratoLocacaoSerializer

    @action(detail=False, url_path='dashboard/(?P<contrato_numero>[^/.]+)')
    def dashboard_contrato(self, request, contrato_numero=None):
        try:
            # Pega os parâmetros de data
            data_inicial = request.query_params.get('data_inicial')
            data_final = request.query_params.get('data_final')

            # Busca o contrato
            contrato = get_object_or_404(ContratosLocacao, contrato=contrato_numero)

            # Busca os itens do contrato
            itens = ItensContratoLocacao.objects.filter(
                contrato=contrato
            ).select_related('categoria')

            # Busca as notas fiscais relacionadas 
            notas_query = NotasFiscaisSaida.objects.filter(
                cliente=contrato.cliente,
            ).prefetch_related('itens')

            # Aplica filtro de data se fornecido
            if data_inicial:
                notas_query = notas_query.filter(data__gte=data_inicial)
            if data_final:
                notas_query = notas_query.filter(data__lte=data_final)

            # Serializa os dados do contrato e itens
            contrato_data = ContratoLocacaoSerializer(contrato).data
            itens_data = ItemContratoLocacaoSerializer(itens, many=True).data

            # Processa as notas e seus itens
            notas_processadas = []
            total_valor_notas = Decimal('0.00')
            total_quantidade_itens = 0

            for nota in notas_query:
                # Serializa a nota
                nota_serializada = NotasFiscaisSaidaSerializer(nota).data
                
                # Busca e serializa os itens da nota
                itens_nota = ItensNfSaida.objects.filter(
                    nota_fiscal=nota
                ).select_related('produto')
                
                itens_serializados = ItensNfSaidaSerializer(itens_nota, many=True).data
                
                # Calcula totais dos itens
                total_itens = itens_nota.aggregate(
                    total_valor=Sum('valor_total'),
                    total_quantidade=Sum('quantidade')
                )

                total_valor = total_itens['total_valor'] or Decimal('0.00')
                total_quantidade = total_itens['total_quantidade'] or 0

                nota_processada = {
                    **nota_serializada,
                    'itens': itens_serializados,
                    'resumo_itens': {
                        'total_valor': str(total_valor),
                        'total_quantidade': total_quantidade
                    }
                }

                notas_processadas.append(nota_processada)
                total_valor_notas += total_valor
                total_quantidade_itens += total_quantidade

            # Monta a resposta final
            return Response({
                'contrato': contrato_data,
                'itens': itens_data,
                'notas_fiscais': {
                    'resumo': {
                        'total_contratos': len(notas_processadas),
                        'total_quantidade_itens': total_quantidade_itens,
                        'valor_total': str(total_valor_notas)
                    },
                    'notas': notas_processadas
                },
                'periodo': {
                    'data_inicial': data_inicial,
                    'data_final': data_final
                }
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, url_path='itens/(?P<contrato_numero>[^/.]+)')
    def itens_contrato(self, request, contrato_numero=None):
        """
        Retorna os itens de um contrato específico pelo número do contrato.
        URL: /api/contratos_locacao/itens/C1234/
        """
        contrato = get_object_or_404(ContratosLocacao, contrato_numero)
        itens = ItensContratoLocacao.objects.filter(
            contrato=contrato
        ).select_related('categoria')
        serializer = ItemContratoLocacaoSerializer(itens, many=True)
        return Response(serializer.data)
    
class CustosAdicionaisFreteViewSet(viewsets.ModelViewSet):
    queryset = CustosAdicionaisFrete.objects.all()
    serializer_class = CustosAdicionaisFreteSerializer
    
class DespesasViewSet(viewsets.ModelViewSet):
    queryset = Despesas.objects.all()
    serializer_class = DespesasSerializer
    
class EmpresasViewSet(viewsets.ModelViewSet):
    queryset = Empresas.objects.all()
    serializer_class = EmpresasSerializer
    
class FornecedoresViewSet(viewsets.ModelViewSet):
    queryset = Fornecedores.objects.all()
    serializer_class = FornecedoresSerializer
    
class FretesViewSet(viewsets.ModelViewSet):
    queryset = Fretes.objects.all()
    serializer_class = FretesSerializer
    
class FuncionariosViewSet(viewsets.ModelViewSet):
    queryset = Funcionarios.objects.all()
    serializer_class = FuncionariosSerializer
    
class GruposViewSet(viewsets.ModelViewSet):
    queryset = Grupos.objects.all()
    serializer_class = GruposSerializer
    
class HistoricoRastreamentoViewSet(viewsets.ModelViewSet):
    queryset = HistoricoRastreamento.objects.all()
    serializer_class = HistoricoRastreamentoSerializer
    
class InventariosViewSet(viewsets.ModelViewSet):
    queryset = Inventarios.objects.all()
    serializer_class = InventariosSerializer
    
class ItensContratoLocacaoViewSet(viewsets.ModelViewSet):
    queryset = ItensContratoLocacao.objects.all()
    serializer_class = ItemContratoLocacaoSerializer

class EtapasFunilViewSet(viewsets.ModelViewSet):
    queryset = EtapasFunil.objects.all()
    serializer_class = EtapasFunilSerializer

class LeadsViewSet(viewsets.ModelViewSet):
    queryset = Leads.objects.all()
    serializer_class = LeadsSerializer

class OportunidadesViewSet(viewsets.ModelViewSet):
    queryset = Oportunidades.objects.all()
    serializer_class = OportunidadesSerializer

class AtividadesCRMViewSet(viewsets.ModelViewSet):
    queryset = AtividadesCRM.objects.all()
    serializer_class = AtividadesCRMSerializer

class PropostasVendaViewSet(viewsets.ModelViewSet):
    queryset = PropostasVenda.objects.all()
    serializer_class = PropostasVendaSerializer

class ItensPropostaVendaViewSet(viewsets.ModelViewSet):
    queryset = ItensPropostaVenda.objects.all()
    serializer_class = ItensPropostaVendaSerializer

class ImpostosFiscaisViewSet(viewsets.ModelViewSet):
    queryset = ImpostosFiscais.objects.all()
    serializer_class = ImpostosFiscaisSerializer

class ApuracoesFiscaisViewSet(viewsets.ModelViewSet):
    queryset = ApuracoesFiscais.objects.all()
    serializer_class = ApuracoesFiscaisSerializer

class ItensApuracaoFiscalViewSet(viewsets.ModelViewSet):
    queryset = ItensApuracaoFiscal.objects.all()
    serializer_class = ItensApuracaoFiscalSerializer

class OrdensProducaoViewSet(viewsets.ModelViewSet):
    queryset = OrdensProducao.objects.all()
    serializer_class = OrdensProducaoSerializer

class ItensOrdemProducaoViewSet(viewsets.ModelViewSet):
    queryset = ItensOrdemProducao.objects.all()
    serializer_class = ItensOrdemProducaoSerializer

class ConsumosProducaoViewSet(viewsets.ModelViewSet):
    queryset = ConsumosProducao.objects.all()
    serializer_class = ConsumosProducaoSerializer

class ApontamentosProducaoViewSet(viewsets.ModelViewSet):
    queryset = ApontamentosProducao.objects.all()
    serializer_class = ApontamentosProducaoSerializer
    
class ItensNfEntradaViewSet(viewsets.ModelViewSet):
    queryset = ItensNfEntrada.objects.all()
    serializer_class = ItensNfEntradaSerializer

class RequisicoesCompraViewSet(viewsets.ModelViewSet):
    queryset = RequisicoesCompra.objects.all()
    serializer_class = RequisicoesCompraSerializer

class ItensRequisicaoCompraViewSet(viewsets.ModelViewSet):
    queryset = ItensRequisicaoCompra.objects.all()
    serializer_class = ItensRequisicaoCompraSerializer

class CotacoesCompraViewSet(viewsets.ModelViewSet):
    queryset = CotacoesCompra.objects.all()
    serializer_class = CotacoesCompraSerializer

class ItensCotacaoCompraViewSet(viewsets.ModelViewSet):
    queryset = ItensCotacaoCompra.objects.all()
    serializer_class = ItensCotacaoCompraSerializer

class PedidosCompraViewSet(viewsets.ModelViewSet):
    queryset = PedidosCompra.objects.all()
    serializer_class = PedidosCompraSerializer

class ItensPedidoCompraViewSet(viewsets.ModelViewSet):
    queryset = ItensPedidoCompra.objects.all()
    serializer_class = ItensPedidoCompraSerializer

class ItensNfSaidaViewSet(viewsets.ModelViewSet):
    queryset = ItensNfSaida.objects.all()
    serializer_class = ItensNfSaidaSerializer

class OrcamentosVendaViewSet(viewsets.ModelViewSet):
    queryset = OrcamentosVenda.objects.all()
    serializer_class = OrcamentosVendaSerializer

class ItensOrcamentoVendaViewSet(viewsets.ModelViewSet):
    queryset = ItensOrcamentoVenda.objects.all()
    serializer_class = ItensOrcamentoVendaSerializer

class PedidosVendaViewSet(viewsets.ModelViewSet):
    queryset = PedidosVenda.objects.all()
    serializer_class = PedidosVendaSerializer

class ItensPedidoVendaViewSet(viewsets.ModelViewSet):
    queryset = ItensPedidoVenda.objects.all()
    serializer_class = ItensPedidoVendaSerializer

class ComissoesVendaViewSet(viewsets.ModelViewSet):
    queryset = ComissoesVenda.objects.all()
    serializer_class = ComissoesVendaSerializer
    
class LocaisEstoqueViewSet(viewsets.ModelViewSet):
    queryset = LocaisEstoque.objects.all()
    serializer_class = LocaisEstoqueSerializer
    
class LotesViewSet(viewsets.ModelViewSet):
    queryset = Lotes.objects.all()
    serializer_class = LotesSerializer
    
class MarcasViewSet(viewsets.ModelViewSet):
    queryset = Marcas.objects.all()
    serializer_class = MarcasSerializer
    
class MovimentacoesEstoqueViewSet(viewsets.ModelViewSet):
    queryset = MovimentacoesEstoque.objects.all()
    serializer_class = MovimentacoesEstoqueSerializer
    
class NotasFiscaisEntradaViewSet(viewsets.ModelViewSet):
    queryset = NotasFiscaisEntrada.objects.all()
    serializer_class = NotasFiscaisEntradaSerializer
    
class NotasFiscaisSaidaViewSet(viewsets.ModelViewSet):
    queryset = NotasFiscaisSaida.objects.all()
    serializer_class = NotasFiscaisSaidaSerializer
    
class OcorrenciasFreteViewSet(viewsets.ModelViewSet):
    queryset = OcorrenciasFrete.objects.all()
    serializer_class = OcorrenciasFreteSerializer
    
class PagamentosFuncionariosViewSet(viewsets.ModelViewSet):
    queryset = PagamentosFuncionarios.objects.all()
    serializer_class = PagamentosFuncionariosSerializer
    
class PosicoesEstoqueViewSet(viewsets.ModelViewSet):
    queryset = PosicoesEstoque.objects.all()
    serializer_class = PosicoesEstoqueSerializer
    
class ProdutosViewSet(viewsets.ModelViewSet):
    queryset = Produtos.objects.all()
    serializer_class = ProdutoSerializer

class ProdutoFiscalViewSet(viewsets.ModelViewSet):
    queryset = ProdutoFiscal.objects.all()
    serializer_class = ProdutoFiscalSerializer

class ProdutoVariacaoViewSet(viewsets.ModelViewSet):
    queryset = ProdutoVariacao.objects.all()
    serializer_class = ProdutoVariacaoSerializer

class ProdutoComposicaoViewSet(viewsets.ModelViewSet):
    queryset = ProdutoComposicao.objects.all()
    serializer_class = ProdutoComposicaoSerializer

class ProdutoConversaoUnidadeViewSet(viewsets.ModelViewSet):
    queryset = ProdutoConversaoUnidade.objects.all()
    serializer_class = ProdutoConversaoUnidadeSerializer

class ProdutoHistoricoPrecoViewSet(viewsets.ModelViewSet):
    queryset = ProdutoHistoricoPreco.objects.all()
    serializer_class = ProdutoHistoricoPrecoSerializer

class TabelaPrecoViewSet(viewsets.ModelViewSet):
    queryset = TabelaPreco.objects.all()
    serializer_class = TabelaPrecoSerializer

class TabelaPrecoItemViewSet(viewsets.ModelViewSet):
    queryset = TabelaPrecoItem.objects.all()
    serializer_class = TabelaPrecoItemSerializer

class PoliticaDescontoViewSet(viewsets.ModelViewSet):
    queryset = PoliticaDesconto.objects.all()
    serializer_class = PoliticaDescontoSerializer

class ProdutoSubstitutoViewSet(viewsets.ModelViewSet):
    queryset = ProdutoSubstituto.objects.all()
    serializer_class = ProdutoSubstitutoSerializer

class ProdutoCustoLocalViewSet(viewsets.ModelViewSet):
    queryset = ProdutoCustoLocal.objects.all()
    serializer_class = ProdutoCustoLocalSerializer
    
class RegioesEntregaViewSet(viewsets.ModelViewSet):
    queryset = RegioesEntrega.objects.all()
    serializer_class = RegioesEntregaSerializer
    
class SaldosEstoqueViewSet(viewsets.ModelViewSet):
    queryset = SaldosEstoque.objects.all()
    serializer_class = SaldosEstoqueSerializer
    
class TabelasFreteViewSet(viewsets.ModelViewSet):
    queryset = TabelasFrete.objects.all()
    serializer_class = TabelasFreteSerializer
    
class TiposMovimentacaoEstoqueViewSet(viewsets.ModelViewSet):
    queryset = TiposMovimentacaoEstoque.objects.all()
    serializer_class = TiposMovimentacaoEstoqueSerializer
    
class TransportadorasViewSet(viewsets.ModelViewSet):
    queryset = Transportadoras.objects.all()
    serializer_class = TransportadorasSerializer


# Importações adicionais necessárias para a nova view
from rest_framework.decorators import api_view
from django.db.models import Q, Sum, Count, F
from datetime import datetime


@api_view(['GET'])
def suprimentos_por_contrato(request):
    """
    Endpoint para buscar suprimentos por contrato considerando a vigência do contrato
    """
    try:
        # Parâmetros de entrada
        data_inicial = request.GET.get('data_inicial')
        data_final = request.GET.get('data_final')
        contrato_id = request.GET.get('contrato_id')
        cliente_id = request.GET.get('cliente_id')
        
        # Validação de parâmetros obrigatórios
        if not data_inicial or not data_final:
            return Response({
                'error': 'Parâmetros data_inicial e data_final são obrigatórios'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Conversão de strings para datetime
        try:
            data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d').date()
            data_final = datetime.strptime(data_final, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Formato de data inválido. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validação de período
        if data_inicial > data_final:
            return Response({
                'error': 'A data inicial não pode ser maior que a data final'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 1. FILTRAR CONTRATOS VIGENTES NO PERÍODO
        # Um contrato está vigente no período se:
        # - Início do contrato <= data_final do período consultado
        # - Fim do contrato >= data_inicial do período consultado (ou fim = NULL)
        contratos_vigentes = ContratosLocacao.objects.filter(
            Q(inicio__lte=data_final) &  # Contrato começou antes ou no final do período
            (Q(fim__gte=data_inicial) | Q(fim__isnull=True))  # Contrato termina depois do início do período OU está ativo
        ).select_related('cliente')
        
        # Aplicar filtros adicionais se fornecidos
        if contrato_id:
            contratos_vigentes = contratos_vigentes.filter(id=contrato_id)
            
        if cliente_id:
            contratos_vigentes = contratos_vigentes.filter(cliente_id=cliente_id)
        
        # 2. BUSCAR NOTAS FISCAIS DE SUPRIMENTOS
        # Query otimizada para detectar apenas "SIMPLES REMESSA"
        filtro_remessa = Q(operacao__icontains='SIMPLES REMESSA')
        
        # Filtrar notas dos clientes com contratos vigentes no período
        clientes_com_contratos_vigentes = contratos_vigentes.values_list('cliente_id', flat=True).distinct()
        
        notas_query = NotasFiscaisSaida.objects.filter(
            filtro_remessa,
            data__range=[data_inicial, data_final],
            cliente_id__in=clientes_com_contratos_vigentes
        ).select_related('cliente', 'vendedor', 'transportadora')
        
        # 2.5. CALCULAR CUSTO TOTAL ÚNICO (sem duplicação por múltiplos contratos)
        # Isso é importante porque um cliente pode ter múltiplos contratos
        custo_total_unico = Decimal('0.00')
        notas_processadas_custos = set()
        
        for nota in notas_query:
            if nota.id not in notas_processadas_custos:
                notas_processadas_custos.add(nota.id)
                # Calcular custo de aquisição para esta NF
                itens_nota = ItensNfSaida.objects.filter(nota_fiscal=nota)
                for item in itens_nota:
                    quantidade = item.quantidade or Decimal('0')
                    ultima_entrada = ItensNfEntrada.objects.filter(
                        produto_id=item.produto_id,
                        nota_fiscal__data_entrada__lte=nota.data
                    ).order_by('-nota_fiscal__data_entrada', '-id').first()
                    
                    if ultima_entrada:
                        custo_unitario = ultima_entrada.valor_unitario or Decimal('0')
                    else:
                        custo_unitario = Decimal('0')
                    
                    custo_total_unico += quantidade * custo_unitario
        
        # 3. PROCESSAR RESULTADOS POR CONTRATO VIGENTE
        resultados = []
        total_geral_valor = Decimal('0.00')
        total_geral_notas = 0
        total_contratos = 0
        total_faturamento_periodo = Decimal('0.00')  # Faturamento baseado em valores mensais
        
        # Calcular faturamento proporcional ao período
        def calcular_faturamento_proporcional(data_inicio, data_fim, contrato_inicio, contrato_fim, valor_mensal):
            """
            Calcula o faturamento proporcional aos dias do período consultado
            """
            # Período efetivo é a interseção entre período consultado e vigência do contrato
            inicio_efetivo = max(data_inicio, contrato_inicio)
            fim_efetivo = min(data_fim, contrato_fim) if contrato_fim else data_fim
            
            # Calcular dias vigentes no período
            dias_vigentes = (fim_efetivo - inicio_efetivo).days + 1  # +1 para incluir o último dia
            
            # Calcular faturamento proporcional (assumindo mês de 30 dias)
            faturamento_proporcional = (valor_mensal * dias_vigentes) / 30
            
            return {
                'dias_vigentes': dias_vigentes,
                'faturamento_proporcional': faturamento_proporcional,
                'inicio_efetivo': inicio_efetivo,
                'fim_efetivo': fim_efetivo
            }
        
        # Rastrear NFs já processadas globalmente para evitar duplicação
        notas_globais_processadas = set()
        
        for contrato in contratos_vigentes:
            # Buscar notas específicas deste contrato no período
            notas_contrato = notas_query.filter(
                cliente_id=contrato.cliente.id
            )
            
            # Calcular totais específicos do contrato
            totais_contrato = notas_contrato.aggregate(
                total_valor=Sum('valor_total_nota'),
                quantidade_notas=Count('id')
            )
            
            # Calcular faturamento proporcional do contrato no período
            valor_mensal = contrato.valorpacela or Decimal('0.00')
            calculo_proporcional = calcular_faturamento_proporcional(
                data_inicial, data_final, 
                contrato.inicio, contrato.fim,
                valor_mensal
            )
            
            dias_vigentes = calculo_proporcional['dias_vigentes']
            faturamento_contrato = calculo_proporcional['faturamento_proporcional']
            inicio_efetivo = calculo_proporcional['inicio_efetivo']
            fim_efetivo = calculo_proporcional['fim_efetivo']
            
            # Incluir contrato nos resultados mesmo sem notas no período (para mostrar contratos vigentes)
            # mas destacar se teve atividade de suprimentos
            
            # Buscar todas as notas ordenadas por data
            todas_as_notas_contrato = notas_contrato.order_by('-data')
            
            notas = []
            custo_aquisicao_contrato = Decimal('0.00')  # Custo total de aquisição do contrato
            valor_total_notas_contrato = Decimal('0.00')
            qtd_notas_contrato = 0
            
            for nota in todas_as_notas_contrato:
                if nota.id in notas_globais_processadas:
                    continue
                notas_globais_processadas.add(nota.id)
                qtd_notas_contrato += 1
                valor_total_notas_contrato += nota.valor_total_nota or Decimal('0.00')

                # Calcular custo de aquisição dos itens da NF
                custo_nota = Decimal('0.00')
                itens_nota = ItensNfSaida.objects.filter(nota_fiscal=nota).select_related('produto')
                
                for item in itens_nota:
                    quantidade = item.quantidade or Decimal('0')
                    # Buscar última entrada do produto antes da data da nota
                    ultima_entrada = ItensNfEntrada.objects.filter(
                        produto_id=item.produto_id,
                        nota_fiscal__data_entrada__lte=nota.data
                    ).order_by('-nota_fiscal__data_entrada', '-id').first()
                    
                    if ultima_entrada:
                        custo_unitario = ultima_entrada.valor_unitario or Decimal('0')
                    else:
                        custo_unitario = Decimal('0')
                    
                    custo_nota += quantidade * custo_unitario
                
                custo_aquisicao_contrato += custo_nota
                
                notas.append({
                    'id': nota.id,
                    'numero_nota': nota.numero_nota,
                    'data': nota.data.strftime('%Y-%m-%d') if nota.data else None,
                    'operacao': nota.operacao or '',
                    'cfop': nota.cfop or '',
                    'valor_total_nota': float(nota.valor_total_nota or 0),
                    'custo_aquisicao': float(custo_nota),  # Novo campo: custo de aquisição
                    'obs': nota.obs[:100] + '...' if nota.obs and len(nota.obs) > 100 else nota.obs or ''
                })
            
            resultado_contrato = {
                'contrato_id': contrato.id,
                'contrato_numero': contrato.contrato,
                'vigencia': {
                    'inicio': contrato.inicio.strftime('%Y-%m-%d') if contrato.inicio else None,
                    'fim': contrato.fim.strftime('%Y-%m-%d') if contrato.fim else None,
                    'ativo_no_periodo': True,  # Já filtrado por vigência
                    'periodo_efetivo': {
                        'inicio': inicio_efetivo.strftime('%Y-%m-%d'),
                        'fim': fim_efetivo.strftime('%Y-%m-%d'),
                        'dias_vigentes': dias_vigentes
                    }
                },
                'valores_contratuais': {
                    'valor_mensal': float(contrato.valorpacela or 0),  # Valor da parcela mensal
                    'valor_total_contrato': float(contrato.valorcontrato or 0),
                    'numero_parcelas': contrato.numeroparcelas,
                    'faturamento_proporcional': float(faturamento_contrato),  # Valor proporcional aos dias
                    'calculo': f"R$ {float(contrato.valorpacela or 0):.2f} × {dias_vigentes} dias ÷ 30 dias"
                },
                'cliente': {
                    'id': contrato.cliente.id,
                    'nome': contrato.cliente.nome
                },
                'suprimentos': {
                    'total_valor': float(valor_total_notas_contrato),
                    'custo_aquisicao': float(custo_aquisicao_contrato),
                    'quantidade_notas': qtd_notas_contrato,
                    'notas': notas
                },
                'analise_financeira': {
                    'faturamento_proporcional': float(faturamento_contrato),
                    'custo_suprimentos': float(custo_aquisicao_contrato),  # Usar custo de aquisição
                    'margem_bruta': float(faturamento_contrato - custo_aquisicao_contrato),
                    'percentual_margem': float(
                        ((faturamento_contrato - custo_aquisicao_contrato) / faturamento_contrato * 100) 
                        if faturamento_contrato > 0 else 0
                    ),
                    'observacao': f"Faturamento proporcional a {dias_vigentes} dias do período"
                }
            }
            
            resultados.append(resultado_contrato)
            total_contratos += 1
            total_faturamento_periodo += faturamento_contrato
            
            # Somar totais gerais usando custo de aquisição
            if qtd_notas_contrato > 0:
                total_geral_valor += custo_aquisicao_contrato  # Usar custo de aquisição
                total_geral_notas += qtd_notas_contrato
        
        # 4. RESPOSTA FINAL COM INFORMAÇÕES DE VIGÊNCIA E FATURAMENTO
        response_data = {
            'periodo': {
                'data_inicial': data_inicial.strftime('%Y-%m-%d'),
                'data_final': data_final.strftime('%Y-%m-%d')
            },
            'filtros_aplicados': {
                'vigencia_considerada': True,
                'contrato_id': contrato_id,
                'cliente_id': cliente_id,
                'observacao': 'Apenas contratos vigentes no período são incluídos'
            },
            'resumo': {
                'total_contratos_vigentes': total_contratos,
                'total_suprimentos': float(custo_total_unico),  # Usar custo único (sem duplicação)
                'total_notas': len(notas_processadas_custos),  # Quantidade de NFs únicas
                'contratos_com_atividade': len([r for r in resultados if r['suprimentos']['quantidade_notas'] > 0])
            },
            'resumo_financeiro': {
                'faturamento_total_proporcional': float(total_faturamento_periodo),
                'custo_total_suprimentos': float(custo_total_unico),  # Usar custo único (sem duplicação)
                'margem_bruta_total': float(total_faturamento_periodo - custo_total_unico),
                'percentual_margem_total': float(
                    ((total_faturamento_periodo - custo_total_unico) / total_faturamento_periodo * 100) 
                    if total_faturamento_periodo > 0 else 0
                ),
                'metodo_calculo': 'proporcional',
                'observacao': 'Faturamento calculado proporcionalmente aos dias vigentes no período (base: 30 dias/mês)'
            },
            'resultados': resultados
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Erro interno: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def relatorio_financeiro_periodo(request):
    """
    Fornece um relatório de contas a pagar e a receber com base no vencimento
    dentro de um período especificado.
    """
    try:
        # 1. Obter e validar parâmetros de data
        today = date.today()
        data_inicial_str = request.query_params.get('data_inicial', today.strftime('%Y-%m-01'))
        data_final_str = request.query_params.get('data_final', (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1))
        
        data_inicial = datetime.strptime(data_inicial_str, '%Y-%m-%d').date()
        data_final = datetime.strptime(data_final_str, '%Y-%m-%d').date()

        # 2. Consultar Contas a Pagar
        contas_a_pagar_qs = ContasPagar.objects.filter(
            vencimento__range=[data_inicial, data_final],
            status='A'  # Apenas contas em aberto
        ).select_related('fornecedor').order_by('vencimento')

        # 3. Consultar Contas a Receber
        contas_a_receber_qs = ContasReceber.objects.filter(
            vencimento__range=[data_inicial, data_final],
            status='A'  # Apenas contas em aberto
        ).select_related('cliente').order_by('vencimento')

        # 4. Calcular totais
        total_a_pagar = contas_a_pagar_qs.aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        total_a_receber = contas_a_receber_qs.aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

        # 5. Serializar os dados
        pagar_serializer = ContasPagarSerializer(contas_a_pagar_qs, many=True)
        receber_serializer = ContasReceberSerializer(contas_a_receber_qs, many=True)

        # 6. Estruturar a resposta
        response_data = {
            'periodo': {
                'data_inicial': data_inicial,
                'data_final': data_final,
            },
            'resumo': {
                'total_a_pagar': total_a_pagar,
                'total_a_receber': total_a_receber,
                'saldo_previsto': total_a_receber - total_a_pagar
            },
            'contas_a_pagar': pagar_serializer.data,
            'contas_a_receber': receber_serializer.data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Erro interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def contas_por_data_vencimento(request):
    """
    Filtra contas a pagar e receber por data de vencimento
    Parâmetros:
    - data_inicio: Data inicial de vencimento (YYYY-MM-DD)
    - data_fim: Data final de vencimento (YYYY-MM-DD)
    - tipo: 'pagar', 'receber' ou 'ambos' (padrão: 'ambos')
    - status: 'P' (Pago), 'A' (Aberto), 'C' (Cancelado) ou 'todos' (padrão: 'A')
    - incluir_vencidas: 'true' ou 'false' (padrão: 'true')
    """
    try:
        # 1. Obter e validar parâmetros
        data_inicio_str = request.query_params.get('data_inicio')
        data_fim_str = request.query_params.get('data_fim')
        tipo_filtro = request.query_params.get('tipo', 'ambos').lower()
        status_filtro = request.query_params.get('status', 'A').upper()
        incluir_vencidas = request.query_params.get('incluir_vencidas', 'true').lower() == 'true'
        
        if not data_inicio_str or not data_fim_str:
            return Response({
                'error': 'Os parâmetros data_inicio e data_fim são obrigatórios'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Formato de data inválido. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if data_inicio > data_fim:
            return Response({
                'error': 'A data de início deve ser anterior ou igual à data de fim'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. Validar filtros
        if tipo_filtro not in ['pagar', 'receber', 'ambos']:
            return Response({
                'error': 'Tipo deve ser: pagar, receber ou ambos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if status_filtro not in ['P', 'A', 'C', 'TODOS']:
            return Response({
                'error': 'Status deve ser: P (Pago), A (Aberto), C (Cancelado) ou TODOS'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        hoje = date.today()
        
        resultado = {
            'periodo': {
                'data_inicio': data_inicio,
                'data_fim': data_fim
            },
            'filtros': {
                'tipo': tipo_filtro,
                'status': status_filtro,
                'incluir_vencidas': incluir_vencidas
            },
            'resumo': {
                'total_contas_pagar': 0,
                'valor_total_pagar': Decimal('0.00'),
                'total_contas_receber': 0,
                'valor_total_receber': Decimal('0.00'),
                'contas_vencidas_pagar': 0,
                'valor_vencidas_pagar': Decimal('0.00'),
                'contas_vencidas_receber': 0,
                'valor_vencidas_receber': Decimal('0.00')
            },
            'contas_a_pagar': [],
            'contas_a_receber': []
        }
        
        # 3. Filtrar Contas a Pagar
        if tipo_filtro in ['pagar', 'ambos']:
            contas_pagar_qs = ContasPagar.objects.filter(
                vencimento__date__range=[data_inicio, data_fim]
            ).select_related('fornecedor')
            
            if status_filtro != 'TODOS':
                contas_pagar_qs = contas_pagar_qs.filter(status=status_filtro)
            
            # Separar contas vencidas
            contas_pagar_vencidas = contas_pagar_qs.filter(
                vencimento__date__lt=hoje,
                status='A'  # Apenas contas em aberto podem estar vencidas
            )
            
            contas_pagar_qs = contas_pagar_qs.order_by('vencimento', 'fornecedor__nome')
            
            # Serializar e calcular totais
            contas_pagar_data = ContasPagarSerializer(contas_pagar_qs, many=True).data
            resultado['contas_a_pagar'] = contas_pagar_data
            resultado['resumo']['total_contas_pagar'] = contas_pagar_qs.count()
            resultado['resumo']['valor_total_pagar'] = contas_pagar_qs.aggregate(
                total=Sum('valor')
            )['total'] or Decimal('0.00')
            
            # Totais das vencidas
            resultado['resumo']['contas_vencidas_pagar'] = contas_pagar_vencidas.count()
            resultado['resumo']['valor_vencidas_pagar'] = contas_pagar_vencidas.aggregate(
                total=Sum('valor')
            )['total'] or Decimal('0.00')
        
        # 4. Filtrar Contas a Receber
        if tipo_filtro in ['receber', 'ambos']:
            contas_receber_qs = ContasReceber.objects.filter(
                vencimento__date__range=[data_inicio, data_fim]
            ).select_related('cliente')
            
            if status_filtro != 'TODOS':
                contas_receber_qs = contas_receber_qs.filter(status=status_filtro)
            
            # Separar contas vencidas
            contas_receber_vencidas = contas_receber_qs.filter(
                vencimento__date__lt=hoje,
                status='A'  # Apenas contas em aberto podem estar vencidas
            )
            
            contas_receber_qs = contas_receber_qs.order_by('vencimento', 'cliente__nome')
            
            # Serializar e calcular totais
            contas_receber_data = ContasReceberSerializer(contas_receber_qs, many=True).data
            resultado['contas_a_receber'] = contas_receber_data
            resultado['resumo']['total_contas_receber'] = contas_receber_qs.count()
            resultado['resumo']['valor_total_receber'] = contas_receber_qs.aggregate(
                total=Sum('valor')
            )['total'] or Decimal('0.00')
            
            # Totais das vencidas
            resultado['resumo']['contas_vencidas_receber'] = contas_receber_vencidas.count()
            resultado['resumo']['valor_vencidas_receber'] = contas_receber_vencidas.aggregate(
                total=Sum('valor')
            )['total'] or Decimal('0.00')
        
        # 5. Calcular saldo previsto se ambos os tipos estão incluídos
        if tipo_filtro == 'ambos':
            resultado['resumo']['saldo_previsto'] = (
                resultado['resumo']['valor_total_receber'] - 
                resultado['resumo']['valor_total_pagar']
            )
            resultado['resumo']['saldo_vencidas'] = (
                resultado['resumo']['valor_vencidas_receber'] - 
                resultado['resumo']['valor_vencidas_pagar']
            )
        
        return Response(resultado, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Erro interno: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def contas_por_data_pagamento(request):
    """
    Filtra contas a pagar e receber por data de pagamento
    Parâmetros:
    - data_inicio: Data inicial de pagamento (YYYY-MM-DD)
    - data_fim: Data final de pagamento (YYYY-MM-DD)
    - tipo: 'pagar', 'receber' ou 'ambos' (padrão: 'ambos')
    - status: 'P' (Pago), 'A' (Aberto), 'C' (Cancelado) ou 'todos' (padrão: 'P')
    """
    try:
        # 1. Obter e validar parâmetros
        data_inicio_str = request.query_params.get('data_inicio')
        data_fim_str = request.query_params.get('data_fim')
        tipo_filtro = request.query_params.get('tipo', 'ambos').lower()
        status_filtro = request.query_params.get('status', 'P').upper()
        
        if not data_inicio_str or not data_fim_str:
            return Response({
                'error': 'Os parâmetros data_inicio e data_fim são obrigatórios'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Formato de data inválido. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if data_inicio > data_fim:
            return Response({
                'error': 'A data de início deve ser anterior ou igual à data de fim'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. Validar filtros
        if tipo_filtro not in ['pagar', 'receber', 'ambos']:
            return Response({
                'error': 'Tipo deve ser: pagar, receber ou ambos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if status_filtro not in ['P', 'A', 'C', 'TODOS']:
            return Response({
                'error': 'Status deve ser: P (Pago), A (Aberto), C (Cancelado) ou TODOS'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resultado = {
            'periodo': {
                'data_inicio': data_inicio,
                'data_fim': data_fim
            },
            'filtros': {
                'tipo': tipo_filtro,
                'status': status_filtro
            },
            'resumo': {
                'total_contas_pagar': 0,
                'valor_total_pagar': Decimal('0.00'),
                'total_contas_receber': 0,
                'valor_total_receber': Decimal('0.00')
            },
            'contas_a_pagar': [],
            'contas_a_receber': []
        }
        
        # 3. Filtrar Contas a Pagar
        if tipo_filtro in ['pagar', 'ambos']:
            contas_pagar_qs = ContasPagar.objects.filter(
                data_pagamento__date__range=[data_inicio, data_fim]
            ).select_related('fornecedor')
            
            if status_filtro != 'TODOS':
                contas_pagar_qs = contas_pagar_qs.filter(status=status_filtro)
            
            contas_pagar_qs = contas_pagar_qs.order_by('data_pagamento', 'fornecedor__nome')
            
            # Serializar e calcular totais
            contas_pagar_data = ContasPagarSerializer(contas_pagar_qs, many=True).data
            resultado['contas_a_pagar'] = contas_pagar_data
            resultado['resumo']['total_contas_pagar'] = contas_pagar_qs.count()
            resultado['resumo']['valor_total_pagar'] = contas_pagar_qs.aggregate(
                total=Sum('valor_pago')
            )['total'] or Decimal('0.00')
        
        # 4. Filtrar Contas a Receber
        if tipo_filtro in ['receber', 'ambos']:
            contas_receber_qs = ContasReceber.objects.filter(
                data_pagamento__date__range=[data_inicio, data_fim]
            ).select_related('cliente')
            
            if status_filtro != 'TODOS':
                contas_receber_qs = contas_receber_qs.filter(status=status_filtro)
            
            contas_receber_qs = contas_receber_qs.order_by('data_pagamento', 'cliente__nome')
            
            # Serializar e calcular totais
            contas_receber_data = ContasReceberSerializer(contas_receber_qs, many=True).data
            resultado['contas_a_receber'] = contas_receber_data
            resultado['resumo']['total_contas_receber'] = contas_receber_qs.count()
            resultado['resumo']['valor_total_receber'] = contas_receber_qs.aggregate(
                total=Sum('recebido')
            )['total'] or Decimal('0.00')
        
        # 5. Calcular saldo líquido se ambos os tipos estão incluídos
        if tipo_filtro == 'ambos':
            resultado['resumo']['saldo_liquido'] = (
                resultado['resumo']['valor_total_receber'] - 
                resultado['resumo']['valor_total_pagar']
            )
        
        return Response(resultado, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Erro interno: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def relatorio_valor_estoque(request):
    """
    Calcula o valor total do estoque em uma data específica.
    """
    try:
        # 1. Obter e validar o parâmetro de data
        data_posicao_str = request.query_params.get('data', date.today().strftime('%Y-%m-%d'))
        data_posicao = datetime.strptime(data_posicao_str, '%Y-%m-%d').date()

        # 2. Calcular saldos de estoque na data
        saldos = MovimentacoesEstoque.objects.filter(
            data_movimentacao__date__lte=data_posicao,
            produto__isnull=False  # Filtrar movimentações sem produto
        ).values(
            'produto_id', 
            'produto__descricao', 
            'produto__nome',
            'produto__preco_custo',
            'produto__grupo_id'
        ).annotate(
            saldo_final=Sum(
                Case(
                    When(tipo_movimentacao__tipo='E', then=F('quantidade')),
                    When(tipo_movimentacao__tipo='S', then=-F('quantidade')),
                    default=0,
                    output_field=DecimalField()
                )
            )
        ).order_by('produto__nome')

        # 3. Calcular o valor total e preparar detalhes
        valor_total_estoque = Decimal('0.00')
        detalhes_produtos = []
        
        # Buscar nomes dos grupos/categorias para otimizar consultas
        grupos_ids = [saldo['produto__grupo_id'] for saldo in saldos if saldo['produto__grupo_id'] and saldo['saldo_final'] > 0]
        grupos_dict = {grupo.id: grupo.nome for grupo in Grupos.objects.filter(id__in=grupos_ids)} if grupos_ids else {}

        for saldo in saldos:
            if saldo['saldo_final'] > 0:
                custo = saldo['produto__preco_custo'] or Decimal('0.00')
                valor_produto = saldo['saldo_final'] * custo
                valor_total_estoque += valor_produto
                
                # Obter nome da categoria/grupo
                grupo_id = saldo['produto__grupo_id']
                categoria_nome = grupos_dict.get(grupo_id, 'Sem categoria') if grupo_id else 'Sem categoria'
                
                detalhes_produtos.append({
                    'produto_id': saldo['produto_id'],
                    'produto_descricao': saldo['produto__descricao'] or saldo['produto__nome'] or 'Produto sem nome',
                    'categoria': categoria_nome,
                    'quantidade_em_estoque': saldo['saldo_final'],
                    'custo_unitario': custo,
                    'valor_total_produto': valor_produto
                })

        # 4. Estruturar a resposta
        response_data = {
            'data_posicao': data_posicao,
            'valor_total_estoque': valor_total_estoque,
            'total_produtos_em_estoque': len(detalhes_produtos),
            'detalhes_por_produto': detalhes_produtos
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Erro interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def contas_nao_pagas_por_data_corte(request):
    """
    Endpoint para mostrar total de contas a pagar e receber não pagas 
    antes e depois de uma data de corte, agrupadas por fornecedor/cliente.
    
    Parâmetros:
    - data_corte: Data de referência (YYYY-MM-DD) - obrigatório
    - tipo: 'pagar', 'receber' ou 'ambos' (padrão: 'ambos')
    - incluir_canceladas: true/false (padrão: false)
    - filtrar_por_data_emissao: true/false (padrão: false) - filtra apenas contas com data de emissão anterior à data de corte
    """
    
    def classificar_tipo_custo(especificacao):
        """
        Classifica fornecedores como custos fixos ou variáveis baseado na especificação
        """
        custos_fixos = {
            'SALARIOS', 'PRO-LABORE', 'HONOR. CONTABEIS', 'LUZ', 'AGUA', 'TELEFONE',
            'IMPOSTOS', 'ENCARGOS', 'REFEICAO', 'BENEFICIOS', 'OUTRAS DESPESAS',
            'MAT. DE ESCRITORIO', 'PAGTO SERVICOS', 'EMPRESTIMO', 'DESP. FINANCEIRAS'
        }
        
        custos_variaveis = {
            'FORNECEDORES', 'FRETE', 'COMISSOES', 'DESP. VEICULOS'
        }
        
        if not especificacao:
            return 'NÃO CLASSIFICADO'
        
        especificacao_upper = especificacao.upper()
        
        if especificacao_upper in custos_fixos:
            return 'FIXO'
        elif especificacao_upper in custos_variaveis:
            return 'VARIÁVEL'
        else:
            return 'NÃO CLASSIFICADO'
    try:
        # 1. Validar parâmetros
        data_corte_str = request.query_params.get('data_corte')
        tipo_filtro = request.query_params.get('tipo', 'ambos').lower()
        incluir_canceladas = request.query_params.get('incluir_canceladas', 'false').lower() == 'true'
        filtrar_por_data_emissao = request.query_params.get('filtrar_por_data_emissao', 'false').lower() == 'true'
        
        if not data_corte_str:
            return Response({
                'error': 'O parâmetro data_corte é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data_corte = datetime.strptime(data_corte_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Formato de data inválido. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if tipo_filtro not in ['pagar', 'receber', 'ambos']:
            return Response({
                'error': 'Tipo deve ser: pagar, receber ou ambos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resultado = {
            'data_corte': data_corte,
            'filtros': {
                'tipo': tipo_filtro,
                'incluir_canceladas': incluir_canceladas,
                'filtrar_por_data_emissao': filtrar_por_data_emissao
            },
            'resumo_geral': {
                'antes_data_corte': {
                    'total_contas_pagar': 0,
                    'valor_total_pagar': Decimal('0.00'),
                    'total_contas_receber': 0,
                    'valor_total_receber': Decimal('0.00'),
                    'total_fornecedores': 0,
                    'total_clientes': 0
                },
                'depois_data_corte': {
                    'total_contas_pagar': 0,
                    'valor_total_pagar': Decimal('0.00'),
                    'total_contas_receber': 0,
                    'valor_total_receber': Decimal('0.00'),
                    'total_fornecedores': 0,
                    'total_clientes': 0
                }
            },
            'detalhamento': {
                'contas_a_pagar': {
                    'antes_data_corte': [],
                    'depois_data_corte': []
                },
                'contas_a_receber': {
                    'antes_data_corte': [],
                    'depois_data_corte': []
                }
            }
        }
        
        # 2. Processar Contas a Pagar
        if tipo_filtro in ['pagar', 'ambos']:
            # Base query para considerar contas que estavam não pagas na data de corte
            # Critério: registro anterior à data de corte (data de emissão) e pagamento posterior à data de corte (ou sem pagamento)
            base_query = ContasPagar.objects.all().select_related('fornecedor')

            if not incluir_canceladas:
                base_query = base_query.exclude(status='C')

            # Contas não pagas NA DATA DE CORTE (emissão < data_corte e (sem pagamento ou pagamento > data_corte))
            contas_antes = base_query.filter(
                Q(data__lt=data_corte) & (Q(data_pagamento__isnull=True) | Q(data_pagamento__gt=data_corte))
            ).values(
                'fornecedor__id',
                'fornecedor__nome',
                'fornecedor__cpf_cnpj',
                'fornecedor__especificacao'
            ).annotate(
                total_contas=Count('id'),
                valor_total=Sum('valor'),
                menor_vencimento=Min('vencimento'),
                maior_vencimento=Max('vencimento')
            ).order_by('fornecedor__especificacao', 'fornecedor__nome')

            # Contas originadas após a data de corte e ainda não pagas após a data
            contas_depois = base_query.filter(
                Q(data__gte=data_corte) & (Q(data_pagamento__isnull=True) | Q(data_pagamento__gt=data_corte))
            ).values(
                'fornecedor__id',
                'fornecedor__nome',
                'fornecedor__cpf_cnpj',
                'fornecedor__especificacao'
            ).annotate(
                total_contas=Count('id'),
                valor_total=Sum('valor'),
                menor_vencimento=Min('vencimento'),
                maior_vencimento=Max('vencimento')
            ).order_by('fornecedor__especificacao', 'fornecedor__nome')
            
            # Formatar dados de contas a pagar
            def formatar_contas_pagar(queryset):
                lista = []
                for item in queryset:
                    especificacao = item['fornecedor__especificacao']
                    tipo_custo = classificar_tipo_custo(especificacao)
                    
                    lista.append({
                        'fornecedor': {
                            'id': item['fornecedor__id'],
                            'nome': item['fornecedor__nome'],
                            'cnpj_cpf': item['fornecedor__cpf_cnpj'],
                            'especificacao': especificacao,
                            'tipo_custo': tipo_custo
                        },
                        'total_contas': item['total_contas'],
                        'valor_total': float(item['valor_total'] or Decimal('0.00')),
                        'periodo_vencimento': {
                            'menor_data': item['menor_vencimento'],
                            'maior_data': item['maior_vencimento']
                        }
                    })
                return lista
            
            resultado['detalhamento']['contas_a_pagar']['antes_data_corte'] = formatar_contas_pagar(contas_antes)
            resultado['detalhamento']['contas_a_pagar']['depois_data_corte'] = formatar_contas_pagar(contas_depois)
            
            # Função para calcular totais por tipo de custo
            def calcular_totais_por_tipo_custo(contas_lista):
                totais = {
                    'FIXO': {'total_contas': 0, 'valor_total': 0.0},
                    'VARIÁVEL': {'total_contas': 0, 'valor_total': 0.0},
                    'NÃO CLASSIFICADO': {'total_contas': 0, 'valor_total': 0.0}
                }
                
                for conta in contas_lista:
                    tipo_custo = conta['fornecedor']['tipo_custo']
                    totais[tipo_custo]['total_contas'] += conta['total_contas']
                    totais[tipo_custo]['valor_total'] += conta['valor_total']
                
                return totais
            
            # Calcular totais para contas a pagar
            resultado['resumo_geral']['antes_data_corte']['total_contas_pagar'] = sum(c['total_contas'] for c in resultado['detalhamento']['contas_a_pagar']['antes_data_corte'])
            resultado['resumo_geral']['antes_data_corte']['valor_total_pagar'] = sum(c['valor_total'] for c in resultado['detalhamento']['contas_a_pagar']['antes_data_corte'])
            resultado['resumo_geral']['antes_data_corte']['total_fornecedores'] = len(resultado['detalhamento']['contas_a_pagar']['antes_data_corte'])
            resultado['resumo_geral']['antes_data_corte']['custos_por_tipo'] = calcular_totais_por_tipo_custo(resultado['detalhamento']['contas_a_pagar']['antes_data_corte'])
            
            resultado['resumo_geral']['depois_data_corte']['total_contas_pagar'] = sum(c['total_contas'] for c in resultado['detalhamento']['contas_a_pagar']['depois_data_corte'])
            resultado['resumo_geral']['depois_data_corte']['valor_total_pagar'] = sum(c['valor_total'] for c in resultado['detalhamento']['contas_a_pagar']['depois_data_corte'])
            resultado['resumo_geral']['depois_data_corte']['total_fornecedores'] = len(resultado['detalhamento']['contas_a_pagar']['depois_data_corte'])
            resultado['resumo_geral']['depois_data_corte']['custos_por_tipo'] = calcular_totais_por_tipo_custo(resultado['detalhamento']['contas_a_pagar']['depois_data_corte'])
        
        # 3. Processar Contas a Receber
        if tipo_filtro in ['receber', 'ambos']:
            # Base query para considerar contas que estavam não recebidas na data de corte
            base_query = ContasReceber.objects.all().select_related('cliente')

            if not incluir_canceladas:
                base_query = base_query.exclude(status='C')

            # Contas não recebidas NA DATA DE CORTE (emissão < data_corte e (sem pagamento ou pagamento > data_corte))
            contas_antes = base_query.filter(
                Q(data__lt=data_corte) & (Q(data_pagamento__isnull=True) | Q(data_pagamento__gt=data_corte))
            ).values(
                'cliente__id',
                'cliente__nome',
                'cliente__cpf_cnpj'
            ).annotate(
                total_contas=Count('id'),
                valor_total=Sum('valor'),
                menor_vencimento=Min('vencimento'),
                maior_vencimento=Max('vencimento')
            ).order_by('cliente__nome')

            # Contas originadas após a data de corte ainda não recebidas
            contas_depois = base_query.filter(
                Q(data__gte=data_corte) & (Q(data_pagamento__isnull=True) | Q(data_pagamento__gt=data_corte))
            ).values(
                'cliente__id',
                'cliente__nome',
                'cliente__cpf_cnpj'
            ).annotate(
                total_contas=Count('id'),
                valor_total=Sum('valor'),
                menor_vencimento=Min('vencimento'),
                maior_vencimento=Max('vencimento')
            ).order_by('cliente__nome')
            
            # Formatar dados de contas a receber
            def formatar_contas_receber(queryset):
                lista = []
                for item in queryset:
                    lista.append({
                        'cliente': {
                            'id': item['cliente__id'],
                            'nome': item['cliente__nome'],
                            'cnpj_cpf': item['cliente__cpf_cnpj']
                        },
                        'total_contas': item['total_contas'],
                        'valor_total': float(item['valor_total'] or Decimal('0.00')),
                        'periodo_vencimento': {
                            'menor_data': item['menor_vencimento'],
                            'maior_data': item['maior_vencimento']
                        }
                    })
                return lista
            
            resultado['detalhamento']['contas_a_receber']['antes_data_corte'] = formatar_contas_receber(contas_antes)
            resultado['detalhamento']['contas_a_receber']['depois_data_corte'] = formatar_contas_receber(contas_depois)
            
            # Calcular totais para contas a receber
            resultado['resumo_geral']['antes_data_corte']['total_contas_receber'] = sum(c['total_contas'] for c in resultado['detalhamento']['contas_a_receber']['antes_data_corte'])
            resultado['resumo_geral']['antes_data_corte']['valor_total_receber'] = sum(c['valor_total'] for c in resultado['detalhamento']['contas_a_receber']['antes_data_corte'])
            resultado['resumo_geral']['antes_data_corte']['total_clientes'] = len(resultado['detalhamento']['contas_a_receber']['antes_data_corte'])
            
            resultado['resumo_geral']['depois_data_corte']['total_contas_receber'] = sum(c['total_contas'] for c in resultado['detalhamento']['contas_a_receber']['depois_data_corte'])
            resultado['resumo_geral']['depois_data_corte']['valor_total_receber'] = sum(c['valor_total'] for c in resultado['detalhamento']['contas_a_receber']['depois_data_corte'])
            resultado['resumo_geral']['depois_data_corte']['total_clientes'] = len(resultado['detalhamento']['contas_a_receber']['depois_data_corte'])
        
        # 4. Calcular saldos líquidos
        antes_valor_receber = Decimal(str(resultado['resumo_geral']['antes_data_corte']['valor_total_receber']))
        antes_valor_pagar = Decimal(str(resultado['resumo_geral']['antes_data_corte']['valor_total_pagar']))
        depois_valor_receber = Decimal(str(resultado['resumo_geral']['depois_data_corte']['valor_total_receber']))
        depois_valor_pagar = Decimal(str(resultado['resumo_geral']['depois_data_corte']['valor_total_pagar']))
        
        antes_saldo = antes_valor_receber - antes_valor_pagar
        depois_saldo = depois_valor_receber - depois_valor_pagar
        
        resultado['resumo_geral']['antes_data_corte']['saldo_liquido'] = float(antes_saldo)
        resultado['resumo_geral']['depois_data_corte']['saldo_liquido'] = float(depois_saldo)
        resultado['resumo_geral']['saldo_total'] = float(antes_saldo + depois_saldo)
        
        # 5. Adicionar metadados
        resultado['metadados'] = {
            'data_consulta': datetime.now().isoformat(),
            'total_registros_antes': (resultado['resumo_geral']['antes_data_corte']['total_contas_pagar'] + 
                                    resultado['resumo_geral']['antes_data_corte']['total_contas_receber']),
            'total_registros_depois': (resultado['resumo_geral']['depois_data_corte']['total_contas_pagar'] + 
                                     resultado['resumo_geral']['depois_data_corte']['total_contas_receber'])
        }
        
        return Response(resultado, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Erro interno: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
