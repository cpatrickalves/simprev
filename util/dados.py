# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

# Lista de Siglas
ids_pop_ibge = ['PopIbgeH','PopIbgeM'] 
ids_pop_pnad = ['PopPnadH','PopPnadM', 'PopUrbPnadH',
                'PopUrbPnadM','PopRurPnadH','PopRurPnadM',
                'PeaUrbPnadH','PeaUrbPnadM','PeaRurPnadH',
                'PeaRurPnadM', 'PopOcupUrbPnadH', 'PopOcupUrbPnadM',
                'PopOcupRurPnadH', 'PopOcupRurPnadM', 'PopOcupUrbSmPnadH',
                'PopOcupUrbAcimPnadH', 'PopOcupUrbSmPnadM',
                'PopOcupUrbAcimPnadM', 'SegEspRurPnadH','ContrRurPnadH',
                'SegPotRurPnadH', 'SegEspRurPnadM', 'ContrRurPnadM',
                'SegPotRurPnadM', 'SegRurPnadH', 'SegRurPnadM'] 

# Função que retorna uma lista de benefícios de acordo como filtro
def get_id_beneficios(filtros=[], info=''):

# A tag info é usada no momento de leitura das tabelas no arquivo
# Es = estoque
# Co = conceções
# Ce = cessações

# Exemplos de filtros:
# Apin = Aposentadoria por Invalidez
# Auxd = Auxílio doença
# SalMat = Salário Maternidade
    
    # Lista com todos os benefícios utilizando o mesmo padrão do simulador da Fazenda    
    beneficios = ["ApinUrbPisoH", "ApinUrbPisoM", "ApidUrbPisoH", "ApidUrbPisoM",
                      "AtcnUrbPisoH", "AtcnUrbPisoM", "AtceUrbPisoH", "AtceUrbPisoM",
                      "AtcpUrbPisoH", "AtcpUrbPisoM", "AtcdUrbPisoH", "AtcdUrbPisoM",
                      "AinvUrbPisoH", "AinvUrbPisoM", 

                      "ApinRurH", "ApinRurM", "ApidRurH", "ApidRurM",
                      "AtcnRurH", "AtcnRurM", "AtceRurH", "AtceRurM",
                      "AtcpRurH", "AtcpRurM", "AtcdRurH","AtcdRurM",
                      "AinvRurH", "AinvRurM",  

                      "ApinUrbAcimH", "ApinUrbAcimM", "ApidUrbAcimH", "ApidUrbAcimM", 
                      "AtcnUrbAcimH", "AtcnUrbAcimM", "AtceUrbAcimH", "AtceUrbAcimM", 
                      "AtcpUrbAcimH", "AtcpUrbAcimM", "AtcdUrbAcimH", "AtcdUrbAcimM",
                      "AinvUrbAcimH", "AinvUrbAcimM", 
             
                      "AuxdUrbPisoH", "AuxdUrbPisoM", "AuxdRurH", "AuxdRurM",                
                      "AuxdUrbAcimH", "AuxdUrbAcimM", "AuxaUrbPisoH", "AuxaUrbPisoM",
                      "AuxrUrbPisoH", "AuxrUrbPisoM", "AuxaRurH", "AuxaRurM", 
                      "AuxrRurH", "AuxrRurM", "AuxaUrbAcimH",
                      "AuxaUrbAcimM", "AuxrUrbAcimH", "AuxrUrbAcimM",
             
                      "SalMatUrbPisoM","SalMatRurM", "SalMatUrbAcimM" , 
                      "PensUrbPisoH", "PensUrbPisoM", "PensRurH", 
                      "PensRurM", "PensUrbAcimH", "PensUrbAcimM" , 
                      "LoasIdoH", "LoasIdoM", "LoasDefH", 
                      "LoasDefM", "RmvH", "RmvM"]
    
    # lista que será retornada
    lista_final = []
    
    # Verifica se a lista está vazia, nesse caso retorna todos os benefícios
    if len(filtros) == 0:   
        for l in beneficios:
            lista_final.append(info+l)       
    
    # Aplica o filtro na lista
    else:
        for f in filtros:  
            for l in beneficios:
                if f in l:
                    lista_final.append(info+l)  
    
    return lista_final


# Função que extrai as tabelas do arquivo
# Recebe o arquivo (planilha) e a lista de tabelas a serem extraídas
def get_tabelas(lista, xls, info=False):

    # Dicionário que salva as tabelas
    colecao_tabelas = {}

    # Lista com as tabelas com dados ausentes
    tabsIncompletas = []
    tabsInexistentes = []

    # Lê cada uma das tabelas dentro do arquivo
    # Converte cada tabela em um DataFrame e salva no dicionário
    for sigla in lista:
                
        # Remove os 2 primeiro caracteres para o caso de estoques, concessões
        # ou cessações (ex: 'EsApidRurH' -> 'ApidRurH')
        if sigla[0:2] in ['Es', 'Co', 'Ce'] and sigla[0:5] != 'Contr':            
            chave = sigla[2:]  
        else:
            chave = sigla
            
        try:
            colecao_tabelas[chave] = xls.parse(sigla, index_col=0)          # Converte a tabela para um DataFrame
            colecao_tabelas[chave].drop('Total', inplace=True)              # Elimina a linha 'Total'
            colecao_tabelas[chave].dropna(how='all', axis=1, inplace=True)  # Elimina colunas com dados ausentes
            colecao_tabelas[chave].dropna(how='all', inplace=True)          # Elimina linhas completamente vazias
            colecao_tabelas[chave].fillna(0, inplace=True)                  # Substitui os NaN por zeros       
            colecao_tabelas[chave].index.names = ['IDADE']                  # Renomeia o índice 

            # Indica se todos os elementos da Tabela são zero
            zerada = False
            if (colecao_tabelas[chave] == 0.0).all().all():
                zerada = True
            
            # Remove as tabelas que possuem dados ausentes ou todos os valores iguais a zero
            if colecao_tabelas[chave].empty or zerada:
                tabsIncompletas.append(sigla)   # Salva o nome da tabela incompleta
                colecao_tabelas.pop(chave)  # Remove a tabela

        except:
            # Salva o nome das tabelas que não existem
            tabsInexistentes.append(sigla)
           
    if info:        
        print(get_significado_sigla(lista[0][0:2]))
        print('Total de tabelas de carregadas: %s' % len(colecao_tabelas))
        print('Total de tabelas inexistentes: %s' % len(tabsInexistentes))
        print('Total de tabelas incompletas e removidas: %s \n' % len(tabsIncompletas))

    return colecao_tabelas

# Identifica idades em que o número de Concessões não bate com o Estoque 
# do ano e idade seguintes e faz uma correção. 
# Essas correções são utilizadas nos cálculos das probabilidades
def corrige_erros_estoque(estoques, concessoes, cessacoes):
    
    count = 0
    # Para todos os benefícios...    
    for beneficio in concessoes:   
        # Verifica se existe o benefício nas outras tabelas        
        if beneficio in estoques.keys() and beneficio in cessacoes.keys():                         
            for ano in concessoes[beneficio]:
                for idade in range(1,90):                                
                    con = concessoes[beneficio][ano][idade]
                    est = estoques[beneficio][ano][idade]
                    ces = cessacoes[beneficio][ano][idade]
                    
                    # Identifica idades em que o número de Concessões é maior que o Estoque do ano e idade seguinte
                    if con - ces > est:                        
                        #print('{} | ano = {}| id = {} | Con = {} | Ces = {} | Est = {}'.format(beneficio, ano, idade,con,ces,est))
                        # Corrige o estoque para as idades onde o erro foi encontrado
                        estoques[beneficio].loc[idade, ano] = round(con - ces)
                        count+=1
    #print(count)
    return estoques


# Identifica e retorna a Clientela de um benefício
def get_clientela(beneficio):
    for clientela in ['UrbPiso', 'UrbAcim', 'Rur']:
        if clientela in beneficio:
            return clientela
    
    return 'Clientela não identificada'

    
# Funçao que retorna o Significado de uma sigla
def get_significado_sigla(chave):
    
    #Dicionário de siglas
    siglas = {'Apos' : 'Aposentadorias',
            'Apin' : 'Aposentadoria por Idade (Normal ou Usual)',
            'Apid' : 'Aposentadoria por Idade da Pessoa com Deficiência',
            'Atcn' : 'Aposentadoria por Tempo de Contribuição (Normal ou Usual)',
            'Atce' : 'Aposentadoria por Tempo de Contribuição Especial',
            'Atcp' : 'Aposentadoria por Tempo de Contribuição do(a) Professor(a)',
            'Atcd' : 'Aposentadoria por Tempo de Contribuição da Pessoa com Deficiência',
            'Ainv' : 'Aposentadoria por Invalidez',
            'Aux' : 'Auxílios',
            'Auxd' : 'Auxílio-Doença',
            'Auxa' : 'Auxílio-Acidente',
            'Auxr' : 'Auxílio-Reclusão',
            'Ce' : 'Cessações',
            'Co' : 'Concessões',
            'Es' : 'Estoque',
            'SalMat' : 'Salário-Maternidade',
            'PensTot' : 'Pensões por Morte Totais',
            'PensTipoA' : 'Pensões Tipo A',
            'PensTipoB' : 'Pensões Tipo B',
            'LoasIdo' : 'Amparo Assistencial da Lei Orgânica da Previdência Social (LOAS) ao Idoso',
            'LoasDef' : 'Amparo Assistencial da LOAS da Pessoa com Deficiência',
            'RmvIda' : 'Renda Mensal Vitalícia (RMV) por Idade',
            'RmvInv' : 'Renda Mensal Vitalícia (RMV) por Invalidez',
            'Client' : 'Clientela',
            'Rur' : 'Clientela Rural',
            'Urb' : 'Clientela Urbana',
            'Piso' : 'Clientela Urbana Piso Previdenciário',
            'Acim' : 'Clientela Urbana Acima do Piso Previdenciário',
            'Sm' : 'Clientela Urbana Contribuinte Salário Mínimo',
            'AcimSm' : 'Clientela Urbana Contribuinte Acima do Salário Mínimo',
            'Seg' : 'Segurados',
            'H' : 'Homens',
            'M' : 'Mulheres',
            'Pop' : 'População',
            'Mort' : 'Mortalidade',
            'Txmortimpl' : 'Taxa de Mortalidade Implícita da População'

            }     
            
    return siglas[chave]
