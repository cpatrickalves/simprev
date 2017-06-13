# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.tabelas import LerTabelas
import pandas as pd

def calc_estoques(estoques, concessoes, probabilidades, populacao, segurados, periodo):
    
    calc_estoq_apos(estoques, concessoes, probabilidades, segurados, periodo)
    #calc_estoq_aux(estoques, probabilidades, segurados, periodo)
    #calc_estoq_salMat(estoques, populacao , segurados, periodo)

    return estoques

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
        
            sexo = benef[-1]                # Obtém o Sexo
            id_prob_morte = 'Mort'+ sexo    # ex: MortH
            id_fam = 'fam'+benef            # fator de ajuste de mortalidade            
            id_segurado = dados.get_id_segurados(benef)  # ex: CsmUrbH
            
            for ano in periodo:                
                # Adiciona uma nova coluna (ano) no DataFrame com valores zero
                est[benef][ano] = 0
                
                # 1 a 90 anos - Equação 11 da LDO de 2018
                for idade in range(1,91): 
                    est_ano_anterior = est[benef][ano-1][idade-1]
                    prob_sobreviver = 1 - prob[id_prob_morte][ano][idade] * prob[id_fam][idade]
                    entradas = seg[id_segurado][ano][idade] * prob[benef][idade]
                    est[benef].loc[idade, ano] = est_ano_anterior * prob_sobreviver + entradas     # Eq. 11
                    
                    # Salva a quantidade de concessões para uso posterior
                    conc[benef].loc[idade,ano] = entradas
                
                # Calculo para a idade zero
                est[benef].loc[0, ano] = seg[id_segurado][ano][0] * prob[benef][0]
                # Salva a quantidade de concessões para uso posterior
                conc[benef].loc[0, ano] = est[benef].loc[0, ano]
                
                # Ajuste para a idade de 90+ anos (modelo UFPA) - REVISAR
                #est[benef].loc[90, ano] = est[benef].loc[90, ano] + est[benef].loc[90, ano - 1]
                

    return est

# Projeta estoques para Auxílios Doença, Reclusão e Acidente - Equação 17 da LDO de 2018
def calc_estoq_aux(est, prob, seg, periodo):

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    for benef in dados.get_id_beneficios(['Auxd', 'Auxa']):#'Auxr']): # REVISAR
        # Verifica se existe no Estoque
        if benef in est:            
            id_seg = dados.get_id_segurados(benef)
            
            for ano in periodo:
                # REVISAR: a Equação original usa a Pop, mas o certo seria os Segurados
                est[benef][ano] = seg[id_seg][ano] * prob[benef]     # Eq. 17
    
    return est
                
            
# Projeta estoques para Salário-Maternidade - Equação 20 da LDO de 2018 - REVISAR
def calc_estoq_salMat(est, pop, seg, periodo):

    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()

    for benef in dados.get_id_beneficios('SalMat'):            
        if benef in est:
            # Armazena valores do ano 
            est_acumulado = pd.Series(index=est[benef].columns)
                      
            id_seg = dados.get_id_segurados(benef)
            
            # Acumula mulheres de 16 a 45 anos para o estoque existente
            for ano in est[benef]:    
                est_acumulado[ano] = est[benef][ano].sum()
                    
            # Realiza projeção    
            for ano in periodo:
                est_acumulado[ano] = 0     # Cria um novo ano com valores zeros
                nascimentos = pop['PopIbgeM'][ano][0] + pop['PopIbgeH'][ano][0]
                
                # Acumula mulheres de 16 a 45 anos
                seg_16_45 = 0
                pop_16_45 = 0                                
                for idade in range(16,46):
                    seg_16_45 += seg[id_seg][ano][idade]
                    pop_16_45 += pop['PopIbgeM'][ano][idade]
                  
                est_acumulado[ano] = (seg_16_45/pop_16_45) * nascimentos    # Eq. 20
                
            est[benef] = est_acumulado
            
    return est
    

# Projeta os estoque de pensões - Equações 21 a 27 da LDO de 2018
def calc_estoq_pensoes(est, prob, periodo):
    
    # Cria o objeto dados que possui os IDs das tabelas
    dados = LerTabelas()
    # Obtém o conjunto de benefícios do tipo pensão
    lista_pensoes = dados.get_id_beneficios('Pen')
    
        
    PeA = 0
    
    # Calcula pensões do tipo A
    for benef in lista_pensoes:    
        for ano in periodo:
                        
            # Cria uma nova entrada no DataFrame que armazena os estoques
            est[benef][ano] = 0
            
            sexo = benef[-1]                                # Obtém o Sexo
            id_prob_morte = 'Mort'+ sexo                    # ex: MortH
            id_fam = 'fam'+benef                            # fator de ajuste de mortalidade
            id_pens = benef.replace('Pens', 'PensA_')       # Cria um Id para pensão do tipo A
            
            # Copia os dados de estoque para Pensão do tipo A 
            est[id_pens] = est[benef].copy()
            
            # Projeta pensões do tipo A
            # Como não se tem novas concessões desse tipo de pensão, calcula-se
            # nas idades de 1 a 90 anos.
            for idade in range(1,91):
                est_ano_anterior = est[benef][ano-1][idade-1]
                prob_sobreviver = 1 - prob[id_prob_morte][ano][idade] * prob[id_fam][idade]
                                
                # Eq. 22
                est[id_pens].loc[idade, ano] = est_ano_anterior * prob_sobreviver
              
    PeB = 0
        
    Pe = PeA + PeB      # Eq. 21
    
    return Pe

