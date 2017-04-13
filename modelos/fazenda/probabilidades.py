# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

from util.carrega_dados import get_id_beneficios
import pandas as pd

def calc_probabilidades(populacao):
    probabilidades = {}
    
    # Para cada um dos sexos em população calcula a probabilidade de morte
    prob_morte = calc_prob_morte_ufpa(populacao) # REVISAR
    
    probabilidades.update(prob_morte)

    return probabilidades
    
    
# Calcula probabilidades de entrada em benefícios
def calc_prob_apos(estoques, concessoes, segurados, populacao, periodo):
        
    prob = {}               # Dicionário que salvas as probabilidades para cada benefício
    ano_prob = periodo[0]   # ano inicial da projeção
    tag_apos= ['Apin', 'Atcn', 'Apid', 'Atcp', 'Ainv', 'Atce', 'Atcd']
        
    # Calcula probabilidades de entrada em aposentadorias
    for beneficio in get_id_beneficios(tag_apos):
        # Verifica se o possui os dados de estoque e concessões do benefício
        if beneficio in estoques.keys() and beneficio in concessoes.keys():
            prob[beneficio] = pd.DataFrame(concessoes[beneficio][ano_prob] / 
                (estoques[beneficio][ano_prob-1] + (concessoes[beneficio][ano_prob]/2)))
            prob[beneficio].columns = [ano_prob]                 # nome da coluna no Dataframe
            prob[beneficio][ano_prob].fillna(0, inplace = True)  # Substitui os NaN (not a number) por zeros

    # Calcula probabilidades de entrada em auxílios reclusão e acidente    
    for beneficio in get_id_beneficios(['Auxa', 'Auxr']):
        # Verifica se o possui os dados de estoque e concessões do benefício
        if beneficio in estoques.keys() and beneficio in concessoes.keys():
            prob[beneficio] = pd.DataFrame(estoques[beneficio][ano_prob] / segurados[beneficio][ano_prob]/2)
            prob[beneficio].columns = [ano_prob]
            prob[beneficio][ano_prob].fillna(0, inplace = True)

    # O cálculo do Auxílio doença e diferente dos demais auxílios
    for beneficio in get_id_beneficios('Auxd'):
        # Verifica se o possui os dados de estoque e concessões do benefício
        if beneficio in estoques.keys() and beneficio in concessoes.keys():
            prob[beneficio] = pd.DataFrame(concessoes[beneficio][ano_prob] / (segurados[beneficio][ano_prob-1] + (concessoes[beneficio][ano_prob]/2)))
            prob[beneficio].columns = [ano_prob]
            prob[beneficio][ano_prob].fillna(0, inplace = True)
        
    
# Calcula probabilidade de morte baseado no método da fazenda - REVISAR
def calc_prob_morte(pop, sexo, periodo):

    txMort = pd.DataFrame(index=range(0,91), columns=periodo) 
    
    for ano in periodo:
        for idade in range(1,90):
            pop_atual = pop[sexo][ano][idade]
            pop_ano_passado = pop[sexo][ano-1][idade-1]    
            pop_prox_ano = pop[sexo][ano+1][idade+1]
    
            mortalidade = (pop_atual - pop_ano_passado)/2 + (pop_prox_ano - pop_atual)/2
            txMort[ano][idade] = mortalidade/pop_atual
     
        # Calculo para a idade de 90 anos
        txMort[ano][90] = 1 - (pop[sexo][ano+1][90] - pop[sexo][ano][89] * (1 - txMort[ano][89])) / pop[sexo][ano][90]

        # Calculo para a idade de 0 anos
        txMort[ano][0] = 1
     
    return txMort

'''
(Patrick)
Estou usando esse por enquanto, pois nao consegui calcular pelo método
da fazenda.
'''
# Calcula probabilidade de morte baseado no método do LTS/UFPA
def calc_prob_morte_ufpa(pop):

    # Obtem os anos da base do IBGE
    periodo = list(pop['PopIbgeH'].columns)
    
    # Dicionário que armazena as probabilidades    
    probMorte = {}
       
    for sexo in ['H', 'M']:    
        
        # Cria o DataFrame que armazena as probabilidades para um sexo
        mort = pd.DataFrame(index=range(0,91), columns=periodo) 
        chave_pop = 'PopIbge'+sexo
        
        for ano in periodo[0:-1]:  # Vai do primeiro ao penúltimo ano
            for idade in range(0,89): 
                pop_atual = pop[chave_pop][ano][idade]            
                pop_prox_ano = pop[chave_pop][ano+1][idade+1]                
                mort[ano][idade] = 1 - (pop_prox_ano/pop_atual)
         
            # Calculo para a idade de 89 anos
            mort[ano][89] = mort[ano][88]
    
            # Calculo para a idade de 90 anos
            mort[ano][90] = 1 - (pop[chave_pop][ano+1][90] - pop[chave_pop][ano][89] \
                            * (1 - mort[ano][89])) / pop[chave_pop][ano][90]
         
        # Repete a Prob do ultimo ano como valor do antepenultimo
        mort[periodo[-1]] = mort[periodo[-2]]
        
        probMorte['Mort'+sexo] = mort

    return probMorte
    
