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












