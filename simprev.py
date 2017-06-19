# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

from util.tabelas import LerTabelas
from util.dados import DadosLDO
import modelos.fazenda as fz


# Não usado por enquanto
def main():
    pass

#  Sò queremos que nossa função main() seja executada se o módulo for
# o principal. Caso ele tenha sido importado, a aplicação só deverá ser
# executada se main() for chamado explicitamente.
if __name__ == "__main__":
    main()

###################### Parâmetros de simulação ###############################

# dicionário que armazena os parâmetros (incompleto) - REVISAR
parametros = {}

# Período de projeção 
ano_inicial = 2015
ano_final = 2060

# Ano de referência para cálculo das probabilidades
ano_probabilidade = 2014

# Taxa de crescimento de Produtividade em %
produtividade = 1.7  # Pag 45 LDO 2018

# Salário Mínimo de 2014
salMin = 724.00

# Teto do RGPS de 2014 a 2017
tetoRGPS = [4390.24, 4663.75, 5189.82, 5531.31]

# Alíquota efetiva média
aliquota = 0.31

# PIB 2014
pib_inicial = 5521256074049.36

# Objeto que armazena dados da LDO de 2018
dadosLDO2018 = DadosLDO.get_tabelas()

#############################################################################

# Cria uma lista com os anos a serem projetados
periodo = list(range(ano_inicial, ano_final+1))

resultados = {}


#############################################################################

print('--- Iniciando projeção --- \n')
print('Lendo arquivo de dados ... \n')
# Arquivo com os dados da Fazenda
arquivo = '../datasets/FAZENDA/dados_fazenda.xlsx'
# Abri o arquivo
dados = LerTabelas(arquivo)

print('Carregando tabelas ...\n')

# Lista de Ids dos beneficios
ids_estoques = dados.get_id_beneficios([], 'Es')
ids_concessoes = dados.get_id_beneficios([], 'Co')
ids_cessacoes = dados.get_id_beneficios([], 'Ce')
ids_despesas = dados.get_id_beneficios([], 'ValEs')
#ids_valMedBen = dados.get_id_beneficios([], 'ValEs')

# Obtem as tabelas e armazena nos dicionários correspondentes
estoques = dados.get_tabelas(ids_estoques, info=True)
concessoes = dados.get_tabelas(ids_concessoes, info=True)
cessacoes = dados.get_tabelas(ids_cessacoes, info=True)
despesas = dados.get_tabelas(ids_despesas)
populacao = dados.get_tabelas(dados.ids_pop_ibge)
populacao_pnad = dados.get_tabelas(dados.ids_pop_pnad)
salarios = dados.get_tabelas(dados.ids_salarios)
#valMedBen = dados.get_tabelas(ids_valMedBen)

# Calcula taxas de urbanização, participação e ocupação
print('Calculando taxas ...\n')
taxas = fz.calc_taxas(populacao_pnad, periodo)

# Calcula: Pop Urbana|Rural, PEA e Pop Ocupada,
# Contribuintes, Segurados
print('Calculando dados demográficos ...\n')
segurados = fz.calc_demografia(populacao, taxas)

# Corrige inconsistências nos estoques
dados.corrige_erros_estoque(estoques, concessoes, cessacoes)

# Calcula as probabilidades de entrada em benefício e morte
print('Calculando probabilidades ...\n')
probabilidades = fz.calc_probabilidades(populacao, segurados, estoques,
                                     concessoes, cessacoes, periodo)

# Projeta Estoques
print('Projetando Estoques ...\n')
estoques = fz.calc_estoques(estoques, concessoes, probabilidades,
                         populacao, segurados, periodo)

# Projeta Salarios
print('Projetando Salários ...\n')
salarios = fz.calc_salarios(salarios, populacao, segurados,
                         produtividade, salMin, dadosLDO2018,
                         periodo)

# Projeta Valoers médios dos benefícios
print('Projetando Valores dos benefícios ...\n')
valMedBenef = fz.calc_valMedBenef(estoques, despesas, dadosLDO2018, periodo)

# Calcula o número médio de parcelas para cada beneficio
nparcelas = fz.calc_n_parcelas(estoques, despesas, valMedBenef, periodo)

# Projeta receitas e respesas
print('Projetando Receita e PIB ...\n')
resultados['receitas'] = fz.calc_receitas(salarios, aliquota, periodo)
resultados = fz.calc_pib(resultados, salarios, pib_inicial, periodo)

print('Projetando Despesas ...\n')
resultados = fz.calc_despesas(despesas, estoques, concessoes, salarios,
                            valMedBenef, probabilidades, dadosLDO2018, 
                            nparcelas, resultados, periodo)


# Compara as equações da LDO com a do DOcumento da fazenda
# Existem probabilidades de morte negativa - fam rmv tb
# corrigir calculos para idade 90
# Comparar os segurados calculados com os segurados das planilhas
# Nos estoques aparecem aposentadorias com menos de 45 anos (corrigir)
# Alterar as porcentagens 
# Calcular taxa de crescimento da massa salarial de contribuintes