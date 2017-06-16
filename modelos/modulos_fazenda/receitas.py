# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
import pandas as pd


# Projeta a receita de acordo com a LDO de 2018
def calc_receitas(salarios, aliquota, periodo):

    # Cria um objeto do tipo Serie com índices iguais a lista período e
    # todos os valores iguais a zero
    receita = pd.Series(0, index=periodo)

    # Para cada sexo e clientela calcula as receitas (Eq. 39)
    for sexo in ['H','M']:
        for clientela in ['Ca', 'Csm']:
            for ano in periodo:
                id_sal = 'MSal' + clientela + 'Urb' + sexo
                receita[ano] += salarios[id_sal][ano].sum()

    # Aplica a alíquota efetiva média
    receita = receita * aliquota

    return receita

    
# Projeta o PIB de acordo com a LDO de 2018
def calc_pib(resultados, salarios, pib_inicial, periodo):
    
    # Cria um objetos do tipo Serie com índices iguais a lista periodo e
    # todos os valores iguais a zero
    pib = pd.Series(0.0, index=periodo)
    tx_cres_pib = pd.Series(0.0, index=periodo)
    MSal_total = pd.Series(0.0, index=periodo)

    # Calcula os valores totais de Massa Salarial da Pop Ocupada (Eq. 41)
    for sexo in ['H','M']:
        for clientela in ['Urb', 'Rur']:
            for ano in periodo:
                id_sal = 'MSalPopOcup'+ clientela + sexo
                MSal_total[ano] += salarios[id_sal][ano].sum()


    # Calcula a taxa de Crescimento da Massa Salarial (Eq. 42)
    for ano in periodo[1:]:  # pula o primeiro ano
        tx_cres_pib[ano] = (MSal_total[ano] - MSal_total[ano-1])/MSal_total[ano-1]


    # Faz a Projeção do PIB (Eq. 43)
    pib[periodo[0]] = pib_inicial
    for ano in periodo[1:]:
        pib[ano] = pib[ano-1] * (1 + tx_cres_pib[ano])


    # Salva as variáveis em um dicionário
    resultados['MSal_total'] = MSal_total
    resultados['tx_cres_pib'] = tx_cres_pib
    resultados['PIB'] = pib

    return resultados

    
