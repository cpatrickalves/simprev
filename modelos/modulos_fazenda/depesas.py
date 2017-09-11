# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.tabelas import LerTabelas
import pandas as pd


# Calcula despesas com benefícios
def calc_despesas(despesas, estoques, concessoes, salarios, valMedBenef, probabilidades, dadosLDO, nparcelas, resultados, periodo):

    # Objeto criado para uso das funções da Classe LerTabelas
    dados = LerTabelas()
        
    ##### Calcula despesas para clientelas Rurais, Urbanas e assistenciais que recebem o Piso (1 SM) #####
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
                        npar = nparcelas[beneficio]

                        # Calcula a despesa para cada benefício (Eq. 44)
                        despesas[beneficio][ano] = ((estoq_total + estoq_total_ano_ant)/2) * valor_benef * npar

    
    ##### Calcula despesas para clientela Urbana que recebe acima do Piso #####
   
    for beneficio in dados.get_id_beneficios('Acim'):
        
        # Pula o SalMat pois o calculo é diferente e feito posteriormente
        if 'SalMat' in beneficio:                        
            continue
        
        # Verifica se existem estoques 
        if beneficio in estoques:            
            sexo = beneficio[-1]
                       
            # Caso o benefício seja uma Apos. por Tempo de
            # Contribuição Normal, Professor ou Especial
            # Eq. 49 e 50
            #if ('tcn' in beneficio or 'tce' in beneficio or 'tcp' in beneficio):
                #fator_prev = 1
                #ajuste = 1
                #val_med_novos_ben = fator_prev * ajuste * salarios['SalMedSegUrbAcimPnad'+sexo] # REVISAR Equação
            
            for ano in periodo:
                if ano in estoques[beneficio].columns:      # verifica se existe projeção para esse ano
                
                    # Cálculo das despesas com os Auxílios 
                    if 'Aux' in beneficio:                                          
                        est_ano = estoques[beneficio][ano]
                        vmb = valMedBenef[beneficio][ano]
                        npar = nparcelas[beneficio]
                        
                        # Eq. 46
                        despesas[beneficio][ano] = est_ano * vmb * npar
                        
                    else:
                        # Cálculo para Aposentadorias e Pensões
                        val_med_novos_ben = valMedBenef[beneficio] # REVISAR
                        # Idade de 1 a 90 anos
                        for idade in range(1,91):
                            
                            desp_anterior = despesas[beneficio][ano-1][idade-1]
                            conc_anterior = concessoes[beneficio][ano-1][idade-1]
                            tx_rep_anterior = 1
                            # REVISAR: Acredito que o correto seria usar os segurados e nao a PopOcup
                            rend_med_ocup_ant = salarios['SalMedPopOcupUrbAcimPnad'+sexo][ano-1][idade-1]
                            npar = nparcelas[beneficio]
                            prob_morte = probabilidades['Mort'+sexo][ano][idade]
                            fam = probabilidades['fam'+beneficio][ano][idade]
                            # REVISAR - Os valores de salario já tem reajuste, acho que não é necessário aqui
                            reajuste = dadosLDO['TxReajusteBeneficios'][ano]
                            novas_conc = concessoes[beneficio][ano][idade]
                            valor_med_conc = val_med_novos_ben[ano][idade]
                            

                            # Eq. 45
                            part1 = desp_anterior + conc_anterior * tx_rep_anterior * rend_med_ocup_ant * (npar/2)
                            part2 = (1 - prob_morte * fam) * (1 + reajuste/100)
                            part3 = (novas_conc * valor_med_conc * (npar/2))
                            despesas[beneficio].loc[idade, ano] = part1 * part2 + part3
                            
                        # Idade zero
                        novas_conc = concessoes[beneficio][ano][0]
                        valor_med_conc = val_med_novos_ben[ano][0]
                        npar = nparcelas[beneficio]
                        despesas[beneficio].loc[0, ano] = novas_conc * valor_med_conc * (npar/2)
                        

    ##### Calcula despesas para o Salário Maternidade #####
    for beneficio in dados.get_id_beneficios('SalMat'):        
        # 2014-2060
        anos = estoques[beneficio].index
        
        # Verifica se existe estoque para o beneficio
        if beneficio in estoques:                        
            # Objeto do tipo Series que armazena as despesas acumuladas por ano 
            desp_acumulada = pd.Series(0.0, index=anos)
                                                
            # Obtem o estoques acumulados do ano atual 
            for ano in anos:
                estoq_total = estoques[beneficio][ano]
                
                # REVISAR
                # Obtem o valor médio do benefício
                #if dados.get_clientela(beneficio) == 'UrbAcim':
                    # Como não se usa dados desagregados de idade, utiliza-se a média
                    # Considera somente a faixa de 16 a 45 anos
                #    valor_benef = valMedBenef[beneficio][ano][16:46].mean()
                #else:
                #    valor_benef = salarios['salarioMinimo'][ano]                    
                valor_benef = salarios['salarioMinimo'][ano]                    

                npar = nparcelas[beneficio]
                            
                # OBS: A LDO não descreve a equação para o calculo de despesas para o SalMat
                desp_acumulada[ano] = estoq_total * valor_benef * npar  
                
            # Salva no DataFrame
            despesas[beneficio] = desp_acumulada


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

    resultados['Despesas'] = desp_total    
    
    return resultados


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
    for benef in dados.get_id_beneficios('Pe'):
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
    
    
    