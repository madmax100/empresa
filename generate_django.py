import psycopg2
from typing import Dict, List, Tuple

def analyze_database_structure():
    try:
        # Conectar ao PostgreSQL
        conn = psycopg2.connect(
            dbname='c3mcopiasdb',
            user='cirilomax',
            password='226cmm100',
            host='localhost',
            port='5432'
        )
        
        cursor = conn.cursor()
        
        # Buscar todas as tabelas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        table_structures = {}
        foreign_keys = {}
        
        # Analisar cada tabela
        for table in tables:
            table_name = table[0]
            
            # Buscar estrutura das colunas
            cursor.execute("""
                SELECT 
                    column_name, 
                    data_type, 
                    character_maximum_length, 
                    is_nullable,
                    column_default,
                    numeric_precision,
                    numeric_scale
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            
            columns = cursor.fetchall()
            table_structures[table_name] = columns
            
            # Buscar chaves estrangeiras
            cursor.execute("""
                SELECT
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = %s;
            """, (table_name,))
            
            fks = cursor.fetchall()
            if fks:
                foreign_keys[table_name] = fks
        
        # Gerar arquivo models.py
        models_code = """from django.db import models

"""
        for table_name, columns in table_structures.items():
            model_name = ''.join(word.title() for word in table_name.split('_'))
            models_code += f"class {model_name}(models.Model):\n"
            
            for col in columns:
                column_name = col[0]
                data_type = col[1]
                max_length = col[2]
                nullable = col[3] == 'YES'
                default = col[4]
                numeric_precision = col[5]
                numeric_scale = col[6]
                
                # Pular coluna id
                if column_name == 'id':
                    continue
                
                # Verificar se é chave estrangeira
                is_fk = False
                fk_reference = None
                if table_name in foreign_keys:
                    for fk in foreign_keys[table_name]:
                        if fk[0] == column_name:
                            is_fk = True
                            fk_reference = fk[1]
                            break
                
                if is_fk:
                    ref_model = ''.join(word.title() for word in fk_reference.split('_'))
                    field_def = f"    {column_name} = models.ForeignKey('{ref_model}', on_delete=models.PROTECT"
                    if nullable:
                        field_def += ", null=True, blank=True"
                    field_def += ")\n"
                    models_code += field_def
                    continue
                
                # Mapear tipos de dados
                if data_type == 'character varying':
                    if column_name == 'estado':
                        field_def = f"    {column_name} = models.CharField(max_length=2"
                    elif column_name == 'modalidade_frete':
                        field_def = f"    {column_name} = models.CharField(max_length=1"
                    else:
                        field_def = f"    {column_name} = models.CharField(max_length={max_length or 255}"
                elif data_type == 'text':
                    field_def = f"    {column_name} = models.TextField("
                elif data_type == 'integer':
                    field_def = f"    {column_name} = models.IntegerField("
                elif data_type == 'numeric':
                    field_def = f"    {column_name} = models.DecimalField(max_digits={numeric_precision or 10}, decimal_places={numeric_scale or 2}"
                elif data_type == 'boolean':
                    field_def = f"    {column_name} = models.BooleanField("
                elif data_type == 'date':
                    field_def = f"    {column_name} = models.DateField("
                elif data_type == 'timestamp without time zone':
                    if column_name == 'data_cadastro':
                        field_def = f"    {column_name} = models.DateTimeField(auto_now_add=True"
                    else:
                        field_def = f"    {column_name} = models.DateTimeField("
                else:
                    field_def = f"    {column_name} = models.CharField(max_length=255"  # Fallback
                
                if nullable:
                    field_def += ", null=True, blank=True"
                
                if default and 'nextval' not in default:
                    if data_type == 'boolean':
                        field_def += f", default={'True' if default.lower() == 'true' else 'False'}"
                    elif data_type == 'numeric':
                        field_def += f", default={float(default)}"
                    else:
                        field_def += f", default='{default}'"
                
                field_def += ")\n"
                models_code += field_def
            
            # Adicionar Meta e __str__
            models_code += f"""
    class Meta:
        db_table = '{table_name}'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

"""
        
        # Gerar arquivo serializers.py
        serializers_code = """from rest_framework import serializers
from .models import *

"""
        for table_name in table_structures.keys():
            model_name = ''.join(word.title() for word in table_name.split('_'))
            serializers_code += f"""class {model_name}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {model_name}
        fields = '__all__'
        
"""
        
        return models_code, serializers_code
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        return None, None
    finally:
        if 'conn' in locals():
            conn.close()

def save_files(models_code, serializers_code):
    try:
        with open('models.py', 'w', encoding='utf-8') as f:
            f.write(models_code)
        print("Arquivo models.py gerado com sucesso!")
        
        with open('serializers.py', 'w', encoding='utf-8') as f:
            f.write(serializers_code)
        print("Arquivo serializers.py gerado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao salvar arquivos: {str(e)}")

if __name__ == "__main__":
    models_code, serializers_code = analyze_database_structure()
    if models_code and serializers_code:
        save_files(models_code, serializers_code)