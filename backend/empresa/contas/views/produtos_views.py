from decimal import Decimal

from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.access import (
    PoliticaDesconto,
    ProdutoComposicao,
    ProdutoConversaoUnidade,
    Produtos,
    TabelaPrecoItem,
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
