# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.tabelas import LerTabelas
import pandas as pd


# Calcula despesas com benefícios
# Baseado nas Equações da LDO de 2018 e Planilhas do MF
def calc_despesas(despesas, estoques, concessoes, valCoBen, salarios, valMedBenef, probabilidades, dadosLDO, nparcelas, resultados, periodo):

    # Objeto criado para uso das funções da Classe LerTabelas
    dados = LerTabelas()
    ult_ano_estoq = periodo[0]-1 # 2014
    
    ##### Calcula despesa com o dados conhecidos (2011-2014)
    # O valor no banco de dados é mensal
    for beneficio in despesas.keys():
        
        # Auxílio doença para os que recebem Acima do Piso
        if 'AuxdUrbAcim' in beneficio:
            despesas[beneficio] = valCoBen[beneficio] * nparcelas[beneficio]
        
        # Aposentadorias e Pensões para quem recebe acima do piso
        elif 'Acim' in beneficio:        
            desp_dez = despesas[beneficio]  # despesas dos mes de dezembro
            despesas[beneficio] = desp_dez * nparcelas[beneficio]            
            
        # Demais auxílios
        elif 'Aux' in beneficio:            
            qtd_benef = 0
    
            if 'Auxd' in beneficio:
                qtd_benef = concessoes[beneficio][ult_ano_estoq]            
            else:
                qtd_benef = estoques[beneficio][ult_ano_estoq]
    
            # OBS: Para o Auxílio-acidente a regra é 50% do valor do “Salário de Benefício”
            # fonte: http://www.previdencia.gov.br/servicos-ao-cidadao/informacoes-gerais/valor-beneficios-incapacidade/
            if 'Auxa' in beneficio:
                valor_benef = salarios['salarioMinimo'][ult_ano_estoq] * 0.5
            else:
                valor_benef = salarios['salarioMinimo'][ult_ano_estoq]
                
            npar = nparcelas[beneficio][ult_ano_estoq]

            # Calcula a despesa para cada benefício
            despesas[beneficio][ult_ano_estoq] = qtd_benef * valor_benef * npar
            
        # Demais tipos
        else:            
            estoq_total = estoques[beneficio][ult_ano_estoq]
            estoq_total_ano_ant = estoques[beneficio][ult_ano_estoq-1]
            valor_benef = salarios['salarioMinimo'][ult_ano_estoq]
            npar = nparcelas[beneficio][ult_ano_estoq]
            estoq_medio = ((estoq_total + estoq_total_ano_ant)/2) 

            # Calcula a despesa para cada benefício (Eq. 44)
            despesas[beneficio][ult_ano_estoq] = estoq_medio * valor_benef * npar          

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
                        # Calculo para Auxílios
                        if 'Aux' in beneficio:                        
                            qtd_benef = estoques[beneficio][ano]
                            valor_benef = salarios['salarioMinimo'][ano]
                                        
                            # OBS: Para o Auxílio-acidente a regra é 50% do valor do “Salário de Benefício”
                            # fonte: http://www.previdencia.gov.br/servicos-ao-cidadao/informacoes-gerais/valor-beneficios-incapacidade/
                            if 'Auxa' in beneficio:
                                valor_benef = salarios['salarioMinimo'][ano] * 0.5
                            
                            npar = nparcelas[beneficio][ano]
                
                            # Calcula a despesa para cada benefício
                            despesas[beneficio][ano] = qtd_benef * valor_benef * npar
                        
                        # Cálculo para os demais    
                        else:                                              
                            # Obtem o estoques do ano e do ano anterior
                            estoq_total = estoques[beneficio][ano]
                            estoq_total_ano_ant = estoques[beneficio][ano-1]
                            valor_benef = salarios['salarioMinimo'][ano]
                            npar = nparcelas[beneficio][ano]
    
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
                #val_med_novos_ben = fator_prev * ajuste * salarios['SalMedSegUrbAcimPnad'+sexo] 
            
            for ano in periodo:
                if ano in estoques[beneficio].columns:      # verifica se existe projeção para esse ano
                
                    # Cálculo das despesas com os Auxílios 
                    if 'Aux' in beneficio:                                          
                        est_ano = estoques[beneficio][ano]
                        vmb = valMedBenef[beneficio][ano]
                        npar = nparcelas[beneficio][ano]
                        
                        # Eq. 46
                        despesas[beneficio][ano] = est_ano * vmb * npar
                        
                    else:                       
                        # Cálculo para Aposentadorias e Pensões
                        val_med_novos_ben = valMedBenef[beneficio] 
                        # Idade de 1 a 90 anos
                        for idade in range(1,91):
                            
                            # Para a idade de 90 anos 
                            if idade == 90: 
                                desp_anterior = despesas[beneficio][ano-1][idade-1] + despesas[beneficio][ano-1][idade]
                            else:
                                desp_anterior = despesas[beneficio][ano-1][idade-1]
                                
                            conc_anterior = concessoes[beneficio][ano-1][idade-1]
                            
                            # OBS: Acredito que o correto seria usar os segurados e nao a PopOcup
                            # OBS: O rend_med_ocup_ant já inclui a taxa de reposição da Eq. 45
                            valor_med_conc_ant = val_med_novos_ben[ano-1][idade-1]
                            npar = nparcelas[beneficio][ano]
                            npar_ant = nparcelas[beneficio][ano-1]
                            prob_morte = probabilidades['Mort'+sexo][ano][idade]
                            fam = probabilidades['fam'+beneficio][ano][idade]                            
                            # Nas planilhas usa-se o termo Atualização Monetária
                            reajuste = dadosLDO['TxReajusteBeneficios'][ano] 
                            novas_conc = concessoes[beneficio][ano][idade]
                            valor_med_conc = val_med_novos_ben[ano][idade]
                            
                            # Eq. 45                            
                            part1 = desp_anterior + conc_anterior * valor_med_conc_ant * (npar_ant/2)
                            part2 = (1 - prob_morte * fam) * (1 + reajuste/100)
                            part3 = (novas_conc * valor_med_conc * (npar/2))
                            despesas[beneficio].loc[idade, ano] = part1 * part2 + part3
                            
                        # Idade zero
                        novas_conc = concessoes[beneficio][ano][0]
                        valor_med_conc = val_med_novos_ben[ano][0]
                        npar = nparcelas[beneficio][ano]
                        despesas[beneficio].loc[0, ano] = novas_conc * valor_med_conc * (npar/2)
                        

    ##### Calcula despesas para o Salário Maternidade #####
    for beneficio in dados.get_id_beneficios('SalMat'):        
        
        # 2014-2060
        anos = [periodo[0]-1] + periodo
        
        # Verifica se existe estoque para o beneficio
        if beneficio in estoques:   
                     
            # Objeto do tipo Series que armazena as despesas acumuladas por ano 
            desp_acumulada = pd.Series(0.0, index=anos)
                                                
            # Obtem o estoques acumulados do ano atual 
            for ano in anos:
                estoq_total = estoques[beneficio][ano]
                
                # se a clientela for UrbAcim 
                if 'Acim' in beneficio:
                    valor_benef = valMedBenef['SalMatUrbAcimM'][ano]
                else:
                    valor_benef = salarios['salarioMinimo'][ano]                    
                    
                npar = nparcelas[beneficio][ano]
                            
                # OBS: A LDO não descreve a equação para o calculo de despesas para o SalMat
                desp_acumulada[ano] = estoq_total * valor_benef * npar  
                
            # Salva no DataFrame
            despesas[beneficio] = desp_acumulada


    ##### Calcula a despesa total #####
    anos = [periodo[0]-1] + periodo             #2014-2060
    desp_total = pd.Series(0.0, index=anos)     # Objeto do tipo Serie que armazena a despesa total
    for ano in anos:
        for beneficio in despesas.keys():            
            # Verifica se o benefício é do tipo Salário Maternidade
            # O objeto que armazena as despesas com Salário Maternidade é diferente            
            if 'SalMat' in beneficio:                                
                if ano in despesas[beneficio].index:      # verifica se existe projeção para esse ano                                                
                    desp_total[ano] += despesas[beneficio][ano]                                    
            else:
            # Calculo para os demais benefícios                
                if ano in despesas[beneficio].columns:      # verifica se existe projeção para esse ano
                    desp_total[ano] += despesas[beneficio][ano].sum()               


    # Calcula a taxa de crescimento da Despesa
    tx_cres_desp = pd.Series(0.0, index=periodo)
    for ano in periodo:  # pula o primeiro ano
        tx_cres_desp[ano] = desp_total[ano]/desp_total[ano-1] - 1


    resultados['despesas'] = desp_total    
    resultados['tx_cres_despesa'] = tx_cres_desp
    
    return resultados


# Calcula o número de parcelas paga por ano por um benefício
# Existe uma descrição de cálculo na seção 4.6 da LDO (pag. 43)
# Porém, são necessários o valores totaais e despesas por beneficios para fazer esse cálculo
# como só temos dados do mês de dezembro, os valores foram fixados manualmente
# OBS: Valores obtidos das planilhas do MF
def calc_n_parcelas(estoques, despesa, valMedBenef, periodo):
    
    # ano_estoq = periodo[0]-1    # 2014
    
    dados = LerTabelas()    

    # Dicionário que armazena o número médio de parcelas para tipo de beneficio
    n_parcelas = {}
    # 2014
    ano_estoque = periodo[0]-1
    # 2014-2060
    anos = [ano_estoque] + periodo    
       
    # Aposentadorias Idade Normal
    for benef in dados.get_id_beneficios('Apin'):
        
        # Rurais e Urbanos tem valores diferentes
        if 'Rur' in benef:
            n_parcelas[benef] = pd.Series(13.0, index=anos)
            n_parcelas[benef].loc[periodo[0]] = 12.95                 # 2015
            n_parcelas[benef].loc[periodo[1]:] = 12.82                # 2016-2060
        else:        
            n_parcelas[benef] = pd.Series(13.0, index=anos)
            n_parcelas[benef].loc[periodo[0]] = 12.7                  # 2014-2015
            n_parcelas[benef].loc[periodo[1]:] = 12.95                # 2016-2060

    # Aposentadorias TC Normal
    for benef in dados.get_id_beneficios('Atcn'):
        
        # Rurais e Urbanos tem valores diferentes
        if 'Rur' in benef:
            n_parcelas[benef] = pd.Series(13.0, index=anos)
            n_parcelas[benef].loc[periodo[0]:] = 12.92                # 2015-2060
        else:        
            n_parcelas[benef] = pd.Series(13.0, index=anos)
            n_parcelas[benef].loc[periodo[0]] = 11.7                  # 2015
            n_parcelas[benef].loc[periodo[1]:] = 12.0                 # 2016-2060       
    
        
    # Aposentadorias Idade Deficiente
    for benef in dados.get_id_beneficios('Apid'):
        n_parcelas[benef] = pd.Series(13.0, index=anos)               # 2014-2060
        
    # Aposentadorias TC Professor
    for benef in dados.get_id_beneficios('Atcp'):
        # Rurais e Urbanos tem valores diferentes
        if 'Rur' in benef:
            n_parcelas[benef] = pd.Series(13.0, index=anos)           # 2014-2060
        else:        
            n_parcelas[benef] = pd.Series(13.0, index=anos)
            n_parcelas[benef].loc[periodo[0]] = 13.46                 # 2015
            n_parcelas[benef].loc[periodo[1]:] = 14.5                 # 2016-2060    
        
    # Aposentadorias Invalidez
    for benef in dados.get_id_beneficios('Ainv'):
        # Rurais e Urbanos tem valores diferentes
        if 'Rur' in benef:
            n_parcelas[benef] = pd.Series(13.0, index=anos)
            n_parcelas[benef].loc[periodo[0]] = 13.09                 # 2015
            n_parcelas[benef].loc[periodo[1]:] = 12.96                # 2016-2060
        else:        
            n_parcelas[benef] = pd.Series(13.0, index=anos)
            n_parcelas[benef].loc[periodo[0]] = 12.3                  # 2015
            n_parcelas[benef].loc[periodo[1]:] = 11.9                 # 2016-2060
        
    # Aposentadorias TC especial
    for benef in dados.get_id_beneficios('Atce'):
        # Rurais e Urbanos tem valores diferentes
        if 'Rur' in benef:
            n_parcelas[benef] = pd.Series(13.0, index=anos)          # 2014-2060
        else:        
            n_parcelas[benef] = pd.Series(13.0, index=anos)
            n_parcelas[benef].loc[periodo[0]] = 12.5                 # 2015
            n_parcelas[benef].loc[periodo[1]:] = 13.6                # 2016-2060    
        
    # Aposentadorias TC Deficiente
    for benef in dados.get_id_beneficios('Atcd'):
        n_parcelas[benef] = pd.Series(13.0, index=anos)              # 2014-2060

    # Pensões
    for benef in dados.get_id_beneficios('Pe'):
        # Rurais e Urbanos tem valores diferentes
        if 'Rur' in benef:
            n_parcelas[benef] = pd.Series(13.0, index=anos)
            n_parcelas[benef].loc[periodo[0]] = 12.97                 # 2015
            n_parcelas[benef].loc[periodo[1]:] = 12.89                # 2016-2060
        else:        
            n_parcelas[benef] = pd.Series(13.0, index=anos)
            n_parcelas[benef].loc[periodo[0]] = 12.70                 # 2015
            n_parcelas[benef].loc[periodo[1]:] = 13.10                # 2016-2060
        
    # Auxilios Doença
    for benef in dados.get_id_beneficios('Auxd'):
        # Rurais e Urbanos tem valores diferentes
        if 'Rur' in benef:
            n_parcelas[benef] = pd.Series(12.0, index=anos)
            n_parcelas[benef].loc[periodo[0]] = 11.83                 # 2015-2015
            n_parcelas[benef].loc[periodo[1]:] = 13.32                # 2016-2060
        else:        
            n_parcelas[benef] = pd.Series(12.0, index=anos)
            n_parcelas[benef].loc[periodo[0]] = 8.33                  # 2015
            n_parcelas[benef].loc[periodo[1]:] = 9.01                 # 2016-2060

    # Auxilios Acidente
    for benef in dados.get_id_beneficios('Auxa'):
        # Rurais e Urbanos tem valores diferentes
        if 'Rur' in benef:
            n_parcelas[benef] = pd.Series(12.0, index=anos)
            n_parcelas[benef].loc[periodo[0]] = 12.99                 # 2015
            n_parcelas[benef].loc[periodo[1]:] = 13.46                # 2016-2060
        else:        
            n_parcelas[benef] = pd.Series(12.0, index=anos)
            n_parcelas[benef].loc[periodo[0]] = 12.43                 # 2015
            n_parcelas[benef].loc[periodo[1]:] = 12.56                # 2016-2060

    # Auxilios Reclusão
    for benef in dados.get_id_beneficios('Auxr'):
        # Rurais e Urbanos tem valores diferentes
        if 'Rur' in benef:
            n_parcelas[benef] = pd.Series(12.0, index=anos)
            n_parcelas[benef].loc[periodo[0]] = 12.06                 # 2015
            n_parcelas[benef].loc[periodo[1]:] = 12.18                # 2016-2060
        else:        
            n_parcelas[benef] = pd.Series(12.0, index=anos)
            n_parcelas[benef].loc[periodo[0]] = 12.31                 # 2015
            n_parcelas[benef].loc[periodo[1]:] = 14.03                # 2016-2060
        
    # Salario Maternidade
    for benef in dados.get_id_beneficios('SalMat'):
        n_parcelas[benef] = pd.Series(4.0, index=anos)                # 2014-2060

    # Assistenciais LoasDef
    for benef in dados.get_id_beneficios('LoasDef'):
        n_parcelas[benef] = pd.Series(12.0, index=anos)
        n_parcelas[benef].loc[periodo[0]] = 12.05                     # 2015
        n_parcelas[benef].loc[periodo[1]:] = 12.00                    # 2016-2060
    
    # Assistenciais LoasIdo
    for benef in dados.get_id_beneficios('LoasIdo'):
        n_parcelas[benef] = pd.Series(12.0, index=anos)
        n_parcelas[benef].loc[periodo[0]] = 11.96                     # 2015
        n_parcelas[benef].loc[periodo[1]:] = 11.73                    # 2016-2060
        
    # Assistenciais RMV
    for benef in dados.get_id_beneficios('Rmv'):
        n_parcelas[benef] = pd.Series(12.0, index=anos)
        n_parcelas[benef].loc[periodo[0]] = 12.09                     # 2015
        n_parcelas[benef].loc[periodo[1]:] = 12.06                    # 2016-2060


   # for beneficio in estoques.keys():
   #     # Verifica se existe dados de despesa para o beneficio
   #     if beneficio in despesa.keys():
   #         desp = despesa[beneficio][ano_estoq].sum()
   #         est = estoques[beneficio][ano_estoq].sum()
   #         vm = valMedBenef[beneficio][ano_estoq].mean()
   #         n_parcelas[beneficio] = Dt/(vm*est)
                   
    return n_parcelas
    
    
    