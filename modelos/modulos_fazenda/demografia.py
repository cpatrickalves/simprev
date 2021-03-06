# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.tabelas import LerTabelas


# Calcula as populações urbana e rural   
def calc_pop_urb_rur(populacao, taxas):
        
    # Dicionário que armazena as populações urbanas e rurais
    pop_urb_rur = {}

    # Cria o objeto dados que possui os IDs das tabelas de populações
    dados = LerTabelas()

    # Para cada um dos sexos calcula as clientelas 
    # Equações 1 e 2 da LDO de 2018
    for pop in dados.ids_pop_ibge:                      # dados.ids_pop_ibge retorna uma lista de IDs das tabelas
        chave_urb = pop.replace('Ibge', 'Urb')          # Substitui a String 'Ibge' por 'Urb'
        chave_rur = pop.replace('Ibge', 'Rur')
        chave_tx = pop.replace('PopIbge', 'txUrb')
        pop_urb_rur[chave_urb] = populacao[pop] * taxas[chave_tx]           # Eq. 1
        pop_urb_rur[chave_rur] = populacao[pop] * (1 - taxas[chave_tx])     # Eq. 2
        
        # Elimina colunas com dados ausentes
        pop_urb_rur[chave_urb].dropna(axis=1, inplace=True)  
        pop_urb_rur[chave_rur].dropna(axis=1, inplace=True)  
        
    return pop_urb_rur


# Calcula a população economicamente ativa urbana e rural    
def calc_pea_urb_rur(pop, taxas):
        
    # Dicionário que armazena as populações urbanas e rurais
    pea_urb_rur = {}
    
    # Para cada uma das clientelas e sexos calcula a pea
    # Equação 4 da LDO de 2018
    for clientela in ['Urb','Rur']:
        for sexo in ['H','M']:
            chave_pea = 'Pea'+clientela+sexo            
            chave_tx = 'txPart'+clientela+sexo
            chave_pop = 'Pop'+clientela+sexo
            pea_urb_rur[chave_pea] = pop[chave_pop] * taxas[chave_tx]       # Eq. 4         
            
            # Elimina colunas com dados ausentes
            pea_urb_rur[chave_pea].dropna(axis=1, inplace=True)  
              
    return pea_urb_rur


# Calcula as populações ocupadas urbana e rural    
def calc_pocup_urb_rur(pea, taxas):
        
    # Dicionário que armazena as populações ocupadas urbanas e rurais
    pocup_urb_rur = {}
    
    # Para cada uma das clientelas e sexos calcula a Pocup
    # Equação 6 da LDO de 2018
    for clientela in ['Urb','Rur']:
        for sexo in ['H','M']:
            chave_pocup = 'Ocup'+clientela+sexo            
            chave_tx = 'txOcup'+clientela+sexo
            chave_pea = 'Pea'+clientela+sexo
            pocup_urb_rur[chave_pocup] = pea[chave_pea] * taxas[chave_tx]   # Eq. 6          
            
            # Elimina colunas com dados ausentes
            pocup_urb_rur[chave_pocup].dropna(axis=1, inplace=True)  
              
    # Para cada uma das clientelas e sexos calcula a Pop desocupada
    # Equação 7 da LDO de 2018
    for clientela in ['Urb','Rur']:
        for sexo in ['H','M']:
            chave_pdesocup = 'Desocup'+clientela+sexo   
            chave_pocup = 'Ocup'+clientela+sexo                        
            chave_pea = 'Pea'+clientela+sexo
            pocup_urb_rur[chave_pdesocup] = pea[chave_pea] - pocup_urb_rur[chave_pocup]   # Eq. 7         
            
            # Elimina colunas com dados ausentes
            pocup_urb_rur[chave_pdesocup].dropna(axis=1, inplace=True)  
                        
    return pocup_urb_rur


# Calcula as populações ocupadas urbana que recebem o SM e acima do SM
# OBS: Este cálculo não é descrito na LDO de 2018
def calc_pocup_Csm_Ca(pocup, taxas):
        
    # Dicionário que armazena os Contribuintes Urbanos que recebem
    # o SM e acima do SM
    csm_ca = {}
            
    for clientela in ['OcupUrbPiso', 'OcupUrbAcim']:    
        for sexo in ['H','M']:
            chave = clientela+sexo                    
            chave_pocup = 'OcupUrb'+sexo
            chave_tx = 'tx'+clientela+sexo
            csm_ca[chave] = pocup[chave_pocup] * taxas[chave_tx]    # Eq. 8         
            
            # Elimina colunas com dados ausentes
            csm_ca[chave].dropna(axis=1, inplace=True)  
                                         
    return csm_ca


# Calcula os segurados urbanos que recebem o SM e acima do SM
# Equação 8 da LDO de 2018   
def calc_segurados_urb(pocup, taxas):
        
    # Dicionário que armazena os Contribuintes Urbanos que recebem
    # o SM e acima do SM
    csm_ca = {}
            
    for clientela in ['CsmUrb', 'CaUrb']:    
        for sexo in ['H','M']:
            chave = clientela+sexo                    
            chave_pocup = 'OcupUrb'+sexo
            chave_tx = 'txSeg'+clientela+sexo
            csm_ca[chave] = pocup[chave_pocup] * taxas[chave_tx]    # Eq. 8         
            
            # Elimina colunas com dados ausentes
            csm_ca[chave].dropna(axis=1, inplace=True)  
                                         
    return csm_ca


# Calcula Empregados Contribuintes, Segurados Especiais
# e Potenciais segurados especiais para clientela Rural
# Equações 9 e 10 da LDO de 2018  
def calc_segurados_rur(pea_rur, taxas):
        
    # Dicionário que armazena os Segurados Rurais
    segurados_rur = {}
            
    for clientela_rural in ['SegEspRur', 'ContrRur', 'SegPotRur']:
        for sexo in ['H','M']:
            chave = clientela_rural+sexo                    
            chave_pea = 'PeaRur'+sexo
            chave_tx = 'tx'+clientela_rural+sexo
            segurados_rur[chave] = pea_rur[chave_pea] * taxas[chave_tx]    # Eq. 10            
            
            # Elimina colunas com dados ausentes
            segurados_rur[chave].dropna(axis=1, inplace=True)  


    # Soma dos Segurados Rurais, pois no cálculo dos estoques usa-se o valor
    # agregado para a clientela Rural
    # Eq. 9
    for sexo in ['H','M']:
        segurados_rur['Rur'+sexo] = (segurados_rur['SegEspRur'+sexo] +
                                     segurados_rur['ContrRur'+sexo] + 
                                     segurados_rur['SegPotRur'+sexo])
                                         
    return segurados_rur
