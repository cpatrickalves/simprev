# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 07:56:21 2017

@author: Patrick Alves
"""

from modulos.carrega_dados import get_beneficios, get_tabelas
import modulos.probabilidades 

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


# Arquivo com os dados da Fazenda
arquivo = '../datasets/FAZENDA/dados_fazenda.xlsx'

######### Carregando os dados
# Dicionários que armazenarão os estoques, concessões, etc.
estoques = get_tabelas(get_beneficios([], 'Es'), arquivo, info=True)  
concessoes = get_tabelas(get_beneficios([], 'Co'), arquivo, info=True)
cessacoes = get_tabelas(get_beneficios([], 'Ce'), arquivo, info=True)
populacao = get_tabelas(['PopIbgeH','PopIbgeM'], arquivo)  

prob = modulos.probabilidades.calc_probabilidades(populacao)
#segurados ?
  


'''
# Anotações

usar a funcao linspace para gerar x valores em um intervalo

'''