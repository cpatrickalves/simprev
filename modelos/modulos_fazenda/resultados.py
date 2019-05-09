# -*- coding: utf-8 -*-
"""

@author: Patrick Alves
"""
from util.tabelas import LerTabelas
import pandas as pd
import os


def calc_resultados(resultados, despesas, estoques, segurados, salarios, valMedBenef, dadosLDO, parametros, mostrar=False):
    
    periodo = parametros['periodo']
    ano_estoque = periodo[0]
    
    ###### Calcula receita e despesa sobre o PIB
        
    rec_pib = resultados['receitas'] / resultados['PIB']
    desp_pib = resultados['despesas'] / resultados['PIB']
    
    resultados['receitas_PIB'] = rec_pib * 100
    resultados['despesas_PIB'] = desp_pib * 100
        
    
    ###### Cálcula necessidade de Financiamento
    
    necess_fin = resultados['receitas'] - resultados['despesas']
    necess_fin_pib =  necess_fin / resultados['PIB']
    
    resultados['resultado_financeiro'] = necess_fin
    resultados['resultado_financeiro_PIB'] = necess_fin_pib * 100
    
    
    ###### Cálcula contribuintes, beneficiários e razão de dependência
    
    total_contribuintes = segurados['CsmUrbH'].sum() + segurados['CaUrbH'].sum() + segurados['CaUrbM'].sum() + segurados['CsmUrbM'].sum()    
    total_beneficiarios = 0
    total_beneficiarios_urb = 0
    total_beneficiarios_rur = 0
    total_aposentados = 0
    
    # Soma os beneficiários de cada benefício - Todos os benefícios
    for b in estoques.keys():
        # Pula os benefícios assistenciais e subtipos de pensões (tipo A e B)
        if 'Loas' in b or 'tipo' in b:
            continue                                       
        elif 'Urb' in b:
            total_beneficiarios_urb +=  estoques[b].sum()
        else:
            total_beneficiarios_rur +=  estoques[b].sum()
    
    total_beneficiarios =  total_beneficiarios_urb + total_beneficiarios_rur
    
    # Soma a quantidade de beneficiários de aposentadorias
    tabelas = LerTabelas()
    # Ids aposentadorias
    ids_apos= ['Apin', 'Atcn', 'Apid', 'Atcp', 'Ainv', 'Atce', 'Atcd']
    
    for b in tabelas.get_id_beneficios(ids_apos):
        # Verifica se o estoque para o benefício existe
        if b in estoques.keys():
            total_aposentados +=  estoques[b].sum()
    
    # Salva a partir de 2014
    resultados['contribuintes'] = total_contribuintes.loc[ano_estoque:]
    resultados['beneficiarios'] = total_beneficiarios.loc[ano_estoque:]
    resultados['beneficiarios_urb'] = total_beneficiarios_urb.loc[ano_estoque:]
    resultados['beneficiarios_rur'] = total_beneficiarios_rur.loc[ano_estoque:]
    resultados['aposentados'] = total_aposentados.loc[ano_estoque:]
    
    # Calcula a Razão de dependência previdenciária    
    # OBS: No livro 2, o RDP considerava somente as aposentadorias
    resultados['RDP'] = resultados['aposentados']/resultados['contribuintes']
    
    ###### Cálcula salário médio, valor médio dos benefícios e a taxa de reposição
    
    salario_medio = (salarios['SalMedSegUrbAcimPnadH'].mean() + salarios['SalMedSegUrbAcimPnadM'].mean() + salarios['salarioMinimo'])/3
    soma_media_beneficios = 0
    qtd_benef = 0
    
    # Calcula a média dos valores dos beneficios
    for b in valMedBenef.keys():
        # Pula a txReposicao - OBS: tirar essa variável daqui
        if 'txRep' in b:
            continue
        
        soma_media_beneficios +=  valMedBenef[b].mean()
        qtd_benef += 1
    # Soma com o salário mínimo
    soma_media_beneficios +=  salarios['salarioMinimo']
    qtd_benef += 1
    
    # Salva a partir de 2014
    resultados['salario_medio'] = salario_medio.loc[ano_estoque:]
    resultados['valor_medio_beneficios'] = soma_media_beneficios.loc[ano_estoque:]/qtd_benef
    
    # Calcula a Taxa de Reposição
    resultados['taxa_reposicao'] = resultados['valor_medio_beneficios']/resultados['salario_medio']
        
    aliquota = parametros['aliquota_media']
    ###### Cálcula Indicador sintético da sustentabilidade
    resultados['ISS'] = (aliquota/100)/(resultados['taxa_reposicao'] * resultados['RDP'])
    
    
    ###### Obtém resultados da LDO de 2018
        
    # Receita, despesa e PIB da LDO
    rec_ldo = dadosLDO['Tabela_6.2']['Receita']
    desp_ldo = dadosLDO['Tabela_6.2']['Despesa']
    pib_ldo = dadosLDO['Tabela_6.2']['PIB']
    
    # Receita e despesa sobre o PIB da LDO
    rec_ldo_pib = dadosLDO['Tabela_6.2']['Receita / PIB'] * 100
    desp_ldo_pib = dadosLDO['Tabela_6.2']['Despesa / PIB'] * 100
    
    resultados['receitas_PIB_LDO'] = rec_ldo_pib
    resultados['despesas_PIB_LDO'] = desp_ldo_pib
        
    
    ###### Calcula variação em relação a LDO de 2018
    
    # Variação na despesa, receita e PIB com relação a LDO de 2018 em %
    erro_receita = 100 * (resultados['receitas'] - rec_ldo) / rec_ldo
    erro_despesa = 100 * (resultados['despesas'] - desp_ldo) / desp_ldo
    erro_pib = 100 * (resultados['PIB'] - pib_ldo) / pib_ldo
    
    # Diferença na despesa e receita sobre o PIB
    erro_receita_pib =  resultados['receitas_PIB'] - rec_ldo_pib 
    erro_despesa_pib =  resultados['despesas_PIB'] - desp_ldo_pib

    resultados['erro_receitas'] = erro_receita
    resultados['erro_despesas'] = erro_despesa
    resultados['erro_PIB'] = erro_pib
    resultados['erro_receitas_PIB'] = erro_receita_pib
    resultados['erro_despesas_PIB'] = erro_despesa_pib
    resultados['receitas_LDO'] = rec_ldo
    resultados['despesas_LDO'] = desp_ldo
    
    
    ###### Comparação com os dados de 2014 e 2015 do AEPS
    
    tabelas = LerTabelas()
    
    # Calcula o estoque total de aposentadorias e Pensões
    est_apos_total = pd.DataFrame(0.0, columns=estoques['AinvRurH'].columns,index=estoques['AinvRurH'].index)
    est_pens_total = est_apos_total.copy()
    
    # Para todas as aposentadorias
    for benef in tabelas.get_id_beneficios(['Apin', 'Atcn', 'Atce', 'Atcp', 'Ainv']):
        if benef in estoques.keys():
            est_apos_total += estoques[benef]
    
    # Para todas as Pensoes
    for benef in tabelas.get_id_beneficios(['Pens']):
        if benef in estoques.keys():
            est_pens_total += estoques[benef]
    
    erros_aeps = pd.DataFrame(index=[2014,2015], columns=['Receitas', 'Despesas', 'Aposentadorias', 'Pensões'])
    
    erros_aeps['Aposentadorias'] = (est_apos_total.sum() / dadosLDO['Aposentadorias AEPS']) - 1
    erros_aeps['Pensões'] = (est_pens_total.sum() / dadosLDO['Pensões AEPS']) - 1
    erros_aeps['Receitas'] = (resultados['receitas'] / dadosLDO['Receitas AEPS']) - 1
    erros_aeps['Despesas'] = (resultados['despesas'] / dadosLDO['Despesas AEPS']) - 1
    
    resultados['erros_AEPS'] = erros_aeps * 100
    
    # Salva os resultados em arquivos CSV
    save_results(resultados, despesas, estoques, segurados, salarios, valMedBenef, parametros)
         
    # Se mostrar = True os resultados serão exibidos no Prompt    
    if mostrar:
        print('RESULTADOS DA PROJEÇÃO: \n')
        
        print('Receita em 2018 = {}'.format(resultados['receitas'][2018]))
        print('Receita em 2060 = {}'.format(resultados['receitas'][2060]))
        print('Receita/PIB em 2060 = {}'.format(resultados['receitas_PIB'][2060]))
        print()
        print('Despesa em 2018 = {}'.format(resultados['despesas'][2018]))
        print('Despesa em 2060 = {}'.format(resultados['despesas'][2060]))
        print('Despesa/PIB em 2060 = {}'.format(resultados['despesas_PIB'][2060]))
        print()
        print('Resultado Financeiro em 2018 = {}'.format(resultados['resultado_financeiro'][2018]))
        print('Resultado Financeiro em 2060 = {}'.format(resultados['resultado_financeiro'][2060]))    
        print('Resultado Financeiro/PIB em 2060 = {}'.format(resultados['resultado_financeiro_PIB'][2060]))    
        
        print("\nVARIAÇÕES EM RELAÇÃO A LDO DE 2018:")

        print('Variação da Despesa em 2018 (%) = {}'.format(round(resultados['erro_despesas'][2018], 2)))
        print('Variação da Despesa em 2060 (%) = {}'.format(round(resultados['erro_despesas'][2060], 2)))
        print()
        print('Variação da Receita em 2018 (%) = {}'.format(round(resultados['erro_receitas'][2018], 2)))
        print('Variação da Receita em 2060 (%) = {}'.format(round(resultados['erro_receitas'][2060], 2)))
        print()
        print('Variação no PIB em 2018 (%) = {}'.format(round(resultados['erro_PIB'][2018], 2)))
        print('Variação no PIB em 2060 (%) = {}'.format(round(resultados['erro_PIB'][2060], 2)))
        print()
        print('Diferença na Receita/PIB em 2018 = {}'.format(resultados['erro_receitas_PIB'][2018]))
        print('Diferença na Receita/PIB em 2060 = {}'.format(resultados['erro_receitas_PIB'][2060]))
        print()
        print('Diferença na Despesa/PIB em 2018 = {}'.format(resultados['erro_despesas_PIB'][2018]))
        print('Diferença na Despesa/PIB em 2060 = {}'.format(resultados['erro_despesas_PIB'][2060]))        
        print('\n')
        
    return resultados


# Exporta todos os resultados para um arquivo CSV
def save_results(resultados, despesas, estoques, segurados, salarios, valor_beneficio, parametros):
    
    periodo = parametros['periodo']
    ano_estoque = periodo[0]
    
    # Cria o DataFrame que irá armazena cada resultado em uma coluna
    todos_resultados = pd.DataFrame(index=range(ano_estoque,periodo[-1]+1))
    todos_resultados.index.names = ['ANO']
    
    # Salva os resultados gerais 
    lista_resultados_gerais = list(resultados.keys())
    lista_resultados_gerais.remove('erros_AEPS')          # Remove o erro_AEPS pois já um DataFrame
    lista_resultados_gerais.sort()                        # Ordena a lista
        
    # Salva cada resultado como uma coluna do DataFrame
    for r in lista_resultados_gerais:            
        todos_resultados[r] = resultados[r]       
    
    # Cria diretório onde são salvos os resultados caso não exista
    result_dir = 'resultados'
    if not os.path.isdir(result_dir):
            os.makedirs(result_dir)  
            
    # Salva o arquivo em formato CSV
    try:            
        todos_resultados.to_csv((os.path.join('resultados', 'resultados.csv')), sep=';', decimal=',')    
    except:
        print('--> Erro ao salvar arquivo {}'.format((os.path.join('resultados','resultados.csv'))))
    
    # Dicionário com a lista dos objetos com os resultados
    lista_resultados = {'despesas':despesas, 'estoques':estoques, 'segurados':segurados, 'salarios':salarios, 'valor_beneficio':valor_beneficio}
    
    # Cria os demais diretórios para os outros resultados    
    for res in lista_resultados.keys():
        diretorio = os.path.join(result_dir,res)
        if not os.path.isdir(diretorio):
            os.makedirs(diretorio)            
    
    # Salva os resultados de estoque
        for item in lista_resultados[res].keys():
            
            # pula taxa de reposição
            if item == 'txReposicao':
                continue
            
            # Salva o arquivo em formato CSV
            arquivo = item+'.csv'                    
            lista_resultados[res][item].index.name = 'Idade'    # Corrige o index para evitar erro no Excel
            
            # Salva o arquivo               
            try:            
                lista_resultados[res][item].to_csv((os.path.join(diretorio,arquivo)), sep=';', decimal=',')    
            except:
                print('--> Erro ao salvar arquivo {}'.format((os.path.join(diretorio,arquivo))))    