# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

from util.tabelas import LerTabelas
import pandas as pd


# Calcula probabilidades de entrada em benefícios - Equação 16 da lDO
def calc_prob_apos(segurados, concessoes, periodo):

    probabilidades = {}       # Dicionário que salvas as prob. para cada benefício
    ano_prob = periodo[0]-1   # ano utilizado para cálculo (2014)
    ids_apos= ['Apin', 'Atcn', 'Apid', 'Atcp', 'Ainv', 'Atce', 'Atcd']

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    # Calcula probabilidades de entrada em aposentadorias
    for beneficio in dados.get_id_beneficios(ids_apos):
        
        # Verifica se existem dados de concessões do benefício 
        if beneficio in concessoes.keys():

            id_segurado = dados.get_id_segurados(beneficio)
            
            # Calcula a probabilidade de entrada
            # Nesse caso prob_entrada é do tipo Series e não DataFrame, pois
            # Possui somente uma dimensão (não possui colunas/anos)
            # A versão da LDO trabalha com estoques, porém o correto seriam os segurados
            # Eq. 16
            prob_entrada = concessoes[beneficio][ano_prob] / (segurados[id_segurado][ano_prob-1] + (concessoes[beneficio][ano_prob]/2))
                        
            # Adiciona no dicionário
            probabilidades[beneficio] = prob_entrada            
            # Substitui os NaN (not a number) por zeros
            probabilidades[beneficio].fillna(0, inplace = True)

    return probabilidades


'''
# VERSAO ORIGINAL - Equação 16
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

# Calcula probabilidades de entrada em auxílios - Equações 18 e 19 da LDO de 2018
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
            prob_auxd = conc / (seg_ano_ant + (conc/2))      # Eq. 18
            
            # Substitui os NaN por zero
            prob_auxd.fillna(0, inplace = True)
            probabilidades[beneficio] = prob_auxd
            

    # Calcula probabilidades de entrada em auxílios reclusão e acidente
    for beneficio in dados.get_id_beneficios(['Auxa' ]):#, 'Auxr']):
        # Verifica se o possui os dados de estoque e concessões do benefício
        if beneficio in estoques.keys():
            est = estoques[beneficio][ano_prob]
            id_seg = dados.get_id_segurados(beneficio)
            seg = segurados[id_seg][ano_prob]
            # REVISAR, para o caso do Auxr tem-se muitas divisões por zero, gerando inf
            prob_aux_ar = est / seg                        # Eq. 19
            
            # Substitui os NaN por zero
            prob_aux_ar.fillna(0, inplace = True)
            probabilidades[beneficio] = prob_aux_ar

    
    return probabilidades


# Calcula probabilidade de morte baseado no método da fazenda
# Equações 12 e 13 da LDO de 2018
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

                mortalidade = (pop_ano_passado - pop_atual)/2 + (pop_atual - pop_prox_ano)/2    # Eq. 13
                mort[ano][idade] = mortalidade/pop_atual                                        # Eq. 12

            # Calculo para a idade de 90 anos - REVISAR
            # Como não é possível usar a Eq. 13 para a idade de 90 anos, usou-se o método da UFPA
            mort[ano][90] = 1 - (pop[chave_pop][ano+1][90] - pop[chave_pop][ano][89] * (1 - mort[ano][89])) / pop[chave_pop][ano][90]
            #mort[ano][90] = (pop[chave_pop][ano-1][90] - pop[chave_pop][ano-1][89]) / pop[chave_pop][ano][90]

            # Para idade 0 anos  = (pop_atual - pop_prox_ano)/ pop_atual
            mort[ano][0] = ( pop[chave_pop][ano][0] - pop[chave_pop][ano+1][1])/pop[chave_pop][ano][0]

        # Repete a Prob do ultimo ano como valor do antepenultimo
        mort[periodo[-1]] = mort[periodo[-2]]

        # Adiciona o DataFrame no dicionário com as chaves 'MortH' e 'MortM'
        mort.dropna(how='all', axis=1, inplace=True)  # Elimina colunas com dados ausentes
        probMorte['Mort'+sexo] = mort

    return probMorte


# Calcula o Fator de Ajuste de Mortalidade - Equações 14 e 15 - REVISAR - gera probabilidades zero que quando usadas nas equações zera tudo
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

            # Taxa de cessações - Eq. 15 - REVISAR (ver PDF comentado)
            tx_ces = ces_ano_atual/(est_ano_ant + (ces_ano_atual/2))
            
            # Probabilidade de morte
            mort = probMort['Mort'+beneficio[-1]][ano_prob]

            # Salva a Série no dicionário - Eq. 14
            fat_ajuste['fam'+beneficio] = tx_ces/mort

            # Substitui os NaN por zero
            fat_ajuste['fam'+beneficio].fillna(0, inplace=True)

    return fat_ajuste # REVISAR - Confirmar se é fixa para todos os anos


# Calcula probabilidades para pensões
def calc_prob_pensao(concessoes, prob_mort, fam, periodo):
    pass


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
