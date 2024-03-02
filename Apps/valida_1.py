import re
import sys
from time import sleep
import pandas as pd
from PrettyColorPrinter import add_printer
from lxml2pandas import subprocess_parsing
import unicodedata

add_printer(1)
loop = True


def normalizar_texto(texto):
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')


try:  # Tenta executar o código dentro do bloco try
    nome_do_arquivo = 'saved_page_20240214T181156.983Z.html'  # Substitua 'seu_arquivo.html' pelo nome do seu arquivo
    with open(nome_do_arquivo, 'r',
              encoding='utf-8') as arquivo:  # Certifique-se de usar o encoding correto para o seu arquivo
        conteudo_arquivo = arquivo.read()  # Lê o conteúdo do arquivo

    # O resto do seu código permanece o mesmo, mas você usará `conteudo_arquivo` no lugar de `stdout[0]`
    htmldata = [(x[0], x[1]) for x in
                re.findall(
                    br'<div><p>ELEMENTSEPSTART(\d+)</p></div>(.*?)<div><p>ELEMENTSEPEND\d+</p></div>'
                    ,
                    conteudo_arquivo.encode())]  # Lembre-se de codificar o conteúdo se estiver trabalhando com expressões regulares em bytes

    df = subprocess_parsing(  # Chama a função subprocess_parsing para converter os dados HTML em um DataFrame do Pandas
        htmldata,
        chunks=1,
        processes=5,
        fake_header=True,
        print_stdout=False,
        print_stderr=True,
    )

    print(df)
    # breakpoint()

    # ml1-MatchLiveSoccerModule_AnimWrapper - classe da tela com o jogo e atualização em tempo real. com coordenadas x y em tempo real.
    # allelementsdf = df.loc[df.aa_attr_values == 'ipe-EventViewNavBar_Scroller'] <<-- lista das opçoes que tem no topo, podemos usar como validação para ver se esta na página correta?
    # Filtra o DataFrame para elementos com o atributo 'ovm-Fixture_Container'

    # allelementsdf = df.loc[df.aa_attr_values == 'ovm-Fixture_Container']  # Filtra o DataFrame para elementos com o atributo 'ovm-Fixture_Container'
    allelementsdf = df.loc[
        df.aa_attr_values == 'gl-MarketGroupPod sip-MarketGroup']  # <<-- após acessar um jogo, todos os grids possuem esta classe # Filtra o DataFrame para elementos com o atributo 'ovm-Fixture_Container'
    allframes = []  # Inicializa uma lista para armazenar DataFrames
    for key, item in allelementsdf.iterrows():  # Itera sobre cada elemento filtrado
        df2 = df.loc[df.aa_element_id.isin(
            item.aa_all_children) &  # Filtra o DataFrame original para elementos que são filhos do elemento atual
                     (df.aa_doc_id == item.aa_doc_id)]
        df3 = df2.loc[df2.aa_attr_values.isin(
            ['ovm-ParticipantOddsOnly_Odds',  # Filtra ainda mais para elementos com atributos específicos
             'ovm-FixtureDetailsTwoWay_TeamName'])]  # lsb-ScoreBasedScoreboardAggregate_TeamName lsb-ScoreBasedScoreboardAggregate_TeamName-aggregate | score board --> lsb-ScoreBasedScoreboardAggregate_ScoreContainer

        # lsb - ScoreBasedScoreboardAggregate_TeamContainer
        # lsb - ScoreBasedScoreboardAggregate_Team1Container
        #
        # lsb - ScoreBasedScoreboardAggregate_TeamContainer
        # lsb - ScoreBasedScoreboardAggregate_Team2Container

        if len(df3) == 5:  # Verifica se o número de elementos filtrados é exatamente 5
            allframes.append(df3.aa_text.reset_index(
                drop=True).to_frame().T)  # Adiciona os textos dos elementos filtrados como uma linha em um novo DataFrame
    dffinal = (pd.concat(allframes)).astype({2: 'Float64',
                                             # Concatena todos os DataFrames da lista em um único DataFrame e converte colunas específicas para Float64
                                             3: 'Float64', 4:
                                                 'Float64'}).reset_index(drop=True)

    # Aplica a função de normalização a todas as strings no DataFrame
    for coluna in dffinal.columns:
        if dffinal[coluna].dtype == "object":
            dffinal[coluna] = dffinal[coluna].apply(normalizar_texto)


    print(dffinal)  # Imprime o DataFrame final

    # breakpoint()
    sleep(1.5)
    loop = False

except Exception as e:  # Captura qualquer exceção que ocorra durante a execução do bloco try
    print('something is wrong!')
    sys.stderr.write(f'{e}\n')  # Escreve a mensagem de erro no stderr
    sys.stderr.flush()  # Limpa o buffer de stderr
