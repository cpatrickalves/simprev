# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.carrega_dados import ids_pop_ibge

# Calcula todas as taxas
def calc_taxas(pop_pnad):
    
    taxas = {}

    txurb = calc_tx_urb(pop_pnad)
    txpart = calc_tx_part(pop_pnad)
    txocup = calc_tx_ocup(pop_pnad)
    
    taxas.update(txurb)
    taxas.update(txpart)
    taxas.update(txocup)

    return taxas

# Calcula dados demográficos
def calc_demografia(populacao, taxas):
    
    # Calcula Pop Urbana e Rural    
    pop_ur = calc_pop_urb_rur(populacao, taxas)
    
    # Calcula PEA Urbana e Rural
    pea = calc_pea_urb_rur(pop_ur, taxas)
    
    # Calcula Pocupada Urbana e Rural
    pocup = calc_pocup_urb_rur(pea, taxas)
    
    # Adiciona as novas populações no dicionário população
    populacao.update(pop_ur)
    populacao.update(pea)
    populacao.update(pocup)
    
    return populacao    

# Calcula taxa de urbanizacao
def calc_tx_urb(pop_pnad):
    
    # Dicionário que armazena as taxas de urbanização
    txurb = {}
    tx_crescimento_urb = 0 # REVISAR
    limite_crescimento = 0 # REVISAR

    for sexo in ['H','M']:
        chave = 'txUrb'+sexo         
        txurb[chave] = (pop_pnad['PopUrbPnad'+sexo]/pop_pnad['PopPnad'+sexo])*(1 + tx_crescimento_urb )

        # Preenche valores Nan com zero      
        txurb[chave].fillna(0, inplace=True)
        
    # Crescimento a partir de 2015
    for taxa in txurb:
        for ano in range(2015,2061):
            txurb[taxa][ano] = txurb[taxa][ano-1] * (1 + tx_crescimento_urb ) 
        
    return txurb

# Calcula taxa de participação    
def calc_tx_part(pop_pnad):
    
    # Dicionário que armazena as taxas de urbanização
    txpart = {}
    tx_crescimento_part = 0 # REVISAR
    limite_crescimento = 0 # REVISAR
    
    for clientela in ['Urb', 'Rur']:
        for sexo in ['H','M']:
            chave = 'txPart'+clientela+sexo         
            pea = pop_pnad['Pea'+clientela+'Pnad'+sexo]
            pia = pop_pnad['Pop'+clientela+'Pnad'+sexo]
            txpart[chave] = pea/pia
                  
            # Preenche valores NaN com zero      
            txpart[chave].fillna(0, inplace=True)

    # Crescimento da taxa a partir de 2015
    for taxa in txpart:
        for ano in range(2015,2061):
            txpart[taxa][ano] = txpart[taxa][ano-1] * (1 + tx_crescimento_part) 
        
    return txpart

# Calcula taxa de Ocupação
def calc_tx_ocup(pop_pnad):
    
    # Dicionario que armazena as taxas de ocupação
    txocup = {}
    
    for clientela in ['Urb', 'Rur']:
        for sexo in ['H', 'M']:
            chave = 'txOcup'+clientela+sexo
            pocup = pop_pnad['PopOcup'+clientela+'Pnad'+sexo]
            pea = pop_pnad['Pea'+clientela+'Pnad'+sexo]
            txocup[chave] = pocup/pea
            
            # Preenche valores NaN com zero      
            txocup[chave].fillna(0, inplace=True)

    # Repete o ultimo ano nos demais anos
    for taxa in txocup:
        for ano in range(2015,2061):
            txocup[taxa][ano] = txocup[taxa][ano-1] 
                
    return txocup


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
    
    # para cada uma das clientelas e sexos calcula a pea
    for clientela in ['Urb','Rur']:
        for sexo in ['H','M']:
            chave_pocup = 'Ocup'+clientela+sexo            
            chave_tx = 'txOcup'+clientela+sexo
            chave_pea = 'Pea'+clientela+sexo
            pocup_urb_rur[chave_pocup] = pea[chave_pea] * taxas[chave_tx]            
            
            # Elimina colunas com dados ausentes
            pocup_urb_rur[chave_pocup].dropna(axis=1, inplace=True)  
              
    return pocup_urb_rur