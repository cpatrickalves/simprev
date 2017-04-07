# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 07:56:21 2017

@author: Patrick Alves
"""

from util.carrega_dados import get_beneficios, get_tabelas
import modelos.fazenda.probabilidades 
import pandas as pd

# Não usado pode enquanto
def main():
    pass

#  Sò queremos que nossa função main() seja executada se o módulo for
# o principal. Caso ele tenha sido importado, a aplicação só deverá ser 
# executada se main() for chamado explicitamente.
if __name__ == "__main__":
    main()

###### Parâmetros de simulação

ano_prob = 2014 # Ano referência para cálculo das probabilidades
tags_populacao = ['PopIbgeH','PopIbgeM'] # tags utilizadas no modelo da Fazenda

# Arquivo com os dados da Fazenda
arquivo = '../datasets/FAZENDA/dados_fazenda.xlsx'
# Abri o arquivo
dados = pd.ExcelFile(arquivo)

######### Carregando os dados
# Dicionários que armazenarão os estoques, concessões, etc.
estoques = get_tabelas(get_beneficios([], 'Es'), dados, info=True)  
concessoes = get_tabelas(get_beneficios([], 'Co'), dados, info=True)
cessacoes = get_tabelas(get_beneficios([], 'Ce'), dados, info=True)
populacao = get_tabelas(tags_populacao, arquivo)  

prob = modelos.fazenda.probabilidades.calc_probabilidades(populacao)
#segurados ?
  


'''
# Anotações

usar a funcao linspace para gerar x valores em um intervalo

'''