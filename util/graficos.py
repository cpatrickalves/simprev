# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from matplotlib import pyplot as plt

# Gera diversos gráficos

def plot_erros(resultados):
        
    plt.plot(resultados['Erro Despesa'], label='Despesa',lw=4 )
    plt.plot(resultados['Erro Receita'], label='Receita', lw=4)    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('VARIAÇÃO (%)')
    plt.title('Variação da Projeção do SimPrev com relação a LDO')
    plt.legend()
    plt.show()
    

def plot_resultados(resultados):
    
    plt.plot(resultados['Despesas LDO'], label='LDO',lw=4 )
    plt.plot(resultados['Despesas'], label='LTS/UFPA', lw=4)    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('VALOR (R$)')
    plt.title('Despesas do RGPS')
    plt.legend()
    plt.show()
    
    plt.plot(resultados['Receitas LDO'], label='LDO',lw=4 )
    plt.plot(resultados['Receitas'], label='LTS/UFPA', lw=4)    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('VALOR (R$)')
    plt.title('Receitas do RGPS')
    plt.legend()
    plt.show()
    