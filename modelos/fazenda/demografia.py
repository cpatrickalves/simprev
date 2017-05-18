# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.tabelas import LerTabelas

# Calcula dados demográficos
def calc_demografia(populacao, taxas):
    
    
    # Dicionário que armazena os segurados rurais e contribuintes urbanos
    segurados = {}
    
    # Calcula Pop Urbana e Rural    
    pop_ur = calc_pop_urb_rur(populacao, taxas)
    
    # Calcula PEA Urbana e Rural
    pea = calc_pea_urb_rur(pop_ur, taxas)
    
    # Calcula Pocupada Urbana e Rural
    pocup = calc_pocup_urb_rur(pea, taxas)
    
    # Calcula Pocupada Urbana e Rural
    csm_ca = calc_Csm_Ca(pocup, taxas)
        
    # Calcula os Segurados Rurais
    segurados_rur = calc_segurados_rur(pea, taxas)
    
    
    # Adiciona as novas populações no dicionário população
    populacao.update(pop_ur)
    populacao.update(pea)
    populacao.update(pocup)
    
    # Adiciona contribuintes e segurados no dicionário segurados
    segurados.update(csm_ca)
    segurados.update(segurados_rur)
    
    return segurados    


# Calcula as populações urbana e rural    
def calc_pop_urb_rur(populacao, taxas):
        
    # Dicionário que armazena as populações urbanas e rurais
    pop_urb_rur = {}

    # Cria o objeto dados que possui os IDs das tabelas de populações
    dados = LerTabelas()

    # Para cada um dos sexos calcula as clientelas
    for pop in dados.ids_pop_ibge:
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
            
    for clientela in ['CsmUrb', 'CaUrb']:    
        for sexo in ['H','M']:
            chave = clientela+sexo                    
            chave_pocup = 'OcupUrb'+sexo
            chave_tx = 'tx'+clientela+sexo
            csm_ca[chave] = pocup[chave_pocup] * taxas[chave_tx]            
            
            # Elimina colunas com dados ausentes
            csm_ca[chave].dropna(axis=1, inplace=True)  
                                         
    return csm_ca


# Calcula Empregados Contribuintes, Segurados Especiais
# e Potenciais segurados especiais para clientela Rural
def calc_segurados_rur(pea_rur, taxas):
        
    # Dicionário que armazena os Segurados Rurais
    segurados_rur = {}
            
    for clientela_rural in ['SegEspRur', 'ContrRur', 'SegPotRur']:
        for sexo in ['H','M']:
            chave = clientela_rural+sexo                    
            chave_pea = 'PeaRur'+sexo
            chave_tx = 'tx'+clientela_rural+sexo
            segurados_rur[chave] = pea_rur[chave_pea] * taxas[chave_tx]            
            
            # Elimina colunas com dados ausentes
            segurados_rur[chave].dropna(axis=1, inplace=True)  

    # Soma dos Segurados Rurais, pois no cálculo dos estoques usa-se o valor
    # agregado para a clientela Rural
    for sexo in ['H','M']:
        segurados_rur['Rur'+sexo] = (segurados_rur['SegEspRur'+sexo] +
                                     segurados_rur['ContrRur'+sexo] + 
                                     segurados_rur['SegPotRur'+sexo])
                                         
    return segurados_rur
