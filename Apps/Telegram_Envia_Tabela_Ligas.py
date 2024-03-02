import requests
import json
import os
from PrettyColorPrinter import add_printer  # Adiciona uma impressora colorida para logs, presumivelmente para debug ou visualização
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

    def format_column(self, data, width=20):
        """Formata os dados de uma coluna para ter largura máxima 'width', adicionando quebras de linha se necessário."""
        if isinstance(data, str):
            return '\n'.join(textwrap.wrap(data, width))
        return data

    def format_df(self, df, col_width=20, title="Tabela de Jogos", custom_headers=None):
        if custom_headers is None:
            custom_headers = {
                'Date': 'Hora',
                'R': 'G x G',
                '-': 'Resultado'
            }

        formatted_str = title + ":\n"
        table_width = col_width * len(df.columns) + (len(df.columns) - 1) * 3  # 3 espaços para " | "
        formatted_str += "-" * table_width + "\n"

        # Usando cabeçalhos personalizados se fornecidos
        col_header = " | ".join([custom_headers.get(col, col).center(col_width) for col in df.columns])
        formatted_str += col_header + "\n"
        formatted_str += "-" * table_width + "\n"

        for _, row in df.iterrows():
            formatted_row = " | ".join([str(cell).center(col_width) for cell in row])
            formatted_str += formatted_row + "\n"

        formatted_str += "-" * table_width + "\n"
        return formatted_str

    def retorna_partidas(self, league_url, tabulated=True):
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
            titles = ["Tabela de jogos passados", "Tabela de próximos jogos"]

            for i, df in enumerate(df_list):
                # Alterar os cabeçalhos conforme especificado
                df.rename(columns={'Date': 'Hora', 'R': 'G x G', '-': 'Resultado'}, inplace=True)

                title = titles[i] if i < len(titles) else f"Tabela {i}"
                if tabulated:
                    # Utilizar tabulate para formatar a tabela
                    table_str = tabulate(df, headers='keys', tablefmt='psql', showindex=False)
                else:
                    table_str = df.to_string(index=False, max_colwidth=50)
                result_str += f'{title}:\n{table_str}\n\n'
        else:
            result_str += 'Falha ao baixar a página. Código de status: ' + str(response.status_code) + '\n'

        return result_str




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

    def responder(self, resposta, chat_id):  # Método para enviar a resposta ao usuário
        link_de_envio = f'{self.url_base}sendMessage?chat_id={chat_id}&text={resposta}'  # Formata a URL para enviar a mensagem
        requests.get(link_de_envio)  # Faz a requisição para enviar a mensagem

# Cria uma instância da classe TelegramBot e inicia o bot
bot = TelegramBot()
bot.Iniciar()