from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Q, F
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from ..models.access import (
    ItensNfEntrada,
    ItensNfSaida,
    MovimentacoesEstoque,
    Produtos,
    TiposMovimentacaoEstoque,
    EstoqueInicial
)
from datetime import datetime, date

class ComparativoEstoqueView(APIView):
    """
    Endpoint para comparar a variação de estoque calculada por dois métodos:
    1. Notas Fiscais (ItensNfEntrada/Saida)
    2. Movimentações de Estoque (MovimentacoesEstoque)
    """

    def get(self, request):
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
        # Verifique se é uma solicitação de detalhe
        acao = request.query_params.get('acao')
        tipo_detalhe = request.query_params.get('tipo')
        produto_id = request.query_params.get('produto_id')

        if acao == 'detalhe' and produto_id and tipo_detalhe:
            return self.get_detalhe(data_inicio, data_fim, produto_id, tipo_detalhe)

        # =========================================================================
        # 1. MÉTODO FISCAL (Notas Fiscais)
        # =========================================================================
        
        # Entradas (NF Entrada)
        # Filtrando pela data de ENTRADA da nota (quando efetivamente entra no estoque)
        # Entradas (NF Entrada)
        # Filtrando pela data de ENTRADA da nota (quando efetivamente entra no estoque)
        entradas_nf = ItensNfEntrada.objects.filter(
            nota_fiscal__data_entrada__range=[data_inicio, data_fim]
        ).values('produto_id').annotate(
            total_qtd=Sum('quantidade'),
            total_val=Sum('valor_total')
        )

        # Saídas (NF Saída)
        saidas_nf = ItensNfSaida.objects.filter(
            nota_fiscal__data__range=[data_inicio, data_fim]
        ).values('produto_id').annotate(
            total_qtd=Sum('quantidade'),
            total_val=Sum('valor_total')
        )

        # =========================================================================
        # 1.1 CÁLCULO DE CUSTOS (PREÇO MÉDIO)
        # =========================================================================
        
        # Preço Médio de Entrada no Período (Fiscal)
        precos_medios = {}
        
        # Agrupa entradas fiscais por produto para calcular preço médio ponderado
        # Reutilizando entradas_nf que já tem total_qtd e total_val
        for item in entradas_nf:
            pid = item['produto_id']
            qtd = item['total_qtd'] or Decimal(0)
            val = item['total_val'] or Decimal(0)
            if pid and qtd > 0:
                precos_medios[pid] = val / qtd

        # Fallback: Preço de Custo atual do Produto (para quem não teve entrada no período)
        # Necessário pegar IDs de saídas também para garantir que temos custo para todos
        ids_movimentados = set(item['produto_id'] for item in entradas_nf) | set(item['produto_id'] for item in saidas_nf)
        
        produtos_custo = Produtos.objects.filter(id__in=ids_movimentados).values('id', 'preco_custo')
        produtos_custo_map = {p['id']: p['preco_custo'] or 0 for p in produtos_custo}
        
        for pid in ids_movimentados:
            if pid not in precos_medios:
                precos_medios[pid] = produtos_custo_map.get(pid, Decimal(0))

        dados_fiscal = defaultdict(lambda: {
            'entrada': Decimal(0), 'saida': Decimal(0),
            'val_entrada': Decimal(0), 'val_saida': Decimal(0)
        })

        for item in entradas_nf:
             if item['produto_id']:
                dados_fiscal[item['produto_id']]['entrada'] += item['total_qtd'] or Decimal(0)
                dados_fiscal[item['produto_id']]['val_entrada'] += item['total_val'] or Decimal(0)

        for item in saidas_nf:
            pid = item['produto_id']
            if pid:
                qtd = item['total_qtd'] or Decimal(0)
                dados_fiscal[pid]['saida'] += qtd
                
                # UPDATE: Valorar saída pelo Custo Médio, não pelo Valor da Venda
                # val_original = item['total_val'] or Decimal(0) 
                custo_medio = precos_medios.get(pid, Decimal(0))
                dados_fiscal[pid]['val_saida'] += qtd * custo_medio

        # =========================================================================
        # 2. MÉTODO FÍSICO (Movimentações de Estoque)
        # =========================================================================

        # Buscar movimentações
        movs = MovimentacoesEstoque.objects.filter(
            data_movimentacao__date__range=[data_inicio, data_fim]
        ).select_related('tipo_movimentacao').values(
            'produto_id', 
            'tipo_movimentacao__tipo', 
            'quantidade'
        )

        dados_fisico = defaultdict(lambda: {'entrada': Decimal(0), 'saida': Decimal(0)})

        for m in movs:
            if not m['produto_id']: continue
            
            # Tipo: E=Entrada, S=Saída (Assumindo padrão comum, ajustar se necessário)
            qtd = m['quantidade'] or Decimal(0)
            tipo = m['tipo_movimentacao__tipo']
            
            if tipo == 'E':
                dados_fisico[m['produto_id']]['entrada'] += qtd
            elif tipo == 'S':
                dados_fisico[m['produto_id']]['saida'] += qtd

        # =========================================================================
        # 3. SALDO INICIAL FÍSICO (EstoqueInicial + Movimentações Anteriores)
        # =========================================================================
        
        # 3.1 Busca Estoque Inicial Base (01/01/2025)
        data_base_inicial = date(2025, 1, 1)

        estoque_base = {
            e.produto_id: e.quantidade_inicial 
            for e in EstoqueInicial.objects.all()
        }
        
        # 3.2 Movimentações anteriores ao período (01/01/2025 até data_inicio - 1 dia)
        movimentos_anteriores = MovimentacoesEstoque.objects.filter(
            data_movimentacao__gte=date(2025, 1, 1),
            data_movimentacao__lt=data_inicio
        ).values('produto_id', 'tipo_movimentacao__tipo').annotate(
            total=Sum('quantidade')
        )

        saldo_anterior_calculado = defaultdict(Decimal)
        
        # Inicia com o base
        for pid, qtd in estoque_base.items():
            saldo_anterior_calculado[pid] = qtd
            
        # Aplica movimentos intermediários
        for mov in movimentos_anteriores:
            pid = mov['produto_id']
            tipo = mov['tipo_movimentacao__tipo']
            qtd = mov['total'] or 0
            
            if tipo == 'E':
                saldo_anterior_calculado[pid] += qtd
            elif tipo == 'S':
                saldo_anterior_calculado[pid] -= qtd

        # =========================================================================
        # 5. CONSOLIDAÇÃO E COMPARATIVO
        # =========================================================================

        all_products = set(dados_fiscal.keys()) | set(dados_fisico.keys())
        
        # Buscar nomes dos produtos para exibição
        produtos = Produtos.objects.filter(id__in=all_products).values('id', 'codigo', 'nome')
        prod_map = {p['id']: p for p in produtos}

        comparativo = []

        for pid in all_products:
            prod = prod_map.get(pid, {'codigo': '???', 'nome': 'Produto Desconhecido'})
            
            # Dados Fiscais
            fisc = dados_fiscal.get(pid, {
                'entrada': Decimal(0), 'saida': Decimal(0),
                'val_entrada': Decimal(0), 'val_saida': Decimal(0)
            })
            
            # Dados Físicos
            fis = dados_fisico.get(pid, {'entrada': Decimal(0), 'saida': Decimal(0)})
            
            # Saldo Inicial e Final Físico
            saldo_ini = saldo_anterior_calculado.get(pid, Decimal(0))
            saldo_fim = saldo_ini + fis['entrada'] - fis['saida']

            # Valoração Físico (usando preço médio ou custo)
            custo_ref = precos_medios.get(pid, Decimal(0))
            val_fis_ent = fis['entrada'] * custo_ref
            val_fis_sai = fis['saida'] * custo_ref
            val_fis_saldo_ini = saldo_ini * custo_ref
            val_fis_saldo_fim = saldo_fim * custo_ref

            comparativo.append({
                'produto_id': pid,
                'codigo': prod['codigo'],
                'nome': prod['nome'],
                'fiscal': {
                    'entrada': float(fisc['entrada']),
                    'saida': float(fisc['saida']),
                    'saldo_fluxo': float(fisc['entrada'] - fisc['saida']),
                    'valor_entrada': float(fisc['val_entrada']),
                    'valor_saida': float(fisc['val_saida']),
                    'valor_saldo_fluxo': float(fisc['val_entrada'] - fisc['val_saida'])
                },
                'fisico': {
                    'saldo_inicial': float(saldo_ini),
                    'entrada': float(fis['entrada']),
                    'saida': float(fis['saida']),
                    'saldo_fluxo': float(fis['entrada'] - fis['saida']),
                    'saldo_final': float(saldo_fim),
                    'valor_entrada': float(val_fis_ent),
                    'valor_saida': float(val_fis_sai),
                    'valor_saldo_inicial': float(val_fis_saldo_ini),
                    'valor_saldo_final': float(val_fis_saldo_fim)
                },
                'diferenca': {
                    'entrada': float(fisc['entrada'] - fis['entrada']),
                    'saida': float(fisc['saida'] - fis['saida']),
                    'saldo_fluxo': float((fisc['entrada'] - fisc['saida']) - (fis['entrada'] - fis['saida']))
                }
            })
            
        # Ordenar: prioridade para divergências de fluxo, depois por saldo final
        comparativo.sort(key=lambda x: (abs(x['diferenca']['saldo_fluxo']), x['fisico']['saldo_final']), reverse=True)

        return Response({
            'periodo': {
                'inicio': data_inicio.strftime('%Y-%m-%d'), 
                'fim': data_fim.strftime('%Y-%m-%d')
            },
            'comparativo': comparativo
        })

    def get_detalhe(self, data_inicio, data_fim, produto_id, tipo):
        """
        Retorna os registros detalhados que compõem o saldo/movimentação.
        """
        # Formatter para datas, pode ser movido para utilitário se reutilizado
        fmt = '%d/%m/%Y'
        
        if tipo == 'fiscal_entrada':
            itens = ItensNfEntrada.objects.filter(
                nota_fiscal__data_entrada__range=[data_inicio, data_fim],
                produto_id=produto_id
            ).select_related('nota_fiscal', 'nota_fiscal__fornecedor').order_by('nota_fiscal__data_entrada')
            
            dados = []
            for item in itens:
                dados.append({
                    'data': item.nota_fiscal.data_entrada.strftime(fmt) if item.nota_fiscal.data_entrada else '-',
                    'documento': f"NF {item.nota_fiscal.numero_nota} ({item.nota_fiscal.serie_nota or ''})",
                    'parceiro': item.nota_fiscal.fornecedor.nome if item.nota_fiscal.fornecedor else 'Fornecedor Desconhecido',
                    'quantidade': float(item.quantidade or 0),
                    'valor_unitario': float(item.valor_unitario or 0),
                    'valor_total': float(item.valor_total or 0),
                })
            return Response(dados)

        elif tipo == 'fiscal_saida':
            itens = ItensNfSaida.objects.filter(
                nota_fiscal__data__range=[data_inicio, data_fim],
                produto_id=produto_id
            ).select_related('nota_fiscal', 'nota_fiscal__cliente').order_by('nota_fiscal__data')
            
            dados = []
            for item in itens:
                dados.append({
                    'data': item.nota_fiscal.data.strftime(fmt) if item.nota_fiscal.data else '-',
                    'documento': f"NFS {item.nota_fiscal.numero_nota}",
                    'parceiro': item.nota_fiscal.cliente.nome if item.nota_fiscal.cliente else 'Cliente Desconhecido',
                    'quantidade': float(item.quantidade or 0),
                    'valor_unitario': float(item.valor_unitario or 0),
                    'valor_total': float(item.valor_total or 0),
                })
            return Response(dados)

        elif tipo == 'fisico_entrada':
            movs = MovimentacoesEstoque.objects.filter(
                data_movimentacao__date__range=[data_inicio, data_fim],
                produto_id=produto_id,
                tipo_movimentacao__tipo='E'
            ).select_related('tipo_movimentacao').order_by('data_movimentacao')
            
            dados = []
            for m in movs:
                dados.append({
                    'data': m.data_movimentacao.strftime(fmt),
                    'documento': m.documento_referencia or '-',
                    'parceiro': m.tipo_movimentacao.descricao if m.tipo_movimentacao else 'Entrada Manual/Outra',
                    'quantidade': float(m.quantidade or 0),
                    'valor_unitario': float(m.custo_unitario or 0), # Aproximado
                    'valor_total': float(m.valor_total or 0),
                })
            return Response(dados)

        elif tipo == 'fisico_saida':
            movs = MovimentacoesEstoque.objects.filter(
                data_movimentacao__date__range=[data_inicio, data_fim],
                produto_id=produto_id,
                tipo_movimentacao__tipo='S'
            ).select_related('tipo_movimentacao').order_by('data_movimentacao')

            dados = []
            for m in movs:
                dados.append({
                    'data': m.data_movimentacao.strftime(fmt),
                    'documento': m.documento_referencia or '-',
                    'parceiro': m.tipo_movimentacao.descricao if m.tipo_movimentacao else 'Saída Manual/Outra',
                    'quantidade': float(m.quantidade or 0),
                    'valor_unitario': float(m.custo_unitario or 0),
                    'valor_total': float(m.valor_total or 0),
                })
            return Response(dados)

        return Response([])
