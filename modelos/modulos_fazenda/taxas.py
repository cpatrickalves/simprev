# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

# Calcula taxa de urbanizacao 
# OBS: A LDO não descreve como calcular essa taxa, a Eq. utilizada foi deduzida
# a partir da lógica aplicada no cálculo de outras taxas (ex: taxa de Participação)
def calc_tx_urb(pop_pnad, periodo):
    
    # Dicionário que armazena as taxas de urbanização
    txurb = {}
    tx_crescimento_urb = 0 
    limite_crescimento = 1000   # OBS: A LDO não define nenhum valor de limite

    for sexo in ['H','M']:
        chave = 'txUrb'+sexo         
        txurb[chave] = (pop_pnad['PopUrbPnad'+sexo]/pop_pnad['PopPnad'+sexo])*(1 + tx_crescimento_urb )

        # Preenche valores Nan com zero      
        txurb[chave].fillna(0, inplace=True)
    
    
    # Crescimento a partir de 2015 - Eq. 3 da LDO de 2018
    for taxa in txurb:
                
        # OBS: De acordo com o DOC110/MF, para o anod e 2015 deve-se utilizar as médias de 2011-2014
        # Esse procedimento não é descrito na LDO de 2018
        txurb[taxa][2015] = txurb[taxa].loc[:,2011:2014].mean(axis=1)
        
        # A partir de 2016
        for ano in periodo[1:]:
            txurb[taxa][ano] = txurb[taxa][ano-1] * (1 + tx_crescimento_urb ) 
        
        # Verifica se existe alguma taxa maior que o limite definido        
        if (txurb[taxa][ano] > limite_crescimento).any():
            pass # OBS: Como não existe limite definido na LDO, será implementado em outro momento.           
    
    return txurb

# Calcula taxa de Participação no Mercado de Trabalho  
def calc_tx_part(pop_pnad, periodo):
    
    # Dicionário que armazena as taxas de urbanização
    txpart = {}
    tx_crescimento_part = 0 
    limite_crescimento = 1000   # OBS: A LDO não define nenhum valor de limite
    
    # Calculo feito de acordo com o 3o item da Seção 4.6 da LDO    
    for clientela in ['Urb', 'Rur']:
        for sexo in ['H','M']:
            chave = 'txPart'+clientela+sexo         
            pea = pop_pnad['Pea'+clientela+'Pnad'+sexo]
            pop = pop_pnad['Pop'+clientela+'Pnad'+sexo]
            txpart[chave] = pea/pop
                  
            # Preenche valores NaN com zero      
            txpart[chave].fillna(0, inplace=True)

    # Crescimento da taxa a partir de 2015 - Eq. 5 da LDO de 2018
    for taxa in txpart:
        for ano in periodo:
            txpart[taxa][ano] = txpart[taxa][ano-1] * (1 + tx_crescimento_part) 
                      
        # Verifica se existe alguma taxa maior que o limite definido        
        if (txpart[taxa][ano] > limite_crescimento).any():
            pass # OBS: Como não existe limite definido na LDO, será implementado em outro momento.   
            
    return txpart

# Calcula taxa de Ocupação
def calc_tx_ocup(pop_pnad, periodo):
    
    # Dicionario que armazena as taxas de ocupação
    txocup = {}
    
    # Calculo feito de acordo com o 4o item da Seção 4.6 da LDO de 2018
    for clientela in ['Urb', 'Rur']:
        for sexo in ['H', 'M']:
            chave = 'txOcup'+clientela+sexo
            pocup = pop_pnad['PopOcup'+clientela+'Pnad'+sexo]
            pea = pop_pnad['Pea'+clientela+'Pnad'+sexo]
            txocup[chave] = pocup/pea
            
            # Preenche valores NaN com zero      
            txocup[chave].fillna(0, inplace=True)

    # Repete as taxas do ultimo ano nos demais
    for taxa in txocup:
        for ano in periodo:
            txocup[taxa][ano] = txocup[taxa][ano-1] 
                
    return txocup


# Calcula taxa/propoção da Pop. Ocupada por SM e acima do SM para população ocupada
def calc_tx_ocup_csm_ca(pop_pnad, periodo):
    
    # Dicionario que armazena as taxas 
    txcober = {}
    
    # Padrão da chave: PopOcupUrbSmPnadH 
            
    # Taxa de Cobertura Contributiva para o SM
    for sexo in ['H', 'M']:
       chave = 'txOcupUrbPiso'+sexo
       pocupSm = pop_pnad['PopOcupUrbSmPnad'+sexo]   
       pocup = pop_pnad['PopOcupUrbPnad'+sexo]
       txcober[chave] = pocupSm/pocup

       # Preenche valores NaN com zero      
       txcober[chave].fillna(0, inplace=True)

               
    # taxa de Cobertura Contributiva acima do SM
    for sexo in ['H', 'M']:
       chave = 'txOcupUrbAcim'+sexo
       pocupAcima = pop_pnad['PopOcupUrbAcimPnad'+sexo]   
       pocup = pop_pnad['PopOcupUrbPnad'+sexo]
       txcober[chave] = pocupAcima/pocup

       # Preenche valores NaN com zero      
       txcober[chave].fillna(0, inplace=True)

    # Repete as taxas para todos os anos
    for taxa in txcober:
        for ano in periodo:
            txcober[taxa][ano] = txcober[taxa][ano-1] 
                
    return txcober


# Calcula taxa de Segurados por SM (Csm) e acima do SM (Ca)
def calc_tx_segurados_urb(pop_pnad, periodo):
    
    # Dicionario que armazena as taxas 
    txcober = {}
    
    # Padrão da chave: SegUrbAcimPnadH # REVISAR
    
    # Pag. 42 da LDO: taxas de cobertura contributiva por SM e acima do SM
    # calculadas pela relação da população de contribuintes para o sistema previdenciário
    # sobre a população ocupada;
        
    # Taxa de Cobertura Contributiva para o SM
    for sexo in ['H', 'M']:
       chave = 'txSegCsmUrb'+sexo
       segSm = pop_pnad['SegUrbSmPnad'+sexo]   
       pocup = pop_pnad['PopOcupUrbPnad'+sexo]
       txcober[chave] = segSm/pocup

       # Preenche valores NaN com zero      
       txcober[chave].fillna(0, inplace=True)
               
    # taxa de Cobertura Contributiva acima do SM
    for sexo in ['H', 'M']:
       chave = 'txSegCaUrb'+sexo
       segAcima = pop_pnad['SegUrbAcimPnad'+sexo]   
       pocup = pop_pnad['PopOcupUrbPnad'+sexo]
       txcober[chave] = segAcima/pocup

       # Preenche valores NaN com zero      
       txcober[chave].fillna(0, inplace=True)

    # Repete as taxas para todos os anos
    for taxa in txcober:
        for ano in periodo:
            txcober[taxa][ano] = txcober[taxa][ano-1] 
                
    return txcober


# Calcula taxa de empregados Contribuintes, Segurados Especiais
# e Potenciais segurados especiais para clientela Rural
def calc_tx_segurados_rur(pop_pnad, periodo):
    
    # Dicionario que armazena as taxas 
    tx_seg_rur = {}
    
    # Padrões da chave: SegEspRurPnadH, ContrRurPnadH, SegPotRurPnadH 
    # A LDO não descreve como calcular essa taxa
    # O documento inicial do modelo do STN, IPEA e SPE diz para usar 
    # a PeaRur como denominador, mas acho que o correto seria a SegRurPnadH.
    # Página 42 da LDO - REVISAR
    
    # Taxas de participação de subconuntos da população rural
    for clientela_rural in ['SegEspRur', 'ContrRur', 'SegPotRur']:
        for sexo in ['H', 'M']:
           chave = 'tx'+clientela_rural+sexo
           pnad_rur = pop_pnad[clientela_rural+'Pnad'+sexo]   
           pea_rur = pop_pnad['PeaRurPnad'+sexo]
           tx_seg_rur[chave] = pnad_rur/pea_rur
    
           # Preenche valores NaN com zero      
           tx_seg_rur[chave].fillna(0, inplace=True)
        
    # Repete as taxas para todos os anos
    for taxa in tx_seg_rur:
        for ano in periodo:
            tx_seg_rur[taxa][ano] = tx_seg_rur[taxa][ano-1] 
    
            
    return tx_seg_rur


