# -*- coding: utf-8 -*-
"""

@author: Patrick Alves
"""

# Calcula todas as taxas
def calc_taxas(pop_pnad):
    
    taxas = {}

    txurb = calc_tx_urb(pop_pnad)
    txpart = calc_tx_part(pop_pnad)
    txocup = calc_tx_ocup(pop_pnad)
    txCsm_Ca = calc_tx_cobertura_sm(pop_pnad)
    txSegurados_rur = calc_tx_segurados_rur(pop_pnad)
    
    taxas.update(txurb)
    taxas.update(txpart)
    taxas.update(txocup)
    taxas.update(txCsm_Ca)
    taxas.update(txSegurados_rur)

    return taxas


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

# Calcula taxa de Cobertura Contributiva por SM e acima do SM
def calc_tx_cobertura_sm(pop_pnad):
    
    # Dicionario que armazena as taxas 
    txcober = {}
    
    # Padrão da chave: PopOcupUrbSmPnadH # REVISAR
    
    # taxa de Cobertura Contributiva para o SM
    for sexo in ['H', 'M']:
       chave = 'txCsmUrb'+sexo
       pocupSm = pop_pnad['PopOcupUrbSmPnad'+sexo]   
       pocup = pop_pnad['PopOcupUrbPnad'+sexo]
       txcober[chave] = pocupSm/pocup

       # Preenche valores NaN com zero      
       txcober[chave].fillna(0, inplace=True)

               
    # taxa de Cobertura Contributiva acima do SM
    for sexo in ['H', 'M']:
       chave = 'txCaUrb'+sexo
       pocupSm = pop_pnad['PopOcupUrbAcimPnad'+sexo]   
       pocup = pop_pnad['PopOcupUrbPnad'+sexo]
       txcober[chave] = pocupSm/pocup

       # Preenche valores NaN com zero      
       txcober[chave].fillna(0, inplace=True)

    # Repete o ultimo ano nos demais anos
    for taxa in txcober:
        for ano in range(2015,2061):
            txcober[taxa][ano] = txcober[taxa][ano-1] 
    
            
    return txcober


# Calcula taxa de empregados Contribuintes, Segurados Especiais
# e Potenciais segurados especiais para clientela Rural
def calc_tx_segurados_rur(pop_pnad):
    
    # Dicionario que armazena as taxas 
    tx_seg_rur = {}
    
    # Padrões da chave: SegEspRurPnadH, ContrRurPnadH, SegPotRurPnadH 
    # REVISAR: O texto diz para usar a PeaRur como denominador, mas acho
    # que seria a SegRurPnadH.
    
    # taxa de Cobertura Contributiva para o SM
    for clientela_rural in ['SegEspRur', 'ContrRur', 'SegPotRur']:
        for sexo in ['H', 'M']:
           chave = 'tx'+clientela_rural+sexo
           pnad_rur = pop_pnad[clientela_rural+'Pnad'+sexo]   
           pea_rur = pop_pnad['PeaRurPnad'+sexo]
           tx_seg_rur[chave] = pnad_rur/pea_rur
    
           # Preenche valores NaN com zero      
           tx_seg_rur[chave].fillna(0, inplace=True)
        
    # Repete o ultimo ano nos demais anos
    for taxa in tx_seg_rur:
        for ano in range(2015,2061):
            tx_seg_rur[taxa][ano] = tx_seg_rur[taxa][ano-1] 
    
            
    return tx_seg_rur


