# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
import pandas as pd

class DadosLDO():
    
    def get_tabelas():
        
        dados = {}
        periodo = list(range(2015, 2061))   
        
        # Taxa de Crescimento do Salário Mínimo em % (2015-2060)
        ValoresTxCrescimentoSalMin = [8.84 , 11.68, 6.48, 4.62, 5.02, 7.1, 7.1, 7.2, 7.5, 7.43, 7.39, 7.32, 7.25,
                    7.17, 7.1, 7.02, 6.94, 6.87, 6.79, 6.72, 6.65, 6.57, 6.5,
                    6.41, 6.33, 6.26, 6.19, 6.11, 6.05, 5.98, 5.92, 5.86, 5.81,
                    5.75, 5.7, 5.65, 5.61, 5.57, 5.54, 5.49, 5.46, 5.43, 5.39,
                    5.37, 5.35, 5.32]
        
        # Reajustes retirados das LDOs de 2017 e 2018
        reajuste_2015_2018 = [6.23, 11.28, 7.5, 4.62]

        # Taxa de Reajuste dos demais benefícios em %  (2015-2060) 
        ValoresTxReajusteBeneficios = reajuste_2015_2018 + ([4.5] * 42)   
        
        # Taxa de Reajuste dos demais benefícios em %  (2015-2060) 
        TxCresMassaSalContribuintes = [7.52, 7.36, 7.42, 7.35, 7.28, 7.24, 7.17, 7.09, 7.01, 6.93, 6.85,
                                       6.78, 6.70, 6.62, 6.53, 6.45, 6.37, 6.29, 6.21, 6.14, 6.06, 5.98, 
                                       5.91, 5.83, 5.77, 5.70, 5.64, 5.59, 5.55, 5.50, 5.46, 5.42, 5.39, 
                                       5.37, 5.34, 5.32, 5.30, 5.27, 5.25, 5.22, 5.20, 5.18, 5.15]
        
        
         # Tabela 6.1 da LDO de 2018
        dados['TxCrescimentoSalMin'] = pd.Series(ValoresTxCrescimentoSalMin, index=periodo)
        dados['TxReajusteBeneficios'] = pd.Series(ValoresTxReajusteBeneficios, index=periodo)
        #dados['pib_2014'] = 7235139000000
        
        return dados
       
