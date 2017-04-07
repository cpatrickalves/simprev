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
    
    