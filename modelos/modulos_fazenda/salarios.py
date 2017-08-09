# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
import pandas as pd


# Calcula rendimento médio
def calc_salarios(salarios, populacao, segurados, produtividade, 
                  salMinInicial, dadosLDO, periodo):
        
    # último ano do estoque (2014)
    ano_inicial = periodo[0]-1
    # Objeto do tipo Serie que armazena o Salario Minimo
    salarioMinimo =  pd.Series(index=[ano_inicial])

    # Inicializa com o valor conhecido
    salarioMinimo[ano_inicial] = salMinInicial
    
    # Projeta crescimento do Salário Mínimo (Eq. 36)
    for txCres in dadosLDO['TxCrescimentoSalMin']:
        ano_inicial += 1
        salarioMinimo[ano_inicial] = salarioMinimo[ano_inicial-1] * (1 + txCres/100) 

    # Salva a Serie no dicionário
    salarios['salarioMinimo']  = salarioMinimo  
    
    # Projeta crescimento dos salários da Pop. Ocupada a partir dos 
    # dados da Pnad e da produtividade (Eq 32)
    # A equação original não considera Inflação, mas é necessário adicionar pois a inflação 
    # é considerada no cálculo dos valores dos benefícios
    for clientela in ['Urb', 'Rur']:
        for sexo in ['H', 'M']:
            for ano in periodo:
                id_sal = 'SalMedPopOcup' + clientela + 'Pnad' + sexo
                inflacao = dadosLDO['TxInflacao'][ano]
                salarios[id_sal][ano] = salarios[id_sal][ano-1] * (1 + produtividade/100 + inflacao/100)             
    
                
    # Projeta crescimento dos salários dos Segurados acima do SM apartir da produtividade (Eq. 37)
    # A equação original não considera Inflação, mas é necessário adicionar pois a inflação 
    # é considerada no cálculo dos valores dos benefícios
    for sexo in ['H', 'M']:
        for ano in periodo:
            id_sal = 'SalMedSegUrbAcimPnad' + sexo
            inflacao = dadosLDO['TxInflacao'][ano]
            salarios[id_sal][ano] = salarios[id_sal][ano-1] * (1 + produtividade/100 + inflacao/100)             
    
    
    # Projeta crescimento dos salários da Pop. Ocupada que recebe acima do piso
    # a partir da Pnad e da produtividade
    # REVISAR: Esses valores são utilizados na Eq. 45, porém acredito que deveriam
    # Ser utilizados os segurados e náo a PopOcup
    for sexo in ['H', 'M']:
        for ano in periodo:
            id_sal = 'SalMedPopOcupUrbAcimPnad' + sexo
            inflacao = dadosLDO['TxInflacao'][ano]
            salarios[id_sal][ano] = salarios[id_sal][ano-1] * (1 + produtividade/100 + inflacao/100)                    
     
            
    # Projeta Massa Salarial para Pop. Ocupada (Eq. 33)
    for clientela in ['Urb', 'Rur']:
        for sexo in ['H', 'M']:            
            id_msal = 'MSalPopOcup' + clientela + sexo
            id_sal = 'SalMedPopOcup' + clientela + 'Pnad' + sexo
            id_pocup = 'Ocup' + clientela + sexo
            salarios[id_msal] = salarios[id_sal] * populacao[id_pocup]
                    
    
    # Projeta Massa Salarial para Contribuintes Urbanos que recebem o SM (Eq. 34)
    for sexo in ['H', 'M']:            
        id_csm = 'CsmUrb' + sexo
        id_msal = 'MSal' + id_csm
        # Multiplica SM do ano correspondente pela quantidade de trabalhadores
        # em cada idade        
        salarios[id_msal] = salarios['salarioMinimo'] * segurados[id_csm]
        # Elimina colunas vazias
        salarios[id_msal].dropna(how='all', axis=1, inplace=True)  
            
    
    # Projeta Massa Salarial para Segurados que recebem acima do SM (Eq. 35)
    for sexo in ['H', 'M']:            
        id_msal = 'MSalCaUrb' + sexo
        id_sal = 'SalMedSegUrbAcimPnad'+ sexo
        id_seg = 'CaUrb' + sexo
        salarios[id_msal] = salarios[id_sal] * segurados[id_seg]
         # Elimina colunas vazias
        salarios[id_msal].dropna(how='all', axis=1, inplace=True)  
        
    return salarios
        