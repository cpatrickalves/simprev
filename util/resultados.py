# -*- coding: utf-8 -*-
"""

@author: Patrick Alves
"""

def calc_resultados(resultados, dadosLDO):
            
    rec_ldo = dadosLDO['Tabela_6.2']['Receita']
    desp_ldo = dadosLDO['Tabela_6.2']['Despesa']
    
    # Erro na despesa e receita com relação a LDO de 2018 em %
    erro_receita = 100 * (resultados['Receitas'] - rec_ldo) / rec_ldo
    erro_despesa = 100 * (resultados['Despesas'] - desp_ldo) / desp_ldo

    resultados['Erro Receita'] = erro_receita
    resultados['Erro Despesa'] = erro_despesa
    resultados['Receitas LDO'] = rec_ldo
    resultados['Despesas LDO'] = desp_ldo
    
    return resultados

    
    
    