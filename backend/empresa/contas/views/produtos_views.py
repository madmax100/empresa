from decimal import Decimal

from django.db import models
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.access import (
    PoliticaDesconto,
    ProdutoComposicao,
    ProdutoConversaoUnidade,
    ProdutoFiscal,
    ProdutoCustoLocal,
    Produtos,
    TabelaPrecoItem,
    ProdutoHistoricoPreco,
    ProdutoSubstituto,
    ProdutoVariacao,
)


class ProdutosPrecoView(APIView):
    """
    Calcula preço efetivo de um produto considerando tabela, desconto e quantidade.
    """

    def post(self, request):
        data = request.data or {}
        produto_id = data.get('produto_id')
        tabela_id = data.get('tabela_id')
        cliente_id = data.get('cliente_id')
        quantidade = Decimal(str(data.get('quantidade', 1)))
        data_base = data.get('data_base')

        if not produto_id:
            return Response({'error': 'produto_id é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            produto = Produtos.objects.get(id=produto_id)
        except Produtos.DoesNotExist:
            return Response({'error': 'Produto não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        base_preco = Decimal(str(produto.preco_venda or 0))
        preco_minimo = None
        desconto_maximo = None
        tabela_item_id = None

        if tabela_id:
            tabela_item = TabelaPrecoItem.objects.filter(
                tabela_id=tabela_id,
                produto_id=produto_id,
                ativo=True,
            ).first()
            if tabela_item:
                base_preco = Decimal(str(tabela_item.preco))
                preco_minimo = tabela_item.preco_minimo
                desconto_maximo = tabela_item.desconto_maximo
                tabela_item_id = tabela_item.id

        politica = self._obter_politica_desconto(produto_id, tabela_id, cliente_id, data_base)
        desconto_percentual = Decimal('0')
        desconto_valor = Decimal('0')
        politica_id = None

        if politica:
            politica_id = politica.id
            if politica.percentual:
                desconto_percentual = Decimal(str(politica.percentual))
            if politica.valor:
                desconto_valor = Decimal(str(politica.valor))

        if desconto_maximo is not None and desconto_percentual > Decimal(str(desconto_maximo)):
            desconto_percentual = Decimal(str(desconto_maximo))

        desconto_calculado = (base_preco * desconto_percentual / Decimal('100')) + desconto_valor
        preco_final = base_preco - desconto_calculado

        if preco_minimo is not None:
            preco_final = max(preco_final, Decimal(str(preco_minimo)))

        total = preco_final * quantidade

        return Response({
            'produto_id': produto_id,
            'tabela_id': tabela_id,
            'tabela_item_id': tabela_item_id,
            'politica_id': politica_id,
            'quantidade': float(quantidade),
            'preco_base': float(base_preco),
            'desconto_percentual': float(desconto_percentual),
            'desconto_valor': float(desconto_valor),
            'preco_final': float(preco_final),
            'total': float(total),
        })

    def _obter_politica_desconto(self, produto_id, tabela_id, cliente_id, data_base):
        base_date = timezone.now().date()
        if data_base:
            try:
                base_date = timezone.datetime.strptime(data_base, '%Y-%m-%d').date()
            except ValueError:
                return None

        politicas = PoliticaDesconto.objects.filter(ativo=True).filter(
            Q(produto_id=produto_id) | Q(produto_id__isnull=True),
            Q(tabela_id=tabela_id) | Q(tabela_id__isnull=True),
            Q(cliente_id=cliente_id) | Q(cliente_id__isnull=True),
        ).filter(
            Q(data_inicio__lte=base_date) | Q(data_inicio__isnull=True),
            Q(data_fim__gte=base_date) | Q(data_fim__isnull=True),
        )

        if not politicas.exists():
            return None

        def prioridade(politica):
            return (
                1 if politica.cliente_id else 0,
                1 if politica.produto_id else 0,
                1 if politica.tabela_id else 0,
            )

        return sorted(politicas, key=prioridade, reverse=True)[0]


class ProdutosConversaoView(APIView):
    """
    Converte quantidade entre unidades cadastradas para um produto.
    """

    def post(self, request):
        data = request.data or {}
        produto_id = data.get('produto_id')
        unidade_origem = data.get('unidade_origem')
        unidade_destino = data.get('unidade_destino')
        quantidade = data.get('quantidade')

        if not produto_id or not unidade_origem or not unidade_destino or quantidade is None:
            return Response({'error': 'Campos obrigatórios: produto_id, unidade_origem, unidade_destino, quantidade.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            quantidade = Decimal(str(quantidade))
        except Exception:
            return Response({'error': 'Quantidade inválida.'}, status=status.HTTP_400_BAD_REQUEST)

        conversao = ProdutoConversaoUnidade.objects.filter(
            produto_id=produto_id,
            unidade_origem=unidade_origem,
            unidade_destino=unidade_destino,
            ativo=True,
        ).first()

        if not conversao:
            return Response({'error': 'Conversão não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        quantidade_convertida = quantidade * Decimal(str(conversao.fator_conversao))

        return Response({
            'produto_id': produto_id,
            'unidade_origem': unidade_origem,
            'unidade_destino': unidade_destino,
            'quantidade': float(quantidade),
            'quantidade_convertida': float(quantidade_convertida),
            'fator_conversao': float(conversao.fator_conversao),
        })


class ProdutosComposicaoResumoView(APIView):
    """
    Retorna a composição (BOM/kit) de um produto com custos estimados.
    """

    def get(self, request, produto_id):
        componentes = ProdutoComposicao.objects.filter(
            produto_pai_id=produto_id,
            ativo=True,
        ).select_related('produto_componente_id')

        if not componentes.exists():
            return Response({'produto_id': produto_id, 'componentes': [], 'custo_estimado': 0.0})

        itens = []
        custo_total = Decimal('0')

        for componente in componentes:
            produto = componente.produto_componente_id
            custo_unitario = Decimal(str(produto.preco_custo or 0))
            quantidade = Decimal(str(componente.quantidade))
            custo_item = quantidade * custo_unitario
            custo_total += custo_item
            itens.append({
                'produto_id': produto.id,
                'codigo': produto.codigo,
                'nome': produto.nome,
                'quantidade': float(quantidade),
                'unidade_medida': componente.unidade_medida or produto.unidade_medida,
                'custo_unitario': float(custo_unitario),
                'custo_total': float(custo_item),
            })

        return Response({
            'produto_id': produto_id,
            'componentes': itens,
            'custo_estimado': float(custo_total),
        })


class ProdutosAlertasView(APIView):
    """
    Retorna alertas operacionais do cadastro de produtos.
    """

    def get(self, request):
        limite = int(request.GET.get('limite', 50))
        estoques_criticos = Produtos.objects.filter(
            ativo=True,
            estoque_minimo__isnull=False,
            estoque_atual__lt=models.F('estoque_minimo'),
        ).values('id', 'codigo', 'nome', 'estoque_atual', 'estoque_minimo')[:limite]

        sem_preco = Produtos.objects.filter(
            ativo=True,
            preco_venda__isnull=True,
        ).values('id', 'codigo', 'nome')[:limite]

        sem_ean = Produtos.objects.filter(
            ativo=True,
        ).filter(Q(ean__isnull=True) | Q(ean__exact='')).values('id', 'codigo', 'nome')[:limite]

        sem_sku = Produtos.objects.filter(
            ativo=True,
        ).filter(Q(sku__isnull=True) | Q(sku__exact='')).values('id', 'codigo', 'nome')[:limite]

        return Response({
            'limite': limite,
            'estoque_critico': list(estoques_criticos),
            'sem_preco_venda': list(sem_preco),
            'sem_ean': list(sem_ean),
            'sem_sku': list(sem_sku),
        })


class ProdutosHistoricoPrecoView(APIView):
    """
    Retorna histórico de preços de um produto com o último preço vigente.
    """

    def get(self, request, produto_id):
        historico = ProdutoHistoricoPreco.objects.filter(
            produto_id=produto_id,
        ).order_by('-data_inicio')

        itens = [
            {
                'id': item.id,
                'preco_custo': float(item.preco_custo or 0),
                'preco_venda': float(item.preco_venda or 0),
                'data_inicio': item.data_inicio,
                'data_fim': item.data_fim,
                'origem': item.origem,
                'observacoes': item.observacoes,
            }
            for item in historico
        ]

        ultimo = itens[0] if itens else None

        return Response({
            'produto_id': produto_id,
            'ultimo_preco': ultimo,
            'historico': itens,
        })


class ProdutosSubstitutosView(APIView):
    """
    Lista substitutos de um produto.
    """

    def get(self, request, produto_id):
        substitutos = ProdutoSubstituto.objects.filter(
            produto_id=produto_id,
            ativo=True,
        ).select_related('produto_substituto_id')

        itens = [
            {
                'id': item.id,
                'produto_substituto_id': item.produto_substituto_id_id,
                'codigo': item.produto_substituto_id.codigo,
                'nome': item.produto_substituto_id.nome,
                'motivo': item.motivo,
            }
            for item in substitutos
        ]

        return Response({
            'produto_id': produto_id,
            'substitutos': itens,
        })


class ProdutosFichaTecnicaView(APIView):
    """
    Consolida informações de cadastro do produto (fiscal, variações, composição, substitutos e custos).
    """

    def get(self, request, produto_id):
        try:
            produto = Produtos.objects.get(id=produto_id)
        except Produtos.DoesNotExist:
            return Response({'error': 'Produto não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        fiscal = ProdutoFiscal.objects.filter(produto_id=produto_id, ativo=True).values().first()
        variacoes = list(ProdutoVariacao.objects.filter(produto_id=produto_id, ativo=True).values())
        substitutos = list(ProdutoSubstituto.objects.filter(produto_id=produto_id, ativo=True).values())
        composicao = list(ProdutoComposicao.objects.filter(produto_pai_id=produto_id, ativo=True).values())
        custos_local = list(ProdutoCustoLocal.objects.filter(produto_id=produto_id).values())
        ultimo_preco = ProdutoHistoricoPreco.objects.filter(produto_id=produto_id).order_by('-data_inicio').values().first()

        return Response({
            'produto': {
                'id': produto.id,
                'codigo': produto.codigo,
                'nome': produto.nome,
                'descricao': produto.descricao,
                'referencia': produto.referencia,
                'sku': produto.sku,
                'ean': produto.ean,
                'unidade_medida': produto.unidade_medida,
                'preco_custo': float(produto.preco_custo or 0),
                'preco_venda': float(produto.preco_venda or 0),
                'estoque_minimo': produto.estoque_minimo,
                'ponto_reposicao': produto.ponto_reposicao,
                'lead_time_dias': produto.lead_time_dias,
            },
            'fiscal': fiscal,
            'variacoes': variacoes,
            'composicao': composicao,
            'substitutos': substitutos,
            'custos_local': custos_local,
            'ultimo_preco': ultimo_preco,
        })
