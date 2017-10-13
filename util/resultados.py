# -*- coding: utf-8 -*-
"""

@author: Patrick Alves
"""

def calc_resultados(resultados, dadosLDO):
    
    ###### Calcula erro com relação a LDO ######
    
    rec_ldo = dadosLDO['Tabela_6.2']['Receita']
    desp_ldo = dadosLDO['Tabela_6.2']['Despesa']
    
    # Erro na despesa e receita com relação a LDO de 2018 em %
    erro_receita = 100 * (resultados['Receitas'] - rec_ldo) / rec_ldo
    erro_despesa = 100 * (resultados['Despesas'] - desp_ldo) / desp_ldo

    resultados['Erro Receita'] = erro_receita
    resultados['Erro Despesa'] = erro_despesa
    resultados['Receitas LDO'] = rec_ldo
    resultados['Despesas LDO'] = desp_ldo
    
    
    ###### Calcula receita e despesa sobre o PIB
        
    rec_pib = resultados['Receitas'] / resultados['PIB']
    desp_pib = resultados['Despesas'] / resultados['PIB']
    
    resultados['Receitas/PIB'] = rec_pib * 100
    resultados['Despesas/PIB'] = desp_pib * 100
    
    
    ###### Cálcula necessidade de Financiamento
    
    necess_fin = resultados['Receitas'] - resultados['Despesas']
    necess_fin_pib =  necess_fin / resultados['PIB']
    
    resultados['NecFinanc'] = necess_fin
    resultados['NecFinanc/PIB'] = necess_fin_pib * 100
    
    
    return resultados

    
    
    