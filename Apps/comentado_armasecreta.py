import re
import sys
from time import sleep
import pandas as pd
from PrettyColorPrinter import add_printer

add_printer(1)
from usefuladb import AdbControl
from lxml2pandas import subprocess_parsing

# adb=r"C:\Android\android-sdk\platform-tools\adb.exe"
adb = r"C:\ADB\platform-tools\adb.exe"
# To connect to all devices at once, you can use this static method (Windows only):
AdbControl.connect_to_all_tcp_devices_windows(
    adb_path=adb,
)
# Blocking Shell
# - Waits until stderr/stdout have finished processing.
# - if you run "cd /sdcard/" and then another command "ls", for example, you will see the contents of /sdcard/.
# - If you switch to su, you will remain in the superuser mode.
# - Commands are not base64 encoded
addr = "127.0.0.1:5555"

eval_shell = AdbControl(
    adb_path=adb,
    device_serial=addr,
    use_busybox=False,
    connect_to_device=True,
    invisible=True,
    print_stdout=False,
    print_stderr=True,
    limit_stdout=3,
    limit_stderr=3,  # limits the history of shellcommands - can be checked at blocking_shell.stderr
    limit_stdin=None,
    convert_to_83=True,
    wait_to_complete=0,
    flush_stdout_before=True,
    flush_stdin_before=True,
    flush_stderr_before=True,
    exitcommand="xxxCOMMANDxxxDONExxx",
    capture_stdout_stderr_first=True,
    global_cmd=True,
    global_cmd_timeout=10,
    use_eval=True,  # executes commands using eval
    eval_timeout=60,  # timeout for eval (netcat transfer)
)
df = eval_shell.get_all_activity_elements(as_pandas=True)
x, y = df.loc[df.ELEMENT_ID == 'app:id/optional_toolbar_button'][['CENTER_X', 'CENTER_Y']].__array__()[0]
sleeptime = 1
script = """#!/bin/bash
cd /sdcard/Download
rm * -f
check_if_finished_writing() {
    timeout2=$(($SECONDS + timeoutfinal))
    while true; do
        if [ $SECONDS -gt "$timeout2" ]; then
            return 1
        fi
        initial_size=$(stat -c %s "$1")
        sleep "$2"
        current_size=$(stat -c %s "$1")
        if [ "$current_size" -eq "$initial_size" ]; then
            return 0
        fi
    done
}
while true; do
    input tap XCOORD YCOORD
    sleep SLEEPTIME
    file_contents=$(ls *.html -1 | tail -n 1)
    if [ -z "$file_contents" ]; then
        continue
    else
        if check_if_finished_writing "$file_contents" 0.1; then
            cat "$file_contents"
            rm * -f
        fi
    fi
    break
done""".replace('XCOORD', str(x)).replace('YCOORD', str(y)).replace('SLEEPTIME', str(sleeptime))

while True:  # Inicia um loop infinito
    try:  # Tenta executar o código dentro do bloco try
        stdout, stderr = eval_shell.execute_sh_command(script)  # Executa o script shell no dispositivo conectado e captura a saída padrão e de erro
        htmldata = [(x[0].decode(), x[1]) for x in  # Decodifica a saída padrão capturada e extrai os dados HTML
                    re.findall(  # Utiliza expressão regular para encontrar todos os elementos HTML que correspondem ao padrão especificado
                        br'<div><p>ELEMENTSEPSTART(\d+)</p></div>(.*?)<div><p>ELEMENTSEPEND\d+</p></div>'
                        , stdout[0])]
        df = subprocess_parsing(  # Chama a função subprocess_parsing para converter os dados HTML em um DataFrame do Pandas
            htmldata,
            chunks=1,
            processes=5,
            fake_header=True,
            print_stdout=False,
            print_stderr=True,
        )

        # ml1-MatchLiveSoccerModule_AnimWrapper - classe da tela com o jogo e atualização em tempo real. com coordenadas x y em tempo real.
        # allelementsdf = df.loc[df.aa_attr_values == 'ipe-EventViewNavBar_Scroller'] <<-- lista das opçoes que tem no topo, podemos usar como validação para ver se esta na página correta?
        # Filtra o DataFrame para elementos com o atributo 'ovm-Fixture_Container'

        allelementsdf = df.loc[df.aa_attr_values == 'ovm-Fixture_Container']  # Filtra o DataFrame para elementos com o atributo 'ovm-Fixture_Container'
        # allelementsdf = df.loc[df.aa_attr_values == 'gl-MarketGroupPod sip-MarketGroup '] <<-- após acessar um jogo, todos os grids possuem esta classe # Filtra o DataFrame para elementos com o atributo 'ovm-Fixture_Container'
        allframes = []  # Inicializa uma lista para armazenar DataFrames
        for key, item in allelementsdf.iterrows():  # Itera sobre cada elemento filtrado
            df2 = df.loc[df.aa_element_id.isin(item.aa_all_children) &  # Filtra o DataFrame original para elementos que são filhos do elemento atual
                         (df.aa_doc_id == item.aa_doc_id)]
            df3 = df2.loc[df2.aa_attr_values.isin(['ovm-ParticipantOddsOnly_Odds',  # Filtra ainda mais para elementos com atributos específicos
                                                   'ovm-FixtureDetailsTwoWay_TeamName'])] # lsb-ScoreBasedScoreboardAggregate_TeamName lsb-ScoreBasedScoreboardAggregate_TeamName-aggregate | score board --> lsb-ScoreBasedScoreboardAggregate_ScoreContainer

            # lsb - ScoreBasedScoreboardAggregate_TeamContainer
            # lsb - ScoreBasedScoreboardAggregate_Team1Container
            #
            # lsb - ScoreBasedScoreboardAggregate_TeamContainer
            # lsb - ScoreBasedScoreboardAggregate_Team2Container

            if len(df3) == 5:  # Verifica se o número de elementos filtrados é exatamente 5
                allframes.append(df3.aa_text.reset_index(drop=True).to_frame().T)  # Adiciona os textos dos elementos filtrados como uma linha em um novo DataFrame
        dffinal = (pd.concat(allframes)).astype({2: 'Float64',  # Concatena todos os DataFrames da lista em um único DataFrame e converte colunas específicas para Float64
                                                 3: 'Float64', 4:
                                                     'Float64'}).reset_index(drop=True)
        print(dffinal)  # Imprime o DataFrame final
    except Exception as e:  # Captura qualquer exceção que ocorra durante a execução do bloco try
        sys.stderr.write(f'{e}\n')  # Escreve a mensagem de erro no stderr
        sys.stderr.flush()  # Limpa o buffer de stderr
