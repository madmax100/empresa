-- Relacionamento entre as tabelas "fornecedores" e "enderecos"
ALTER TABLE fornecedores
ADD CONSTRAINT fk_fornecedores_enderecos
FOREIGN KEY (endereco_id) REFERENCES enderecos(id);

-- Relacionamento entre as tabelas "funcionarios" e "enderecos"
ALTER TABLE funcionarios
ADD CONSTRAINT fk_funcionarios_enderecos
FOREIGN KEY (endereco_id) REFERENCES enderecos(id);

-- Relacionamento entre as tabelas "produtos" e "grupos"
ALTER TABLE produtos
ADD CONSTRAINT fk_produtos_grupos
FOREIGN KEY (grupo_id) REFERENCES grupos(id);

-- Relacionamento entre as tabelas "produtos" e "fornecedores"
ALTER TABLE produtos
ADD CONSTRAINT fk_produtos_fornecedores
FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id);

-- Relacionamento entre as tabelas "contratos" e "categorias_contrato"
ALTER TABLE contratos
ADD CONSTRAINT fk_contratos_categorias
FOREIGN KEY (categoria_id) REFERENCES categorias_contrato(id);

-- Relacionamento entre as tabelas "contratos" e "clientes"
ALTER TABLE contratos
ADD CONSTRAINT fk_contratos_clientes
FOREIGN KEY (cliente_id) REFERENCES clientes(id);

-- Relacionamento entre as tabelas "itens_contrato" e "contratos"
ALTER TABLE itens_contrato
ADD CONSTRAINT fk_itens_contrato_contratos
FOREIGN KEY (contrato_id) REFERENCES contratos(id);

-- Relacionamento entre as tabelas "itens_contrato" e "tecnicos"
ALTER TABLE itens_contrato
ADD CONSTRAINT fk_itens_contrato_tecnicos
FOREIGN KEY (tecnico_id) REFERENCES tecnicos(id);

-- Relacionamento entre as tabelas "conhecimentos_frete" e "transportadoras"
ALTER TABLE conhecimentos_frete
ADD CONSTRAINT fk_conhecimentos_frete_transportadoras
FOREIGN KEY (transportadora_id) REFERENCES transportadoras(id);

-- Relacionamento entre as tabelas "itens_nota_fiscal" e "notas_fiscais"
ALTER TABLE itens_nota_fiscal
ADD CONSTRAINT fk_itens_nota_fiscal_notas_fiscais
FOREIGN KEY (nota_fiscal_id) REFERENCES notas_fiscais(id);

-- Relacionamento entre as tabelas "itens_nota_fiscal" e "produtos"
ALTER TABLE itens_nota_fiscal
ADD CONSTRAINT fk_itens_nota_fiscal_produtos
FOREIGN KEY (produto_id) REFERENCES produtos(id);

-- Relacionamento entre as tabelas "notas_fiscais" e "clientes"
ALTER TABLE notas_fiscais
ADD CONSTRAINT fk_notas_fiscais_clientes
FOREIGN KEY (cliente_id) REFERENCES clientes(id);

-- Relacionamento entre as tabelas "ordens_servico" e "clientes"
ALTER TABLE ordens_servico
ADD CONSTRAINT fk_ordens_servico_clientes
FOREIGN KEY (cliente_id) REFERENCES clientes(id);

-- Relacionamento entre as tabelas "ordens_servico" e "equipamentos"
ALTER TABLE ordens_servico
ADD CONSTRAINT fk_ordens_servico_equipamentos
FOREIGN KEY (equipamento_id) REFERENCES equipamentos(id);

-- Relacionamento entre as tabelas "itens_os" e "ordens_servico"
ALTER TABLE itens_os
ADD CONSTRAINT fk_itens_os_ordens_servico
FOREIGN KEY (ordem_servico_id) REFERENCES ordens_servico(id);

-- Relacionamento entre as tabelas "itens_os" e "produtos"
ALTER TABLE itens_os
ADD CONSTRAINT fk_itens_os_produtos
FOREIGN KEY (produto_id) REFERENCES produtos(id);