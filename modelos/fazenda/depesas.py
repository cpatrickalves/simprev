# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.tabelas import LerTabelas
import pandas as pd


class Despesas():

    def calc_despesas(estoques, salarios, periodo):

        # Objeto criado para uso das funções da Classe LerTabelas
        dados = LerTabelas()

        despesas = {}                                   # Dicionário que armazena os resultados de despesa
        desp_benef = {}                                 # Dicionário que armazena a despesa total por beneficio
        desp_total = pd.Series(0.0, index=periodo)      # Objeto do tipo Serie que armazena a despesa total

        ##### Calcula despesas para clientelas Rurais e Urbanos que recebem o Piso (1 SM) #####
        for clientela in ['Rur', 'Piso']:
            beneficios = dados.get_id_beneficios(clientela)
            for beneficio in beneficios:
                if beneficio in estoques:

                    desp_benef[beneficio] = pd.Series(0.0, index=periodo)

                    for ano in periodo:
                        if ano in estoques[beneficio].columns:
                            # Obtem o estoque total do ano e do ano anterior
                            estoq_total = estoques[beneficio][ano].sum()
                            estoq_total_ano_ant = estoques[beneficio][ano-1].sum()
                            valor_benef = salarios['salarioMinimo'][ano]
                            nparcelas = 13 # REVISAR

                            # Calcula a despesa para cada benefício
                            desp_benef[beneficio][ano] = ((estoq_total + estoq_total_ano_ant)/2) * valor_benef * nparcelas

        ##### Calcula despesas para clientela Urbana que recebe acima do Piso #####


        # Calcula a despesa total
        for ano in periodo:
            for beneficio in desp_benef.keys():
                desp_total[ano] += desp_benef[beneficio][ano]


        despesas['total'] = desp_total
        despesas['beneficio'] = desp_benef

        return despesas