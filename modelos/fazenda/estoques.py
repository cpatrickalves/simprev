# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from util.dados import get_id_beneficios

def calc_estoques(estoques, probabilidades, populacao):
    
    es_apos = calc_estoq_apos(estoques, probabilidades)
        

def calc_estoq_apos(est, prob, pop):
    
    periodo = list(range(2015,2061))
    Reajuste = 1 # REVISAR
    
    #padrão dos estoques: EsAinvUrbAcimM    
    
    # Obtem os IDs das aposentadorias
    lista_benef = get_id_beneficios(['Apin'])
'''    
    for benef in lista_benef:
        id_prob_morte = 'Mort'+benef[-1]
        id_prob_benef = 
        for ano in periodo:
            for idade in range(1,91): 
                est_ano_anterior = est[benef][ano-1][idade-1]
                prob_sobreviver = 1-prob['Mort'+benef[-1]]*Reajuste
                concessoes = segurados * prov[]
                saidas = est_ano_anterior *
                
'''    
    
def calc_estoq_aux():
    pass


'''
Distribuidora Convicta comercio de produtos alimentícios
Fernando - Criasim
cnpj 

Avenida Max Porpino 5539

    for sexo in ['H', 'M']:    
        
        # Cria o DataFrame que armazena as probabilidades para um sexo
        mort = pd.DataFrame(index=range(0,91), columns=periodo) 
        chave_pop = 'PopIbge'+sexo
        
        for ano in periodo[0:-1]:  # Vai do primeiro ao penúltimo ano
            for idade in range(0,89): 
                pop_atual = pop[chave_pop][ano][idade]            
                pop_prox_ano = pop[chave_pop][ano+1][idade+1]                
                mort[ano][idade] = 1 - (pop_prox_ano/pop_atual)
'''
