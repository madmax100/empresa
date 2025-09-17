# Endpoint para produtos resetados
# Adicionar este código ao estoque_views.py

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
            lista_produtos = list(produtos_resetados.values())
            
            # Ordenação
            if ordem == 'data_reset':
                lista_produtos.sort(key=lambda x: x['data_reset'], reverse=reverso)
            elif ordem == 'nome':
                lista_produtos.sort(key=lambda x: x['nome'] or '', reverse=reverso)
            elif ordem == 'codigo':
                lista_produtos.sort(key=lambda x: x['codigo'] or 0, reverse=reverso)
            elif ordem == 'valor_atual':
                lista_produtos.sort(key=lambda x: x['valor_atual'], reverse=reverso)
            elif ordem == 'estoque_atual':
                lista_produtos.sort(key=lambda x: x['estoque_atual'], reverse=reverso)
            elif ordem == 'grupo_nome':
                lista_produtos.sort(key=lambda x: x['grupo_nome'], reverse=reverso)

            # Paginação
            total_registros = len(lista_produtos)
            inicio = offset
            fim = offset + limite
            produtos_paginados = lista_produtos[inicio:fim]

            # Estatísticas
            produtos_ativos = sum(1 for p in lista_produtos if p['ativo'])
            produtos_com_estoque = sum(1 for p in lista_produtos if p['estoque_atual'] > 0)
            valor_total = sum(p['valor_atual'] for p in lista_produtos)

            # Agrupar por mês
            resets_por_mes = defaultdict(int)
            for produto in lista_produtos:
                mes_ano = produto['data_reset'].strftime('%Y-%m')
                resets_por_mes[mes_ano] += 1

            return Response({
                'success': True,
                'data': produtos_paginados,
                'meta': {
                    'total_registros': total_registros,
                    'limite': limite,
                    'offset': offset,
                    'tem_proximo': offset + limite < total_registros,
                    'tem_anterior': offset > 0
                },
                'estatisticas': {
                    'total_produtos_resetados': total_registros,
                    'produtos_ativos': produtos_ativos,
                    'produtos_com_estoque': produtos_com_estoque,
                    'valor_total_estoque': float(valor_total),
                    'data_limite': data_limite.strftime('%Y-%m-%d'),
                    'resets_por_mes': dict(resets_por_mes)
                }
            })

        except Exception as e:
            return Response(
                {'error': f'Erro interno no servidor: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )