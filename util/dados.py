# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
import pandas as pd

class DadosLDO():
    
    def get_parametros_ldo2018(self):
        '''
        Abre o arquivo com os dados da LDO de 2018 
        '''
        arquivo = 'dados/TabelasLDO2018.xlsx'
        # Abre arquivo
        dados = pd.ExcelFile(arquivo)
        
        periodo = list(range(2015, 2061))   

        INFLACAO = 4.5
        ALIQUOTA_MED = 26.8 #26.8  
            
        # Taxa de Crescimento do Salário Mínimo em % (2015-2060)
        # Valores retirados das Planilhas do MF
        # Os 3 primeiros valores estão somados com a inflação (2015-2017)
        # Valores correspondem a TxCrescimentoSalMin da LDO menos a inflação        
        #self.ValoresTxCrescimentoSalMin = [8.84 , 11.68, 6.48, 0.0, 0.50, 2.49, 2.49, 
        #                                   2.58, 2.87, 2.81,2.76, 2.70, 2.63, 2.56, 2.49, 
        #                                   2.42, 2.34, 2.27, 2.20, 2.13, 2.06, 1.98, 1.91,
        #                                   1.83, 1.76, 1.69, 1.62, 1.55, 1.48, 1.42, 1.36, 
        #                                   1.30, 1.25, 1.20, 1.15, 1.10, 1.07, 1.03, 1.00, 
        #                                   0.95, 0.92, 0.89, 0.86, 0.84, 0.81, 0.79]
        
        # Carrega os valores a partir da Tabela da LDO
        valoresTxCrescimentoSalMin = dados.parse('Tabela 6.1', index_col=0).Tx_Reaj_SM         
        # Desconta a Inflação dos valores de taxa de crescimento
        valoresTxCrescimentoSalMin = valoresTxCrescimentoSalMin - (INFLACAO/100)
        # Transforma tudo em uma lista converte para % e adiciona os valores de inflação de 2015 a 2017
        valoresTxCrescimentoSalMin = [8.84 , 11.68, 6.48] + list(valoresTxCrescimentoSalMin * 100) 
        
        # Atualização monetária retirados das Planilhas do MF
        reajuste_2015_2018 = [6.41, 10.67, 6.29, 4.62]
        # OBS: Inflação é zero em 2018
        inflacao_2015_2018 = [6.41, 10.67, 6.29, 0.0]
                        
        # Valores reais
        #reajuste_2015_2018 = [6.23, 11.28, 6.58, 4.62]
        #inflacao_2015_2018 = [6.23, 11.28, 6.58, 4.5]
              
        # Taxa de Reajuste dos demais benefícios em %  (2015-2060) 
        valoresTxReajusteBeneficios = reajuste_2015_2018 + ([INFLACAO] * 42)   
        
        # Taxa de Inflação em %  (2015-2060) 
        TxInflacao = inflacao_2015_2018 + ([INFLACAO] * 42)   
        #self.TxInflacao = self.inflacao_2015_2018 + ([0.0] * 42)   
        
        # Taxa de Reajuste dos demais benefícios em %  (2015-2060) 
        #txCresMassaSalContribuintes = [7.52, 7.36, 7.42, 7.35, 7.28, 7.24, 7.17, 7.09, 7.01, 6.93, 6.85,
        #                               6.78, 6.70, 6.62, 6.53, 6.45, 6.37, 6.29, 6.21, 6.14, 6.06, 5.98, 
        #                               5.91, 5.83, 5.77, 5.70, 5.64, 5.59, 5.55, 5.50, 5.46, 5.42, 5.39, 
        #                               5.37, 5.34, 5.32, 5.30, 5.27, 5.25, 5.22, 5.20, 5.18, 5.15]                    
                
        # Aliquotas médias de 2014 a 2060
        # aliqMed = receita/MassaSalarial        
        aliquotasPlanilhasMF = [28.3, 27.2, 25.0] + ([ALIQUOTA_MED] * 44)
        #self.aliquotasPlanilhasMF = [28.3, 27.2, 25.0, 24.0, 24.3, 24.6, 24.9, 25.2, 25.5, 25.8] + ([26.1] * 37)

        # PIBs 2014-2016 (fonte: Planilhas do MF)
        PIBs = [5687309000000,	5904331214709, 6220495999366]
        
        # 2010-2016 (fonte: Planilhas do MF)
        #receitas_planilha = [284233000000, 304642000000, 314834000000, 330596000000]

        # Dados dos Anuários Estatísticos da Previdência Social

        # 2013-2015 (fonte: AEPS 2015 - Tabelas 42.1, 42.4, 42.5 (BENEFÍCIOS))
        receitas_aeps = [292675804000,	312740405000, 319674728000]
        despesas_aeps = [383070416000,	390735753000, 428530621000]

        # 2013-2015 (fonte: AEPS 2015 - Tabela C.1)
        aposentadorias_aeps  = [17248792, 17845805, 18331635]
        pensoes_aeps = [7165712, 7323921, 7429823]
    
        # Dicionário que armazena os dados
        dados_ldo = {}        

        dados_ldo['TxCrescimentoSalMin'] = pd.Series(valoresTxCrescimentoSalMin, index=periodo)
        dados_ldo['TxReajusteBeneficios'] = pd.Series(valoresTxReajusteBeneficios, index=periodo)
        dados_ldo['TxInflacao'] = pd.Series(TxInflacao, index=periodo)
        dados_ldo['AliqEfMed'] = pd.Series(aliquotasPlanilhasMF, index=[2014]+periodo)

        # Tabela 6.1 da LDO de 2018
        dados_ldo['Tabela_6.1'] = dados.parse('Tabela 6.1', index_col=0)
        # Tabela 6.2 da LDO de 2018
        dados_ldo['Tabela_6.2'] = dados.parse('Tabela 6.2', index_col=0)
                
        # Corrige a unidade (os dados estão em milhões)
        dados_ldo['Tabela_6.2']['Receita'] *= 10**6 
        dados_ldo['Tabela_6.2']['Despesa'] *= 10**6 
        dados_ldo['Tabela_6.2']['Necessidade de Fin.'] *= 10**6 
        dados_ldo['Tabela_6.2']['PIB'] *= 10**6 
        
        # Carrega os dados de PIB
        dados_ldo['PIB Planilhas'] = PIBs
        
        # Informações do AEPS 2015
        dados_ldo['Receitas AEPS'] = pd.Series(receitas_aeps, index=[2013, 2014, 2015])
        dados_ldo['Despesas AEPS'] = pd.Series(despesas_aeps, index=[2013, 2014, 2015])
        dados_ldo['Aposentadorias AEPS'] = pd.Series(aposentadorias_aeps, index=[2013, 2014, 2015])
        dados_ldo['Pensões AEPS'] = pd.Series(pensoes_aeps, index=[2013, 2014, 2015])
        
                
        return dados_ldo