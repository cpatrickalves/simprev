# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
import pandas as pd


# Projeta a receita de acordo com a LDO de 2018
def calc_receitas(salarios, aliquota, periodo):

    # Dicionário que armazenas os resultados
    resultados = {}
    
    # Cria um objeto do tipo Serie com índices iguais aos descritos na lista período e
    # todos os valores iguais a zero
    mSalContrTotal = pd.Series(0, index=periodo)
    receita = pd.Series(0, index=periodo)
        
    # Para cada sexo e clientela calcula as receitas (Eq. 39)
    # O Fator de Anulização foi adicionado conforme planilhas do MF
    for ano in periodo:
        for sexo in ['H','M']:
            for clientela in ['Ca', 'Csm']:            
                id_sal = 'MSal' + clientela + 'Urb' + sexo
                mSalContrTotal[ano] += salarios[id_sal][ano].sum() 

    # Aplica a alíquota efetiva média
    receita = mSalContrTotal * (aliquota/100)

    resultados['Receitas'] = receita
    resultados['MSalContrib'] = mSalContrTotal

    return resultados


# Projeta o PIB de acordo com a LDO de 2018 conforme Equações 41, 42 e 43
def calc_pib_MF(resultados, salarios, PIBs, periodo):
    
    # Cria um objetos do tipo Serie com índices iguais a lista periodo e
    # todos os valores iguais a zero
    pib = pd.Series(PIBs, index=[2014,2015,2016])
    tx_cres_pib = pd.Series(0.0, index=periodo)
    MSal_total = pd.Series(0.0, index=periodo)      # PopOcupada

    # Calcula os valores totais de Massa Salarial da Pop Ocupada (Eq. 41)
    for ano in periodo:
        for sexo in ['H','M']:
            for clientela in ['Piso', 'Acim']:                      
                id_msal = 'MSalOcupUrb' + clientela + sexo
                MSal_total[ano] += salarios[id_msal][ano].sum()

    # Calcula a taxa de Crescimento da Massa Salarial (Eq. 42)
    for ano in periodo[1:]:  # pula o primeiro ano
        tx_cres_pib[ano] = MSal_total[ano]/MSal_total[ano-1] - 1

    # Faz a Projeção do PIB (Eq. 43)    
    # 2017-2060
    for ano in periodo[2:]:
        pib[ano] = pib[ano-1] * (1 + tx_cres_pib[ano])

    # Salva as variáveis em um dicionário
    resultados['MSalPopOcup'] = MSal_total
    resultados['tx_cres_pib'] = tx_cres_pib
    resultados['PIB'] = pib

    return resultados

    
# Projeta o PIB de acordo com a LDO de 2018 conforme Equações 41, 42 e 43
def calc_pib_ldo2018(resultados, salarios, PIBs, periodo):
    
    # Cria um objetos do tipo Serie com índices iguais a lista periodo e
    # todos os valores iguais a zero
    pib = pd.Series(PIBs, index=[2014,2015,2016])
    tx_cres_pib = pd.Series(0.0, index=periodo)
    MSal_total = pd.Series(0.0, index=periodo)      # PopOcupada

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
    # 2017-2060
    for ano in periodo[2:]:
        pib[ano] = pib[ano-1] * (1 + tx_cres_pib[ano])

    # Salva as variáveis em um dicionário
    resultados['MSalPopOcup'] = MSal_total
    resultados['tx_cres_pib'] = tx_cres_pib
    resultados['PIB'] = pib

    return resultados

    
