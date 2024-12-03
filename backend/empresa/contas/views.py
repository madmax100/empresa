from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Q, F, FloatField
from django.db.models.functions import Cast
from django.db.models.functions import Coalesce
from decimal import Decimal
from datetime import datetime, timedelta, date
import time





from .serializers import ItemContratoLocacaoSerializer, ProdutoSerializer
from .models import *
from .serializers import *

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
    
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from decimal import Decimal
from datetime import date
import time

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
        """
        Atualiza o status de um título específico
        """
        try:
            conta = self.get_object()
            novo_status = request.data.get('status')
            
            if novo_status not in ['A', 'P', 'C']:
                return Response(
                    {'error': 'Status inválido. Use A, P ou C.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            conta.status = novo_status
            conta.save()

            # Retorna o objeto atualizado
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
                    Q(fornecedor__nome__icontains=search_term) |
                    Q(historico__icontains=search_term)
                )

            # Aplicar filtro de status
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
        """
        Atualiza o status de um título específico
        """
        try:
            conta = self.get_object()
            novo_status = request.data.get('status')
            
            if novo_status not in ['A', 'P', 'C']:
                return Response(
                    {'error': 'Status inválido. Use A, P ou C.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            conta.status = novo_status
            conta.save()

            # Retorna o objeto atualizado
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
            itens = ItensContratoLocacao.objects.filter(contrato=contrato)

            # Busca as notas fiscais relacionadas com prefetch otimizado
            notas_query = NotasFiscaisSaida.objects.filter(
                cliente=contrato.cliente,
            ).prefetch_related(
                'itens',
                'itens__produto'  # Prefetch dos produtos associados aos itens
            )

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
                
                # Busca e serializa os itens da nota com produtos
                itens_nota = ItensNfSaida.objects.filter(
                    nota_fiscal_id=nota
                ).select_related('produto')  # Otimiza a consulta dos produtos
                
                itens_serializados = ItensNfSaidaSerializer(itens_nota, many=True).data
                
                # Calcula totais dos itens
                total_itens = itens_nota.aggregate(
                    total_valor=Sum('valor_total'),
                    total_quantidade=Sum('quantidade')
                )

                nota_processada = {
                    **nota_serializada,
                    'itens': itens_serializados,
                    'resumo_itens': {
                        'total_valor': float(total_itens['total_valor'] or 0),
                        'total_quantidade': total_itens['total_quantidade'] or 0
                    }
                }

                notas_processadas.append(nota_processada)
                total_valor_notas += total_itens['total_valor'] or 0
                total_quantidade_itens += total_itens['total_quantidade'] or 0

            # Calcula resumo geral
            resumo_geral = {
                'total_valor': float(total_valor_notas),
                'quantidade_notas': len(notas_processadas),
                'total_quantidade_itens': total_quantidade_itens
            }

            return Response({
                'contrato': contrato_data,
                'itens': itens_data,
                'notas_fiscais': {
                    'resumo': resumo_geral,
                    'notas': notas_processadas
                },
                'periodo': {
                    'data_inicial': data_inicial,
                    'data_final': data_final
                }
            })

        except Exception as e:
            import traceback
            print(f"Erro detalhado: {traceback.format_exc()}")
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
        itens = ItensContratoLocacao.objects.filter(contrato=contrato)
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
    
