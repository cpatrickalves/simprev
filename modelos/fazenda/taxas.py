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
    
    taxas.update(txurb)
    taxas.update(txpart)
    taxas.update(txocup)
    taxas.update(txCsm_Ca)

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
       chave = 'txCsm'+sexo
       pocupSm = pop_pnad['PopOcupUrbSmPnad'+sexo]   
       pocup = pop_pnad['PopOcupUrbPnad'+sexo]
       txcober[chave] = pocupSm/pocup

       # Preenche valores NaN com zero      
       txcober[chave].fillna(0, inplace=True)

               
    # taxa de Cobertura Contributiva acima do SM
    for sexo in ['H', 'M']:
       chave = 'txCa'+sexo
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

