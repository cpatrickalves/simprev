# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from matplotlib import pyplot as plt
import numpy as np

# Modulo que cria gráficos com os resultados


def plot_erros_LDO2018(resultados, savefig=False):
    
    x = resultados['Erro Despesas'].index  #2014-2060
    
    plt.plot(resultados['Erro Despesas'], label='Despesa',lw=4, ls='--' )
    plt.plot(resultados['Erro Receitas'], label='Receita', lw=4)    
    plt.plot(resultados['Erro PIB'], label='PIB', lw=4, ls=':')    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('VARIAÇÃO (%)')
    #plt.title('Variação da Projeção do SimPrev com relação a LDO')
    plt.xticks(np.arange(min(x)+6, max(x)+1, 5.0))   
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),ncol=3)
    if savefig: plt.savefig('variacao_simprev_LDO.png', dpi=300, format='png')
    plt.show()
    
    plt.plot(resultados['Despesas/PIB'], label='SimPrev',lw=4, ls='--' )
    plt.plot(resultados['Despesas/PIB LDO'], label='LDO', lw=4)            
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('DESPESA/PIB (%)')
    #plt.title('Variação da Projeção da Despesa/PIB do SimPrev com relação a LDO')
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))   
    plt.legend(loc=0)
    if savefig: plt.savefig('despesas_pib_simprev_LDO.png', dpi=300, format='png')
    plt.show()
    
    plt.plot(resultados['Receitas/PIB'], label='SimPrev',lw=4, ls='--' )
    plt.plot(resultados['Receitas/PIB LDO'], label='LDO', lw=4)            
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('RECEITA/PIB(%)')
    #plt.title('Variação da Projeção da Receita/PIB do SimPrev com relação a LDO')
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))   
    plt.legend(loc=0)
    if savefig: plt.savefig('receitas_pib_simprev_LDO.png', dpi=300, format='png')
    plt.show()
    
    plt.plot(resultados['Despesas LDO'], label='LDO',lw=4, ls='--' )
    plt.plot(resultados['Despesas'], label='SimPrev', lw=4)    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('VALOR (R$)')
    #plt.title('Despesas do RGPS')
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))
    plt.legend(loc=0)
    if savefig: plt.savefig('despesas_simprev_LDO.png', dpi=300, format='png')
    plt.show()
    
    plt.plot(resultados['Receitas LDO'], label='LDO',lw=4, ls='--'  )
    plt.plot(resultados['Receitas'], label='SimPrev', lw=4)    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('VALOR (R$)')
    #plt.title('Receitas do RGPS')
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))   
    plt.legend(loc=0)
    if savefig: plt.savefig('receitas_simprev_LDO.png', dpi=300, format='png')
    plt.show()


def plot_resultados(resultados, savefig=False):
    
    x = resultados['Despesas'].index  #2014-2060
    
    plt.plot(resultados['Receitas'], label='Receitas',lw=4)
    plt.plot(resultados['Despesas'], label='Despesas', lw=4)    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('VALOR (R$)')
    #plt.title('Receitas e Despesas do RGPS')
    plt.set_cmap('jet')    
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))    
    plt.legend(loc=0)
    if savefig: plt.savefig('receitas_despesa_simprev.png', dpi=300, format='png')
    plt.show()
    
    plt.plot(resultados['Receitas/PIB'], label='Receitas/PIB',lw=4 )
    plt.plot(resultados['Despesas/PIB'], label='Despesas/PIB', lw=4)    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('RECEITA E DESPESA / PIB (%)')
    #plt.title('Receitas e Despesas do RGPS sobre o PIB')
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))       
    plt.legend(loc=0)
    if savefig: plt.savefig('receita_despesa_pib_simprev.png', dpi=300, format='png')
    plt.show()
    
    plt.plot(resultados['NecFinanc'],lw=4 )    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('NECESSIDADE DE FINANCIAMENTO  (R$)')   
    #plt.title('Necessidade de Financiamento do RGPS')
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))      
    plt.legend(loc=0)
    if savefig: plt.savefig('resultado_financeiro_simprev.png', dpi=300, format='png')
    plt.show()
        
    plt.plot(resultados['NecFinanc/PIB'],lw=4 )    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('NECESSIDADE DE FINANCIAMENTO/PIB (%)') 
    #plt.title('Necessidade de Financiamento do RGPS pelo PIB')
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))   
    plt.legend(loc=0)
    if savefig: plt.savefig('resultado_financeiro_pib_simprev.png', dpi=300, format='png')
    plt.show()
        
