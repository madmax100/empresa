#!/usr/bin/env node
/**
 * Script de Debug - Endpoints Financeiros
 * ======================================
 * 
 * Testa os endpoints /contas/contas_receber/dashboard/ e /contas/contas_pagar/dashboard/
 * para verificar a estrutura real dos dados, especialmente os campos de data de pagamento.
 */

const http = require('http');

// Configuração
const BASE_URL = 'http://127.0.0.1:8000';
const ENDPOINTS = [
    '/contas/contas_receber/dashboard/',
    '/contas/contas_pagar/dashboard/'
];

/**
 * Faz requisição HTTP GET
 */
function makeRequest(url) {
    return new Promise((resolve, reject) => {
        const req = http.get(url, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                try {
                    const jsonData = JSON.parse(data);
                    resolve({
                        status: res.statusCode,
                        data: jsonData
                    });
                } catch (e) {
                    resolve({
                        status: res.statusCode,
                        data: data,
                        parseError: e.message
                    });
                }
            });
        });
        
        req.on('error', (err) => {
            reject(err);
        });
        
        req.setTimeout(10000, () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });
    });
}

/**
 * Analisa a estrutura de um objeto, focando em campos de data
 */
function analyzeDataStructure(obj, path = '', depth = 0) {
    if (depth > 3) return; // Limitar profundidade
    
    const indent = '  '.repeat(depth);
    
    if (Array.isArray(obj)) {
        console.log(`${indent}${path}: Array[${obj.length}]`);
        if (obj.length > 0) {
            console.log(`${indent}  Exemplo do primeiro item:`);
            analyzeDataStructure(obj[0], `${path}[0]`, depth + 1);
        }
    } else if (obj && typeof obj === 'object') {
        console.log(`${indent}${path}: Object`);
        Object.keys(obj).forEach(key => {
            const value = obj[key];
            const newPath = path ? `${path}.${key}` : key;
            
            // Destacar campos que podem ser data de pagamento
            if (key.toLowerCase().includes('pagamento') || 
                key.toLowerCase().includes('quitacao') || 
                key.toLowerCase().includes('data')) {
                console.log(`${indent}  🔍 ${key}: ${JSON.stringify(value)} (CAMPO DE DATA/PAGAMENTO)`);
            } else if (typeof value === 'string' || typeof value === 'number' || value === null) {
                console.log(`${indent}  ${key}: ${JSON.stringify(value)}`);
            } else {
                analyzeDataStructure(value, newPath, depth + 1);
            }
        });
    } else {
        console.log(`${indent}${path}: ${JSON.stringify(obj)}`);
    }
}

/**
 * Testa um endpoint específico
 */
async function testEndpoint(endpoint) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`🔍 TESTANDO: ${endpoint}`);
    console.log(`${'='.repeat(60)}`);
    
    const url = `${BASE_URL}${endpoint}`;
    
    try {
        console.log(`📡 Fazendo requisição para: ${url}`);
        const response = await makeRequest(url);
        
        console.log(`📊 Status Code: ${response.status}`);
        
        if (response.parseError) {
            console.log(`❌ Erro ao fazer parse do JSON: ${response.parseError}`);
            console.log(`📄 Resposta raw:`);
            console.log(response.data.substring(0, 500) + (response.data.length > 500 ? '...' : ''));
            return;
        }
        
        if (response.status !== 200) {
            console.log(`❌ Erro HTTP ${response.status}`);
            console.log(`📄 Resposta:`, response.data);
            return;
        }
        
        console.log(`✅ Requisição bem-sucedida!`);
        console.log(`\n📋 ESTRUTURA DOS DADOS:`);
        analyzeDataStructure(response.data);
        
        // Análise específica para campos de pagamento
        console.log(`\n🔍 ANÁLISE DE CAMPOS DE PAGAMENTO:`);
        
        if (response.data && typeof response.data === 'object') {
            // Procurar em todas as propriedades que podem conter arrays de movimentos
            Object.keys(response.data).forEach(key => {
                const value = response.data[key];
                if (Array.isArray(value) && value.length > 0) {
                    console.log(`\n  📦 Array "${key}" (${value.length} itens):`);
                    
                    // Analisar primeiro item para ver estrutura
                    const firstItem = value[0];
                    if (firstItem && typeof firstItem === 'object') {
                        console.log(`    Campos do primeiro item:`);
                        Object.keys(firstItem).forEach(itemKey => {
                            const itemValue = firstItem[itemKey];
                            if (itemKey.toLowerCase().includes('pagamento') || 
                                itemKey.toLowerCase().includes('quitacao') || 
                                itemKey.toLowerCase().includes('data')) {
                                console.log(`      🎯 ${itemKey}: ${JSON.stringify(itemValue)} (POSSÍVEL CAMPO DE PAGAMENTO)`);
                            }
                        });
                        
                        // Verificar se existem campos específicos que procuramos
                        const camposPagamento = ['data_pagamento', 'dt_pagamento', 'data_quitacao', 'dt_quitacao'];
                        camposPagamento.forEach(campo => {
                            if (firstItem.hasOwnProperty(campo)) {
                                console.log(`      ✅ Campo "${campo}" encontrado: ${JSON.stringify(firstItem[campo])}`);
                            } else {
                                console.log(`      ❌ Campo "${campo}" NÃO encontrado`);
                            }
                        });
                    }
                }
            });
        }
        
    } catch (error) {
        console.log(`❌ Erro na requisição: ${error.message}`);
    }
}

/**
 * Função principal
 */
async function main() {
    console.log(`🚀 INICIANDO TESTE DOS ENDPOINTS FINANCEIROS`);
    console.log(`📅 Data/Hora: ${new Date().toLocaleString('pt-BR')}`);
    console.log(`🔗 Base URL: ${BASE_URL}`);
    
    for (const endpoint of ENDPOINTS) {
        await testEndpoint(endpoint);
        
        // Pequena pausa entre requisições
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    console.log(`\n${'='.repeat(60)}`);
    console.log(`🏁 TESTE CONCLUÍDO`);
    console.log(`${'='.repeat(60)}`);
    
    console.log(`\n💡 PRÓXIMOS PASSOS:`);
    console.log(`1. Verificar se os campos de data de pagamento estão presentes`);
    console.log(`2. Confirmar os nomes corretos dos campos no backend`);
    console.log(`3. Atualizar o mapeamento no financialService.ts`);
    console.log(`4. Testar novamente no frontend`);
}

// Executar
main().catch(console.error);
