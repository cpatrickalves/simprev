# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.tabelas import LerTabelas
import pandas as pd


class Despesas():

    def calc_despesas(despesas, estoques, salarios, periodo):

        # Objeto criado para uso das funções da Classe LerTabelas
        dados = LerTabelas()

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
                            nparcelas = 13 # REVISAR

                            # Calcula a despesa para cada benefício (Eq. 44)
                            despesas[beneficio][ano] = ((estoq_total + estoq_total_ano_ant)/2) * valor_benef * nparcelas

        ##### Calcula despesas para clientela Urbana que recebe acima do Piso #####
        for beneficio in dados.get_id_beneficios('Acim'):
            if beneficio in estoques:
                for ano in periodo:
                    if ano in estoques[beneficio].columns:      # verifica se existe projeção para esse ano
                        if 'Aux' in beneficio:                  # Verifica se o beneficio e um Auxílio
                            pass
                        else:
                            # Cálculo para Aposentadorias e Pensões
                            pass # OBTER HISTORICO DE DESEPSAS DA PLANILHA!!!!!!!!

        ##### Calcula a despesa total #####
        desp_total = pd.Series(0.0, index=periodo)  # Objeto do tipo Serie que armazena a despesa total
        for ano in periodo:
            for beneficio in despesas.keys():
                 if ano in despesas[beneficio].columns:      # verifica se existe projeção para esse ano                     
                     desp_total[ano] += despesas[beneficio][ano].sum()

        despesas['total'] = desp_total

        return despesas