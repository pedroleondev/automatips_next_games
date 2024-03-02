import requests
import json
import os
from PrettyColorPrinter import add_printer
from datetime import datetime
from tabulate import tabulate
import pandas as pd
class TelegramBot:
    def __init__(self):
        add_printer(1)
        self.token = '6119477838:AAHFH9P6rMM7wUuKVn_Pz9upU3WEIFUFsnc'
        self.url_base = f'https://api.telegram.org/bot{self.token}/'
        self.update_id = None

    def retorna_partidas(self, league_url):  # Adicionado 'self' aqui
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

        if response.status_code == 200:
            df_list = pd.read_html(response_content, attrs={'class': 'table'})
            for i, table in enumerate(df_list):
                result_str += f'Tabela {i}:\n{table.to_string()}\n\n'
            if len(df_list) < 2:
                result_str += "Foi identificado apenas uma tabela.\n"
        else:
            result_str += 'Falha ao baixar a página. Código de status: ' + str(response.status_code) + '\n'

        return result_str

    def retorna_partidas_tabulated(self, league_url):
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

        if response.status_code == 200:
            df_list = pd.read_html(response_content, attrs={'class': 'table'})
            for i, df in enumerate(df_list):
                # Formatando a tabela usando tabulate
                table_str = tabulate(df, headers='keys', tablefmt='psql', showindex=False)
                result_str += f'Tabela {i}:\n{table_str}\n\n'
        else:
            result_str += 'Falha ao baixar a página. Código de status: ' + str(response.status_code) + '\n'

        return result_str



    def Iniciar(self):
        print('Bot iniciado')
        while True:
            atualizacao = self.obterMensagens()
            mensagens = atualizacao['result']
            if mensagens:
                for mensagem in mensagens:
                    if 'message' in mensagem and 'from' in mensagem['message'] and 'id' in mensagem['message']['from']:
                        chat_id = mensagem['message']['from']['id']
                        primeiraMensagem = mensagem['message']['message_id'] == 1
                        resposta = self.criarResposta(mensagem, primeiraMensagem)
                        self.responder(resposta, chat_id)
                        self.update_id = mensagem['update_id'] + 1

    def obterMensagens(self):
        link_requisicao = f'{self.url_base}getUpdates?timeout=100'
        if self.update_id:
            link_requisicao = f'{link_requisicao}&offset={self.update_id}'
        resposta = requests.get(link_requisicao)
        if resposta.status_code == 200:
            return json.loads(resposta.content)
        return {'result': []}

    def criarResposta(self, mensagem, primeiraMensagem):
        urls = {
            '1': 'https://pt.betsapi.com/l/22614/Esoccer-Battle--8-mins-play',
            '2': 'https://betsapi.com/l/33440/Esoccer-Adriatic-League--10-mins-play',
            '3': 'https://pt.betsapi.com/l/23118/Esoccer-GT-Leagues--12-mins-play'
        }
        texto_mensagem = mensagem['message']['text'] if 'text' in mensagem['message'] else ''

        if primeiraMensagem or texto_mensagem.lower() == '/menu':
            return '''
            Seja bem-vindo ao UNFEK_BOT.
            1 - Tabela de Jogos: Battle Liga - 8 Minutos (+12 Jogos)
            2 - Tabela de Jogos Adriatic Liga - 10 Minutos (+12 Jogos)
            3 - Tabela de Jogos GT Liga - 12 Minutos (+12 Jogos)
            '''
        elif texto_mensagem in urls:
            #return self.retorna_partidas(urls[texto_mensagem])  # Use 'self.' para chamar o método
            return self.retorna_partidas_tabulated(urls[texto_mensagem])  # Use 'self.' para chamar o método


        elif texto_mensagem.lower() in ('s', 'sim'):
            return 'Interessante. Vamos começar!'
        else:
            return 'Gostaria de voltar ao Menu? Digite "menu".'

    # Não esqueça de definir a função retorna_partidas fora da classe, caso ela não faça parte da mesma


    def responder(self, resposta, chat_id):
        link_de_envio = f'{self.url_base}sendMessage?chat_id={chat_id}&text={resposta}'
        requests.get(link_de_envio)

bot = TelegramBot()
bot.Iniciar()
