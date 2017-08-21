# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.tabelas import LerTabelas
import pandas as pd


def calc_estoq_apos(est, conc, prob, seg, periodo):
    
    # Identificações das aposentadorias 
    ids_apos= ['Apin', 'Atcn', 'Apid', 'Atcp', 'Ainv', 'Atce', 'Atcd']

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    # Obtem as aposentadorias para todas as clientelas e sexos
    lista_benef = dados.get_id_beneficios(ids_apos)
        
    for benef in lista_benef:
        # Verifica se o beneficio existe no Estoque
        if benef in est:
        
            sexo = benef[-1]                             # Obtém o Sexo
            id_prob_morte = 'Mort'+ sexo                 # ex: MortH
            id_fam = 'fam'+benef                         # fator de ajuste de mortalidade
            id_segurado = dados.get_id_segurados(benef)  # ex: CsmUrbH
            
            for ano in periodo:                
                # Adiciona uma nova coluna (ano) no DataFrame com valores zero
                est[benef][ano] = 0
                
                # 1 a 90 anos - Equação 11 da LDO de 2018
                for idade in range(1,91): 
                    est_ano_anterior = est[benef][ano-1][idade-1]
                    prob_sobreviver = 1 - prob[id_prob_morte][ano][idade] * prob[id_fam][idade]
                    entradas = seg[id_segurado][ano][idade] * prob[benef][idade]
                    # Eq. 11
                    est[benef].loc[idade, ano] = est_ano_anterior * prob_sobreviver + entradas     # Eq. 11
                    # Salva a quantidade de concessões para uso posterior
                    conc[benef].loc[idade,ano] = entradas
                
                # Calculo para a idade zero
                est[benef].loc[0, ano] = seg[id_segurado][ano][0] * prob[benef][0]
                # Salva a quantidade de concessões para uso posterior
                conc[benef].loc[0, ano] = est[benef].loc[0, ano]
                
                # Ajuste para a idade de 90+ anos (modelo UFPA) - REVISAR
                #est[benef].loc[90, ano] = est[benef].loc[90, ano] + est[benef].loc[90, ano - 1]
                

    return est


# Projeta estoques para Auxílios Doença, Reclusão e Acidente - Equação 17 da LDO de 2018
def calc_estoq_aux(est, prob, seg, periodo):

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    for benef in dados.get_id_beneficios(['Auxd', 'Auxa']):#'Auxr']): # REVISAR
        # Verifica se existe no Estoque
        if benef in est:            
            id_seg = dados.get_id_segurados(benef)
            
            for ano in periodo:
                # REVISAR: a Equação original usa a Pop, mas o certo seria os Segurados
                est[benef][ano] = seg[id_seg][ano] * prob[benef]     # Eq. 17
    
    return est
                
            
# Projeta estoques para Salário-Maternidade - Equação 20 da LDO de 2018 - REVISAR
def calc_estoq_salMat(est, pop, seg, periodo):

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    for benef in dados.get_id_beneficios('SalMat'):            
        if benef in est:
            # Armazena valores do ano 
            est_acumulado = pd.Series(index=est[benef].columns)
            # Obtem o tipo de segurado a partir do benefício
            id_seg = dados.get_id_segurados(benef)
            
            # Os estoques de SalMat são agrupados por ano  
            # Acumula os estoques de mulheres ja presentes no estoque            
            for ano in est[benef]:    
                est_acumulado[ano] = est[benef][ano].sum()
                    
            # Realiza projeção    
            for ano in periodo:
                est_acumulado[ano] = 0     # Cria um novo ano 
                nascimentos = pop['PopIbgeM'][ano][0] + pop['PopIbgeH'][ano][0]
                
                # Acumula mulheres de 16 a 45 anos
                seg_16_45 = 0
                pop_16_45 = 0                                
                for idade in range(16,46):
                    seg_16_45 += seg[id_seg][ano][idade]
                    pop_16_45 += pop['PopIbgeM'][ano][idade]

                # Eq. 20
                est_acumulado[ano] = (seg_16_45/pop_16_45) * nascimentos    
            
            # Cria uma nova entrada no dicionário para armazenar os estoques acumulados
            est[benef+"_total"] = est_acumulado
            
    return est
    

# Projeta os estoque de pensões - Equações 21 a 27 da LDO de 2018
def calc_estoq_pensoes(est, concessoes, cessacoes, probabilidades, segurados, periodo):
    
    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()
    # Obtém o conjunto de benefícios do tipo pensão
    lista_pensoes = dados.get_id_beneficios('Pe')
    
    # Calcula pensões do tipo A
    for benef in lista_pensoes:   
        sexo = benef[-1]                # Obtém o Sexo
        id_prob_morte = 'Mort'+ sexo    # ex: MortH
        id_fam = 'fam'+benef            # fator de ajuste de mortalidade
        id_pens = benef+"_tipoA"        # Cria um Id para pensão do tipo A
        
        # Cria um novo DataFrame para Pensão do tipo A 
        est[id_pens] = pd.DataFrame(0.0, index=range(0,91), columns=[2014]+periodo)
        est[id_pens].index.name = "IDADE"    
        
        # Copia os dados de estoque de 2014
        est[id_pens][2014] = est[benef][2014]
        
        for ano in periodo:          
            
            # Adiciona uma nova coluna (ano) no DataFrame com valores zero
            est[id_pens][ano] = 0
            
            # Projeta pensões do tipo A
            # Como não se tem novas concessões desse tipo de pensão, calcula-se
            # somente nas idades de 1 a 90 anos.
            for idade in range(1,91):
                est_ano_anterior = est[id_pens][ano-1][idade-1]
                prob_sobreviver = 1 - probabilidades[id_prob_morte][ano][idade] * probabilidades[id_fam][idade]
                                
                # Eq. 22
                est[id_pens].loc[idade, ano] = est_ano_anterior * prob_sobreviver               
    
    
        # Obtém concessões e cessalções do tipo B
    concessoes = calc_concessoes_pensao(concessoes, est, segurados, probabilidades, periodo)    
    cessacoes = calc_cessacoes_pensao(cessacoes, concessoes, probabilidades, periodo)
    
    # Calcula pensões de tipo B - Equação 23
    for benef in lista_pensoes:  
        
        sexo = benef[-1]                                                         # Obtém o Sexo       
        id_prob_morte = 'Mort'+ sexo                                             # ex: MortH        
        id_fam = 'fam'+benef                                                     # fator de ajuste de mortalidade
        id_pens = benef+"_tipoB"                                                 # Cria um Id para pensão do tipo A
            
        # Cria DataFrame para armazenar o estoque de Pensões do tipo B 
        est[id_pens] = pd.DataFrame(0.0, index=range(0,91), columns=[2014]+periodo)
        est[id_pens].index.name = "IDADE"        
        
        # Projeta anos seguintes
        for ano in periodo:          
            
            # Pula anos inferiores a 2015
            if ano < 2015:
                continue
            
            # Projeta pensões do tipo B            
            # Idades de 1 a 90 anos.
            for idade in range(1,91):                 
                est_ano_anterior = est[id_pens][ano-1][idade-1]
                prob_sobreviver = 1 - probabilidades[id_prob_morte][ano][idade] * probabilidades[id_fam][idade]                                
                conc = concessoes[benef][ano][idade]
                cess = cessacoes[benef][ano][idade]
                                
                # Eq. 23
                est[id_pens].loc[idade, ano] = est_ano_anterior * prob_sobreviver + conc - cess                
                        
    
    # Calcula total de pensões
    for benef in lista_pensoes:   
        est[benef] = est[benef+"_tipoA"] + est[benef+"_tipoB"]      # Eq. 21
    
    return est


# Calcula as concessões de Pensões - REVISAR
# Equaçóes 24 e 25
def calc_concessoes_pensao(concessoes, estoques, segurados, probabilidades, periodo):

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()
    
    # Obtém o conjunto de benefícios do tipo pensão
    lista_pensoes = dados.get_id_beneficios('Pe')
    
    # Obtém estoque acumulado de aposentadorias por clientela e sexo
    estoq_acum = calc_estoq_acumulado(estoques, periodo)
    
    # Eq. 26
    # Hipótese de que o diferencial de idade médio entre cônjuges é de 4 anos (pag. 45 LDO de 2018)
    Dit = 4
    
    # Calcula concessões de pensões do tipo B 
    for benef in lista_pensoes:  
        
        sexo = benef[-1]                                                         # Obtém o Sexo
        sexo_oposto = 'M' if sexo=='H' else 'H'                                  # Obtém o oposto
        id_mort_sex_op = 'Mort'+ sexo_oposto                                     # ex: MortM                
        id_seg = dados.get_id_segurados(benef).replace(sexo, sexo_oposto)        # Obtem o Id do segurado trocando o sexo
        clientela = dados.get_clientela(benef)   
        id_prob_entr = benef.replace(sexo, sexo_oposto)
                        
        for ano in periodo:           
            # Tipo de Pensão válida a partir de 2015            
            if ano < 2015:
                continue    # Pula anos inferiores a 2015
            
            # Cria nova entrada no DataFrame
            concessoes[benef][ano] = 0
            
            # Calcula concessões
            # Idades de 1 a 90 anos.
            for idade in range(1,91):
                                
                # A soma ou subtração depende do sexo
                if sexo == 'H':
                    i_Dit = idade - Dit
                else:
                    i_Dit = idade + Dit
                
                # Trata valores negativos e maiores que 90
                if i_Dit < 0:
                    i_Dit = 0
                
                if i_Dit > 90:
                    i_Dit = 90
                                
                prob_entrada = probabilidades[id_prob_entr][i_Dit] 
                seg = segurados[id_seg][ano][i_Dit]
                est_ac = estoq_acum[clientela + sexo_oposto][ano][i_Dit]
                pmort = probabilidades[id_mort_sex_op][ano][i_Dit]
                
                # Eq. 24 e 25
                concessoes[benef].loc[idade, ano] = prob_entrada * (seg + est_ac) * pmort
                
    return concessoes

# Calcula as cessações baseada no mecanismo legal de
# cessação automática da Lei nº 13.135/2015 - Equação 27
# REVISAR - Cessacoes e concessoes para mulheres esta dando um valor fixo para idades finais
def calc_cessacoes_pensao(cessacoes, concessoes, probabilidades, periodo):
    
    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    # Parte da Eq. 27
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

    # Calcula as cessações para cada tipo de pensão
    for beneficio in dados.get_id_beneficios(['Pe']):
        
        sexo = beneficio[-1]    # Obtém o sexo a partir do nome do benefício
        
        # Verifica se existe dados de concessões
        if beneficio in concessoes.keys():
            for ano in periodo:
                
                # Essa regra só vale a partir de 2015
                if ano < 2015:
                    continue    # Pula iteração
                
                # Cria nova entrada no Dataframe
                cessacoes[beneficio][ano] = 0
                
                # Como o ji é 3 para idades menores que 23                                
                # cessações são zero para i < 3
                for idade in range(3,91):
                    ji = get_ji(idade)
                    
                    # As pensões do tipo B só existem a partir de 2015
                    if (ano-ji) < 2015:                        
                        cessacoes[beneficio].loc[idade, ano] = 0
                        
                    else:                    
                        conc = concessoes[beneficio][ano-ji][idade-ji]                     
                        produtorio = 1
                        k = idade-ji
                        for i in range(k,idade):                        
                            pmorte = probabilidades ['Mort'+sexo][ano-(i-k)][k]
                            fator = probabilidades['fam'+beneficio][k]
                            produtorio *= (1 - pmorte * fator)
                            
                        cessacoes[beneficio].loc[idade, ano] = conc * produtorio
                        
                    # REVISAR - Existem casos em que todas as concessões são cessadasSão gerados cessações para estoques que não existem
                    # Ex: PensRurM - 2015 - 24                     
    return cessacoes
                    

# Calcula estoque acumulado de aposentadorias por clientela e sexo
def calc_estoq_acumulado(estoques, periodo):
    
    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()
    
    ids_apos= ['Apin', 'Atcn', 'Apid', 'Atcp', 'Ainv', 'Atce', 'Atcd']
    
    # Adiciona o ano de 2014 na lista de anos
    anos = [2014] + periodo
    
    # Dicionário que armazena o Estoque acumulado
    est_acumulado = {}
    
    # As chaves do dicionário são as clientelas
    for clientela in ['UrbPiso', 'UrbAcim', 'Rur']:                
        # Cria o DataFrame
        est_acumulado[clientela+'H'] = pd.DataFrame(0.0, index=range(0,91), columns=anos)        
        est_acumulado[clientela+'M'] = pd.DataFrame(0.0, index=range(0,91), columns=anos)        
        
        # Obtém todas as aposentadorias e faz o somatório por clientela
        for beneficio in dados.get_id_beneficios(ids_apos):                   
            # Verifica se o estoque para o benefício existe
            if beneficio in estoques.keys():
                sexo = beneficio[-1]
                if dados.get_clientela(beneficio) == clientela:                    
                    est_acumulado[clientela+sexo] += estoques[beneficio]
                                    
    return est_acumulado
                                    

def calc_estoq_assistenciais(estoques, concessoes, populacao, prob, periodo):
    
    ids_assistenciais= ['LoasDef', 'LoasIdo', 'Rmv']

    for tipo in ids_assistenciais:
        for sexo in ['H', 'M']:            
            beneficio = tipo+sexo
            id_mort = 'Mort'+sexo
            id_fam = 'fam'+beneficio
            id_pop = "PopIbge"+sexo
            
            # Verifica se existe estoque para o benefício
            if beneficio in estoques.keys():
                for ano in periodo:                
                    # Cria uma nova entrada no DataFrame
                    estoques[beneficio][ano] = 0
                    
                    # Idades de 1 a 89 anos 
                    for idade in range(1,90):
                        est_ano_ant = estoques[beneficio][ano-1][idade-1]
                        prob_sobrev = 1 - prob[id_mort][ano][idade] * prob[id_fam][idade]
                        
                        # O RMV está em extinção (sem novas concessões)                    
                        if tipo == 'Rmv':
                            conc = 0
                        else:
                            conc = prob[beneficio][idade] * populacao[id_pop][ano][idade]
                            # Guarda histórico de concessões
                            concessoes[beneficio].loc[idade, ano] = conc
                       
                        # Eq.28 
                        est = (est_ano_ant * prob_sobrev) + conc
                        # Salva no DataFrame
                        estoques[beneficio].loc[idade, ano] = est                        
                        
                    # Idade zero e 90 - REVISAR                    
                    est_90_ant = estoques[beneficio][ano-1][90]
                    # O RMV está em extinção (sem novas concessões)                    
                    if tipo == 'Rmv':
                        conc = 0
                    else:
                        # Idade zero - REVISAR - o valor esta aumentando muito
                        estoques[beneficio].loc[0, ano] = prob[beneficio][0] * populacao[id_pop][ano][0]
                        concessoes[beneficio].loc[0, ano] = estoques[beneficio].loc[0, ano]
                        # Idade 90 - REVISAR - Tendência de queda constante
                        conc = prob[beneficio][90] * (populacao[id_pop][ano][90] - est_90_ant)                  
                        concessoes[beneficio].loc[90, ano] = conc
                                            
                    prob_sobrev = 1 - prob[id_mort][ano][90] * prob[id_fam][90]
                    estoques[beneficio].loc[90, ano] = (est_90_ant * prob_sobrev) + conc
                    
    return estoques
                    