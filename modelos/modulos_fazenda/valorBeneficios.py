# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

import pandas as pd
import numpy as np


# Calcula valor médio dos benefícios utilizando o método descrito nas planilhas do MF
# Divide o valor total de concessões pelo número de concessões
def calc_valMedBenef(estoques, despesas, valCoBen, concessoes, dadosLDO, salarios, segurados, periodo):

    # ultimo com despesa/estoque conhecida (2014)
    ultimo_ano = periodo[0] - 1

    # Dicionário que armazena os valores médios para cada benefício
    valMedBenef = {}

    # Para cada benefício no dicionário de estoques
    for beneficio in valCoBen.keys():                          
        
        # Pula os benefícios que recebem o piso (Salario Mínimo)
        if 'UrbAcim' not in beneficio:
            continue
        
        valMed = 0
        
        # Para os Auxílios reclusão e acidente o cálculo é baseado nos estoques
        if 'Auxr' in beneficio or 'Auxa' in beneficio:
            # Calcula valor médio
            desp = despesas[beneficio][ultimo_ano]
            estoq = estoques[beneficio][ultimo_ano]
            valMed = desp/estoq 
            
        # Para os demais são utilizados os dados de concessões (valorConcessões/QtdConcessões)             
        else:
            valCo = valCoBen[beneficio][ultimo_ano]
            conc = concessoes[beneficio][ultimo_ano]
            valMed = valCo/conc
            
        # Converte para um dataframe
        valMedBenef[beneficio] = pd.DataFrame(valMed, columns=[ultimo_ano])
        # Substitui os NaN por zeros
        valMedBenef[beneficio].fillna(0.0, inplace=True)            
        
        # OBS: Aplica atualização monetária (6.41%) para o ano de 2014 de acordo com as planilhas do MF        
        atualizMonet = 1#1.0641
        valMedBenef[beneficio][2014] = valMedBenef[beneficio][2014] * atualizMonet

    
     # Calcula taxa de reposiçao para todos os anos da projeçao usando a Eq. 48
    txReposicao = calc_tx_reposicao(valMedBenef, salarios, periodo)
        
    # Projeta o valor dos benefícios para os anos seguintes    
    for beneficio in valMedBenef.keys():
        for ano in periodo:        
            sexo = beneficio[-1]
            # Para as pensões usa-se os segurados do sexo oposto
            if 'Pens' in beneficio:
                sexo_oposto = 'M' if sexo == 'H' else 'H'
                
                # Lógica utilizada nas planilhas do MF
                sal = salarios['SalMedSegUrbAcimPnad'+sexo][ano]
                contr = segurados['CaUrb'+sexo][ano]
                contrTotal = segurados['CaUrb'+sexo][ano].sum()
                media = (sal * contr).sum() / contrTotal
                
                sal_sexo_op = salarios['SalMedSegUrbAcimPnad'+sexo_oposto][ano]
                contr_sexo_op = segurados['CaUrb'+sexo_oposto][ano]
                contrTotal_sexo_op = segurados['CaUrb'+sexo_oposto][ano].sum()
                media_sexo_op = (sal_sexo_op * contr_sexo_op).sum() / contrTotal_sexo_op
                                
                mediaTotal = ((media * contrTotal) + (media_sexo_op * contrTotal_sexo_op)) / (contrTotal + contrTotal_sexo_op)
                
                valMedBenef[beneficio][ano] = txReposicao[beneficio][ano] * mediaTotal              
            
            else:                
                # Eq. 47
                valMedBenef[beneficio][ano] = txReposicao[beneficio][ano] * salarios['SalMedSegUrbAcimPnad'+sexo][ano]
             
    # Limita o valor dos benefícios pelo teto        
    for beneficio in valMedBenef.keys():
        for ano in valMedBenef[beneficio]:
            teto = salarios['tetoRGPS'][ano]
            for idade in valMedBenef[beneficio].index:                
                if valMedBenef[beneficio][ano][idade] > teto:
                    valMedBenef[beneficio].loc[idade, ano] = teto
                    
    # Garante que o benefício não seja menor que 1 SM
    for beneficio in valMedBenef.keys():
        for ano in valMedBenef[beneficio]:
            sm = salarios['salarioMinimo'][ano]
            for idade in valMedBenef[beneficio].index:                
                if valMedBenef[beneficio][ano][idade] < sm:                    
                    valMedBenef[beneficio].loc[idade, ano] = sm
     
    valMedBenef['txReposicao'] = txReposicao                                   
    
    # REVISAR - Esta pendente a implementação do cálculo do Fator Previdenciário para as AposTC
    # Isso influencia nas txRepos e nos ValMeds
   
    ##### Cálculo para o Salário Maternidade    
    # Calculo baseado no Salario Medio das seguradas e na quantidade de seguradas
    # Necessário somente para as seguradas urbanas que recebem acima do piso
    # Esse cálculo não é descrito na LDO de 2018, foi baseado nas planilhas do MF
          
    # Os valores de SalMat são indexados apenas por ano (2014-2060)
    salMat = pd.Series(0.0, index=[ultimo_ano]+periodo)
    for ano in salMat.index:
        # Total de contribuintes em idade fértil (16 a 45 anos)
        totalContr = segurados['CaUrbM'][ano][16:46].sum()      # OBS: esse cálculo nas planilhas usa sempre o ano de 2014
        salMedMidadeFertil = 0.0 
        
        for idade in range(16,46):  # 16 a 45 anos                        
            salmed_x_qtd = (segurados['CaUrbM'][ano][idade] * salarios['SalMedSegUrbAcimPnadM'][ano][idade])/ totalContr
            salMedMidadeFertil += salmed_x_qtd      # acumula os valores
            
        # Salva o salário médio das mulheres em idade fértil
        salMat[ano] = salMedMidadeFertil
    
    # Salva no dicionário    
    valMedBenef['SalMatUrbAcimM'] = salMat
        
    return valMedBenef


# Calcula a taxa de reposição (Eq. 48)
def calc_tx_reposicao(valMedBenef, salarios, periodo):

    # Dicionário que armazena as taxas de reposição
    txReposicao = {}
    
    # Ano inicial com valores de benefícios(2014)
    ano_benef = periodo[0] - 1
    
    # Insere o ano de 2014 na lista periodos
    anos = [ano_benef] + periodo

    for beneficio in valMedBenef.keys():
        # Cria Dataframe que armazena as taxas
        txReposicao[beneficio] = pd.DataFrame(0.0, index=range(0,91), columns=anos)        
        
        sexo = beneficio[-1]
        
        # O cálculo para o auxílio reclusão é diferente
        if 'Auxr' in beneficio:                        
            for idade in range(0,91):      
                deslocamento = 0            
                # Na planilha são aplicados deslocamentos nas idades
                if idade < 61 and sexo == 'H': 
                    deslocamento = 25
                elif idade < 61 and sexo == 'M': 
                    deslocamento = 18               
                
                # O rendimento considerado é sempre o do homens
                rend_medio_seg = salarios['SalMedSegUrbAcimPnadH'][ano_benef][idade+deslocamento]
                vmb = valMedBenef[beneficio][ano_benef][idade]
                
                if rend_medio_seg == 0:
                    txReposicao[beneficio].loc[idade, ano_benef] = 0
                else:                
                    # Eq. 48    
                    txReposicao[beneficio].loc[idade, ano_benef] = vmb/rend_medio_seg

        # REVISAR - IMPLEMENTAR CÁLCULO                 
        elif 'Pens' in beneficio:        
            txH = [0.59, 0.61, 0.61, 0.62, 0.63, 0.63, 0.62, 0.63, 0.66, 0.67, 0.65, 0.67,
                  0.68, 0.68, 0.69, 0.68, 0.68, 0.71, 0.69, 0.72, 0.70, 0.69, 0.72, 0.69, 
                  0.72, 0.71, 0.75, 0.75, 0.76, 0.81, 0.79, 0.82, 0.82, 0.83, 0.86, 0.85, 
                  0.88, 0.91, 0.88, 0.87, 0.90, 0.88, 0.88, 0.89, 0.91, 0.89, 0.90, 0.91, 
                  0.89, 0.90, 0.88, 0.90, 0.91, 0.92, 0.90, 0.90, 0.89, 0.90, 0.90, 0.90, 
                  0.89, 0.87, 0.87, 0.85, 0.85, 0.86, 0.87, 0.83, 0.85, 0.84, 0.84, 0.81, 
                  0.84, 0.82, 0.83, 0.82, 0.82, 0.82, 0.80, 0.82, 0.83, 0.84, 0.86, 0.84, 
                  0.89, 0.88, 0.87, 0.90, 0.91, 0.89, 0.97]  
            
            txM = [0.72, 0.77, 0.74, 0.76, 0.79, 0.80, 0.82, 0.81, 0.85, 0.85, 0.92, 0.89,
                   0.91, 0.91, 0.89, 0.90, 0.90, 0.90, 0.97, 0.99, 1.04, 1.05, 0.95, 1.11, 
                   1.00, 1.01, 0.91, 0.92, 0.97, 0.93, 0.91, 0.84, 0.89, 0.99, 0.89, 0.95, 
                   0.92, 0.83, 0.97, 0.87, 0.86, 0.84, 0.83, 0.82, 0.86, 0.79, 0.79, 0.81, 
                   0.83, 0.82, 0.84, 0.82, 0.79, 0.78, 0.76, 0.76, 0.75, 0.76, 0.77, 0.71,
                   0.70 ,0.72, 0.70, 0.67, 0.70, 0.67, 0.66, 0.64, 0.64, 0.60, 0.62, 0.63, 
                   0.64, 0.62, 0.57, 0.59, 0.59, 0.61, 0.56, 0.57, 0.59, 0.59, 0.59, 0.56,
                   0.52, 0.59, 0.59, 0.54, 0.54, 0.54, 0.55]
            
            for idade in range(0,91):
                if sexo == 'H' :
                    txReposicao[beneficio].loc[idade, ano_benef] = txH[idade]
                else:
                    txReposicao[beneficio].loc[idade, ano_benef] = txM[idade]
            
        else:                
            rend_medio_seg = salarios['SalMedSegUrbAcimPnad'+sexo][ano_benef]
            vmb = valMedBenef[beneficio][ano_benef]
            
            # Eq. 48
            txReposicao[beneficio][ano_benef] = vmb/rend_medio_seg

        # Trata as divisões por zero que geram NaN e Inf
        txReposicao[beneficio].replace([np.inf, -np.inf], np.nan, inplace=True)
        txReposicao[beneficio].fillna(0.0, inplace=True)
        
        # Repete a taxa para os anos seguintes
        for ano in periodo:
            txReposicao[beneficio][ano] = txReposicao[beneficio][ano - 1]
        
    
    return txReposicao




# Calcula os valores médios de todos os benefícios
# Essa função divide o valor das despesas pelos estoques
# OBS: Não utilizado
def calc_valMedBenef_ufpa(estoques, despesas, dadosLDO, salarios, periodo):

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
    # Eq. 38
    for ano in periodo:
        for beneficio in valMedBenef.keys():
            reajuste = 1.0 + dadosLDO['TxReajusteBeneficios'][ano]/100
            valMedBenef[beneficio][ano] = valMedBenef[beneficio][ano-1] * reajuste

    # Limita o valor dos benefícios pelo teto        
    for beneficio in valMedBenef.keys():
        for ano in valMedBenef[beneficio]:
            teto = salarios['tetoRGPS'][ano]
            for idade in valMedBenef[beneficio].index:                
                if valMedBenef[beneficio][ano][idade] > teto:
                    valMedBenef[beneficio].loc[idade, ano] = teto
                    
    # Garante que o benefício não seja menor que 1 SM
    for beneficio in valMedBenef.keys():
        for ano in valMedBenef[beneficio]:
            sm = salarios['salarioMinimo'][ano]
            for idade in valMedBenef[beneficio].index:                
                if valMedBenef[beneficio][ano][idade] < sm:                    
                    valMedBenef[beneficio].loc[idade, ano] = sm
                                        
    
    return valMedBenef
