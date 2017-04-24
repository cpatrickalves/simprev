# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.dados import get_id_beneficios, get_id_segurados

def calc_estoques(estoques, probabilidades, segurados, periodo):
    
    calc_estoq_apos(estoques, probabilidades, segurados, periodo)
    #calc_estoq_aux(estoques, probabilidades, segurados, periodo)

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
    
def calc_estoq_aux(est, prob, seg, periodo):
    
    for benef in get_id_beneficios(['Auxd', 'Auxa', 'Auxr']):
        # Verifica se existe no Estoque
        if benef in est:
            
            id_seg = get_id_segurados(benef)
            
            for ano in periodo:
                # REVISAR: a Eq original usa a Pop, mas o certo seria os Segurados
                est[benef][ano] = seg[id_seg][ano] * prob[benef] # Eq 17 da LDO 2018
    
    return est
                
            
            
            
        
    
    

