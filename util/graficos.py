# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
from matplotlib import pyplot as plt
import numpy as np
import os

##### Modulo que cria gráficos com os resultados

# Diretório onde as figuras serão salvas
fig_dir = os.path.join('resultados', 'figuras')   
if not os.path.isdir(fig_dir):
    os.makedirs(fig_dir)

def plot_erros_LDO2018(resultados, savefig=False, showfig=True):
    
    x = resultados['erro_despesas'].index  #2014-2060
    
    plt.plot(resultados['erro_despesas'], label='Despesa',lw=4, ls='--' )
    plt.plot(resultados['erro_receitas'], label='Receita', lw=4)    
    plt.plot(resultados['erro_PIB'], label='PIB', lw=4, ls=':')    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('VARIAÇÃO (%)')
    plt.title('Variação da Projeção do SimPrev com relação a LDO', y=1.05)
    plt.xticks(np.arange(min(x)+6, max(x)+1, 5.0))   
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
    if savefig: plt.savefig(os.path.join(fig_dir, 'variacao_simprev_LDO.png'), dpi=300, format='png', bbox_inches='tight')
    if showfig: plt.show()
    plt.close()
    
    plt.plot(resultados['despesas_PIB'], label='SimPrev',lw=4, ls='--' )
    plt.plot(resultados['despesas_PIB_LDO'], label='LDO', lw=4)            
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('DESPESA/PIB (%)')
    plt.title('Variação da Projeção da Despesa/PIB do SimPrev com relação a LDO', y=1.05)
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))   
    plt.legend(loc=0)
    if savefig: plt.savefig(os.path.join(fig_dir, 'despesas_pib_simprev_LDO.png'), dpi=300, format='png')
    if showfig: plt.show()
    plt.close()
    
    plt.plot(resultados['receitas_PIB'], label='SimPrev',lw=4, ls='--' )
    plt.plot(resultados['receitas_PIB_LDO'], label='LDO', lw=4)            
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('RECEITA/PIB(%)')
    plt.title('Variação da Projeção da Receita/PIB do SimPrev com relação a LDO', y=1.05)
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))   
    plt.legend(loc=0)
    if savefig: plt.savefig(os.path.join(fig_dir, 'receitas_pib_simprev_LDO.png'), dpi=300, format='png')
    if showfig: plt.show()
    plt.close()
    
    plt.plot(resultados['despesas_LDO'], label='LDO',lw=4, ls='--' )
    plt.plot(resultados['despesas'], label='SimPrev', lw=4)    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('VALOR (R$)')
    plt.title('Despesas do RGPS', y=1.05)
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))
    plt.legend(loc=0)
    if savefig: plt.savefig(os.path.join(fig_dir, 'despesas_simprev_LDO.png'), dpi=300, format='png')
    if showfig: plt.show()
    plt.close()
    
    plt.plot(resultados['receitas_LDO'], label='LDO',lw=4, ls='--'  )
    plt.plot(resultados['receitas'], label='SimPrev', lw=4)    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('VALOR (R$)')
    plt.title('Receitas do RGPS', y=1.05)
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))   
    plt.legend(loc=0)
    if savefig: plt.savefig(os.path.join(fig_dir, 'receitas_simprev_LDO.png'), dpi=300, format='png')
    if showfig: plt.show()
    plt.close()
    
    # Gráfico em barras com os erros comparando com o AEPS           
    index = np.arange(4)
    bar_width = 0.35
        
    plt.bar(index, resultados['erros_AEPS'].loc[2014, :], bar_width, label='2014', color='b')
    plt.bar(index + bar_width, resultados['erros_AEPS'].loc[2015, :], bar_width, label='2015', color='r')    
    plt.grid(True)    
    plt.ylabel('ERRO (%)')
    plt.title('Erros com relação ao AEPS', y=1.05)
    plt.xticks(index + bar_width, ('Receitas', 'Despesas', 'Aposentadorias', 'Pensões'))#    plt.xticks([2014, 2015])   
    plt.legend(loc=0)
    plt.tight_layout()
    if savefig: plt.savefig(os.path.join(fig_dir, 'erros_aeps.png'), dpi=300, format='png')
    if showfig: plt.show()
    plt.close()


def plot_resultados(resultados, savefig=False, showfig=True):
    
    x = resultados['despesas'].index  #2014-2060
    
    # Receitas e Despesas
    plt.plot(resultados['receitas'], label='Receitas',lw=4)
    plt.plot(resultados['despesas'], label='Despesas', lw=4)    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('VALOR (R$)')
    plt.title('Receitas e Despesas do RGPS', y=1.05)
    plt.set_cmap('jet')    
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))    
    plt.legend(loc=0)
    if savefig: plt.savefig(os.path.join(fig_dir, 'receitas_despesa_simprev.png'), dpi=300, format='png')
    if showfig: plt.show()
    plt.close()
    
    # Receitas e Despesas pelo PIB
    plt.plot(resultados['receitas_PIB'], label='Receitas/PIB',lw=4, ls='--', color='b' )
    plt.plot(resultados['despesas_PIB'], label='Despesas/PIB', lw=4, color='r')    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('RECEITA E DESPESA / PIB (%)')
    plt.title('Receitas e Despesas do RGPS sobre o PIB', y=1.05)
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))       
    plt.legend(loc=0)
    if savefig: plt.savefig(os.path.join(fig_dir, 'receita_despesa_pib_simprev.png'), dpi=300, format='png')
    if showfig: plt.show()
    plt.close()
    
    # Resultado Financeiro
    plt.plot(resultados['resultado_financeiro'], lw=4 )    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('RESULTADO FINANCEIRO  (R$)')   
    plt.title('Resultado Financeiro do RGPS', y=1.05)
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))          
    if savefig: plt.savefig(os.path.join(fig_dir, 'resultado_financeiro_simprev.png'), dpi=300, format='png')
    if showfig: plt.show()
    plt.close()
    
    # Resultado Financeiro pelo PIB
    plt.plot(resultados['resultado_financeiro_PIB'],lw=4 )    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('RESULTADO FINANCEIRO/PIB (%)') 
    plt.title('Necessidade de Financiamento do RGPS pelo PIB', y=1.05)
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))       
    if savefig: plt.savefig(os.path.join(fig_dir, 'resultado_financeiro_pib_simprev.png'), dpi=300, format='png')
    if showfig: plt.show()
    plt.close()

    # Quantidades de contribuintes e beneficiários        
    plt.plot(resultados['contribuintes'],lw=4, label='Contribuintes', color='b', ls='--' )    
    plt.plot(resultados['beneficiarios'],lw=4, label='Beneficiários', color='r')    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('QUANTIDADE') 
    plt.title('Quantidade de Contribuintes e Beneficiários', y=1.05)
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))   
    plt.legend(loc=0)
    if savefig: plt.savefig(os.path.join(fig_dir, 'contribuintes_beneficiarios_simprev.png'), dpi=300, format='png')
    if showfig: plt.show()
    plt.close()
    
    # Salário médio e valor médio dos benefícios
    plt.plot(resultados['salario_medio'],lw=4, label='Salário médio', color='b', ls='--' )    
    plt.plot(resultados['valor_medio_beneficios'],lw=4, label='Valor médio benefícios', color='r')    
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('VALOR (R$)') 
    plt.title('Quantidade de Contribuintes e Beneficiários', y=1.05)
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))   
    plt.legend(loc=0)
    if savefig: plt.savefig(os.path.join(fig_dir, 'salarioMedio_valorBeneficio_simprev.png'), dpi=300, format='png')
    if showfig: plt.show()
    plt.close()
        
    # Razão de dependência previdenciária
    plt.plot(resultados['RDP'],lw=4, color='b')        
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('BENEFICIÁRIOS/CONTRIBUINTES') 
    plt.title('Razão de dependência previdenciária', y=1.05)
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))       
    if savefig: plt.savefig(os.path.join(fig_dir, 'rdp_simprev.png'), dpi=300, format='png')
    if showfig: plt.show()
    plt.close()
        
    #Taxa de reposição
    plt.plot(resultados['taxa_reposicao'], lw=4, color='r')        
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('TAXA DE REPOSIÇÃO') 
    plt.title('Taxa de Reposição Média', y=1.05)
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))       
    if savefig: plt.savefig(os.path.join(fig_dir, 'taxa_reposicao_simprev.png'), dpi=300, format='png')
    if showfig: plt.show()
    plt.close()
    
    # Indicador sintético da sustentabilidade
    plt.plot(resultados['ISS'], lw=4, color='r')        
    plt.grid(True)
    plt.xlabel('ANO')
    plt.ylabel('INDICADOR DE SUSTENTABILIDADE') 
    plt.title('Indicador sintético da sustentabilidade', y=1.05)
    plt.xticks(np.arange(min(x)+1, max(x)+1, 5.0))       
    if savefig: plt.savefig(os.path.join(fig_dir, 'iss_simprev.png'), dpi=300, format='png')
    if showfig: plt.show()
    plt.close()
    
