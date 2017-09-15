# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.tabelas import LerTabelas
import pandas as pd


# Cálculo dos estoques de acordo com a Equação 11 da LDO de 2018
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

            sexo = benef[-1]                                          # Obtém o Sexo
            id_prob_morte = 'Mort'+ sexo                              # ex: MortH
            id_fam = 'fam'+benef                                      # fator de ajuste de mortalidade
            id_seg = 'Ocup'+ dados.get_clientela(benef)+ sexo         # ex: OcupUrbPisoH ou CsmUrbH

            # Para os Rurais se utiliza toda a população (Fonte: planilhas do MF)
            if 'Rur' in benef:
                id_seg = 'PopRur'+sexo

            for ano in periodo:
                # Adiciona uma nova coluna (ano) no DataFrame com valores zero
                est[benef][ano] = 0

                # 1 a 90 anos - Equação 11 da LDO de 2018
                for idade in range(1,91):
                    est_ano_anterior = est[benef][ano-1][idade-1]
                    prob_sobreviver = 1 - prob[id_prob_morte][ano][idade] * prob[id_fam][ano][idade]
                    entradas = seg[id_seg][ano][idade] * prob[benef][ano][idade]
                    if idade == 90:
                        est_ano_anterior = est[benef][ano-1][idade-1] + est[benef][ano-1][idade]

                    # Eq. 11
                    est[benef].loc[idade, ano] = est_ano_anterior * prob_sobreviver + entradas     # Eq. 11
                    # Salva a quantidade de concessões para uso posterior
                    conc[benef].loc[idade,ano] = entradas

                # Calculo para a idade zero
                est[benef].loc[0, ano] = seg[id_seg][ano][0] * prob[benef][ano][0]
                # Salva a quantidade de concessões para uso posterior
                conc[benef].loc[0, ano] = est[benef].loc[0, ano]


    return est



# Projeta estoques para Auxílios Doença, Reclusão e Acidente - Equação 17 da LDO de 2018
def calc_estoq_aux(est, prob, seg, periodo):

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    for benef in dados.get_id_beneficios(['Auxd', 'Auxa']):
        # Verifica se existe no Estoque
        if benef in est:
            sexo = benef[-1]
            id_seg = 'Ocup'+ dados.get_clientela(benef)+ sexo    # ex: OcupUrbPisoH ou CaUrbH
            # Para os Rurais se utiliza toda a população (Fonte: planilhas do MF)
            if 'Rur' in benef:
                id_seg = 'PopRur'+sexo

            for ano in periodo:
                est[benef][ano] = seg[id_seg][ano] * prob[benef][ano]     # Eq. 17

    for benef in dados.get_id_beneficios(['Auxr']):
        # Verifica se existe no Estoque
        if benef in est:
            sexo = benef[-1]
            id_seg = 'Ocup'+ dados.get_clientela(benef)+ sexo    # ex: OcupUrbPisoH ou CaUrbH
            # Para os Rurais se utiliza toda a população (Fonte: planilhas do MF)
            if 'Rur' in benef:
                id_seg = 'PopRur'+sexo

            for ano in periodo:
                # Cria uma nova entrada
                est[benef][ano] = 0

                for idade in range(0,91):
                     # Na planilha são aplicados deslocamentos nas idades
                    deslocamento = 0
                    if idade < 61 and sexo == 'H':
                        deslocamento = 25
                    elif idade < 61 and sexo == 'M':
                        deslocamento = 18

                    # Eq. 17
                    est[benef].loc[idade, ano] = seg[id_seg][ano][idade+deslocamento] * prob[benef][ano][idade]
                    # OBS: Nas planilhas o cálculo do deslocamento está errado para as URbAcimM (usa-se 25 ao invés de 18)
                    
    return est


# Projeta estoques para Salário-Maternidade - Equação 20 da LDO de 2018
def calc_estoq_salMat(est, pop, seg, periodo):

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    # 2014, 2015, ...
    anos = [(periodo[0]-1)]+periodo

    for benef in dados.get_id_beneficios('SalMat'):
        # Armazena valores do ano
        est_acumulado = pd.Series(index=anos)
        # Obtem o tipo de segurado a partir do benefício
        id_seg = dados.get_id_segurados(benef)

        # Os estoques de SalMat são agrupados por ano no modelo (não por idade)
        # OBS: O calculo dos estoques de SalMat não dependem da existência de estoques anteriores

        # Realiza projeção
        for ano in anos:
            est_acumulado[ano] = 0     # Cria um novo ano
            nascimentos = pop['PopIbgeM'][ano][0] + pop['PopIbgeH'][ano][0]

            # Acumula mulheres de 16 a 45 anos
            seg_16_45 = 0
            pop_16_45 = 0

            # O calculo para os rurais usa a População Rural e não os segurados rurais
            # OBS: o cálculo para os rurais ainda não bate com os da planilha do MF por causa do
            # cálculo da taxa de ruralização ser diferente
            if 'Rur' in benef:
                for idade in range(16,46):
                    seg_16_45 += pop['PopRurM'][ano][idade]
                    pop_16_45 += pop['PopIbgeM'][ano][idade]
            else:
                for idade in range(16,46):
                    seg_16_45 += seg[id_seg][ano][idade]
                    pop_16_45 += pop['PopIbgeM'][ano][idade]

            # Eq. 20
            est_acumulado[ano] = (seg_16_45/pop_16_45) * nascimentos

        # Cria uma nova entrada no dicionário para armazenar os estoques acumulados
        est[benef] = est_acumulado

    return est


# Projeta os estoque de pensões - Equações 21 a 27 da LDO de 2018
def calc_estoq_pensoes(populacao, est, concessoes, cessacoes, probabilidades, segurados, periodo):

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()
    # Obtém o conjunto de benefícios do tipo pensão
    lista_pensoes = dados.get_id_beneficios('Pe')
    
    ##### Calcula pensões do tipo A
    for benef in lista_pensoes:
        sexo = benef[-1]                # Obtém o Sexo
        id_prob_morte = 'Mort'+ sexo    # ex: MortH
        id_fam = 'fam'+benef            # fator de ajuste de mortalidade
        id_pens = benef+"_tipoA"        # Cria um Id para pensão do tipo A

        # Cria um novo DataFrame para Pensão do tipo A - 2010-2014 - REVISAR
        #est[id_pens] = pd.DataFrame(0.0, index=range(0,91), columns=(est.columns())+periodo)
        #est[id_pens].index.name = "IDADE"

        # Copia os dados de estoque de 2014 (pensões do tipo A)
        #est[id_pens][2014] = est[benef][2014]
        est[id_pens] = est[benef]

        for ano in periodo:

            # Adiciona uma nova coluna (ano) no DataFrame com valores zero
            est[id_pens][ano] = 0

            # Projeta pensões do tipo A
            # Como não se tem novas concessões desse tipo de pensão, calcula-se
            # somente nas idades de 1 a 89 anos.
            for idade in range(1,90):
                est_ano_anterior = est[id_pens][ano-1][idade-1]
                probMorte = probabilidades[id_prob_morte][ano][idade]
                fam = probabilidades[id_fam][ano][idade]
                prob_sobreviver = 1 - (probMorte * fam)

                # Eq. 22
                est[id_pens].loc[idade, ano] = est_ano_anterior * prob_sobreviver

            # Calculo para idade 90
            est_ano_anterior = est[id_pens][ano-1][89] + est[id_pens][ano-1][90]
            id_prob_morte = 'MortH'
            id_fam = ('fam'+benef).replace(sexo, 'H')
            # para o primeiro ano de projeção (2015) a probMorte é para 89 anos
            if ano == periodo[0]:
                probMorte = probabilidades[id_prob_morte][ano][89]
            else:
                probMorte = probabilidades[id_prob_morte][ano][90]
            fam = probabilidades[id_fam][ano][90]
            prob_sobreviver = 1 - probMorte * fam
            est[id_pens].loc[90, ano] = est_ano_anterior * prob_sobreviver


    ##### Calcula pensões de tipo B - Equação 23

    # Obtém projeções de concessões e cessações do tipo B
    concessoes = calc_concessoes_pensao(populacao, concessoes, est, segurados, probabilidades, periodo)
    cessacoes = calc_cessacoes_pensao(cessacoes, concessoes, probabilidades, periodo)

    for benef in lista_pensoes:

        sexo = benef[-1]                     # Obtém o Sexo
        id_prob_morte = 'Mort'+ sexo         # ex: MortH
        id_fam = 'fam'+benef                 # fator de ajuste de mortalidade
        id_pens = benef+"_tipoB"             # Cria um Id para pensão do tipo B

        # Cria DataFrame para armazenar o estoque de Pensões do tipo B
        est[id_pens] = pd.DataFrame(0.0, index=range(0,91), columns=[periodo[0]-2,periodo[0]-1]+periodo) # 2013-2060 - REVISAR - refatorar
        est[id_pens].index.name = "IDADE"

        # Projeta anos seguintes
        for ano in periodo:

            # Pula anos inferiores a 2015
            if ano < 2015:
                continue

            # Projeta pensões do tipo B
            # Idades de 1 a 89 anos.
            for idade in range(1,90):
                est_ano_anterior = est[id_pens][ano-1][idade-1]
                prob_sobreviver = 1 - probabilidades[id_prob_morte][ano][idade] * probabilidades[id_fam][ano][idade]
                conc = concessoes[benef][ano][idade]
                cess = cessacoes[benef][ano][idade]

                # Eq. 23
                est[id_pens].loc[idade, ano] = est_ano_anterior * prob_sobreviver + conc - cess

            # Idade zero
            est[id_pens].loc[0, ano] = concessoes[benef][ano][0] - cessacoes[benef][ano][0]
            # Idade 90
            est_ano_ant90 = est[id_pens][ano-1][89] + est[id_pens][ano-1][90]
            prob_sobr90 = 1 - probabilidades[id_prob_morte][ano][90] * probabilidades[id_fam][ano][90]
            conc90 = concessoes[benef][ano][90]
            cess90 = cessacoes[benef][ano][90]
            est[id_pens].loc[90, ano] = est_ano_ant90 * prob_sobr90 + conc90 - cess90

    # Calcula total de pensões
    for benef in lista_pensoes:        
        est[benef] = est[benef+"_tipoA"].add(est[benef+"_tipoB"])      # Eq. 21        

    return est


# Calcula as concessões de Pensões
# Baseado nas Equaçóes 24 e 25 e planilhas do MF
def calc_concessoes_pensao(populacao, concessoes, estoques, segurados, probabilidades, periodo):

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    # Obtém o conjunto de benefícios do tipo pensão
    lista_pensoes = dados.get_id_beneficios('Pe')

    # Obtém estoque acumulado de aposentadorias por ano, clientela, idade e sexo
    estoq_acum = calc_estoq_apos_acumulado(estoques, periodo)

    # Eq. 26
    # Hipótese de que o diferencial de idade médio entre cônjuges é de 4 anos (pag. 45 LDO de 2018)
    Dit = 4

    # Calcula concessões de pensões do tipo B
    for benef in lista_pensoes:

        sexo = benef[-1]                                              # Obtém o Sexo
        sexo_oposto = 'M' if sexo=='H' else 'H'                       # Obtém o oposto
        id_mort_sex_op = 'Mort'+ sexo_oposto                          # ex: MortM
        # Sempre são usados os segurados do sexo masculino
        id_seg = dados.get_id_segurados(benef).replace(sexo, 'H')     # Obtem o Id do segurado trocando o sexo
        clientela = dados.get_clientela(benef)
        id_prob_entr = benef.replace(sexo, sexo_oposto)

        for ano in periodo:
            # Tipo de Pensão válida a partir de 2015
            if ano < 2015:
                continue    # Pula anos inferiores a 2015

            # Cria nova entrada no DataFrame
            concessoes[benef][ano] = 0

            # Calcula concessões
            # Idades de 0 a 90 anos.
            for idade in range(0,91):

                # Determina o valor de Dit baseado na idade (relação baseada nas planilhas do MF)
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
                if sexo == 'H':
                    i_Dit = idade - Dit
                else:
                    i_Dit = idade + Dit

                # Trata valores negativos e maiores que 90
                #if i_Dit < 0:
                #    i_Dit = 0

                #if i_Dit > 90:
                #    i_Dit = 90

                prob_entrada = probabilidades[id_prob_entr][i_Dit]
                pmort = probabilidades[id_mort_sex_op][ano][i_Dit]

                 # Para os urbanos com idade de 15 anos e para os rurais utiliza-se toda a população por clientela simples (Urb ou Rur)
                if idade < 16 or clientela == 'Rur':
                    clientela_simples = clientela[0:3]
                    potGeradoresPensoes = populacao['Pop' + clientela_simples + sexo_oposto][ano][i_Dit]
                else:
                    seg = segurados[id_seg][ano][i_Dit]
                    est_ac = estoq_acum[clientela + sexo_oposto][ano][i_Dit]
                    potGeradoresPensoes = seg + est_ac

                # Eq. 24 e 25
                concessoes[benef].loc[idade, ano] = prob_entrada * potGeradoresPensoes * pmort


    return concessoes

# Calcula as cessações baseada no mecanismo legal de cessação automática da Lei nº 13.135/2015
# Equação 27
def calc_cessacoes_pensao(cessacoes, concessoes, probabilidades, periodo):

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    # Parte da Eq. 27
    # OBS: Esses valores são diferentes dos descritos na Lei 13.135/2015 - REVISAR
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

        # Verifica se existe dados de concessões do tipo B
        if beneficio in concessoes.keys():
            for ano in periodo:

                # Essa regra só vale a partir de 2015
                if ano < 2015:
                    continue    # Pula iteração

                # Cria nova entrada no Dataframe
                cessacoes[beneficio][ano] = 0

                # Cessações são zero para i <= 2, pois (idade - ji) daria negativo
                for idade in range(3,91):
                    ji = get_ji(idade)

                    # As pensões do tipo B só existem a partir de 2015 e se Ji igual 0 zero não tem cessações
                    if (ano-ji) < 2015 or ji == 0:
                        cessacoes[beneficio].loc[idade, ano] = 0

                    else:
                        conc = concessoes[beneficio][ano-ji][idade-ji]
                        produtorio = 1
                        k = idade-ji
                        for i in range(k,idade+1):
                            pmorte = probabilidades['Mort'+sexo][ano-(i-k)][k]
                            fator = probabilidades['fam'+beneficio][ano-(i-k)][k]
                            produtorio *= (1 - pmorte * fator)

                        # Eq. 27
                        cessacoes[beneficio].loc[idade, ano] = conc * produtorio

    return cessacoes


# Calcula estoque acumulado de aposentadorias por ano, clientela, idade e sexo
def calc_estoq_apos_acumulado(estoques, periodo):

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

        # Obtém todas as aposentadorias e faz o somatório por clientela, sexo e idade
        for beneficio in dados.get_id_beneficios(ids_apos):
            # Verifica se o estoque para o benefício existe
            if beneficio in estoques.keys():
                sexo = beneficio[-1]
                if dados.get_clientela(beneficio) == clientela:
                    est_acumulado[clientela+sexo] += estoques[beneficio]

    return est_acumulado


# Projeta os estoque de benefícios Assistenciais - Equações 28 a 31 da LDO de 2018
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
                        prob_sobrev = 1 - prob[id_mort][ano][idade] * prob[id_fam][ano][idade]

                        # O RMV está em extinção (sem novas concessões)
                        if tipo == 'Rmv':
                            conc = 0
                        else:
                            conc = prob[beneficio][ano][idade] * populacao[id_pop][ano][idade]
                            # Guarda histórico de concessões
                            concessoes[beneficio].loc[idade, ano] = conc

                        # Eq.28
                        est = (est_ano_ant * prob_sobrev) + conc
                        # Salva no DataFrame
                        estoques[beneficio].loc[idade, ano] = est


                    #### Cálculos para idades zero e 90

                    # Estoque atual para 90 anos
                    est_90_ant = estoques[beneficio][ano-1][90] + estoques[beneficio][ano-1][89]

                    # O RMV está em extinção (sem novas concessões)
                    if tipo == 'Rmv':
                        conc_90 = 0
                        conc_0 = 0
                    else:
                        # Idade zero - REVISAR - o valor esta aumentando muito Para o LoadDef
                        conc_0 = prob[beneficio][ano][0] * populacao[id_pop][ano][0]
                        concessoes[beneficio].loc[0, ano] = conc_0

                        # Idade 90 - REVISAR - Tendência de queda constante
                        conc_90 = prob[beneficio][ano][90] * (populacao[id_pop][ano][90] - est_90_ant)
                        concessoes[beneficio].loc[90, ano] = conc_90

                    # Idade zero
                    prob_sobrev = 1 - (prob[id_mort][ano][0] * prob[id_fam][ano][0])
                    estoques[beneficio].loc[0, ano] = conc_0 * prob_sobrev

                    # Idade 90
                    prob_sobrev = 1 - (prob[id_mort][ano][90] * prob[id_fam][ano][90])
                    estoques[beneficio].loc[90, ano] = (est_90_ant * prob_sobrev) + conc_90

    return estoques
