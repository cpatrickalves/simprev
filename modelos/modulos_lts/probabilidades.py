# -*- coding: utf-8 -*-
"""
@author: Patrick Alves

Versão com as correções nas estimativas de probabilidade
Usa os contribuintes ao invés da população ocupada
"""

from util.tabelas import LerTabelas
from modelos.modulos_fazenda.estoques import calc_estoq_apos_acumulado
import pandas as pd
import numpy as np


# Calcula probabilidades de entrada em aposentadorias
# Calculo baseado nas planilhas do DOC110/MF
def calc_prob_apos(segurados, concessoes, periodo):

    probabilidades = {}       # Dicionário que salvas as prob. para cada benefício
    
    ids_apos= ['Apin', 'Atcn', 'Apid', 'Atcp', 'Ainv', 'Atce', 'Atcd']

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    # Obtém a lista de aposentadorias e itera sobre cada tipo
    for beneficio in dados.get_id_beneficios(ids_apos):
        
        # Verifica se existem dados de concessões do benefício 
        if beneficio in concessoes.keys():            
            id_seg = dados.get_id_segurados(beneficio)         # ex: CsmUrbH

            # OBS: A implementação descritas nas planilhas do DOC110/MF usa uma equação diferente da Eq. 16
            # prob_entrada = concessoes/PopOcupada                         
            prob_entrada = concessoes[beneficio] / segurados[id_seg]
            
            # Trata divisões por zero
            prob_entrada.replace([np.inf, -np.inf], np.nan, inplace = True)
            
            # De acordo com as planilhas do DOC110/MF o valor do ano inicial da projeção (2015), deve ser igual a média dos anos anteriores         
            prob_entrada[2015] = prob_entrada.loc[:,:2014].mean(axis=1)
            
            # Repete a última probabilidade(2015) nos anos seguintes(2016-2060)      
            for ano in periodo[1:]:
                prob_entrada[ano] = prob_entrada[ano-1]
            
            # Substitui os NaN (not a number) por zeros
            prob_entrada.fillna(0, inplace = True)

            # Adiciona no dicionário
            probabilidades[beneficio] = prob_entrada            
                       

    return probabilidades


# Calcula probabilidades de entrada em auxílios baseado nas planilhas do DOC110/MF
def calc_prob_aux(segurados, estoques, concessoes, periodo):

    probabilidades = {}       # Dicionário que salvas as prob. para cada benefício
    ano_prob = periodo[0]-1   # ano utilizado para cálculo (2014)

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    # De acordo com as planilhas do DOC110/MF
    # ProbAuxDoenca = Concedidos/popOcupada
    # ProbAuxAcidente = Estoque/popOcupada
    # ProbAuxReclusão = Estoque/popOcupada(somando a idade com 25)

    # O cálculo do Auxílio doença e diferente dos demais auxílios
    for beneficio in dados.get_id_beneficios(['Auxd']):
                
        # Verifica se o possui os dados de estoque e concessões do benefício
        if beneficio in estoques.keys() and beneficio in concessoes.keys():            
            id_seg = dados.get_id_segurados(beneficio)         # ex: CsmUrbH
            
            # concessões conhecidas dos últimos 4 anos (2011-2014)
            conc = concessoes[beneficio].loc[:,(ano_prob-3):] 
            
            seg = segurados[id_seg].loc[:,(ano_prob-3):]
                
            prob_auxd = conc / seg
            
            # Substitui os NaN por zero
            prob_auxd.replace([np.inf, -np.inf], np.nan, inplace = True)
            prob_auxd.fillna(0, inplace = True)
            # Remove colunas com todos os valores iguais a zero
            prob_auxd = prob_auxd.loc[:, (prob_auxd != 0).any(axis=0)]
                        
            # Repete a última probabilidade(2014) nos anos seguintes(2015-2060)      
            for ano in periodo:
                prob_auxd[ano] = prob_auxd[ano-1]
            
            probabilidades[beneficio] = prob_auxd
            

    # Calcula probabilidades de entrada em auxílio acidente
    for beneficio in dados.get_id_beneficios(['Auxa']):
        # Verifica se o possui os dados de estoque e concessões do benefício
        if beneficio in estoques.keys():
            id_seg = dados.get_id_segurados(beneficio)         # ex: CsmUrbH
            # estoques conhecidos dos últimos 4 anos (2011-2014)
            est = estoques[beneficio].loc[:,(ano_prob-3):] 
            
            seg = segurados[id_seg].loc[:,(ano_prob-3):] 
                
            prob_auxa = est / seg                        
            
            # Substitui os inf e NaN por zero
            prob_auxa.replace([np.inf, -np.inf], np.nan, inplace = True)
            prob_auxa.fillna(0, inplace = True)
            
            # Remove colunas com todos os valores iguais a zero
            prob_auxa = prob_auxa.loc[:, (prob_auxa != 0).any(axis=0)]
            
            # para o ano seguinte ao do estoque (2015) a probabilidade é a média dos anos anteriores
            # OBS: Para algumas clientelas as Planilhas repetem o último ano
            prob_auxa[2015] = prob_auxa.loc[:,:2014].mean(axis=1)
            
            # Repete a última probabilidade(2015) nos anos seguintes(2016-2060)      
            for ano in periodo[1:]:
                prob_auxa[ano] = prob_auxa[ano-1]
            
            probabilidades[beneficio] = prob_auxa


    # Calcula probabilidades de entrada em auxílio reclusão
    for beneficio in dados.get_id_beneficios(['Auxr']):
        # Verifica se o possui os dados de estoque e concessões do benefício
        if beneficio in estoques.keys():
            sexo = beneficio[-1]    
            id_seg = dados.get_id_segurados(beneficio)         # ex: CsmUrbH
            
            # Cria objeto do tipo DataFrame
            prob_auxr = pd.DataFrame(0.0, index=range(0,91), columns=[ano_prob]+periodo)
            deslocamento = 0
            
            for idade in range(0,91):
                est = estoques[beneficio][ano_prob][idade]                
                
                # Na planilha são aplicados deslocamentos nas idades
                if idade < 61 and sexo == 'H': 
                    deslocamento = 25
                elif idade < 61 and sexo == 'M': 
                    deslocamento = 18                    
                else:
                    deslocamento = 0
                
                id_seg = dados.get_id_segurados(beneficio)         # ex: CsmUrbH                
                
                # OBS: para o AuxReclusao o sexo utilizado na popOcup é sempre masculino
                if 'Rur' in id_seg:
                    id_seg = 'RurH'
                  
                seg = segurados[id_seg][ano_prob][idade+deslocamento]                        
                
                if seg == 0:
                    prob_auxr[ano_prob][idade] = 0
                else:                        
                    prob_auxr[ano_prob][idade] = est / seg                        
            
            # Substitui os NaN por zero
            prob_auxr.replace([np.inf, -np.inf], np.nan, inplace = True)
            prob_auxr.fillna(0, inplace = True)
            
            # Repete a última probabilidade(2014) nos anos seguintes(2015-2060)      
            for ano in periodo:
                prob_auxr[ano] = prob_auxr[ano-1]
            
            probabilidades[beneficio] = prob_auxr

    
    return probabilidades


# Calcula probabilidade de Morte
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
            for idade in range(1,89): # Vai de 1 até 88 anos
                pop_atual = pop[chave_pop][ano][idade]
                pop_ano_passado = pop[chave_pop][ano-1][idade-1]
                pop_prox_ano = pop[chave_pop][ano+1][idade+1]
                                
                mortalidade = (pop_ano_passado - pop_atual)/2 + (pop_atual - pop_prox_ano)/2    # Eq. 13
                mort[ano][idade] = mortalidade/pop_atual                                        # Eq. 12

            # Calculo para as idades de 89 e 90 anos 
            # Cálculo baseado nas Equações descritas nas planilhas do DOC110/MF
            # 89 anos
            mort[ano][89] = (pop[chave_pop][ano-1][88] - pop[chave_pop][ano][89]) / pop[chave_pop][ano][89]            
            # 90 anos
            mort[ano][90] = (pop[chave_pop][ano-1][89] + pop[chave_pop][ano-1][90] - pop[chave_pop][ano][90]) / pop[chave_pop][ano][90]

            # Para idade 0 anos  = (pop_atual - pop_prox_ano)/ pop_atual
            mort[ano][0] = (pop[chave_pop][ano][0] - pop[chave_pop][ano+1][1])/pop[chave_pop][ano][0]

        # Repete a Prob do ultimo ano como valor do antepenultimo
        mort[periodo[-1]] = mort[periodo[-2]]

        mort.dropna(how='all', axis=1, inplace=True)  # Elimina colunas com dados ausentes
        # Adiciona o DataFrame no dicionário com as chaves 'MortH' e 'MortM'
        probMorte['Mort'+sexo] = mort

    return probMorte


# Calcula o Fator de Ajuste de Mortalidade (FAM) de acordo com a Planilhas do DOC110/MF
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
            
            # A Equação utilizada nas planilhas do MF é diferente da descrita na LDO de 2018 (Eq. 14 e 15)
            # fam = 1, se Cessações = 0
            # fam = (Cessações/Estoque)/txMort
            
            txCes = cessacoes[beneficio] / estoques[beneficio]
            fam = txCes / probMort['Mort'+sexo]
            
            # Elimina colunas com dados ausentes
            fam.dropna(how='all', axis=1, inplace=True)  
            
            # Elimina o ano de 2010 (não é utilizado nas planilhas)
            if 2010 in fam.columns:
                fam.drop(2010, axis=1, inplace=True)
                
            # Trata divisões por zero (gera o valo inf)
            fam.replace([np.inf, -np.inf], np.nan, inplace = True)
            # Garante que não existe valor zero
            fam.replace(0, 1.0, inplace = True)
            # Substitui os NaN por 1.0
            fam.fillna(1.0, inplace=True)
            
            # Para o primeiro ano de projeção (2015), o FAM é igual a média dos anos anteriores
            # Exceto para os Rurais e assistenciais, onde o FAM é igual ao do ano anterior
            if dados.get_clientela(beneficio) == 'Rur' or 'Loas' in beneficio:
                fam[ano_prob+1] = fam[ano_prob]
            else:
                fam[ano_prob+1] = fam.loc[:,:ano_prob].mean(axis=1)
                            
            # Para os anos seguintes o FAM é constante
            for ano in periodo[1:]:
                fam[ano] = fam[ano-1]
            
            # Lógica usada nas planilhas do MF para as Pensões
            # Garante que o beneficiário pare de receber pensão aos 21 anos
            # fam = 1/ProbMorte
            if 'Pens' in beneficio:
                for ano in periodo:                
                    fam.loc[21,ano] = 1/probMort['Mort'+sexo].loc[21,ano]
            
            # Salva no dicionário
            fat_ajuste['fam'+beneficio] = fam
            
        
    return fat_ajuste 


# Calcula probabilidades para pensões baseado nas planilhas do DOC110/MF
def calc_prob_pensao(concessoes, segurados, populacao, estoque, prob_morte, periodo):
    
    # A LDO de 2018 não descreve como calcular as probabilidades para pensões
    # As equações abaixo foram extraídas das planilhas do MF
    
    probabilidades = {}             # Dicionário que salvas as prob. para cada benefício
    ano_estoque = periodo[0] - 1    # 2014
    
    # Eq. 26: Dit = Idh - Idm
    # Hipótese de que o diferencial de idade médio entre cônjuges é de 4 anos (pag. 45 LDO de 2018)
    Dit = 4
        
    lista = LerTabelas()
    est_apos_acumulado = calc_estoq_apos_acumulado(estoque, periodo)   

    for beneficio in lista.get_id_beneficios('Pe'):
        
        # Cria Objeto do tipo Serie que armazena as probabilidades
        probabilidades[beneficio] = pd.Series(0.0, index=range(0,91))
        
        sexo = beneficio[-1]                                # Última letra do benefício
        sexo_oposto = 'M' if sexo=='H' else 'H'             # Obtém o oposto
        clientela = lista.get_clientela(beneficio)
        id_conc = beneficio.replace(sexo, sexo_oposto)      # Troca o sexo do benefício
        # OBS: Sempre são usados os segurados do sexo masculino
        id_segurados = lista.get_id_segurados(beneficio).replace(sexo, 'H')  
        
        # Para cada idade i
        for idade in range(0,91):
           
            if idade > 20 and idade < 87:
                Dit = 4
            elif idade == 87:
                Dit = 3
            elif idade == 88:
                Dit = 2
            elif idade == 89:
                Dit = 1
            else:
                Dit = 0
                        
            # A soma ou subtração depende do sexo
            if sexo == 'M':
                i_Dit = idade + Dit
            else:
                i_Dit = idade - Dit
            
            # Trata valores negativos e maiores que 90 para i_Dit
            if i_Dit < 0:
                i_Dit = 0
            
            if i_Dit > 90:
                i_Dit = 90
                
            conc = concessoes[id_conc][ano_estoque][i_Dit]
            pmorte = prob_morte['Mort'+sexo][ano_estoque][idade]
            
            # Para os urbanos com idade de 15 anos e para os rurais utiliza-se toda a população por clientela simples (Urb ou Rur)
            if idade < 16 or clientela == 'Rur':
                clientela_simples = clientela[0:3] 
                potGeradoresPensoes = populacao['Pop' + clientela_simples + sexo][ano_estoque][idade]
            else:
                seg = segurados[id_segurados][ano_estoque][idade]
                est_ac = est_apos_acumulado[clientela+sexo][ano_estoque][idade]
                potGeradoresPensoes = seg + est_ac
                               
            # Evita divisões por zero
            if potGeradoresPensoes == 0:
                probPensao = 0
            else:
                # Equação baseada nas Eq. 24 e 25
                # OBS: Essa equação gera probabilidades maiores que 1 
                probPensao = conc / (potGeradoresPensoes * pmorte)                                 
                
            probabilidades[beneficio][idade] = probPensao
                
    return probabilidades


# Calcula probabilidades de entrada em benefícios assistênciais baseado nas planilhas do MF
def calc_prob_assist(populacao, concessoes, periodo):

    probabilidades = {}       # Dicionário que salvas as prob. para cada benefício    
    ano_estoq = periodo[0]-1   # 2014
    ids_assist = ['LoasDef', 'LoasIdo']

    # Calcula probabilidades de entrada em benefícios assistênciais
    for tipo in ids_assist:
        for sexo in ['H', 'M']:            
            beneficio = tipo+sexo
            
            # Verifica se existem dados de concessões do benefício 
            if beneficio in concessoes.keys():                     
                # Cria DataFrame que armazena as probabilidades
                prob_assist = pd.DataFrame(0.0, index=range(0,91), columns=concessoes[beneficio].columns)
                
                id_pop = "PopIbge"+sexo # REVISAR 
                
                # Para os anos de 2011-2014
                for ano in prob_assist.columns:                
                    # Calcula a probabilidade de entrada  
                    conc = concessoes[beneficio][ano]
                    pop = populacao[id_pop][ano]
                                        
                    # Calcula probabilidade
                    # OBS: Para o LoasDef na idade zero utiliza-se o estoque ao inves das concessoes
                    prob_assist[ano] = conc / pop
                                    
                # Substitui os NaN (not a number) por zeros
                prob_assist.fillna(0, inplace = True)
                
                # Se for Loas Deficiente
                if 'Def' in beneficio:
                    # Repete a última prob nos anos seguintes                
                    for ano in periodo:
                        prob_assist[ano] = prob_assist[ano-1]
                # Se Loas Idoso
                else:                    
                    # O ano de 2015 é igual ao MAIOR valor dos últimos 4 anos
                    prob_assist[2015] = prob_assist.loc[:,:ano_estoq].max(axis=1)
                    
                    # Repete a última prob nos anos seguintes                
                    for ano in periodo[1:]:
                        prob_assist[ano] = prob_assist[ano-1]
                
                # Adiciona no dicionário
                probabilidades[beneficio] = prob_assist
     
    #  Probabilidade de Concessão no RMV é nula, pois o benefício está em extinção (sem novas concessões)
    for sexo in ['H', 'M']:    
          probabilidades['Rmv'+sexo] = pd.Series(0, index=range(0,91))
                                
    return probabilidades
