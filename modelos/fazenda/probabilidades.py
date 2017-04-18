# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

from util.dados import get_id_beneficios
import pandas as pd

def calc_probabilidades(populacao, estoques, concessoes, cessacoes, periodo):
    probabilidades = {}
    
    # Para cada um dos sexos em população calcula a probabilidade de morte
    prob_morte = calc_prob_morte(populacao) # REVISAR
    prob_entrada_apos = calc_prob_apos(populacao, estoques, concessoes, periodo)  
    fat_ajuste_mort = calc_fat_ajuste_mort(estoques, cessacoes, prob_morte, periodo)
    
    probabilidades.update(prob_morte)
    probabilidades.update(prob_entrada_apos)
    probabilidades.update(fat_ajuste_mort)

    # Busca por probabilidades erradas (ex: > 1)
    busca_erros(probabilidades)
    
    return probabilidades
    
    
# Calcula probabilidades de entrada em benefícios
def calc_prob_apos(populacao, estoques, concessoes, periodo):
        
    probabilidades = {}       # Dicionário que salvas as prob. para cada benefício
    ano_prob = periodo[0]-1   # ano utilizado para cálculo
    tag_apos= ['Apin', 'Atcn', 'Apid', 'Atcp', 'Ainv', 'Atce', 'Atcd']
        
    # Calcula probabilidades de entrada em aposentadorias
    for beneficio in get_id_beneficios(tag_apos):
        # Verifica se o possui os dados de estoque e concessões do benefício que será calculado
        if beneficio in estoques.keys() and beneficio in concessoes.keys():
            
            # Calcula a probabilidade de entrada
            prob_entrada = concessoes[beneficio][ano_prob] / (estoques[beneficio][ano_prob-1] + (concessoes[beneficio][ano_prob]/2))
            # Converte "prob_entrada" para um DataFrame e adiciona no dicionário
            probabilidades[beneficio] = pd.DataFrame(prob_entrada)
            # nome da coluna no Dataframe
            probabilidades[beneficio].columns = [ano_prob]                 
             # Substitui os NaN (not a number) por zeros
            probabilidades[beneficio][ano_prob].fillna(0, inplace = True) 
        
    return probabilidades
            
# Calcula probabilidades de entrada em auxílios
def calc_prob_aux(populacao, estoques, concessoes, periodo):
    
    probabilidades = {}       # Dicionário que salvas as prob. para cada benefício
    ano_prob = periodo[0]-1   # ano utilizado para cálculo
    
    # Calcula probabilidades de entrada em auxílios reclusão e acidente    
    for beneficio in get_id_beneficios(['Auxa', 'Auxr']):
        # Verifica se o possui os dados de estoque e concessões do benefício
        if beneficio in estoques.keys() and beneficio in concessoes.keys():
            probabilidades[beneficio] = pd.DataFrame(estoques[beneficio][ano_prob] / segurados[beneficio][ano_prob]/2)
            probabilidades[beneficio].columns = [ano_prob]
            probabilidades[beneficio][ano_prob].fillna(0, inplace = True)

    # O cálculo do Auxílio doença e diferente dos demais auxílios
    for beneficio in get_id_beneficios('Auxd'):
        # Verifica se o possui os dados de estoque e concessões do benefício
        if beneficio in estoques.keys() and beneficio in concessoes.keys():
            probabilidades[beneficio] = pd.DataFrame(concessoes[beneficio][ano_prob] / (segurados[beneficio][ano_prob-1] + (concessoes[beneficio][ano_prob]/2)))
            probabilidades[beneficio].columns = [ano_prob]
            probabilidades[beneficio][ano_prob].fillna(0, inplace = True)
        
    return probabilidades
    
# Calcula probabilidade de morte baseado no método da fazenda
def calc_prob_morte(pop):

    # Obtem os anos da base do IBGE
    periodo = list(pop['PopIbgeH'].columns)
            
    # Dicionário que armazena as probabilidades    
    probMorte = {}
    
    # Para cada sexo...
    for sexo in ['H', 'M']:   
        
        # Cria o DataFrame que armazena as probabilidades para um sexo
        mort = pd.DataFrame(index=range(0,91), columns=periodo) 
        
        #chave usada para acessar a base do IBGE
        chave_pop = 'PopIbge'+sexo
        
        # Para cada ano...
        for ano in periodo[1:-1]: # Vai do segundo ao penúltimo ano
        
            # Para cada idade...
            for idade in range(1,90): # Vai de 1 até 89 anos 
                pop_atual = pop[chave_pop][ano][idade]
                pop_ano_passado = pop[chave_pop][ano-1][idade-1]    
                pop_prox_ano = pop[chave_pop][ano+1][idade+1]
        
                mortalidade = (pop_ano_passado - pop_atual)/2 + (pop_atual - pop_prox_ano)/2
                mort[ano][idade] = mortalidade/pop_atual
         
            # Calculo para a idade de 90 anos (Método UFPA) - REVISAR
            mort[ano][90] = 1 - (pop[chave_pop][ano+1][90] - pop[chave_pop][ano][89] * (1 - mort[ano][89])) / pop[chave_pop][ano][90]
    
            # Para idade 0 anos  = (pop_atual - pop_prox_ano)/ pop_atual            
            mort[ano][0] = ( pop[chave_pop][ano][0] - pop[chave_pop][ano+1][1])/pop[chave_pop][ano][0]
                        
        # Repete a Prob do ultimo ano como valor do antepenultimo
        mort[periodo[-1]] = mort[periodo[-2]]
        
        # Adiciona o DataFrame no dicionário com as chaves 'MortH' e 'MortM'
        mort.dropna(how='all', axis=1, inplace=True)  # Elimina colunas com dados ausentes
        probMorte['Mort'+sexo] = mort
     
    return probMorte

    
# Calcula o Fator de Ajuste de Mortalidade
def calc_fat_ajuste_mort(estoques, cessacoes, probMort, periodo):
    
    # ano utilizado para cálculo
    ano_prob = periodo[0]-1   #2014
           
    # Dicionário que armazena as probabilidades    
    fat_ajuste = {}

    tag_apos= ['Apin', 'Atcn', 'Apid', 'Atcp', 'Ainv', 'Atce', 'Atcd']
        
    # Calcula o fator de ajuste para cada tipo de aposentadoria
    for beneficio in get_id_beneficios(tag_apos):
        
        # Verifica se existem dados de estoque e cessações do benefício 
        if beneficio in estoques.keys() and beneficio in cessacoes.keys():
            ces_ano_atual = cessacoes[beneficio][ano_prob]
            est_ano_ant = estoques[beneficio][ano_prob-1]
            
            # Taxa de cessações 
            tx_ces = ces_ano_atual/(est_ano_ant + (ces_ano_atual/2))
            # Probabilidade de morte
            mort = probMort['Mort'+beneficio[-1]][ano_prob]
        
            # Salva a Série no dicionário
            fat_ajuste['fam'+beneficio] = tx_ces/mort
            
            # Substitui os NaN por zero
            fat_ajuste['fam'+beneficio].fillna(0, inplace=True)            
                        
    return fat_ajuste

    
    
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

# Verifica todos os valores de probabilidades calculados e indica aqueles
# maiores que 1    
def busca_erros(probabilidades):
            
    # Lista que salva os problemas
    problemas = {}
    # Verifica se existe probabilidades maiores que 1
    for p in probabilidades:
        # Se existe algum elemento em alguma coluna maior que 0.99    
        if (probabilidades[p] > 0.99).any().any():
            # Salva o benefício e uma tabela com os valores maires que 0.99
            problemas[p] = probabilidades[p][probabilidades[p].gt(0.99)].dropna()      
            # Salva em uma tabela
    
    if bool(problemas):
        print('PROBLEMA: Foram encontradas probabilidades maiores que 1\n')
        for p in problemas:
            print('Tabela: %s' %p)
            print(problemas[p])
            print('_________________\n')
            
        
        
            