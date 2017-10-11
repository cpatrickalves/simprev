# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
import pandas as pd

class DadosLDO():
    
    def __init__(self):
        '''
        Abre o arquivo com os dados da LDO de 2018 
        '''
        arquivo = 'util/TabelasLDO2018.xlsx'
        # Abre arquivo
        self.dados = pd.ExcelFile(arquivo)
        
        self.periodo = list(range(2015, 2061))   
        
            
        # Taxa de Crescimento do Salário Mínimo em % (2015-2060)
        # Os 3 primeiros valores estão somados com a inflação (2015-2017)
        # Valores correspondem a TxCrescimentoSalMin da LDO menos a inflação        
        self.ValoresTxCrescimentoSalMin = [8.84 , 11.68, 6.48, 0.0, 0.50, 2.49, 2.49, 
                                           2.58, 2.87, 2.81,2.76, 2.70, 2.63, 2.56, 2.49, 
                                           2.42, 2.34, 2.27, 2.20, 2.13, 2.06, 1.98, 1.91,
                                           1.83, 1.76, 1.69, 1.62, 1.55, 1.48, 1.42, 1.36, 
                                           1.30, 1.25, 1.20, 1.15, 1.10, 1.07, 1.03, 1.00, 
                                           0.95, 0.92, 0.89, 0.86, 0.84, 0.81, 0.79]
        
        #self.ValoresTxCrescimentoSalMin = [8.84 , 11.68, 6.48, 4.62, 5.02, 7.1, 
         #                                  7.1, 7.2, 7.5, 7.43, 7.39, 7.32, 7.25, 
         #                                  7.17, 7.1, 7.02, 6.94, 6.87, 6.79, 6.72,
         #                                  6.65, 6.57, 6.5, 6.41, 6.33, 6.26, 6.19,
         #                                  6.11, 6.05, 5.98, 5.92, 5.86, 5.81, 5.75,
         #                                  5.7, 5.65, 5.61, 5.57, 5.54, 5.49, 5.46,
         #                                  5.43, 5.39, 5.37, 5.35, 5.32]
        
        # Atualização monetária retirados das Planilhas do MF
        self.reajuste_2015_2018 = [6.41, 10.67, 6.29, 4.62]
        # OBS: Inflação é zero em 2018
        self.inflacao_2015_2018 = [6.41, 10.67, 6.29, 0.0]
                        
        # Valores reais
        #self.reajuste_2015_2018 = [6.23, 11.28, 6.58, 4.62]
        #self.inflacao_2015_2018 = [6.23, 11.28, 6.58, 4.5]
        
        # Taxa de Reajuste dos demais benefícios em %  (2015-2060) 
        self.ValoresTxReajusteBeneficios = self.reajuste_2015_2018 + ([4.5] * 42)   
        
        # Taxa de Inflação em %  (2015-2060) 
        self.TxInflacao = self.inflacao_2015_2018 + ([4.5] * 42)   
        #self.TxInflacao = self.inflacao_2015_2018 + ([0.0] * 42)   
        
        # Taxa de Reajuste dos demais benefícios em %  (2015-2060) 
        self.TxCresMassaSalContribuintes = [7.52, 7.36, 7.42, 7.35, 7.28, 7.24, 7.17, 7.09, 7.01, 6.93, 6.85,
                                       6.78, 6.70, 6.62, 6.53, 6.45, 6.37, 6.29, 6.21, 6.14, 6.06, 5.98, 
                                       5.91, 5.83, 5.77, 5.70, 5.64, 5.59, 5.55, 5.50, 5.46, 5.42, 5.39, 
                                       5.37, 5.34, 5.32, 5.30, 5.27, 5.25, 5.22, 5.20, 5.18, 5.15]
                    
        # Aliquota média de 2014
        # Valores retirados da Planilha do MF
        
        
        # Aliquotas médias de 2014 a 2060
        # aliqMed = receita/MassaSalarial        
        self.aliquotasPlanilhasMF = [28.3, 27.2, 25.0] + ([26.8] * 44)
        #self.aliquotasPlanilhasMF = [28.3, 27.2, 25.0, 24.0, 24.3, 24.6, 24.9, 25.2, 25.5, 25.8] + ([26.1] * 37)
                
    def get_tabelas(self):
        
        # Dicionário que armazena os dados
        dados = {}        

        dados['TxCrescimentoSalMin'] = pd.Series(self.ValoresTxCrescimentoSalMin, index=self.periodo)
        dados['TxReajusteBeneficios'] = pd.Series(self.ValoresTxReajusteBeneficios, index=self.periodo)
        dados['TxInflacao'] = pd.Series(self.TxInflacao, index=self.periodo)
        dados['AliqEfMed'] = pd.Series(self.aliquotasPlanilhasMF, index=[2014]+self.periodo)

        # Tabela 6.1 da LDO de 2018
        dados['Tabela_6.1'] = self.dados.parse('Tabela 6.1', index_col=0)
        # Tabela 6.2 da LDO de 2018
        dados['Tabela_6.2'] = self.dados.parse('Tabela 6.2', index_col=0)
                
        # Corrige a unidade (os dados estão em milhões)
        dados['Tabela_6.2']['Receita'] *= 10**6 
        dados['Tabela_6.2']['Despesa'] *= 10**6 
        dados['Tabela_6.2']['Necessidade de Fin.'] *= 10**6 
        dados['Tabela_6.2']['PIB'] *= 10**6 
        
        #dados['pib_2014'] = 7235139000000
        
        return dados
       
