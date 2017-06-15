from modelos.modulos_fazenda.probabilidades import *
from modelos.modulos_fazenda.demografia import *
from modelos.modulos_fazenda.taxas import *
from modelos.modulos_fazenda.estoques import *
from modelos.modulos_fazenda.salarios import calc_salarios
from modelos.modulos_fazenda.receitas import *
from modelos.modulos_fazenda.depesas import *


# Calcula dados demográficos
def calc_demografia(populacao, taxas):
    # Dicionário que armazena os segurados rurais e contribuintes urbanos
    segurados = {}

    # Calcula Pop Urbana e Rural
    pop_ur = calc_pop_urb_rur(populacao, taxas)

    # Calcula PEA Urbana e Rural
    pea = calc_pea_urb_rur(pop_ur, taxas)

    # Calcula Pocupada Urbana e Rural
    pocup = calc_pocup_urb_rur(pea, taxas)

    # Calcula Pocupada Urbana e Rural
    csm_ca = calc_Csm_Ca(pocup, taxas)

    # Calcula os Segurados Rurais
    segurados_rur = calc_segurados_rur(pea, taxas)

    # Adiciona as novas populações no dicionário população
    populacao.update(pop_ur)
    populacao.update(pea)
    populacao.update(pocup)

    # Adiciona contribuintes e segurados no dicionário segurados
    segurados.update(csm_ca)
    segurados.update(segurados_rur)

    return segurados


def calc_estoques(estoques, concessoes, probabilidades, populacao, segurados, periodo):
    calc_estoq_apos(estoques, concessoes, probabilidades, segurados, periodo)
    calc_estoq_pensoes(estoques, concessoes, probabilidades, segurados, periodo)
    # calc_estoq_aux(estoques, probabilidades, segurados, periodo)
    # calc_estoq_salMat(estoques, populacao , segurados, periodo)
    calc_estoq_assistenciais(estoques, concessoes, populacao, probabilidades, periodo)

    return estoques


def calc_probabilidades(populacao, segurados, estoques,
                        concessoes, cessacoes, periodo):
    # Dicionário que armazena as probabilidades
    probabilidades = {}

    prob_morte = calc_prob_morte(populacao)
    fat_ajuste_mort = calc_fat_ajuste_mort(estoques, cessacoes,
                                           prob_morte, periodo)

    prob_entrada_apos = calc_prob_apos(segurados, concessoes, periodo)
    # prob_entrada_aux = calc_prob_aux(segurados, estoques, concessoes, periodo)
    # prob_entrada_pens = calc_prob_pensao(concessoes, prob_morte,
    #                                    fat_ajuste_mort, periodo)
    prob_assist = calc_prob_assist(populacao, concessoes, periodo)
    
    
    probabilidades.update(prob_morte)
    probabilidades.update(fat_ajuste_mort)
    probabilidades.update(prob_entrada_apos)
    # probabilidades.update(prob_entrada_aux)
    # probabilidades.update(prob_entrada_pens)
    probabilidades.update(prob_assist)

    # Busca por probabilidades erradas (ex: > 1)
    busca_erros(probabilidades)

    return probabilidades

# Calcula todas as taxas
def calc_taxas(pop_pnad, periodo):
    
    taxas = {}

    txurb = calc_tx_urb(pop_pnad, periodo)
    txpart = calc_tx_part(pop_pnad, periodo)
    txocup = calc_tx_ocup(pop_pnad, periodo)
    txCsm_Ca = calc_tx_cobertura_sm(pop_pnad, periodo)
    txSegurados_rur = calc_tx_segurados_rur(pop_pnad, periodo)
    
    taxas.update(txurb)
    taxas.update(txpart)
    taxas.update(txocup)
    taxas.update(txCsm_Ca)
    taxas.update(txSegurados_rur)

    return taxas


