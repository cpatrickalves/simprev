# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.tabelas import LerTabelas
import pandas as pd
import numpy as np

def calc_valMedBenef(estoques, despesas, dadosLDO, periodo):

    # ultimo com despesa/estoque conhecida (2014)
    ultimo_ano = periodo[0] - 1

    # Dicionário que armazena os valores médios para cada benefício
    valMedBenef = {}

    for beneficio in estoques.keys():
        if beneficio in despesas.keys():
            # Calcula valor médio
            valMed = despesas[beneficio][ultimo_ano]/estoques[beneficio][ultimo_ano]
            # Converte para um dataframe
            valMedBenef[beneficio] = pd.DataFrame(valMed, columns=[ultimo_ano])
            # Substitui os NaN por zeros
            valMedBenef[beneficio].fillna(0.0, inplace=True)

    # Projeta aumento dos benefícios
    for ano in periodo:
        for beneficio in valMedBenef.keys():
            reajuste = 1.0 + dadosLDO['TxReajusteBeneficios'][ano]/100
            valMedBenef[beneficio][ano] = valMedBenef[beneficio][ano-1] * reajuste


    return valMedBenef


def calc_despesas(despesas, estoques, concessoes, salarios, valMedBenef, probabilidades, dadosLDO, periodo):

    # Objeto criado para uso das funções da Classe LerTabelas
    dados = LerTabelas()
    nparcelas = 13  # REVISAR

    ##### Calcula despesas para clientelas Rurais e Urbanos que recebem o Piso (1 SM) #####
    for clientela in ['Rur', 'Piso']:
        beneficios = dados.get_id_beneficios(clientela)
        for beneficio in beneficios:
            if beneficio in estoques:
                for ano in periodo:
                    if ano in estoques[beneficio].columns:      # verifica se existe projeção para esse ano
                        # Obtem o estoque total do ano e do ano anterior
                        estoq_total = estoques[beneficio][ano].sum()
                        estoq_total_ano_ant = estoques[beneficio][ano-1].sum()
                        valor_benef = salarios['salarioMinimo'][ano]

                        # Calcula a despesa para cada benefício (Eq. 44)
                        despesas[beneficio][ano] = ((estoq_total + estoq_total_ano_ant)/2) * valor_benef * nparcelas

    ##### Calcula despesas para clientela Urbana que recebe acima do Piso #####

    # Calcula taxa de reposiçao para todos os anos da projeçao
    txReposicao = calc_tx_reposicao(valMedBenef, salarios, periodo)

    for beneficio in dados.get_id_beneficios('Acim'):
        if beneficio in estoques:

            sexo = beneficio[-1]
            # Eq. 47
            val_med_novos_ben = txReposicao * salarios['SalMedSegUrbAcimPnad'+sexo] # REVISAR Equação

            # Caso o benefício seja uma Apos. por Tempo de
            # Contribuição Normal, Professor ou Especial
            # Eq. 49 e 50
            #if ('tcn' in beneficio or 'tce' in beneficio or 'tcp' in beneficio):
                #fator_prev = 1
                #ajuste = 1
                #val_med_novos_ben = fator_prev * ajuste * salarios['SalMedSegUrbAcimPnad'+sexo] # REVISAR Equação

            for ano in periodo:
                if ano in estoques[beneficio].columns:      # verifica se existe projeção para esse ano
                    if 'Aux' in beneficio:                  # Verifica se o beneficio e um Auxílio
                        pass
                    else:
                        # Cálculo para Aposentadorias e Pensões

                        # Idade zero
                        #???

                        # Idade de 1 a 90 anos
                        for idade in range(1,91):

                            desp_anterior = despesas[beneficio][ano-1][idade-1]
                            conc_anterior = concessoes[beneficio][ano-1][idade-1]
                            tx_rep_anterior = txReposicao[ano-1][idade-1]
                            rend_med_ocup_ant = salarios['SalMedPopOcupUrbAcimPnad'+sexo][ano-1][idade-1]
                            prob_morte = probabilidades['Mort'+sexo][ano][idade]
                            fam = probabilidades['fam'+beneficio][idade]
                            reajuste = dadosLDO['TxReajusteBeneficios'][ano]
                            novas_conc = concessoes[beneficio][ano][idade]
                            valor_med_conc = val_med_novos_ben[ano][idade]

                            # Eq. 45
                            part1 = desp_anterior + conc_anterior * tx_rep_anterior * rend_med_ocup_ant * (nparcelas/2)
                            part2 = (1 - prob_morte * fam) * (1 + reajuste/100)
                            part3 = (novas_conc * valor_med_conc * (nparcelas/2))
                            despesas[beneficio].loc[idade, ano] = part1 * part2 + part3

    ##### Calcula a despesa total #####
    desp_total = pd.Series(0.0, index=periodo)  # Objeto do tipo Serie que armazena a despesa total
    for ano in periodo:
        for beneficio in despesas.keys():
             if ano in despesas[beneficio].columns:      # verifica se existe projeção para esse ano
                 desp_total[ano] += despesas[beneficio][ano].sum()

    return desp_total

# Calcula a taxa de reposição (Eq. 48)
def calc_tx_reposicao(valMedBenef, salarios, periodo):

    # Dataframe que armazena as taxas
    txReposicao = pd.DataFrame(index=range(0,91), columns=periodo)
    txReposicao.fillna(0.0, inplace=True)

    # Insere o ano de 2014 na lista periodos
    anos = [2014] + periodo

    for ano in anos:
        for beneficio in valMedBenef.keys():
            sexo = beneficio[-1]
            rend_medio_seg = salarios['SalMedSegUrbAcimPnad'+sexo][ano]
            vmb = valMedBenef[beneficio][ano]
            # Eq. 48
            txReposicao[ano] = vmb/rend_medio_seg

    # Trata as divisões por zero que geram NaN e Inf
    txReposicao.replace([np.inf, -np.inf], np.nan, inplace=True)
    txReposicao.fillna(0.0, inplace=True)

    return txReposicao


