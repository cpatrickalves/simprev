# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.dados import get_id_beneficios, get_id_segurados
import pandas as pd

def calc_estoques(estoques, probabilidades, populacao, segurados, periodo):
    
    calc_estoq_apos(estoques, probabilidades, segurados, periodo)
    #calc_estoq_aux(estoques, probabilidades, segurados, periodo)
    #calc_estoq_salMat(estoques, populacao , segurados, periodo)

    return estoques

def calc_estoq_apos(est, prob, seg, periodo):
    
    # Identificações das aposentadorias 
    ids_apos= ['Apin', 'Atcn', 'Apid', 'Atcp', 'Ainv', 'Atce', 'Atcd']
    
    # Obtem as aposentadorias para todas as clientelas e sexos
    lista_benef = get_id_beneficios(ids_apos)
        
    for benef in lista_benef:
        # Verifica se o beneficio existe no Estoque
        if benef in est:
        
            sexo = benef[-1]                # Obtém o Sexo
            id_prob_morte = 'Mort'+ sexo    # ex: MortH
            id_fam = 'fam'+benef            # fator de ajuste de mortalidade            
            id_segurado = get_id_segurados(benef)
            
            for ano in periodo:                
                # Adiciona uma nova coluna (ano) no DataFrame com valores zero
                est[benef][ano] = 0
                
                # 1 a 90 anos                
                for idade in range(1,91): 
                    est_ano_anterior = est[benef][ano-1][idade-1]
                    prob_sobreviver = 1 - prob[id_prob_morte][ano][idade] * prob[id_fam][idade]
                    entradas = seg[id_segurado][ano][idade] * prob[benef][idade]
                    est[benef].loc[idade, ano] = est_ano_anterior * prob_sobreviver + entradas
                
                # Calculo para a idade zero
                est[benef].loc[0, ano] = seg[id_segurado][ano][0] * prob[benef][0]
                
                # Ajuste para a idade de 90+ anos (modelo UFPA) - REVISAR
                #est[benef].loc[90, ano] = est[benef].loc[90, ano] + est[benef].loc[90, ano - 1]
                

    return est

# Projeta estoques para Auxílios Doença, Reclusão e Acidente
def calc_estoq_aux(est, prob, seg, periodo):
    
    for benef in get_id_beneficios(['Auxd', 'Auxa']):#'Auxr']): # REVISAR
        # Verifica se existe no Estoque
        if benef in est:
            
            id_seg = get_id_segurados(benef)
            
            for ano in periodo:
                # REVISAR: a Eq original usa a Pop, mas o certo seria os Segurados
                est[benef][ano] = seg[id_seg][ano] * prob[benef] # Eq 17 da LDO 2018
    
    return est
                
            
# Projeta estoques para Salário-Maternidade - REVISAR
def calc_estoq_salMat(est, pop, seg, periodo):    
    
    for benef in get_id_beneficios('SalMat'):
            
        if benef in est:

            # Armazena valores do ano 
            est_acumulado = pd.Series(index=est[benef].columns)
                      
            id_seg = get_id_segurados(benef)
            
            # Acumula mulheres de 16 a 45 anos para o estoque existente
            for ano in est[benef]:    
                est_acumulado[ano] = est[benef][ano].sum()
                    
            # Realiza projeção    
            for ano in periodo:
                est_acumulado[ano] = 0         # Cria um novo ano com valores zeros
                nascimentos = pop['PopIbgeM'][ano][0] + pop['PopIbgeH'][ano][0]
                
                # Acumula mulheres de 16 a 45 anos
                seg_16_46 = 0
                pop_16_46 = 0                                
                for idade in range(16,46):
                    seg_16_46 += seg[id_seg][ano][idade]
                    pop_16_46 += pop['PopIbgeM'][ano][idade]
                  
                est_acumulado[ano] = (seg_16_46/pop_16_46) * nascimentos
                
            est[benef] = est_acumulado
            
    return est
    

def calc_estoq_pensoes():
    pass

