# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
import pandas as pd


# Calcula rendimento médio
def calc_salarios(salarios, populacao, segurados, produtividade, 
                  salMinInicial, txCresSalMin, periodo):
        
    # último ano do estoque (2014)
    ano_inicial = periodo[0]-1
    # Objeto do tipo Serie que armazena o Salario Minimo
    salarioMinimo =  pd.Series(index=[ano_inicial])
    # Inicializa com os valores conhecidos
    for valor in salMinInicial:
        salarioMinimo[ano_inicial] = valor
        ano_inicial += 1
    
    # Projeta crescimento do Salário Mínimo (Eq 36)
    for txCres in txCresSalMin:
        salarioMinimo[ano_inicial] = salarioMinimo[ano_inicial-1] * (1 + txCres/100) #REVISAR
        ano_inicial += 1
    
    # Salva a Serie no dicionário
    salarios['salarioMinimo']  = salarioMinimo  
    
    # Projeta crescimento dos salários da Pop. Ocupada a partir da produtividade (Eq 32)
    for clientela in ['Urb', 'Rur']:
        for sexo in ['H', 'M']:
            for ano in periodo:
                id_sal = 'SalMedPopOcup' + clientela + 'Pnad' + sexo
                salarios[id_sal][ano] = salarios[id_sal][ano-1] * (1 + produtividade/100)               
                    
    # Projeta crescimento dos salários dos Segurados acima do SM apartir da produtividade (Eq 37)
    for sexo in ['H', 'M']:
        for ano in periodo:
            id_sal = 'SalMedSegUrbAcimPnad' + sexo
            salarios[id_sal][ano] = salarios[id_sal][ano-1] * (1 + produtividade/100)

          
    # Projeta Massa Salarial para Pop. Ocupada (Eq 33)
    for clientela in ['Urb', 'Rur']:
        for sexo in ['H', 'M']:            
            id_msal = 'MSalPopOcup' + clientela + sexo
            id_sal = 'SalMedPopOcup' + clientela + 'Pnad' + sexo
            id_pocup = 'Ocup' + clientela + sexo
            salarios[id_msal] = salarios[id_sal] * populacao[id_pocup]
            
           
    # Projeta Massa Salarial para Urbanos que recebem o SM (Eq 34)
    for sexo in ['H', 'M']:            
        id_csm = 'CsmUrb' + sexo
        id_msal = 'MSal' + id_csm        
        salarios[id_msal] = salarios['salarioMinimo'] * segurados[id_csm]
        # Elimina colunas vazias
        salarios[id_msal].dropna(how='all', axis=1, inplace=True)  
     
    # Projeta Massa Salarial para Segurados que recebem acima do SM (Eq 35)
    for sexo in ['H', 'M']:            
        id_msal = 'MSalCaUrb' + sexo
        id_sal = 'SalMedSegUrbAcimPnad'+ sexo
        id_seg = 'CaUrb' + sexo
        salarios[id_msal] = salarios[id_sal] * segurados[id_seg]
         # Elimina colunas vazias
        salarios[id_msal].dropna(how='all', axis=1, inplace=True)  
            
        
    return salarios
            
        
    
    




