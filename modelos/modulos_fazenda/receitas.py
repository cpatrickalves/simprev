# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
import pandas as pd


# Projeta a receita de acordo com a LDO de 2018
def calc_receitas(salarios, parametros, periodo):

    aliquota = parametros['aliquota_media']
    # Dicionário que armazenas os resultados
    resultados = {}
    ano_inicial = periodo[0] - 1             # 2014
    periodo_total = [ano_inicial]+periodo    # 2014-2060
    tx_cres_rec = pd.Series(0.0, index=periodo)
    
    # Cria um objeto do tipo Serie com índices iguais aos descritos na lista período e
    # todos os valores iguais a zero
    mSalContrTotal = pd.Series(0, index=periodo_total)
    receita = pd.Series(0, index=periodo_total)
        
    # Para cada sexo e clientela calcula as receitas (Eq. 39)
    for ano in periodo_total:
        for sexo in ['H','M']:
            for clientela in ['Ca', 'Csm']:            
                id_sal = 'MSal' + clientela + 'Urb' + sexo
                mSalContrTotal[ano] += salarios[id_sal][ano].sum() 

    # Aplica a alíquota efetiva média
    receita = mSalContrTotal * (aliquota/100)

    # Calcula a taxa de Crescimento da Receita
    for ano in periodo:  # pula o primeiro ano
        tx_cres_rec[ano] = receita[ano]/receita[ano-1] - 1

    resultados['receitas'] = receita
    resultados['msal_contrib'] = mSalContrTotal
    resultados['tx_cres_receita'] = tx_cres_rec

    return resultados


# Projeta o PIB de acordo com a LDO de 2018 conforme Equações 41, 42 e 43
def calc_pib_MF(resultados, salarios, PIBs, periodo):
    
    # 2014 - 2060
    periodo_total = [periodo[0]-1]+periodo    # 2014-2060
    
    # Cria um objetos do tipo Serie com índices iguais a lista periodo e
    # todos os valores iguais a zero
    pib = pd.Series(PIBs, index=[2014,2015,2016])
    tx_cres_pib = pd.Series(0.0, index=periodo)
    tx_cres_msal = pd.Series(0.0, index=periodo)
    MSal_total = pd.Series(0.0, index=periodo_total)      # PopOcupada

    # Calcula os valores totais de Massa Salarial da Pop Ocupada (Eq. 41)
    for ano in periodo_total:
        for sexo in ['H','M']:
            for clientela in ['Piso', 'Acim']:                      
                id_msal = 'MSalOcupUrb' + clientela + sexo
                MSal_total[ano] += salarios[id_msal][ano].sum()

    # Calcula a taxa de Crescimento da Massa Salarial (Eq. 42)
    for ano in periodo:  # pula o primeiro ano
        tx_cres_msal[ano] = MSal_total[ano]/MSal_total[ano-1] - 1

    # Faz a Projeção do PIB (Eq. 43)    
    # 2017-2060
    for ano in periodo[2:]:
        pib[ano] = pib[ano-1] * (1 + tx_cres_msal[ano])

    # Calcula a taxa de Crescimento do PIB
    for ano in periodo:  # pula o primeiro ano
        tx_cres_pib[ano] = pib[ano]/pib[ano-1] - 1
    
    # Salva as variáveis em um dicionário
    resultados['msal_pop_ocup'] = MSal_total
    resultados['tx_cres_pib'] = tx_cres_pib
    resultados['tx_cres_msal'] = tx_cres_msal
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

    
