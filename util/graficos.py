# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from matplotlib import pyplot as plt

# Gera diversos gráficos

def plot_erros(resultados):
    
    resultados['Erro Despesa'].plot()
    resultados['Erro Receita'].plot()

def plot_resultados(resultados):
    
    plt.plot(resultados['Despesas LDO'], label='LDO',lw=4 )
    plt.plot(resultados['Despesas'], label='LTS/UFPA', lw=4)    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('VALOR (R$)')
    plt.title('Despesas do RGPS')
    plt.legend()
    plt.show()
    
