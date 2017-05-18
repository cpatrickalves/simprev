# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

from modelos.fazenda.probabilidades import calc_probabilidades
from modelos.fazenda.demografia import calc_demografia
from modelos.fazenda.taxas import calc_taxas
from modelos.fazenda.estoques import calc_estoques
from modelos.fazenda.salarios import calc_salarios
from util.tabelas import LerTabelas
from util.dados import DadosLDO
import modelos.fazenda.receitas as rc
import modelos.fazenda.depesas as desp

# Não usado pode enquanto
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

# Salário Mínimo de 2014 a 2017
salMin = [724.00, 788.00, 880.00, 937.00]

# Teto do RGPS de 2014 a 2017
tetoRGPS = [4390.24, 4663.75, 5189.82, 5531.31]

# Alíquota efetiva média
aliquota = 0.31

# PIB 2014
pib_inicial = 5521256074049.36

##### DADOS DA LDO ######
# Objeto que armazena dados da LDO de 2018
ldo2018 = DadosLDO()

# Taxa de Crescimento do Salário Mínimo em % (Tabela 6.1)
txCresSalMin = ldo2018.TxCrescimentoSalMin


#############################################################################

# Cria uma lista com os anos a serem projetados
periodo = list(range(ano_inicial, ano_final+1))

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

# Obtem as tabelas e armazena nos dicionários correspondentes
estoques = dados.get_tabelas(ids_estoques, info=True)
concessoes = dados.get_tabelas(ids_concessoes, info=True)
cessacoes = dados.get_tabelas(ids_cessacoes, info=True)
populacao = dados.get_tabelas(dados.ids_pop_ibge)
populacao_pnad = dados.get_tabelas(dados.ids_pop_pnad)
salarios = dados.get_tabelas(dados.ids_salarios)

# Calcula taxas de urbanização, participação e ocupação
print('Calculando taxas ...\n')
taxas = calc_taxas(populacao_pnad)

# Calcula: Pop Urbana|Rural, PEA e Pop Ocupada,
# Contribuintes, Segurados
print('Calculando dados demográficos ...\n')
segurados = calc_demografia(populacao, taxas)

# Corrige inconsistências nos estoques
dados.corrige_erros_estoque(estoques, concessoes, cessacoes)

# Calcula as probabilidades de entrada em benefício e morte
print('Calculando probabilidades ...\n')
probabilidades = calc_probabilidades(populacao, segurados, estoques,
                                     concessoes, cessacoes, periodo)

# Projeta Estoques
print('Projetando Estoques ...\n')
estoques = calc_estoques(estoques, probabilidades, populacao, segurados, periodo)

# Projeta Salarios
print('Projetando Salários ...\n')
salarios = calc_salarios(salarios, populacao, segurados,
                         produtividade, salMin, txCresSalMin,
                         periodo)

# Projeta receita
print('Projetando Receita e PIB ...\n')
receitas = rc.Receitas.calc_receitas(salarios, aliquota, periodo)
resultados = rc.Receitas.calc_pib(salarios, pib_inicial, periodo)
despesas = desp.Despesas.calc_despesas(estoques, salarios, periodo)


# Comparar os segurados calculados com os segurados das planilhas