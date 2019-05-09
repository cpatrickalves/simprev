# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

from util.tabelas import LerTabelas
from util.dados import DadosLDO
from util.busca_erros import corrige_erros_estoque, busca_erros_prob
from util.graficos import *
from util.carrega_parametros import obter_parametros


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
##############################################################################

# Não usado por enquanto
def main():
    pass

#  Sò queremos que nossa função main() seja executada se o módulo for
# o principal. Caso ele tenha sido importado, a aplicação só deverá ser
# executada se main() for chamado explicitamente.
if __name__ == "__main__":
    main()

###################### Parâmetros de simulação ###############################

# dicionário que armazena os parâmetros obtidos do arquivo "parametros.txt"
parametros = obter_parametros()

# Salva uma cópia do dicionário de parâmetros para uso posterior
copia_parametros = parametros.copy()

# Define qual modelo será utilizado
# Modelos disponíveis: LTS e LDO2018
if parametros['modelo'] == 'LTS':
    import modelos.lts as model
else:
    import modelos.fazenda as model

# Teto do RGPS de 2014 a 2017 (valores fixos)
tetoInicialRGPS = [4390.24, 4663.75, 5189.82, 5531.31]  

# Objeto que armazena dados da LDO de 2018
ldo = DadosLDO()
dadosLDO2018 = ldo.get_tabelas()

# Cria uma lista com os anos a serem projetados
ano_inicial = 2015  # valor fixo
ano_final = parametros['ano_final']
periodo = list(range(ano_inicial, ano_final+1))

# Alíquotas média de contribuição
aliquotas_serie = dadosLDO2018['AliqEfMed']
aliquotas_serie.loc[2017:] = parametros['aliquota_media']       # arquivo parametros.txt

# Taxa de inflação anual
inflacao_serie = dadosLDO2018['TxInflacao']
inflacao_serie.loc[2019:] = parametros['inflacao']                  # arquivo parametros.txt

###### Salva os parâmetros no dicionário
parametros['aliquota_media'] = aliquotas_serie
parametros['inflacao'] = inflacao_serie
parametros['periodo'] = periodo
parametros['aliquota_media'] = aliquotas_serie
parametros['tx_reajuste_beneficios'] = dadosLDO2018['TxReajusteBeneficios']

###### Outros parâmetros
# PIBs 2014-2016 (fonte: Planilhas do MF)
PIBs = dadosLDO2018['PIB Planilhas']

### Salário Mínimo de inicial 
salario_minimo = 724.00     # Valor de 2014

# Salva parâmetros em variáveis locais - CORRIGIR
produtividade = parametros['produtividade']

# Determina se os gráficos serão salvos em arquivos
savefig = True

# Determina se os gráficos serão exibidos no Prompt
showfig = False

##############################################################################

mensagem_inicial = '''
                                 SimPrev

        Um Simulador de Receitas e Despesas para a Previdência Social
        -------------------------------------------------------------
                                Versão 1.1

                           Autor: Patrick Alves                       
              <cpatrickalves@gmail.com, patrickalves@ufpa.br>
                  https://github.com/cpatrickalves/simprev
                  
                      Laboratório de Tecnologias Sociais
                         Universidade Federal do Pará
                    
'''

# Cria variável que armazena os logs
logs = []
logs.append(mensagem_inicial)

# Arquivo que salva os logs
log_file = 'logs.txt'

#############################################################################

print(mensagem_inicial)
print('\n:::::::::::::::::::::::::::: Iniciando projeção :::::::::::::::::::::::::::: \n')

print('Parâmetros de Projeção: \n')
for p in copia_parametros:
    print(' {} = {}'.format(p, copia_parametros[p]))

print('\nLendo arquivo de dados ... \n')

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
estoques = dados.get_tabelas(ids_estoques, logs, info=True)
concessoes = dados.get_tabelas(ids_concessoes, logs, info=True)
cessacoes = dados.get_tabelas(ids_cessacoes, logs, info=True)
despesas = dados.get_tabelas(ids_despesas, logs)
populacao = dados.get_tabelas(dados.ids_pop_ibge, logs)
populacao_pnad = dados.get_tabelas(dados.ids_pop_pnad, logs)
salarios = dados.get_tabelas(dados.ids_salarios, logs)
valCoBen = dados.get_tabelas(ids_valConcessoesBen, logs)

# Calcula taxas de urbanização, participação e ocupação
print('Calculando taxas ...\n')
taxas = model.calc_taxas(populacao_pnad, parametros)

# Calcula: Pop Urbana|Rural, PEA e Pop Ocupada, Contribuintes e Segurados
print('Calculando dados demográficos ...\n')
segurados = model.calc_demografia(populacao, taxas)

# Corrige inconsistências nos estoques
#corrige_erros_estoque(estoques, concessoes, cessacoes, logs)

# Calcula as probabilidades de entrada em benefício e morte
print('Calculando probabilidades ...\n')
probabilidades = model.calc_probabilidades(populacao, segurados, estoques,
                                     concessoes, cessacoes, periodo)

# Buscar por erros nas probababilidades
busca_erros_prob(probabilidades, logs, corrigir=False)

# Projeta Estoques
print('Projetando Estoques ...\n')
estoques = model.calc_estoques(estoques, concessoes, cessacoes, probabilidades,
                         populacao, segurados, periodo)

print('Projetando Salários ...\n')
salarios = model.calc_salarios(salarios, populacao, segurados, salario_minimo, 
                            dadosLDO2018, tetoInicialRGPS, parametros)

# Projeta Massa Salarial
print('Projetando Massa Salarial ...\n')
salarios = model.calc_MassaSalarial(salarios, populacao, segurados)

# Projeta Valores médios dos benefícios
print('Projetando Valores dos benefícios ...\n')
valMedBenef = model.calc_valMedBenef(estoques, despesas, valCoBen, concessoes, 
                                  dadosLDO2018, salarios, segurados, periodo)

# Calcula o número médio de parcelas para cada beneficio
nparcelas = model.calc_n_parcelas(estoques, despesas, valMedBenef, periodo)

# Projeta receitas e respesas
print('Projetando Receita e PIB ...\n')
resultados = model.calc_receitas(salarios, parametros, periodo)
resultados = model.calc_pib_MF(resultados, salarios, PIBs, periodo)

print('Projetando Despesas ...\n')
resultados = model.calc_despesas(despesas, estoques, concessoes, valCoBen, salarios,
                            valMedBenef, probabilidades, nparcelas, resultados, parametros)

print('Calculando resultados finais ...\n')
resultados = model.calc_resultados(resultados, despesas, estoques, segurados, 
                                   salarios, valMedBenef, dadosLDO2018, parametros, 
                                   mostrar=True)

print('Gerando gráficos ...\n')
plot_erros_LDO2018(resultados, savefig, showfig)
plot_resultados(resultados, savefig, showfig)

print('\n:::::::::::::::::::::::::::: Fim da Projeção :::::::::::::::::::::::::::: \n')

print('Todos os resultados foram salvos nas pasta resultados/')
print('Para mais detalhes veja o arquivo de log (logs.txt)\n')

# Salva o arquivo do Log
arq = open(log_file,'w')
arq.writelines(logs)
arq.close()

input("Tecle ENTER para finalizar")
