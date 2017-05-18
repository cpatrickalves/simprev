# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

from util.tabelas import LerTabelas
import pandas as pd

def calc_probabilidades(populacao, segurados, estoques, 
                        concessoes, cessacoes, periodo):
    
    # Dicionário que armazena as probabilidades
    probabilidades = {}
    
    prob_morte = calc_prob_morte(populacao) 
    fat_ajuste_mort = calc_fat_ajuste_mort(estoques, cessacoes, 
                                           prob_morte, periodo)
    
    prob_entrada_apos = calc_prob_apos(segurados, concessoes, periodo)      
    #prob_entrada_aux = calc_prob_aux(segurados, estoques, concessoes, periodo)
    #prob_entrada_pens = calc_prob_pensao(concessoes, prob_morte, 
     #                                    fat_ajuste_mort, periodo)

    probabilidades.update(prob_morte)
    probabilidades.update(fat_ajuste_mort)
    probabilidades.update(prob_entrada_apos)
    #probabilidades.update(prob_entrada_aux) 
    #probabilidades.update(prob_entrada_pens) 

    # Busca por probabilidades erradas (ex: > 1)
    busca_erros(probabilidades)

    return probabilidades



# Calcula probabilidades de entrada em benefícios
def calc_prob_apos(segurados, concessoes, periodo):

    probabilidades = {}       # Dicionário que salvas as prob. para cada benefício
    ano_prob = periodo[0]-1   # ano utilizado para cálculo (2014)
    ids_apos= ['Apin', 'Atcn', 'Apid', 'Atcp', 'Ainv', 'Atce', 'Atcd']

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    # Calcula probabilidades de entrada em aposentadorias
    for beneficio in dados.get_id_beneficios(ids_apos):
        # Verifica se o possui os dados de concessões do benefício 
        if beneficio in concessoes.keys():

            id_segurado = dados.get_id_segurados(beneficio)
            
            # Calcula a probabilidade de entrada
            # Nesse caso prob_entrada é do tipo Series e não DataFrame, pois
            # Possui somente uma dimensão (não possui colunas)
            # A versão da LDO trabalha com estoques, porém o correto seriam os segurados
            prob_entrada = concessoes[beneficio][ano_prob] / (segurados[id_segurado][ano_prob-1] + (concessoes[beneficio][ano_prob]/2))
                        
            # Adiciona no dicionário
            probabilidades[beneficio] = prob_entrada            
            # Substitui os NaN (not a number) por zeros
            probabilidades[beneficio].fillna(0, inplace = True)

    return probabilidades


'''
# VERSAO ORIGINAL
# Calcula probabilidades de entrada em benefícios
def calc_prob_apos(estoques, concessoes, periodo):

    probabilidades = {}       # Dicionário que salvas as prob. para cada benefício
    ano_prob = periodo[0]-1   # ano utilizado para cálculo (2014)
    ids_apos= ['Apin', 'Atcn', 'Apid', 'Atcp', 'Ainv', 'Atce', 'Atcd']

    # Dicionário que armazena o Estoque acumulado
    est_acumulado = {}

    # Acumula os estoques por Clientela, Sexo e Idade do ano anterior
    # As chaves do dicionário são as clientelas
    for clientela in ['UrbPiso', 'UrbAcim', 'Rur']:
        
        # Cria o DataFrame
        est_acumulado[clientela] = pd.DataFrame(index=range(0,91), columns=[ano_prob-1])
        # Preenche com zeros
        est_acumulado[clientela].fillna(0.0, inplace=True)
        
        # Obtem todos os benefícios de uma clientela específica e itera sobre eles
        for beneficio in get_id_beneficios([clientela]):
            # Verifica se o estoque para o benefício existe
            if beneficio in estoques.keys():                        
                est_acumulado[clientela] += estoques[beneficio]

    # Calcula probabilidades de entrada em aposentadorias
    for beneficio in get_id_beneficios(ids_apos):
        # Verifica se o possui os dados de estoque e concessões do benefício 
        if beneficio in estoques.keys() and beneficio in concessoes.keys():

            clientela = get_clientela(beneficio)
            
            # Calcula a probabilidade de entrada
            # Nesse caso prob_entrada é do tipo Series e não DataFrame, pois
            # Possui somente uma dimensão (não possui colunas)
            prob_entrada = concessoes[beneficio][ano_prob] / (est_acumulado[clientela][ano_prob-1] + (concessoes[beneficio][ano_prob]/2))
                        
            # Adiciona no dicionário
            probabilidades[beneficio] = prob_entrada            
            # Substitui os NaN (not a number) por zeros
            probabilidades[beneficio].fillna(0, inplace = True)

    return probabilidades
'''

# Calcula probabilidades de entrada em auxílios
def calc_prob_aux(segurados, estoques, concessoes, periodo):

    probabilidades = {}       # Dicionário que salvas as prob. para cada benefício
    ano_prob = periodo[0]-1   # ano utilizado para cálculo

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    # O cálculo do Auxílio doença e diferente dos demais auxílios
    for beneficio in dados.get_id_beneficios(['Auxd']):
                
        # Verifica se o possui os dados de estoque e concessões do benefício
        if beneficio in estoques.keys() and beneficio in concessoes.keys():
            conc = concessoes[beneficio][ano_prob]
            id_seg = dados.get_id_segurados(beneficio)
            seg_ano_ant = segurados[id_seg][ano_prob-1]
            prob_auxd = conc / (seg_ano_ant + (conc/2))     # Eq 18 da LDO2018
            probabilidades[beneficio] = prob_auxd            
            probabilidades[beneficio].fillna(0, inplace = True)

    # Calcula probabilidades de entrada em auxílios reclusão e acidente
    for beneficio in dados.get_id_beneficios(['Auxa' ]):#, 'Auxr']):
        # Verifica se o possui os dados de estoque e concessões do benefício
        if beneficio in estoques.keys():
            est = estoques[beneficio][ano_prob]
            id_seg = dados.get_id_segurados(beneficio)
            seg = segurados[id_seg][ano_prob]
            # REVISAR, para o caso do Auxr tem-se muitas divisões por zero, gerando inf
            prob_aux_ar = est / seg                        # Eq 19 da LDO 2018
            probabilidades[beneficio] = prob_aux_ar
            probabilidades[beneficio].fillna(0, inplace = True)

    
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

    tags = ['Apin', 'Atcn', 'Apid', 'Atcp', 'Ainv', 'Atce', 'Atcd', 'Pens']

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    # Calcula o fator de ajuste para cada tipo de aposentadoria
    for beneficio in dados.get_id_beneficios(tags):

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


# Calcula probabilidades para pensões
def calc_prob_pensao(concessoes, prob_mort, fam, periodo):
    
    # ano utilizado para cálculo
    #ano_prob = periodo[0]-1   #2014

    # Dicionário que armazena as probabilidades
    prob_pensao = {}

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    # ???
    def get_ji(idade):
        
        if idade <= 23:
            return 3
        elif idade >=27 and idade <=32:
            return 6
        elif idade >=37 and idade <=39:
            return 10
        elif idade >=45 and idade <=55:
            return 15
        elif idade >=61 and idade <=63:
            return 20
        else:
            return 0

     # Calcula a probabilidade para cada tipo de pensão
    for beneficio in dados.get_id_beneficios(['Pens']):
        
        sexo = beneficio[-1]
        
        # Verifica se existe dados de estoque
        if beneficio in concessoes.keys():
            for ano in periodo:
                # começo a partir de 3 pois o Ji pode ser 3.
                for idade in range(3,91):
                    ji = get_ji(idade)
                    conc = concessoes[beneficio][ano-ji][idade-ji]
                    ''' 
                    produtorio = 1
                    k = idade-ji
                    for i in range(k,idade):                        
                        pmorte = prob_mort['Mort'+sexo][ano-(i-k)][k]
                        fator = fam['fam'+beneficio][ano-(i-k)][k]
                        produtorio *= 1 - pmorte * fator
                        
                    prob_pensao[beneficio][ano] = conc * produtorio
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

# Verifica todos os valores de probabilidades calculados e indica aqueles
# maiores que 1 ou se todos são iguais a zero
def busca_erros(probabilidades):

    # Lista que salva os problemas
    problemas = {}
    # Verifica se existe probabilidades maiores que 1
    for p in probabilidades:
        
        # Pula os fatores de ajuste de mortalidade
        if p[:3] == 'fam':
            continue
        
        # Se existe algum elemento em alguma coluna maior que 0.99
        if (probabilidades[p] > 0.99).any().any():
            # Salva o benefício e uma tabela com os valores maires que 0.99
            problemas[p] = probabilidades[p][probabilidades[p].gt(0.99)].dropna()
        
        # Verifica se todos os valores são zero
        elif (probabilidades[p] == 0.0).all().all():
            problemas[p] = 'Todas as probabilidades são zero'

    if bool(problemas):
        print('Problemas nas probabilidades\n')
        for p in problemas:
            print('Tabela: %s' %p)
            print(problemas[p])
            print('_________________\n')
