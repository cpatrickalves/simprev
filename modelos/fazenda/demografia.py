# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.carrega_dados import ids_pop_ibge

# Calcula dados demográficos
def calc_demografia(populacao, taxas):
    
    # Calcula Pop Urbana e Rural    
    pop_ur = calc_pop_urb_rur(populacao, taxas)
    
    # Calcula PEA Urbana e Rural
    pea = calc_pea_urb_rur(pop_ur, taxas)
    
    # Calcula Pocupada Urbana e Rural
    pocup = calc_pocup_urb_rur(pea, taxas)
    
    # Calcula Pocupada Urbana e Rural
    csm_ca = calc_Csm_Ca(pocup, taxas)
        
    # Adiciona as novas populações no dicionário população
    populacao.update(pop_ur)
    populacao.update(pea)
    populacao.update(pocup)
    populacao.update(csm_ca)
    
    return populacao    


# Calcula as populações urbana e rural    
def calc_pop_urb_rur(populacao, taxas):
        
    # Dicionário que armazena as populações urbanas e rurais
    pop_urb_rur = {}
    
    # para cada um dos sexos calcula as clientelas
    for pop in ids_pop_ibge:
        chave_urb = pop.replace('Ibge', 'Urb')
        chave_rur = pop.replace('Ibge', 'Rur')
        chave_tx = pop.replace('PopIbge', 'txUrb')
        pop_urb_rur[chave_urb] = populacao[pop] * taxas[chave_tx]
        pop_urb_rur[chave_rur] = populacao[pop] * (1 - taxas[chave_tx])
        
        # Elimina colunas com dados ausentes
        pop_urb_rur[chave_urb].dropna(axis=1, inplace=True)  
        pop_urb_rur[chave_rur].dropna(axis=1, inplace=True)  
        
    return pop_urb_rur

# Calcula as populações urbana e rural    
def calc_pea_urb_rur(pop_ur, taxas):
        
    # Dicionário que armazena as populações urbanas e rurais
    pea_urb_rur = {}
    
    # para cada uma das clientelas e sexos calcula a pea
    for clientela in ['Urb','Rur']:
        for sexo in ['H','M']:
            chave_pea = 'Pea'+clientela+sexo            
            chave_tx = 'txPart'+clientela+sexo
            chave_pop = 'Pop'+clientela+sexo
            pea_urb_rur[chave_pea] = pop_ur[chave_pop] * taxas[chave_tx]            
            
            # Elimina colunas com dados ausentes
            pea_urb_rur[chave_pea].dropna(axis=1, inplace=True)  
              
    return pea_urb_rur


# Calcula as populações ocupadas urbana e rural    
def calc_pocup_urb_rur(pea, taxas):
        
    # Dicionário que armazena as populações ocupadas urbanas e rurais
    pocup_urb_rur = {}
    
    # para cada uma das clientelas e sexos calcula a Pocup
    for clientela in ['Urb','Rur']:
        for sexo in ['H','M']:
            chave_pocup = 'Ocup'+clientela+sexo            
            chave_tx = 'txOcup'+clientela+sexo
            chave_pea = 'Pea'+clientela+sexo
            pocup_urb_rur[chave_pocup] = pea[chave_pea] * taxas[chave_tx]            
            
            # Elimina colunas com dados ausentes
            pocup_urb_rur[chave_pocup].dropna(axis=1, inplace=True)  
              
    # para cada uma das clientelas e sexos calcula a Pop desocupada
    for clientela in ['Urb','Rur']:
        for sexo in ['H','M']:
            chave_pdesocup = 'Desocup'+clientela+sexo   
            chave_pocup = 'Ocup'+clientela+sexo                        
            chave_pea = 'Pea'+clientela+sexo
            pocup_urb_rur[chave_pdesocup] = pea[chave_pea] - pocup_urb_rur[chave_pocup]            
            
            # Elimina colunas com dados ausentes
            pocup_urb_rur[chave_pdesocup].dropna(axis=1, inplace=True)  
                        
    return pocup_urb_rur


# Calcula as populações ocupadas urbana que recebem o SM e acima do SM    
def calc_Csm_Ca(pocup, taxas):
        
    # Dicionário que armazena os Contribuintes Urbanos que recebem
    # o SM e acima do SM
    csm_ca = {}
            
    for clientela in ['Csm', 'Ca']:    
        for sexo in ['H','M']:
            chave = clientela+sexo                    
            chave_pocup = 'OcupUrb'+sexo
            chave_tx = 'tx'+clientela+sexo
            csm_ca[chave] = pocup[chave_pocup] * taxas[chave_tx]            
            
            # Elimina colunas com dados ausentes
            csm_ca[chave].dropna(axis=1, inplace=True)  
                                         
    return csm_ca