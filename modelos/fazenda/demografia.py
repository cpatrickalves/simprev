# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

# Calcula taxa de urbanizacao

def calc_tx_urb(pop_pnad):
    
    # Dicionário que armazena as taxas de urbanização
    txurb = {}
    tx_crescimento_urb = 0 # REVISAR
    limite_crescimento = 0 # REVISAR

    for sexo in ['H','M']:
        chave = 'txUrb'+sexo         
        txurb[chave] = (pop_pnad['PopUrbPnad'+sexo]/pop_pnad['PopPnad'+sexo])*(1 + tx_crescimento_urb )

    # Crescimento a partir de 2015
    for taxa in txurb:
        for ano in range(2015,2061):
            txurb[taxa][ano] = txurb[taxa][ano-1] * (1 + tx_crescimento_urb ) 
        
    return txurb
    
def calc_pop_urb_rur(populacao, taxas):
        
    pop_urb_rur = {}
    
    for pop in populacao:
        chave_urb = pop.replace('Ibge', 'Urb')
        chave_rur = pop.replace('Ibge', 'Rur')
        chave_tx = pop.replace('PopIbge', 'txUrb')
        pop_urb_rur[chave_urb] = populacao[pop] * taxas[chave_tx]
        pop_urb_rur[chave_rur] = populacao[pop] * (1 - taxas[chave_tx])
        
        # Elimina colunas com dados ausentes
        pop_urb_rur[chave_urb].dropna(axis=1, inplace=True)  
        pop_urb_rur[chave_rur].dropna(axis=1, inplace=True)  
        
    return pop_urb_rur