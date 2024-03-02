import requests
import json
import os
import re
from PrettyColorPrinter import add_printer  # Adiciona uma impressora colorida para logs, presumivelmente para debug ou visualização
import prettytable
from datetime import datetime
import pandas as pd
from tabulate import tabulate
import textwrap

'''

**Lógica do Código:**

1. **Inicialização (`__init__`):** Configura o bot com o token e a URL base da API do Telegram. Inicializa o `update_id` como `None`.
2. **`retorna_partidas`:** Faz uma requisição à URL da liga fornecida, extrai informações das tabelas HTML e compila uma string com esses dados.
3. **`Iniciar`:** Entra em um loop infinito onde obtém novas mensagens, processa cada mensagem para determinar a resposta adequada, e envia essa resposta ao usuário.
4. **`obterMensagens`:** Obtém novas mensagens do Telegram usando a API. Usa `update_id` para obter apenas as mensagens mais recentes.
5. **`criarResposta`:** Determina a resposta a ser enviada com base no texto da mensagem recebida. Pode fornecer informações sobre as partidas das ligas de acordo com a escolha do usuário ou responder com mensagens padrão.
6. **`responder`:** Envia a resposta determinada ao usuário que enviou a mensagem original.

**Validação e Execução:**

- O código parece lógico e bem estruturado para um bot do Telegram que responde com informações de partidas de futebol com base na entrada do usuário.
- Assegure-se de que todas as dependências (como `requests`, `pandas`, etc.) estejam instaladas no seu ambiente.
- Substitua `'SEU_TOKEN_AQUI'` pelo token real do seu bot do Telegram.
- Execute o script e interaja com o bot no Telegram para testar sua funcionalidade.



'''


class TelegramBot:
    def __init__(self):
        add_printer(1)  # Inicializa a impressora colorida
        self.token = '6119477838:AAHFH9P6rMM7wUuKVn_Pz9upU3WEIFUFsnc'  # Token do bot do Telegram
        self.url_base = f'https://api.telegram.org/bot{self.token}/'  # URL base para a API do Telegram
        self.update_id = None  # ID da última atualização processada pelo bot

    def abreviar_times(self, texto):
        texto = re.sub(r'\(Esports\)', '', texto)  # Remove "(Esports)"

        # Regex para encontrar palavras fora dos parênteses
        regex = re.compile(r'(?<!\(\w)(\b\w+\b)(?!\w*\))')

        def abreviar(match):
            palavra = match.group(0)
            # Abreviar palavras com mais de 6 letras para as primeiras 3 letras seguidas de um ponto
            return (palavra[:3] + '.') if len(palavra) > 6 else palavra

        # Substituir no texto os nomes dos times pela versão abreviada
        return regex.sub(abreviar, texto)

    def formatar_hora(self, hora_str):
        # Verifica se hora_str é uma string
        if isinstance(hora_str, str):
            # Esta função assume que a data está no formato 'MM/DD HH:MM'
            match = re.match(r'\d{2}/\d{2}\s+(\d{2}:\d{2})', hora_str)
            if match:
                return match.group(1)  # Retorna apenas a parte do horário
        # Retorna a string original se o padrão não corresponder ou não for string
        return hora_str
    def format_column(self, data, width=10):
        """Formata os dados de uma coluna para ter largura máxima 'width', adicionando quebras de linha se necessário."""
        if isinstance(data, str):
            return '\n'.join(textwrap.wrap(data, width))
        return data

    def format_df(self, df, col_width=None, title="Tabela de Jogos", custom_headers=None):
        # Configurações personalizadas para os cabeçalhos
        if custom_headers is None:
            custom_headers = {
                'Date': 'Hora',
                'R': 'G x G',
                '-': 'Resultado'
            }

        # Abreviando os nomes dos times em cada célula, exceto o texto entre parênteses
        df = df.applymap(abreviar_times)

        # Limitar a largura das colunas
        df = df.applymap(lambda x: '\n'.join(textwrap.wrap(x, col_width)))

        # Alterando cabeçalhos se necessário
        if custom_headers:
            df.rename(columns=custom_headers, inplace=True)

        # Convertendo o DataFrame para uma tabela HTML
        formatted_str = f"<b>{title}:</b>\n<pre>{df.to_html(index=False, border=0)}</pre>"
        return formatted_str

    def retorna_partidas(self, league_url):

        '''
        Passo a passo do processo desta função:

        declarar o datetime;
        declarar as ligas;
        declara o request conforme o nome da liga;


        '''
        hoje = datetime.now()
        hoje_str = hoje.strftime("%d-%m-%Y %H-%M-%S")

        league_names = {
            'https://pt.betsapi.com/l/23118/Esoccer-GT-Leagues--12-mins-play': 'E-Soccer Liga GT - 12 minutos',
            'https://betsapi.com/l/33440/Esoccer-Adriatic-League--10-mins-play': 'E-Soccer Liga Adriatic - 10 minutos',
            'https://pt.betsapi.com/l/22614/Esoccer-Battle--8-mins-play': 'E-Soccer Liga Battle - 8 minutos'
        }

        league_name = league_names.get(league_url, 'Unknown League')
        response = requests.get(league_url)
        response_content = response.content

        result_str = f'{league_name} - {hoje_str}\n'
        print(result_str)

        if response.status_code == 200:
            df_list = pd.read_html(response_content, attrs={'class': 'table'})
            print(df_list)
            titles = ["Tabela de jogos passados", "Tabela de próximos jogos"]

            if len(df_list) >= 2:
                for i, df in enumerate(df_list):

                    df.rename(columns={'Date': 'Hora', '-': 'GxG', 'Home vs Away': 'Casa vs Visitante'}, inplace=True)

                    if 'R' in df.columns:
                        df.drop('R', axis=1, inplace=True)
                    if 'Casa vs Visitante' in df.columns:

                        df['Casa vs Visitante'] = df['Casa vs Visitante'].str.replace('Esports', '', case=False,regex=True)
                        #df.rename(columns={'Date': 'Hora'}, inplace=True)
                        df['Hora'] = df['Hora'].apply(self.formatar_hora)


                    # Remoção de "(Esports)" e formatação das horas



                # Renomeia as colunas conforme necessário

                # Criação da tabela prettytable
                table = prettytable.PrettyTable()
                table.field_names = df.columns.tolist()
                table.align = 'l'

                for index, row in df.iterrows():
                    table.add_row(row.values)

                title = titles[i] if i < len(titles) else f"Tabela {i}"
                result_str += f'{title}:\n<pre>{table}</pre>\n\n'  # Uso de <pre> para formatação pré-formatada no HTML
                #result_str += f'{title}:\n{table.get_string()}\n\n'
        else:
            result_str += 'Falha ao baixar a página. Código de status: ' + str(response.status_code) + '\n'

        return result_str

                #result_str += f'{title}:\n<pre>{table}</pre>\n\n'  # Uso de <pre> para formatação pré-formatada no HTML
                #result_str += f'{title}:\n{table.get_string()}\n\n'



    def Iniciar(self):  # Método para iniciar o bot
        print('Bot iniciado')
        while True:  # Loop infinito para manter o bot rodando
            atualizacao = self.obterMensagens()  # Obtém novas mensagens
            mensagens = atualizacao['result']  # Extrai as mensagens do resultado
            if mensagens:  # Se houver mensagens
                for mensagem in mensagens:  # Itera sobre as mensagens
                    # Verifica se a mensagem é válida
                    if 'message' in mensagem and 'from' in mensagem['message'] and 'id' in mensagem['message']['from']:
                        chat_id = mensagem['message']['from']['id']  # ID do chat para responder
                        primeiraMensagem = mensagem['message']['message_id'] == 1  # Verifica se é a primeira mensagem
                        resposta = self.criarResposta(mensagem, primeiraMensagem)  # Cria a resposta
                        self.responder(resposta, chat_id)  # Envia a resposta
                        self.update_id = mensagem['update_id'] + 1  # Atualiza o ID da última mensagem processada

    def obterMensagens(self):  # Método para obter novas mensagens
        link_requisicao = f'{self.url_base}getUpdates?timeout=100'  # URL para obter atualizações
        if self.update_id:  # Se já existe um update_id
            link_requisicao += f'&offset={self.update_id}'  # Adiciona o offset para obter apenas mensagens novas
        resposta = requests.get(link_requisicao) # Faz a requisição para obter atualizações
        if resposta.status_code == 200:
            return json.loads(resposta.content) # Converte a resposta de JSON para um dicionário Python e retorna
        return {'result': []} # Se a resposta não for bem-sucedida, retorna um dicionário vazio

    def criarResposta(self, mensagem, primeiraMensagem):  # Método para criar a resposta com base na mensagem recebida
        # Dicionário com as URLs das ligas
        urls = {
            '1': 'https://pt.betsapi.com/l/22614/Esoccer-Battle--8-mins-play',
            '2': 'https://betsapi.com/l/33440/Esoccer-Adriatic-League--10-mins-play',
            '3': 'https://pt.betsapi.com/l/23118/Esoccer-GT-Leagues--12-mins-play'
        }
        # Extrai o texto da mensagem
        texto_mensagem = mensagem['message']['text'] if 'text' in mensagem['message'] else ''

        # Verifica se é a primeira mensagem ou se o comando '/menu' foi enviado
        if primeiraMensagem or texto_mensagem.lower() == 'menu':
            return '''
            Seja bem-vindo ao UNFEK_BOT.
            1 - Tabela de Jogos: Battle Liga - 8 Minutos (+12 Jogos)
            2 - Tabela de Jogos Adriatic Liga - 10 Minutos (+12 Jogos)
            3 - Tabela de Jogos GT Liga - 12 Minutos (+12 Jogos)
            '''
        elif texto_mensagem in urls:  # Se a mensagem corresponde a uma das opções de liga
            return self.retorna_partidas(urls[texto_mensagem])  # Chama o método retorna_partidas para a URL selecionada
            #return self.retorna_partidas_tabulated(urls[texto_mensagem])  # Use 'self.' para chamar o método
            #return self.retorna_partidas_base(urls[texto_mensagem], formatted=True)

        elif texto_mensagem.lower() in ('s', 'sim'):  # Resposta para 's' ou 'sim'
            return 'Interessante. Vamos começar!'
        else:  # Para qualquer outra entrada
            return 'Gostaria de voltar ao Menu? Digite "menu".'

    def responder(self, resposta, chat_id):
        url = f'{self.url_base}sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': resposta,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        requests.post(url, json=payload)


# Cria uma instância da classe TelegramBot e inicia o bot
bot = TelegramBot()
bot.Iniciar()








TABELA ='''{table}


+-------------+---------------------------------+-------+
| Hora        | Casa vs Visitante               | G x G |
+-------------+---------------------------------+-------+

| 02/20 15:16 | 
Newcastle (Peja)  vs Sevilla (Boki)              |2-1|
| 02/20 15:16 |
 AC Milan (Rodja)  vs Galatasaray (Hermanito)    |5-2|
| 02/20 15:12 |
 RB Leipzig (Izzy)  vs Eintracht (Buconi)        |1-0|
| 02/20 15:12 |
 Xu/Yang vs Wolfsburg (Gabiigol)                 |4-2|
| 02/20 15:04 |
 Inter (Dacum)  vs AC Milan (Rodja)              |0-0|
| 02/20 15:04 |
 Galatasaray (Hermanito)  vs Newcastle (Peja)    |0-2|
| 02/20 15:00 |
 Dortmund (Kallu)  vs RB Leipzig (Izzy)          |3-2|
| 02/20 15:00 |
 Eintracht (Buconi)  vs Bayer 04 (Nicolas_Rage)  |2-2|
| 02/20 14:52 |
 Sevilla (Boki)  vs Galatasaray (Hermanito)      |4-1|
| 02/20 14:52 |
 Newcastle (Peja)  vs Inter (Dacum)              |3-1|
| 02/20 14:48 |
 Barcelona (Rus_1995_LAN)  vs Bayern (d1pseN)    |1-0|
| 02/20 14:48 |
 PSG (WBoy)  vs Man City (lowheels)              |2-3|
+-------------+---------------------------------+-----+



'''


