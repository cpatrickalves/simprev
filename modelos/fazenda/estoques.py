# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.dados import get_id_beneficios, get_clientela

def calc_estoques(estoques, probabilidades, segurados, periodo):
    
    calc_estoq_apos(estoques, probabilidades, segurados, periodo)

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
            clientela = get_clientela(benef)
            id_segurado = clientela + sexo
            
            # Faz o mapeamento Clientela para Segurado
            if clientela == 'UrbPiso':
                id_segurado =  'CsmUrb' + sexo
            elif clientela == 'UrbAcim':
                id_segurado = 'CaUrb' + sexo
            
            for ano in periodo:                
                # Adiciona uma nova coluna (ano) no DataFrame com valores zero
                est[benef][ano] = 0
                
                for idade in range(1,91): 
                    est_ano_anterior = est[benef][ano-1][idade-1]
                    prob_sobreviver = 1 - prob[id_prob_morte][ano][idade] * prob[id_fam][idade]
                    concessoes = seg[id_segurado][ano][idade] * prob[benef][idade]
                    est[benef].loc[idade, ano] = est_ano_anterior * prob_sobreviver + concessoes

    return est
    
def calc_estoq_aux():
    pass

