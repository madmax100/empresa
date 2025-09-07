// Teste específico para verificar filtros por data de pagamento
const axios = require('axios');

async function testarFiltroDataPagamento() {
    try {
        console.log('🔍 Testando filtros por data de pagamento...');
        
        const params = {
            data_inicio: '2025-08-01',
            data_fim: '2025-09-30',
            filtrar_por_data_pagamento: true,
            apenas_contas_pagas: true
        };
        
        console.log('📤 Enviando parâmetros:', params);
        
        // Testar contas a receber
        console.log('\n🟢 === TESTANDO CONTAS A RECEBER ===');
        const recebResp = await axios.get('http://127.0.0.1:8000/contas/contas_receber/dashboard/', { params });
        console.log('📊 Status resposta receber:', recebResp.status);
        console.log('📊 Títulos pagos receber:', recebResp.data?.titulos_pagos_periodo?.length || 0);
        
        if (recebResp.data?.titulos_pagos_periodo?.length > 0) {
            const exemploPago = recebResp.data.titulos_pagos_periodo[0];
            console.log('📋 Exemplo título pago (receber):', {
                id: exemploPago.id,
                data_pagamento: exemploPago.data_pagamento,
                vencimento: exemploPago.vencimento,
                valor: exemploPago.valor,
                status: exemploPago.status
            });
        }
        
        // Testar contas a pagar
        console.log('\n🔴 === TESTANDO CONTAS A PAGAR ===');
        const pagarResp = await axios.get('http://127.0.0.1:8000/contas/contas_pagar/dashboard/', { params });
        console.log('📊 Status resposta pagar:', pagarResp.status);
        console.log('📊 Títulos pagos pagar:', pagarResp.data?.titulos_pagos_periodo?.length || 0);
        
        if (pagarResp.data?.titulos_pagos_periodo?.length > 0) {
            const exemploPago = pagarResp.data.titulos_pagos_periodo[0];
            console.log('📋 Exemplo título pago (pagar):', {
                id: exemploPago.id,
                data_pagamento: exemploPago.data_pagamento,
                vencimento: exemploPago.vencimento,
                valor: exemploPago.valor,
                status: exemploPago.status
            });
        }
        
        // Verificar se há títulos com data de pagamento no período
        console.log('\n🎯 === VERIFICAÇÃO DE PERÍODO ===');
        const dataInicio = new Date('2025-08-01');
        const dataFim = new Date('2025-09-30');
        
        let titulosNoPeriodo = 0;
        let titulosForaPeriodo = 0;
        
        // Verificar contas a receber
        if (recebResp.data?.titulos_pagos_periodo) {
            recebResp.data.titulos_pagos_periodo.forEach(titulo => {
                if (titulo.data_pagamento) {
                    const dataPagamento = new Date(titulo.data_pagamento);
                    if (dataPagamento >= dataInicio && dataPagamento <= dataFim) {
                        titulosNoPeriodo++;
                    } else {
                        titulosForaPeriodo++;
                        console.log(`❌ Título FORA do período: ${titulo.id} - ${titulo.data_pagamento}`);
                    }
                }
            });
        }
        
        // Verificar contas a pagar
        if (pagarResp.data?.titulos_pagos_periodo) {
            pagarResp.data.titulos_pagos_periodo.forEach(titulo => {
                if (titulo.data_pagamento) {
                    const dataPagamento = new Date(titulo.data_pagamento);
                    if (dataPagamento >= dataInicio && dataPagamento <= dataFim) {
                        titulosNoPeriodo++;
                    } else {
                        titulosForaPeriodo++;
                        console.log(`❌ Título FORA do período: ${titulo.id} - ${titulo.data_pagamento}`);
                    }
                }
            });
        }
        
        console.log(`\n📊 RESULTADO:`);
        console.log(`✅ Títulos NO período (ago-set 2025): ${titulosNoPeriodo}`);
        console.log(`❌ Títulos FORA do período: ${titulosForaPeriodo}`);
        
        if (titulosForaPeriodo > 0) {
            console.log('🚨 PROBLEMA: Backend não está filtrando por data de pagamento!');
        } else {
            console.log('✅ SUCCESS: Backend está filtrando corretamente por data de pagamento!');
        }
        
    } catch (error) {
        console.error('❌ Erro ao testar filtros:', error.message);
    }
}

testarFiltroDataPagamento();
