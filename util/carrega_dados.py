# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

import pandas as pd


# Função que retorna uma lista de benefícios de acordo como filtro
def get_beneficios(filtros=[], info=''):

# A tag info é usada no momento de leitura das tabelas no arquivo
# Es = estoque
# Co = conceções
# Ce = cessações

# Exemplos de filtros:
# Apin = Aposentadoria por Invalidez
# Auxd = Auxílio doença
# SalMat = Salário Maternidade
    
    # Lista com todos os benefícios utilizando o mesmo padrão do simulador da Fazenda    
    beneficios = ["ApinUrbPisoH", "ApinUrbPisoM", "ApidUrbPisoH", "ApidUrbPisoM",
                      "AtcnUrbPisoH", "AtcnUrbPisoM", "AtceUrbPisoH", "AtceUrbPisoM",
                      "AtcpUrbPisoH", "AtcpUrbPisoM", "AtcdUrbPisoH", "AtcdUrbPisoM",
                      "AinvUrbPisoH", "AinvUrbPisoM", 

                      "ApinRurH", "ApinRurM", "ApidRurH", "ApidRurM",
                      "AtcnRurH", "AtcnRurM", "AtceRurH", "AtceRurM",
                      "AtcpRurH", "AtcpRurM", "AtcdRurH","AtcdRurM",
                      "AinvRurH", "AinvRurM",  

                      "ApinUrbAcimH", "ApinUrbAcimM", "ApidUrbAcimH", "ApidUrbAcimM", 
                      "AtcnUrbAcimH", "AtcnUrbAcimM", "AtceUrbAcimH", "AtceUrbAcimM", 
                      "AtcpUrbAcimH", "AtcpUrbAcimM", "AtcdUrbAcimH", "AtcdUrbAcimM",
                      "AinvUrbAcimH", "AinvUrbAcimM", 
             
                      "AuxdUrbPisoH", "AuxdUrbPisoM", "AuxdRurH", "AuxdRurM",                
                      "AuxdUrbAcimH", "AuxdUrbAcimM", "AuxaUrbPisoH", "AuxaUrbPisoM",
                      "AuxrUrbPisoH", "AuxrUrbPisoM", "AuxaRurH", "AuxaRurM", 
                      "AuxrRurH", "AuxrRurM", "AuxaUrbAcimH",
                      "AuxaUrbAcimM", "AuxrUrbAcimH", "AuxrUrbAcimM",
             
                      "SalMatUrbPisoM","SalMatRurM", "SalMatUrbAcimM" , 
                      "PensUrbPisoH", "PensUrbPisoM", "PensRurH", 
                      "PensRurM", "PensUrbAcimH", "PensUrbAcimM" , 
                      "LoasIdoH", "LoasIdoM", "LoasDefH", 
                      "LoasDefM", "RmvH", "RmvM"]
    
    # lista que será retornada
    lista_final = []
    
    # Verifica se a lista está vazia, nesse caso retorna todos os benefícios
    if len(filtros) == 0:   
        for l in beneficios:
            lista_final.append(info+l)       
    
    # Aplica o filtro na lista
    else:
        for f in filtros:  
            for l in beneficios:
                if f in l:
                    lista_final.append(info+l)  
    
    return lista_final


# Função que extrai as tabelas do arquivo
# Recebe o arquivo (planilha) e a lista de tabelas a serem extraídas
def get_tabelas(lista, arquivo, info=False):

    # Dicionário que salva as tabelas
    colecao_tabelas = {}

    # Lista com as tabelas com dados ausentes
    tabsIncompletas = []
    tabsInexistentes = []

    # Lê cada uma das tabelas dentro do arquivo
    # Converte cada tabela em um DataFrame e salva no dicionário
    for i in lista:
                
        # Remove os 2 primeiro caracteres para o caso de estoques, concessões
        # ou cessações (ex: 'EsApidRurH' -> 'ApidRurH')
        if i[0:2] in ['Es', 'Co', 'Ce']:            
            chave = i[2:]  
        else:
            chave = i
            
        try:
            colecao_tabelas[chave] = xls.parse(i, index_col=0)              # Converte a tabela para um DataFrame
            colecao_tabelas[chave].drop('Total', inplace=True)              # Elimina a linha 'Total'
            colecao_tabelas[chave].dropna(thresh=89, axis=1, inplace=True)  # Elimina colunas com dados ausentes
            colecao_tabelas[chave].dropna(how='all', inplace=True)          # Elimina linhas completamente vazias

            # Remove as tabelas que possuem dados ausentes
            if colecao_tabelas[chave].empty:
                tabsIncompletas.append(i)   # Salva o nome da tabela incompleta
                colecao_tabelas.pop(chave)  # Remove a tabela

        except:
            # Salva o nome das tabelas que não existem
            tabsInexistentes.append(i)

    if info:
        print('Total de tabelas de carregadas: %s' % len(colecao_tabelas))
        print('Total de tabelas inexistentes: %s' % len(tabsInexistentes))
        print('Total de tabelas incompletas e removidas: %s \n' % len(tabsIncompletas))

    return colecao_tabelas


'''
Lista de Siglas:
Apos ― Aposentadorias
Apin ― Aposentadoria por Idade (Normal ou Usual)
Apid ― Aposentadoria por Idade da Pessoa com Deficiência
Atcn ― Aposentadoria por Tempo de Contribuição (Normal ou Usual)
Atce ― Aposentadoria por Tempo de Contribuição Especial
Atcp ― Aposentadoria por Tempo de Contribuição do(a) Professor(a)
Atcd ― Aposentadoria por Tempo de Contribuição da Pessoa com Deficiência
Ainv ― Aposentadoria por Invalidez
Aux ― Auxílios
Auxd ― Auxílio-Doença
Auxa ― Auxílio-Acidente
Auxr ― Auxílio-Reclusão
SalMat ― Salário-Maternidade
PensTot – Pensões por Morte Totais (Tipo A + Tipo B)
PensTipoA – Pensões Tipo A (anteriores à Lei nº 13.135/2015)
PensTipoB – Pensões Tipo B (a partir da Lei nº 13.135/2015)
LoasIdo ― Amparo Assistencial da Lei Orgânica da Previdência Social (LOAS) ao Idoso
LoasDef ― Amparo Assistencial da LOAS da Pessoa com Deficiência
RmvIda ― Renda Mensal Vitalícia (RMV) por Idade
RmvInv ― Renda Mensal Vitalícia (RMV) por Invalidez
Client ― Clientela
Rur ― Clientela Rural
Urb ― Clientela Urbana
Piso ― Clientela Urbana Piso Previdenciário
Acim ― Clientela Urbana Acima do Piso Previdenciário
Sm – Clientela Urbana Contribuinte Salário Mínimo
AcimSm – Clientela Urbana Contribuinte Acima do Salário Mínimo
Seg ― Segurados
H ― Homens
M ― Mulheres
Pop – População
Mort – Mortalidade
Txmortimpl ― Taxa de Mortalidade Implícita da População

'''