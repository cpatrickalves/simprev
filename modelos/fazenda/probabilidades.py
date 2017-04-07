# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

from util.carrega_dados import get_id_beneficios
import pandas as pd

def calc_probabilidades(populacao):
    prob = {}
    
    # Para cada um dos sexos em população calcula a probabilidade de morte
    for sexo in populacao.keys():            
        prob['txMort'+sexo[-1]] = calc_prob_morte_ufpa(populacao, sexo) # REVISAR
    
    return prob
    
    
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
def calc_prob_morte_ufpa(pop, sexo):

    periodo = list(pop[sexo].columns)
    txMort = pd.DataFrame(index=range(0,91), columns=periodo) 
        
    for ano in periodo[0:-1]:
        for idade in range(0,89):
            pop_atual = pop[sexo][ano][idade]            
            pop_prox_ano = pop[sexo][ano+1][idade+1]                
            txMort[ano][idade] = 1 - (pop_prox_ano/pop_atual)
     
        # Calculo para a idade de 89 anos
        txMort[ano][89] = txMort[ano][88]

        # Calculo para a idade de 90 anos
        txMort[ano][90] = 1 - (pop[sexo][ano+1][90] - pop[sexo][ano][89] * (1 - txMort[ano][89])) / pop[sexo][ano][90]
     
    # Repete a Prob do ultimo ano como valor do antepenultimo
    txMort[periodo[-1]] = txMort[periodo[-2]]

    return txMort
    
