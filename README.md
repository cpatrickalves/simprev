# SimPrev

O simulador previdenciário é um software que permite realizar projeções de estoques, contribuintes, despesas e receitas do Regime Geral de Previdência Social (RGPS). O SimPrev possibilita a avaliação da situação futura do RGPS diante de diversos cenários para economia, demografia e mercado de trabalho. 

O SimPrev é livre, de código aberto, desenvolvido na linguagem Python que possibilita a implementação de diversos modelos atuariais de projeção a longo prazo, além de diversas outras funções descritas na sua documentação.

Na versão atual, o SimPrev implementa o 2º modelo atuarial de projecões a longo prazo do governo federal descrito no Anexo IV.6 (Metas Fiscais) da [Lei de Diretrizes Orçamentárias de 2018](http://www.camara.leg.br/internet/comissao/index/mista/orca/ldo/LDO2018/proposta/anexoIV_6.pdf).

Os seguintes módulos estão em desenvolvimento:

* Módulo para estimativa dos intervalos de confiança das projeções;
* Módulo de simulação de cenários de reforma na Previdência, semelhante a PEC 287;
* Implementação de outros modelos de projeção
    
## Instalação

Os SimPrev pode ser executado de várias formas:

### Versão .exe para Windows

Esta versão é exclusiva para o sistema operacional Windows e não requer instalação.

1. Faça o [Download](https://mega.nz/#!OYIVmSCQ) da última versão
    * Link alternativo [aqui](https://drive.google.com/open?id=1ACAE3xe1zXy3OtNgJnxkMYQZ50IeRIHM)
2. Descompacte o arquivo _zip_

### Utilizando a distribuição Python Anaconda

1. Instale o [Anaconda](https://anaconda.org/anaconda/python)
	* O Anaconda é uma distribuição Python para processamento de dados em larga escala que possui centenas de pacotes Python pré-instalados.
2. Faça o download do [SimPrev](https://github.com/cpatrickalves/simprev/archive/master.zip)
3. O simprev.py pode ser executado de duas formas:
	* Linha de comando, ex: python simprev.py
	* Através da IDE Spyder que vem junto com o Anaconda

### Utilizando o Python e pacotes necessários

1. Instale o [Python 3.x](https://www.python.org/downloads/)
2. Faça o download do [SimPrev](https://github.com/cpatrickalves/simprev/archive/master.zip)
3. Instale os pacotes descritos no arquivo _requirements.txt_
    * pip install -r requirements.txt 
4. Execute o arquivo principal _simprev.py_ 
	* python simprev.py

## Executando projeções

O arquivo _parametros.txt_ possui todos os parâmetros de simulações que serão utilizados pelo SimPrev.
O valores padrão do arquivo são os que foram utilizados na projeções da LDO de 2018.

1. Abra o arquivo parametros.txt e edite os parâmetros de projeções
	* Salve o arquivo com o mesmo nome
	* Linhas que começam com "#" são comentários e são desconsideradas pelo SimPrev
2. Execute o arquivo _simprev.py_ ou _simprev.exe_
3. Os resultados são salvos em arquivos _.csv_ na pasta _resultados_
4. Os gráficos são salvos no formato PNG e salvos na pasta _resultados_

