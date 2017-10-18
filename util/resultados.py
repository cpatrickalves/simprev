# -*- coding: utf-8 -*-
"""

@author: Patrick Alves
"""

def calc_resultados(resultados, dadosLDO):
    
    ###### Obtém resultados da LDO de 2018
    
    # Receita, despesa e PIB da LDO
    rec_ldo = dadosLDO['Tabela_6.2']['Receita']
    desp_ldo = dadosLDO['Tabela_6.2']['Despesa']
    pib_ldo = dadosLDO['Tabela_6.2']['PIB']
    
    # Receita e despesa sobre o PIB da LDO
    rec_ldo_pib = dadosLDO['Tabela_6.2']['Receita / PIB'] * 100
    desp_ldo_pib = dadosLDO['Tabela_6.2']['Despesa / PIB'] * 100
    
    resultados['Receitas/PIB LDO'] = rec_ldo_pib
    resultados['Despesas/PIB LDO'] = desp_ldo_pib
    
    
    ###### Calcula receita e despesa sobre o PIB
        
    rec_pib = resultados['Receitas'] / resultados['PIB']
    desp_pib = resultados['Despesas'] / resultados['PIB']
    
    resultados['Receitas/PIB'] = rec_pib * 100
    resultados['Despesas/PIB'] = desp_pib * 100
    
    ###### Calcula variação em relação a LDO
    
    # Variação na despesa, receita e PIB com relação a LDO de 2018 em %
    erro_receita = 100 * (resultados['Receitas'] - rec_ldo) / rec_ldo
    erro_despesa = 100 * (resultados['Despesas'] - desp_ldo) / desp_ldo
    erro_pib = 100 * (resultados['PIB'] - pib_ldo) / pib_ldo
    
    # Erro na despesa e receita sobre o PIB
    erro_receita_pib = 100 * (resultados['Receitas/PIB'] - rec_ldo_pib) / rec_ldo_pib
    erro_despesa_pib = 100 * (resultados['Despesas/PIB'] - desp_ldo_pib) / desp_ldo_pib

    resultados['Erro Receitas'] = erro_receita
    resultados['Erro Despesas'] = erro_despesa
    resultados['Erro PIB'] = erro_pib
    resultados['Erro Receitas/PIB'] = erro_receita_pib
    resultados['Erro Despesas/PIB'] = erro_despesa_pib
    resultados['Receitas LDO'] = rec_ldo
    resultados['Despesas LDO'] = desp_ldo
    
    
    ###### Cálcula necessidade de Financiamento
    
    necess_fin = resultados['Receitas'] - resultados['Despesas']
    necess_fin_pib =  necess_fin / resultados['PIB']
    
    resultados['NecFinanc'] = necess_fin
    resultados['NecFinanc/PIB'] = necess_fin_pib * 100
    
    
    return resultados

    
    
    