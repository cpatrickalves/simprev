from modelos.modulos_fazenda.probabilidades import *
from modelos.modulos_fazenda.demografia import *
from modelos.modulos_fazenda.taxas import *
from modelos.modulos_fazenda.estoques import *
from modelos.modulos_fazenda.salarios import *
from modelos.modulos_fazenda.receitas import *
from modelos.modulos_fazenda.depesas import *
from modelos.modulos_fazenda.valorBeneficios import *


# Calcula dados demográficos
def calc_demografia(populacao, taxas):

    # Dicionário que armazena os segurados rurais e contribuintes urbanos
    segurados = {}
    
    # Calcula Pop Urbana e Rural    
    pop_ur = calc_pop_urb_rur(populacao, taxas)
    
    # Calcula PEA Urbana e Rural
    pea = calc_pea_urb_rur(pop_ur, taxas)
    
    # Calcula Pop. Ocupada Urbana e Rural
    pocup = calc_pocup_urb_rur(pea, taxas)
    
    # Calcula Pop. ocupada Urbana e Rural que recebe o SM e acima do SM
    pocup_csm_ca = calc_pocup_Csm_Ca(pocup, taxas)
        
    # Calcula Segurados urbanos
    segurados_urb = calc_segurados_urb(pocup, taxas)
        
    # Calcula os Segurados Rurais
    segurados_rur = calc_segurados_rur(pea, taxas)
        
    # Adiciona as novas populações no dicionário população
    populacao.update(pop_ur)
    populacao.update(pea)
    populacao.update(pocup)
        
    # Adiciona contribuintes e segurados no dicionário segurados
    segurados.update(pocup_csm_ca)
    segurados.update(segurados_urb)
    segurados.update(segurados_rur)
    
    # Os segurados rurais são toda a população rural
    segurados['PopRurH'] = pop_ur['PopRurH']
    segurados['PopRurM'] = pop_ur['PopRurM']
    
    # REVISAR TEMP
    segurados['OcupUrbPisoH'] = segurados['CsmUrbH']
    segurados['OcupUrbPisoM'] = segurados['CsmUrbM']
    segurados['OcupUrbAcimH'] = segurados['CaUrbH']
    segurados['OcupUrbAcimM'] = segurados['CaUrbM']
    
    return segurados    


def calc_estoques(estoques, concessoes, cessacoes, probabilidades, populacao, segurados, periodo):
    calc_estoq_apos(estoques, concessoes, probabilidades, segurados, periodo)
    calc_estoq_pensoes(populacao, estoques, concessoes, cessacoes, probabilidades, segurados, periodo)
    calc_estoq_aux(estoques, probabilidades, segurados, periodo)
    calc_estoq_salMat(estoques, populacao , segurados, periodo)
    calc_estoq_assistenciais(estoques, concessoes, populacao, probabilidades, periodo)

    return estoques


def calc_probabilidades(populacao, segurados, estoques,
                        concessoes, cessacoes, periodo):
    # Dicionário que armazena as probabilidades
    probabilidades = {}

    prob_morte = calc_prob_morte(populacao)
    fat_ajuste_mort = calc_fat_ajuste_mort_MF(estoques, cessacoes,
                                           prob_morte, periodo)

    prob_entrada_apos = calc_prob_apos_MF(segurados, concessoes, periodo)
    prob_entrada_aux = calc_prob_aux_MF(segurados, estoques, concessoes, periodo)
    prob_entrada_pens = calc_prob_pensao_MF(concessoes, segurados, populacao, estoques, prob_morte, periodo)  
    prob_assist = calc_prob_assist_MF(populacao, concessoes, periodo)
    
    
    probabilidades.update(prob_morte)
    probabilidades.update(fat_ajuste_mort)
    probabilidades.update(prob_entrada_apos)
    probabilidades.update(prob_entrada_aux)
    probabilidades.update(prob_entrada_pens)
    probabilidades.update(prob_assist)
    
    return probabilidades

# Calcula todas as taxas
def calc_taxas(pop_pnad, parametros):
    
    periodo = parametros['periodo']
    
    taxas = {}

    txurb = calc_tx_urb(pop_pnad, periodo)
    txpart = calc_tx_part(pop_pnad, periodo)
    txocup = calc_tx_ocup(pop_pnad, periodo)
    txocup_csm_ca = calc_tx_ocup_csm_ca(pop_pnad, periodo)
    txSegurados_urb = calc_tx_segurados_urb(pop_pnad, parametros)
    txSegurados_rur = calc_tx_segurados_rur(pop_pnad, periodo)
    
    taxas.update(txurb)
    taxas.update(txpart)
    taxas.update(txocup)
    taxas.update(txocup_csm_ca)
    taxas.update(txSegurados_urb)
    taxas.update(txSegurados_rur)

    return taxas


