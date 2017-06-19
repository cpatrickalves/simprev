# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.tabelas import LerTabelas
import pandas as pd
import numpy as np

# REVISAR - Verificar se não existem beneficio menores que 1 SM
def calc_valMedBenef(estoques, despesas, dadosLDO, periodo):

    # ultimo com despesa/estoque conhecida (2014)
    ultimo_ano = periodo[0] - 1

    # Dicionário que armazena os valores médios para cada benefício
    valMedBenef = {}

    for beneficio in estoques.keys():                          
        if beneficio in despesas.keys():            
            # Calcula valor médio
            desp = despesas[beneficio][ultimo_ano]
            est = estoques[beneficio][ultimo_ano]
            valMed = desp /est
                
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


def calc_despesas(despesas, estoques, concessoes, salarios, valMedBenef, probabilidades, dadosLDO, nparcelas, resultados, periodo):

    # Objeto criado para uso das funções da Classe LerTabelas
    dados = LerTabelas()
        
    ##### Calcula despesas para clientelas Rurais, Urbarnas e assistenciais que recebem o Piso (1 SM) #####
    for clientela in ['Rur', 'Piso', 'Rmv', 'Loas']:
        beneficios = dados.get_id_beneficios(clientela)
        for beneficio in beneficios:
            
            # Pula o SalMat pois o calculo é diferente e feito posteriormente
            if 'SalMat' in beneficio:                        
                continue
            
            # Verifica se existe estoque para o beneficio
            if beneficio in estoques:                
                for ano in periodo:                                        
                    # verifica se existe projeção para esse ano
                    if ano in estoques[beneficio].columns:                  
                        # Obtem o estoques do ano e do ano anterior
                        estoq_total = estoques[beneficio][ano]
                        estoq_total_ano_ant = estoques[beneficio][ano-1]
                        valor_benef = salarios['salarioMinimo'][ano]
                        np = nparcelas[beneficio]

                        # Calcula a despesa para cada benefício (Eq. 44)
                        despesas[beneficio][ano] = ((estoq_total + estoq_total_ano_ant)/2) * valor_benef * np

    
    ##### Calcula despesas para clientela Urbana que recebe acima do Piso #####
    
    # Calcula taxa de reposiçao para todos os anos da projeçao
    txReposicao = calc_tx_reposicao(valMedBenef, salarios, periodo)

    for beneficio in dados.get_id_beneficios('Acim'):
        
        # Pula o SalMat pois o calculo é diferente e feito posteriormente
        if 'SalMat' in beneficio:                        
            continue
        
        if beneficio in estoques:            
            sexo = beneficio[-1]
            
            # Eq. 47
            val_med_novos_ben = txReposicao[beneficio] * salarios['SalMedSegUrbAcimPnad'+sexo] # REVISAR Equação

            # Caso o benefício seja uma Apos. por Tempo de
            # Contribuição Normal, Professor ou Especial
            # Eq. 49 e 50
            #if ('tcn' in beneficio or 'tce' in beneficio or 'tcp' in beneficio):
                #fator_prev = 1
                #ajuste = 1
                #val_med_novos_ben = fator_prev * ajuste * salarios['SalMedSegUrbAcimPnad'+sexo] # REVISAR Equação
            
            for ano in periodo:
                if ano in estoques[beneficio].columns:      # verifica se existe projeção para esse ano
                    # Os auxílios usam um cálculo diferente
                    if 'Aux' in beneficio:                  
                        
                        est_ano = estoques[beneficio][ano]
                        vmb = val_med_novos_ben[ano]
                        
                        # Eq. 46
                        despesas[beneficio][ano] = 0
                        
                    else:
                        # Cálculo para Aposentadorias e Pensões

                        # Idade zero
                        #???
                        
                        # Pula pensões por enquanto - REVISAR
                        if beneficio in dados.get_id_beneficios('Pe'):
                            continue

                        # Idade de 1 a 90 anos - REVISAR - falta idade zero
                        for idade in range(1,91):
                            
                            desp_anterior = despesas[beneficio][ano-1][idade-1]
                            conc_anterior = concessoes[beneficio][ano-1][idade-1]
                            tx_rep_anterior = txReposicao[beneficio][ano-1][idade-1]
                            # REVISAR: Acredito que o correto seria usar os segurados e nao a PopOcup
                            rend_med_ocup_ant = salarios['SalMedPopOcupUrbAcimPnad'+sexo][ano-1][idade-1]
                            np = nparcelas[beneficio]
                            prob_morte = probabilidades['Mort'+sexo][ano][idade]
                            fam = probabilidades['fam'+beneficio][idade]
                            reajuste = dadosLDO['TxReajusteBeneficios'][ano]
                            novas_conc = concessoes[beneficio][ano][idade]
                            valor_med_conc = val_med_novos_ben[ano][idade]
                            

                            # Eq. 45
                            part1 = desp_anterior + conc_anterior * tx_rep_anterior * rend_med_ocup_ant * (np/2)
                            part2 = (1 - prob_morte * fam) * (1 + reajuste/100)
                            part3 = (novas_conc * valor_med_conc * (np/2))
                            despesas[beneficio].loc[idade, ano] = part1 * part2 + part3


    ##### Calcula despesas para o Salário Maternidade #####
    for beneficio in dados.get_id_beneficios('SalMat'):
        # Verifica se existe estoque para o beneficio
        if beneficio in estoques:                        
            # Objeto do tipo Series que armazena as despesas por ano 
            desp_acumulada = pd.Series(index=estoques[beneficio].columns)
            # Acumula as despesas conhecidas 
            for ano in despesas[beneficio].columns:    
                desp_acumulada[ano] = despesas[beneficio][ano].sum()
                        
            # Projeta os anos restantes
            # Obtem o estoques do ano e do ano anterior
            for ano in periodo:
                estoq_total = estoques[beneficio+'_total'][ano]
                #estoq_total_ano_ant = estoques[beneficio+'_total'][ano-1]
                
                # Obtem o valor médio do benefício
                if dados.get_clientela(beneficio) == 'UrbAcim':
                    # Como não se usa dados desagregados de idade, utiliza-se a média
                    # Considera somente a faixa de 16 a 45 anos
                    valor_benef = valMedBenef[beneficio][ano][16:46].mean()
                else:
                    valor_benef = salarios['salarioMinimo'][ano]                    

                np = nparcelas[beneficio]
                            
                # OBS: A LDO não descreve a equação para o calculo de despesas para o SalMat - REVISAR
                desp_acumulada[ano] = estoq_total * valor_benef * np  
                
            # Salva no DataFrame
            despesas[beneficio+'_total'] = desp_acumulada


    ##### Calcula a despesa total #####
    desp_total = pd.Series(0.0, index=periodo)  # Objeto do tipo Serie que armazena a despesa total
    for ano in periodo:
        for beneficio in despesas.keys():
            
            # O objeto que armazena as despesas com Salário Maternidade é diferente
            # Verifica se o benefício é do tipo Salário Maternidade
            if 'SalMat' in beneficio:                
                if '_total' in beneficio:                                     
                    if ano in despesas[beneficio].index:      # verifica se existe projeção para esse ano                                                
                        desp_total[ano] += despesas[beneficio][ano]                        
                continue # Pula para o próximo benefício
            
            # Calculo para os demais benefícios
            if ano in despesas[beneficio].columns:      # verifica se existe projeção para esse ano
                desp_total[ano] += despesas[beneficio][ano].sum()               

    resultados['despesas'] = desp_total
    resultados['txReposicao'] = txReposicao
    
    return resultados
    
# Calcula a taxa de reposição (Eq. 48)
def calc_tx_reposicao(valMedBenef, salarios, periodo):

    # Dicionário que armazena as taxas de reposição
    txReposicao = {}
    
    # Insere o ano de 2014 na lista periodos
    anos = [2014] + periodo

    for beneficio in valMedBenef.keys():
        # Cria Dataframe que armazena as taxas
        txReposicao[beneficio] = pd.DataFrame(index=range(0,91), columns=anos)
        txReposicao[beneficio].fillna(0.0, inplace=True)

        for ano in anos:    
            sexo = beneficio[-1]
            rend_medio_seg = salarios['SalMedSegUrbAcimPnad'+sexo][ano]
            vmb = valMedBenef[beneficio][ano]
            # Eq. 48
            txReposicao[beneficio][ano] = vmb/rend_medio_seg

        # Trata as divisões por zero que geram NaN e Inf
        txReposicao[beneficio].replace([np.inf, -np.inf], np.nan, inplace=True)
        txReposicao[beneficio].fillna(0.0, inplace=True)
        
    return txReposicao

# Calcula o número de parcelas paga por ano por um benefício
# Implementado conforme seção 4.6 da LDO (pag. 43)
def calc_n_parcelas(estoques, despesa, valMedBenef, periodo):
    
    # É necessário o valor total e despesas por beneficios para fazer esse calculo
    # so temos dados do mes de dezembro, por isso os valores foram fixados manualmente
    
    # ano_estoq = periodo[0]-1    # 2014
    
    dados = LerTabelas()    

    # Dicionário que armazena o número médio de parcelas para tipo de beneficio
    n_parcelas = {}
    
    ids_apos = ['Apin', 'Atcn', 'Apid', 'Atcp', 'Ainv', 'Atce', 'Atcd']
    ids_assistenciais= ['LoasDef', 'LoasIdo', 'Rmv']
    
    # Aposentadorias
    for benef in dados.get_id_beneficios(ids_apos):
        n_parcelas[benef] = 13

    # Pensões
    for benef in dados.get_id_beneficios('Pen'):
        n_parcelas[benef] = 13

    # Auxilios
    for benef in dados.get_id_beneficios('Aux'):
        n_parcelas[benef] = 11

    # Salario Maternidade
    for benef in dados.get_id_beneficios('SalMat'):
        n_parcelas[benef] = 6

    # Assistenciais
    for benef in dados.get_id_beneficios(ids_assistenciais):
        n_parcelas[benef] = 12

   # for beneficio in estoques.keys():
   #     # Verifica se existe dados de despesa para o beneficio
   #     if beneficio in despesa.keys():
   #         desp = despesa[beneficio][ano_estoq].sum()
   #         est = estoques[beneficio][ano_estoq].sum()
   #         vm = valMedBenef[beneficio][ano_estoq].mean()
   #         n_parcelas[beneficio] = Dt/(vm*est)
                   
    return n_parcelas
    
    
    