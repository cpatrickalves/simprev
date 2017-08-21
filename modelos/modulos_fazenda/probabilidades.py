# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

from util.tabelas import LerTabelas
from modelos.modulos_fazenda.estoques import calc_estoq_acumulado
import pandas as pd


# Calcula probabilidades de entrada em aposentadorias - Equação 16 da lDO de 2018
def calc_prob_apos(segurados, concessoes, periodo):

    probabilidades = {}       # Dicionário que salvas as prob. para cada benefício
    ano_prob = periodo[0]-1   # ano utilizado para cálculo (2014)
    ids_apos= ['Apin', 'Atcn', 'Apid', 'Atcp', 'Ainv', 'Atce', 'Atcd']

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    # Obtém a lista de aposentadorias e itera sobre cada tipo
    for beneficio in dados.get_id_beneficios(ids_apos):
        
        # Verifica se existem dados de concessões do benefício 
        if beneficio in concessoes.keys():

            id_segurado = dados.get_id_segurados(beneficio)
            
            # Calcula a probabilidade de entrada
            # Nesse caso prob_entrada é do tipo Series e não DataFrame, pois
            # Possui somente uma dimensão (é fixa para o ano = ano_prob)
            # A versão da LDO trabalha com estoques, porém o correto seriam os segurados
            # Eq. 16
            prob_entrada = concessoes[beneficio][ano_prob] / (segurados[id_segurado][ano_prob-1] + (concessoes[beneficio][ano_prob]/2))
                        
            # Adiciona no dicionário
            probabilidades[beneficio] = prob_entrada            
            # Substitui os NaN (not a number) por zeros
            probabilidades[beneficio].fillna(0, inplace = True)

    return probabilidades


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


# Calcula probabilidade de morte
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
                
                # Como a idade 90 anos agrega as seguintes (91,92,etc.) é necessário o calculo abaixo
                if idade == 89:
                    pop_prox_ano = pop_prox_ano - pop[chave_pop][ano][90]
                
                mortalidade = (pop_ano_passado - pop_atual)/2 + (pop_atual - pop_prox_ano)/2    # Eq. 13
                mort[ano][idade] = mortalidade/pop_atual                                        # Eq. 12

            # Calculo para a idade de 90 anos - REVISAR
            # Como não é possível usar a Eq. 13 para a idade de 90 anos, usou-se o método da UFPA
            mort[ano][90] = 1 - (pop[chave_pop][ano+1][90] - pop[chave_pop][ano][89] * (1 - mort[ano][89])) / pop[chave_pop][ano][90]
            #mort[ano][90] = (pop[chave_pop][ano-1][90] - pop[chave_pop][ano-1][89]) / pop[chave_pop][ano][90]

            # Para idade 0 anos  = (pop_atual - pop_prox_ano)/ pop_atual
            mort[ano][0] = (pop[chave_pop][ano][0] - pop[chave_pop][ano+1][1])/pop[chave_pop][ano][0]

        # Repete a Prob do ultimo ano como valor do antepenultimo
        mort[periodo[-1]] = mort[periodo[-2]]

        mort.dropna(how='all', axis=1, inplace=True)  # Elimina colunas com dados ausentes
        # Adiciona o DataFrame no dicionário com as chaves 'MortH' e 'MortM'
        probMorte['Mort'+sexo] = mort

    return probMorte


# Calcula o Fator de Ajuste de Mortalidade - Equações 14 e 15
# REVISAR - gera probabilidades zero que quando usadas nas equações zera tudo e
# algums valores de fam estão muito altos (>100)
def calc_fat_ajuste_mort(estoques, cessacoes, probMort, periodo):

    # ano utilizado para cálculo
    ano_prob = periodo[0]-1   #2014

    # Dicionário que armazena as probabilidades
    fat_ajuste = {}

    # Calculada para aposentadorias, pensões e assistênciais 
    tags = ['Apin', 'Atcn', 'Apid', 'Atcp', 'Ainv', 'Atce', 'Atcd', 
            'Pens', 'LoasDef', 'LoasIdo', 'Rmv']

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    # Calcula o fator de ajuste para cada tipo de aposentadoria
    for beneficio in dados.get_id_beneficios(tags):
        
        sexo = beneficio[-1]

        # Verifica se existem dados de estoque e cessações do benefício
        if beneficio in estoques.keys() and beneficio in cessacoes.keys():
            
            fat_ajuste['fam'+beneficio] = pd.Series(1, index=list(range(0,91)))
                      
            for idade in range(1,91):
                
                ces_ano_atual = cessacoes[beneficio][ano_prob][idade]
                est_ano_ant = estoques[beneficio][ano_prob-1][idade]
                
                # REVISAR: Gerar fam acima de 100 para alguns beneficios em idades baixas. 
                # Isso ocorre devido a pmorte ser muito baixa e os estoques serem muito 
                # pequenos ou zero.Ver pag. 18 do doc da fazenda                 
                
                # Taxa de cessações - Eq. 15
                tx_ces = ces_ano_atual/(est_ano_ant + (ces_ano_atual/2))
                
                # Probabilidade de morte
                mort = probMort['Mort'+sexo][ano_prob][idade]
    
                # Salva a Série no dicionário - Eq. 14
                fat_ajuste['fam'+beneficio][idade] = tx_ces/mort
                             
                # Substitui os NaN por zero
                fat_ajuste['fam'+beneficio].fillna(0, inplace=True)
            
            
    return fat_ajuste 


# Calcula probabilidades para pensões
# O modelo da LDO só considera pensões para o cônjuge
def calc_prob_pensao(concessoes, segurados, estoque, prob_morte, periodo):
    
    # A LDO de 2018 não descreve como calcular as probabilidades para pensões
    # As equações abaixo são resultado de manipulações das Equações 24 e 25 da LDO
    # Onde-se isolou-se a variável v para se chegar na equação de calculo das probabilidades
    
    probabilidades = {}             # Dicionário que salvas as prob. para cada benefício
    ano_estoque = periodo[0] - 1    # 2014
    
    # Eq. 26
    # Hipótese de que o diferencial de idade médio entre cônjuges é de 4 anos (pag. 45 LDO de 2018)
    Dit = 4
        
    lista = LerTabelas()
    est_acumulado = calc_estoq_acumulado(estoque, periodo)   

    for beneficio in lista.get_id_beneficios('Pe'):
        
        # Cria Objeto do tipo Serie que armazena as probabilidades
        probabilidades[beneficio] = pd.Series(0.0, index=range(0,91))
        
        sexo = beneficio[-1]                                # Última letra do benefício
        sexo_oposto = 'M' if sexo=='H' else 'H'             # Obtém o oposto
        clientela = lista.get_clientela(beneficio)
        id_conc = beneficio.replace(sexo, sexo_oposto)      # Troca o sexo do benefício
        id_segurados = lista.get_id_segurados(beneficio)
        
        # Para cada idade i
        for idade in range(0,91):
            
            # A soma ou subtração depende do sexo
            if sexo == 'M':
                i_Dit = idade - Dit
            else:
                i_Dit = idade + Dit
            
            # Trata valores negativos e maiores que 90 para i_Dit
            if i_Dit < 0:
                i_Dit = 0
            
            if i_Dit > 90:
                i_Dit = 90
                
            conc = concessoes[id_conc][ano_estoque][idade]
            seg = segurados[id_segurados][ano_estoque][i_Dit]
            est_ac = est_acumulado[clientela+sexo][ano_estoque][i_Dit]
            pmorte = prob_morte['Mort'+sexo][ano_estoque][i_Dit]
        
            # Se a quantidade de segurados e estoque for zero a prob daria infinito
            if seg == 0 and est_ac == 0:
                probPensao = 0
            else:
                # Equação baseada nas Eq. 26 e 27 - REVISAR
                # Essa equação gera probabilidades maiores que 1
                probPensao = conc / ((seg + est_ac) * pmorte)                 
                
            probabilidades[beneficio][i_Dit] = probPensao
                
    return probabilidades


# Calcula probabilidade de morte baseado no método do LTS/UFPA
# OBS: Mover para outro modelo
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
# REVISAR: Implementar Corrige erros
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



# Calcula probabilidades de entrada em benefícios assistênciais - Equação 31 da lDO
def calc_prob_assist(populacao, concessoes, periodo):

    probabilidades = {}       # Dicionário que salvas as prob. para cada benefício
    ano_prob = periodo[0]-1   # ano utilizado para cálculo (2014)
    ids_assist = ['LoasDef', 'LoasIdo']

    # Calcula probabilidades de entrada em aposentadorias
    for tipo in ids_assist:
        for sexo in ['H', 'M']:            
            beneficio = tipo+sexo
            
            # Verifica se existem dados de concessões do benefício 
            if beneficio in concessoes.keys():                            
                id_pop = "PopIbge"+sexo
                
                # Calcula a probabilidade de entrada  
                conc = concessoes[beneficio][ano_prob]
                pop_ant = populacao[id_pop][ano_prob-1]
                # Eq. 31
                prob_entrada = conc / (pop_ant + (conc/2))
                                
                # Substitui os NaN (not a number) por zeros
                prob_entrada.fillna(0, inplace = True)
                # Adiciona no dicionário
                probabilidades[beneficio] = prob_entrada
     
    #  Probabilidade de Concessão no RMV é nula, pois o benefício está em extinção (sem novas concessões)
    for sexo in ['H', 'M']:    
          probabilidades['Rmv'+sexo] = pd.Series(0, index=range(0,91))
                                
    return probabilidades

