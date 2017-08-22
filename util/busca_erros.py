# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

# Corrige inconsistências nos estoques
def corrige_erros_estoque(estoques, concessoes, cessacoes):
    """
    Identifica idades em que o número de Concessões não bate com o Estoque do ano e idade seguintes
    e faz uma correção. Essas correções são utilizadas nos cálculos das probabilidades
    
    :param estoques: dicionário com os estoques 
    :param concessoes: dicionário com as concessões
    :param cessacoes: dicionário com as cessações
    :return: 
    """

    count = 0
    # Para todos os benefícios...
    for beneficio in concessoes:
        # Verifica se existe o benefício nas outras tabelas
        if beneficio in estoques.keys() and beneficio in cessacoes.keys():
            for ano in concessoes[beneficio]:
                for idade in range(1,90):
                    con = concessoes[beneficio][ano][idade]
                    est = estoques[beneficio][ano][idade]
                    ces = cessacoes[beneficio][ano][idade]

                    # Identifica idades em que o número de Concessões é maior que o Estoque do ano e idade seguinte
                    if con - ces > est:
                        #print('{} | ano = {}| id = {} | Con = {} | Ces = {} | Est = {}'.format(beneficio, ano, idade,con,ces,est))
                        
                        # Corrige o estoque para as idades onde o erro foi encontrado
                        estoques[beneficio].loc[idade, ano] = round(con - ces)
                        
                        count+=1
    #print('Quantidade de erros encontrados: {}'.format(count))
    
    return estoques

    
# Verifica todos os valores de probabilidades calculados e indica aqueles
# maiores que 1 ou se todos são iguais a zero
def busca_erros_prob(probabilidades):

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
            
        # Se existe algum elemento em alguma coluna com valor negativo
        if (probabilidades[p] < 0).any().any():
            # Salva o benefício e uma tabela com os valores maires que 0.99
            problemas[p] = probabilidades[p][probabilidades[p].lt(0)].dropna()
        

    if bool(problemas):
        print('Problemas nas probabilidades\n')
        for p in problemas:
            print('Tabela: %s' %p)
            print(problemas[p])
            print('_________________\n')
