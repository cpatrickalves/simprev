# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

from util.tabelas import LerTabelas
from util.dados import DadosLDO
from util.busca_erros import corrige_erros_estoque, busca_erros_prob
from util.resultados import calc_resultados
from util.graficos import *
import modelos.fazenda as fz


###############################################################################
# SIMPREV  - Simulador para projeção de Receitas e Despesas do RGPS 
###############################################################################
'''
### O SimPrev foi desenvolvido a partir dos documentos:
1) Anexo IV - Metas Fiscais - IV.6 – Projeções Atuariais para o Regime Geral de Previdência Social – RGPS
2) Planilhas Oficiais que implementam o modelo
   Fonte: http://legis.senado.leg.br/comissoes/docsRecCPI?codcol=2093
   Origem: Ministério da Fazenda	
   Arquivos: DOC110 e Mídia 21
   Data: 22/06/2017
   Ofício nº 35/MF   
'''
###############################################################################

# Não usado por enquanto
def main():
    pass

#  Sò queremos que nossa função main() seja executada se o módulo for
# o principal. Caso ele tenha sido importado, a aplicação só deverá ser
# executada se main() for chamado explicitamente.
if __name__ == "__main__":
    main()

###################### Parâmetros de simulação ###############################

# dicionário que armazena os parâmetros (incompleto)
parametros = {}

# Período de projeção 
ano_inicial = 2015
ano_final = 2060

# Ano de referência para cálculo das probabilidades
ano_probabilidade = 2014

# Taxa de crescimento de Produtividade em %
produtividade = 1.7  # Pag 45 LDO 2018

# Taxa de Formalização anual
formalizacao = 1.0
# Ano no qual a taxa de formalização para de ser aplicada
ano_limite_formalizacao = 2025

# Salário Mínimo de 2014
salMin = 724.00

# Teto do RGPS de 2014 a 2017
tetoInicialRGPS = [4390.24, 4663.75, 5189.82, 5531.31]

# Objeto que armazena dados da LDO de 2018
ldo = DadosLDO()
dadosLDO2018 = ldo.get_tabelas()

# Alíquota efetiva média de contribuição utilizada nas Planilhas
aliquota = dadosLDO2018['AliqEfMed']

# PIBs 2014-2016 (fonte: Planilhas do MF)
PIBs = dadosLDO2018['PIB Planilhas']


#############################################################################

# Cria uma lista com os anos a serem projetados
periodo = list(range(ano_inicial, ano_final+1))

# Salva os parâmetros de entrada no dicionário
parametros['produtividade'] = produtividade
parametros['formalizacao'] = formalizacao
parametros['periodo'] = periodo
parametros['ano_limite_formalizacao'] = ano_limite_formalizacao 

# Dicionário que salva os resultados
resultados = {}

# Determina se os gráficos serão salvos em arquivos
savefig = True

# Cria variável que armazena os logs
logs = []

# Arquivo que salva os logs
log_file = 'logs.txt'

#############################################################################

print('--- Iniciando projeção --- \n')
print('Lendo arquivo de dados ... \n')

#### Arquivo com os dados da Fazenda
# Dados disponibilizados em: http://legis.senado.leg.br/comissoes/docsRecCPI?codcol=2093
# DOC nº 110 do Ministério da Fazenda do dia 22/06/2017 - Midia 21

arquivo = 'dados/dados_fazenda.xlsx'
# Abri o arquivo
dados = LerTabelas(arquivo)

print('Carregando tabelas ...\n')

# Lista de Ids dos beneficios
ids_estoques = dados.get_id_beneficios([], 'Es')
ids_concessoes = dados.get_id_beneficios([], 'Co')
ids_cessacoes = dados.get_id_beneficios([], 'Ce')
ids_despesas = dados.get_id_beneficios([], 'ValEs')
ids_valConcessoesBen = dados.get_id_beneficios([], 'ValCo')

# Obtem as tabelas e armazena nos dicionários correspondentes
estoques = dados.get_tabelas(ids_estoques, info=True)
concessoes = dados.get_tabelas(ids_concessoes, info=True)
cessacoes = dados.get_tabelas(ids_cessacoes, info=True)
despesas = dados.get_tabelas(ids_despesas)
populacao = dados.get_tabelas(dados.ids_pop_ibge)
populacao_pnad = dados.get_tabelas(dados.ids_pop_pnad)
salarios = dados.get_tabelas(dados.ids_salarios)
valCoBen = dados.get_tabelas(ids_valConcessoesBen)

# Calcula taxas de urbanização, participação e ocupação
print('Calculando taxas ...\n')
taxas = fz.calc_taxas(populacao_pnad, parametros)

# Calcula: Pop Urbana|Rural, PEA e Pop Ocupada, Contribuintes e Segurados
print('Calculando dados demográficos ...\n')
segurados = fz.calc_demografia(populacao, taxas)

# Corrige inconsistências nos estoques
#corrige_erros_estoque(estoques, concessoes, cessacoes, logs)

# Calcula as probabilidades de entrada em benefício e morte
print('Calculando probabilidades ...\n')
probabilidades = fz.calc_probabilidades(populacao, segurados, estoques,
                                     concessoes, cessacoes, periodo)

# Buscar por erros nas probababilidades
busca_erros_prob(probabilidades, logs, corrigir=False)

# Projeta Estoques
print('Projetando Estoques ...\n')
estoques = fz.calc_estoques(estoques, concessoes, cessacoes, probabilidades,
                         populacao, segurados, periodo)

# Projeta Salarios
print('Projetando Salários ...\n')
salarios = fz.calc_salarios(salarios, populacao, segurados,
                         produtividade, salMin, dadosLDO2018, tetoInicialRGPS,
                         periodo)

# Projeta Massa Salarial
print('Projetando Massa Salarial ...\n')
salarios = fz.calc_MassaSalarial(salarios, populacao, segurados,
                         produtividade, salMin, dadosLDO2018, tetoInicialRGPS,
                         periodo)

# Projeta Valores médios dos benefícios
print('Projetando Valores dos benefícios ...\n')
valMedBenef = fz.calc_valMedBenef(estoques, despesas, valCoBen, concessoes, 
                                  dadosLDO2018, salarios, segurados, periodo)

# Calcula o número médio de parcelas para cada beneficio
nparcelas = fz.calc_n_parcelas(estoques, despesas, valMedBenef, periodo)

# Projeta receitas e respesas
print('Projetando Receita e PIB ...\n')
resultados = fz.calc_receitas(salarios, aliquota, periodo)
resultados = fz.calc_pib_MF(resultados, salarios, PIBs, periodo)

print('Projetando Despesas ...\n')
resultados = fz.calc_despesas(despesas, estoques, concessoes, valCoBen, salarios,
                            valMedBenef, probabilidades, dadosLDO2018, 
                            nparcelas, resultados, periodo)

print('Calculando resultados finais ...\n')
resultados = calc_resultados(resultados, estoques, dadosLDO2018)

plot_erros_LDO2018(resultados, savefig)
plot_resultados(resultados, savefig)

print('RESULTADOS: \n')
print('Erro de Despesa em 2018 = {}'.format(resultados['Erro Despesas'][2018]))
print('Erro de Despesa em 2060 = {}'.format(resultados['Erro Despesas'][2060]))
print()
print('Erro de Receita em 2018 = {}'.format(resultados['Erro Receitas'][2018]))
print('Erro de Receita em 2060 = {}'.format(resultados['Erro Receitas'][2060]))
print()
print('Erro no PIB em 2018 = {}'.format(resultados['Erro PIB'][2018]))
print('Erro no PIB em 2060 = {}'.format(resultados['Erro PIB'][2060]))
print()
print('Erro de Receita/PIB em 2018 = {}'.format(resultados['Erro Receitas/PIB'][2018]))
print('Erro de Receita/PIB em 2060 = {}'.format(resultados['Erro Receitas/PIB'][2060]))
print()
print('Erro de Despesa/PIB em 2018 = {}'.format(resultados['Erro Despesas/PIB'][2018]))
print('Erro de Despesa/PIB em 2060 = {}'.format(resultados['Erro Despesas/PIB'][2060]))


print(' - Fim da Projeção -')
print('Para mais detalhes veja o arquivo de log (logs.txt)')

# Salva o arquivo do Log
arq = open(log_file,'w')
arq.writelines(logs)
arq.close()

# REVISAR:
# Buscar por estoques e outros valores (probabilidades) negativos
# Buscar por fatores de ajuste de mortalidades muito elevados
# Existem probabilidades de morte negativa - fam rmv tb
# Nos estoques aparecem aposentadorias com menos de 45 anos (corrigir)
# Alterar as porcentagens 
# Adicionar a opção de projetar com valores atuais (sem inflacao)
# Transformar os dados da LDO e parâmetros de entrada (alterar parametros das funções)
# Pendente:
    # ajustes da inflação
    # Calculo do número médio de parcelas pagas
    # TAXA DOS RURAIS
    # ERRO DO PIB
    
# Implementar pendências das planilhas (reduzir o erro) - Lembrando que existem calculos errados na planilha
    # Comparar valores médios benefícios
    # Comparar probabilidades
    # Comparar estoques
    # Ver observações no evernote