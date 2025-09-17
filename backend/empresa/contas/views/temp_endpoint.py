    @action(detail=False, methods=['get'])
    def produtos_resetados(self, request):
        """
        Retorna os produtos que tiveram reset de estoque no último ano.
        Reset é identificado por movimentações com documento_referencia='000000'.
        """
        try:
            # Parâmetros da requisição
            meses = int(request.query_params.get('meses', '12'))  # Padrão: último ano
            limite = int(request.query_params.get('limite', '100'))
            offset = int(request.query_params.get('offset', '0'))
            ordem = request.query_params.get('ordem', 'data_reset')
            reverso = request.query_params.get('reverso', 'true').lower() == 'true'

            # Data limite para buscar resets (últimos X meses)
            data_limite = timezone.now().date() - timedelta(days=meses * 30)

            # Buscar movimentações de reset no período
            resets_query = MovimentacoesEstoque.objects.filter(
                documento_referencia='000000',
                data_movimentacao__gte=data_limite
            ).select_related('produto')

            # Agrupar por produto e pegar o reset mais recente de cada um
            produtos_resetados = {}
            
            for reset in resets_query:
                produto_id = reset.produto_id
                
                if produto_id not in produtos_resetados or reset.data_movimentacao > produtos_resetados[produto_id]['data_reset']:
                    try:
                        produto = reset.produto if reset.produto else Produtos.objects.get(id=produto_id)
                        grupo = produto.grupo_id
                        grupo_nome = ''
                        
                        if grupo:
                            try:
                                grupo_obj = Grupos.objects.get(id=grupo)
                                grupo_nome = grupo_obj.nome
                            except Grupos.DoesNotExist:
                                grupo_nome = f'Grupo {grupo}'
                        
                        produtos_resetados[produto_id] = {
                            'produto_id': produto_id,
                            'codigo': produto.codigo,
                            'nome': produto.nome,
                            'grupo_id': grupo,
                            'grupo_nome': grupo_nome or 'Sem Grupo',
                            'data_reset': reset.data_movimentacao.date(),
                            'quantidade_reset': float(reset.quantidade or 0),
                            'estoque_atual': float(produto.estoque_atual or 0),
                            'preco_custo': float(produto.preco_custo or 0),
                            'valor_atual': float((produto.estoque_atual or 0) * (produto.preco_custo or 0)),
                            'ativo': produto.ativo
                        }
                    except Produtos.DoesNotExist:
                        continue

            # Converter para lista
            produtos_list = list(produtos_resetados.values())

            # Ordenação
            reverse_order = reverso
            if ordem == 'data_reset':
                produtos_list.sort(key=lambda x: x['data_reset'], reverse=reverse_order)
            elif ordem == 'codigo':
                produtos_list.sort(key=lambda x: x['codigo'] or '', reverse=reverse_order)
            elif ordem == 'nome':
                produtos_list.sort(key=lambda x: x['nome'] or '', reverse=reverse_order)
            elif ordem == 'grupo':
                produtos_list.sort(key=lambda x: x['grupo_nome'], reverse=reverse_order)
            elif ordem == 'estoque_atual':
                produtos_list.sort(key=lambda x: x['estoque_atual'], reverse=reverse_order)
            elif ordem == 'valor_atual':
                produtos_list.sort(key=lambda x: x['valor_atual'], reverse=reverse_order)

            # Paginação
            total_produtos = len(produtos_list)
            produtos_paginados = produtos_list[offset:offset + limite]

            # Estatísticas
            total_valor_resetado = sum(p['valor_atual'] for p in produtos_list)
            produtos_ativos = sum(1 for p in produtos_list if p['ativo'])
            produtos_com_estoque = sum(1 for p in produtos_list if p['estoque_atual'] > 0)

            # Agrupar por mês de reset
            resets_por_mes = defaultdict(int)
            for produto in produtos_list:
                mes_ano = produto['data_reset'].strftime('%Y-%m')
                resets_por_mes[mes_ano] += 1

            return Response({
                'results': produtos_paginados,
                'estatisticas': {
                    'total_produtos_resetados': total_produtos,
                    'produtos_ativos': produtos_ativos,
                    'produtos_com_estoque_atual': produtos_com_estoque,
                    'valor_total_estoque_atual': total_valor_resetado,
                    'periodo_analise_meses': meses,
                    'data_limite': data_limite.strftime('%Y-%m-%d'),
                    'resets_por_mes': dict(resets_por_mes)
                },
                'parametros': {
                    'limite': limite,
                    'offset': offset,
                    'ordem': ordem,
                    'reverso': reverso,
                    'total_registros': total_produtos,
                    'tem_proximo': offset + limite < total_produtos,
                    'tem_anterior': offset > 0
                }
            })

        except Exception as e:
            return Response(
                {'error': f'Erro interno no servidor: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )