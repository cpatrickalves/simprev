# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

from util.carrega_dados import get_beneficios, get_tabelas
import modelos.fazenda.probabilidades
import modelos.fazenda.demografia
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
tags_populacao_ibge = ['PopIbgeH','PopIbgeM'] 
tags_populacao_pnad = ['PopPnadH','PopPnadM', 'PopUrbPnadH',
                       'PopUrbPnadM','PopRurPnadH','PopRurPnadM',
                       'PeaUrbPnadH','PeaUrbPnadM','PeaRurPnadH',
                       'PeaRurPnadM'] 

# Arquivo com os dados da Fazenda
arquivo = '../datasets/FAZENDA/dados_fazenda.xlsx'
# Abri o arquivo
dados = pd.ExcelFile(arquivo)

######### Carregando os dados
# Dicionários que armazenarão os dados de estoques, concessões, etc.
estoques = get_tabelas(get_beneficios([], 'Es'), dados, info=True)  
concessoes = get_tabelas(get_beneficios([], 'Co'), dados, info=True)
cessacoes = get_tabelas(get_beneficios([], 'Ce'), dados, info=True)
populacao = get_tabelas(tags_populacao_ibge, dados)  
populacao_pnad = get_tabelas(tags_populacao_pnad, dados)  

# Inícia Calculos
# Calcula as probabilidades de entrada em benefício e morte
prob = modelos.fazenda.probabilidades.calc_probabilidades(populacao)

# Calcula taxas de urbanização, participação e ocupação
taxas= modelos.fazenda.demografia.calc_taxas(populacao_pnad)

# Calcula ....
pop_clientelas = modelos.fazenda.demografia.calc_pop_urb_rur(populacao,taxas)
#temp = modelos.fazenda.demografia.calc_tx_part(populacao_pnad)

'''
# Anotações

usar a funcao linspace para gerar x valores em um intervalo

'''