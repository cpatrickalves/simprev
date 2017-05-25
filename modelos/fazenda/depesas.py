# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.tabelas import LerTabelas
import pandas as pd


class Despesas():
    
    def calc_valMedBenef(estoques, despesas, dadosLDO, periodo):
        
        # ultimo ano de despesa/estoque conhecida (2014)
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
        

    def calc_despesas(despesas, estoques, concessoes, salarios, valMedBen, probabilidades, dadosLDO, periodo):

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
        for beneficio in dados.get_id_beneficios('Acim'):
            if beneficio in estoques:
                for ano in periodo:
                    if ano in estoques[beneficio].columns:      # verifica se existe projeção para esse ano

                        sexo = beneficio[-1]

                        if 'Aux' in beneficio:                  # Verifica se o beneficio e um Auxílio
                            pass
                        else:
                            # Cálculo para Aposentadorias e Pensões (Eq. 45)

                            # Idade zero
                            #???

                            # Idade de 1 a 90 anos
                            for idade in range(1,91):
                                
                                rend_medio_seg = salarios['SalMedSegUrbAcimPnad'+sexo][ano][idade]
                                
                                # Eq 48
                                tx_reposicao = salarios['SalMedSegUrbAcimPnad'+sexo]
                                
                                val_med_novos_ben = tx_reposicao 
                                desp_anterior = despesas[beneficio][ano-1][idade-1]
                                conc_anterior = concessoes[beneficio][ano-1][idade-1]
                                
                                tx_reposicao = 0
                                rend_medio = 0
                                prob_morte = probabilidades['Mort'+sexo][ano][idade]
                                fam = probabilidades['fam'+beneficio][ano][idade]
                                reajuste = dadosLDO['TxReajusteBeneficios'][ano]
                                novas_conc = concessoes[beneficio][ano][idade]
                                valor_med_conc = valMedBen[beneficio][ano][idade]
                                cagada = conc_anterior * seg_anterior * rend_medio * (nparcelas/2)

                                despesas[beneficio][ano][idade] = (desp_anterior + (cagada)) * (1 - prob_morte * fam) * \
                                                                  (1 + reajuste/100) + (novas_conc * valor_med_conc *
                                                                                        (nparcelas/2))

        ##### Calcula a despesa total #####
        desp_total = pd.Series(0.0, index=periodo)  # Objeto do tipo Serie que armazena a despesa total
        for ano in periodo:
            for beneficio in despesas.keys():
                 if ano in despesas[beneficio].columns:      # verifica se existe projeção para esse ano                     
                     desp_total[ano] += despesas[beneficio][ano].sum()

        despesas['total'] = desp_total

        return despesas