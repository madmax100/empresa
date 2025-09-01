from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q, Count
from django.db.models.functions import Coalesce, TruncMonth
from decimal import Decimal
from datetime import date, timedelta
import time


from ..models.access import Categorias, CategoriasProdutos, Clientes, ContagensInventario, ContasPagar, ContasReceber, ContratosLocacao, CustosAdicionaisFrete, Despesas, Empresas, Fornecedores, Fretes, Funcionarios, Grupos, HistoricoRastreamento, Inventarios, ItensContratoLocacao, ItensNfEntrada, ItensNfSaida, LocaisEstoque, Lotes, Marcas, MovimentacoesEstoque, NotasFiscaisEntrada, NotasFiscaisSaida, OcorrenciasFrete, PagamentosFuncionarios, PosicoesEstoque, Produtos, RegioesEntrega, SaldosEstoque, TabelasFrete, TiposMovimentacaoEstoque, Transportadoras

from ..serializers.access import ItemContratoLocacaoSerializer, ProdutoSerializer, CategoriaSerializer, CategoriasProdutosSerializer, ClienteSerializer, ContagensInventarioSerializer, ContasPagarSerializer, ContasReceberSerializer, ContratoLocacaoSerializer, CustosAdicionaisFreteSerializer, DespesasSerializer, EmpresasSerializer, FornecedoresSerializer, FretesSerializer, FuncionariosSerializer, GruposSerializer, HistoricoRastreamentoSerializer, InventariosSerializer, ItensNfEntradaSerializer, ItensNfSaidaSerializer, LocaisEstoqueSerializer, LotesSerializer, MarcasSerializer, MovimentacoesEstoqueSerializer, NotasFiscaisEntradaSerializer, NotasFiscaisSaidaSerializer, OcorrenciasFreteSerializer, PagamentosFuncionariosSerializer, PosicoesEstoqueSerializer, RegioesEntregaSerializer, SaldosEstoqueSerializer, TabelasFreteSerializer, TiposMovimentacaoEstoqueSerializer, TransportadorasSerializer

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
        contrato = get_object_or_404(ContratosLocacao, contrato=contrato_numero)
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
    
class ItensNfEntradaViewSet(viewsets.ModelViewSet):
    queryset = ItensNfEntrada.objects.all()
    serializer_class = ItensNfEntradaSerializer
    
class ItensNfSaidaViewSet(viewsets.ModelViewSet):
    queryset = ItensNfSaida.objects.all()
    serializer_class = ItensNfSaidaSerializer
    
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
    Endpoint para buscar suprimentos por contrato
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
        
        # Query otimizada para detectar apenas "SIMPLES REMESSA"
        filtro_remessa = Q(operacao__icontains='SIMPLES REMESSA')
        
        # Base query das notas fiscais de saída
        notas_query = NotasFiscaisSaida.objects.filter(
            filtro_remessa,
            data__range=[data_inicial, data_final]
        ).select_related('cliente', 'vendedor', 'transportadora')
        
        # Filtros opcionais
        if contrato_id:
            # Buscar cliente do contrato específico
            try:
                contrato = ContratosLocacao.objects.get(id=contrato_id)
                notas_query = notas_query.filter(cliente=contrato.cliente)
            except ContratosLocacao.DoesNotExist:
                return Response({
                    'error': f'Contrato {contrato_id} não encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
        
        if cliente_id:
            notas_query = notas_query.filter(cliente_id=cliente_id)
        
        # Buscar contratos que têm notas no período (ou contrato específico se informado)
        contratos_com_notas = ContratosLocacao.objects.filter(
            cliente__in=notas_query.values_list('cliente_id', flat=True).distinct()
        )
        
        if contrato_id:
            contratos_com_notas = contratos_com_notas.filter(id=contrato_id)
        
        # Processar resultados por contrato
        resultados = []
        total_geral_valor = Decimal('0.00')
        total_geral_notas = 0
        total_contratos = 0
        
        for contrato in contratos_com_notas:
            # Buscar notas específicas deste contrato no período
            notas_contrato = notas_query.filter(
                cliente_id=contrato.cliente.id
            )
            
            # Calcular totais específicos do contrato
            totais_contrato = notas_contrato.aggregate(
                total_valor=Sum('valor_total_nota'),
                quantidade_notas=Count('id')
            )
            
            # Se o contrato tem notas no período, incluir nos resultados
            if totais_contrato['quantidade_notas'] and totais_contrato['quantidade_notas'] > 0:
                # Buscar todas as notas ordenadas por data
                todas_as_notas_contrato = notas_contrato.order_by('-data')
                
                notas = []
                for nota in todas_as_notas_contrato:
                    notas.append({
                        'id': nota.id,
                        'numero_nota': nota.numero_nota,
                        'data': nota.data.strftime('%Y-%m-%d') if nota.data else None,
                        'operacao': nota.operacao or '',
                        'cfop': nota.cfop or '',
                        'valor_total_nota': float(nota.valor_total_nota or 0),
                        'obs': nota.obs[:100] + '...' if nota.obs and len(nota.obs) > 100 else nota.obs or ''
                    })
                
                resultado_contrato = {
                    'contrato_id': contrato.id,
                    'contrato_numero': contrato.contrato,
                    'cliente': {
                        'id': contrato.cliente.id,
                        'nome': contrato.cliente.nome
                    },
                    'suprimentos': {
                        'total_valor': float(totais_contrato['total_valor'] or 0),
                        'quantidade_notas': totais_contrato['quantidade_notas'] or 0,
                        'notas': notas
                    }
                }
                
                resultados.append(resultado_contrato)
                total_contratos += 1
                
                # Somar totais gerais
                total_geral_valor += totais_contrato['total_valor'] or Decimal('0.00')
                total_geral_notas += totais_contrato['quantidade_notas'] or 0
        
        # Resposta final
        response_data = {
            'periodo': {
                'data_inicial': data_inicial.strftime('%Y-%m-%d'),
                'data_final': data_final.strftime('%Y-%m-%d')
            },
            'resumo': {
                'total_contratos': total_contratos,
                'total_suprimentos': float(total_geral_valor),
                'total_notas': total_geral_notas
            },
            'resultados': resultados
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Erro interno: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
