# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

# Arquivo com os parâmetros de projeção
arquivo_parametros = "parametros.txt"

def obter_parametros():
    # Dicionário que armazena os parâmetros
    parametros = {}
    
    with open(arquivo_parametros) as arquivo:
        for linha in arquivo:
            linha = linha.strip()                
            if not linha:  # pula linhas em branco
                continue
            if linha.startswith("#"):  # pula comentários
                continue
            
            # Pega a primeira string antes do = e remove os espaços em branco
            variavel = linha.split('=')[0].replace(" ", "")
            # Pega a segunda string antes do = e remove os espaços em branco
            valor = linha.split('=')[1].replace(" ", "")
        
            try:
                parametros[variavel] = int(valor)
            except:
                parametros[variavel] = float(valor)
            
    return parametros