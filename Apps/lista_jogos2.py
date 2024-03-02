from PrettyColorPrinter import add_printer
import pandas as pd
import requests
from time import sleep
from datetime import datetime
import dataframe_image as dfi
import re
import openpyxl

# It's unclear what the add_printer function does without its definition.
# If it's crucial for your code, ensure it's correctly implemented.
add_printer(1)

# Use consistent naming conventions (e.g., snake_case for variables and functions in Python).

API_TOKEN = '6119477838:AAHFH9P6rMM7wUuKVn_Pz9upU3WEIFUFsnc'
last_update_id = None


def abreviar_times(texto):
    texto = re.sub(r'\(Esports\)', '', texto)  # Remove "(Esports)"

    # Regex para encontrar palavras fora dos parênteses
    regex = re.compile(r'(?<!\(\w)(\b\w+\b)(?!\w*\))')

    def abreviar(match):
        palavra = match.group(0)
        # Abreviar palavras com mais de 6 letras para as primeiras 3 letras seguidas de um ponto
        return (palavra[:3] + '.') if len(palavra) > 6 else palavra

    # Substituir no texto os nomes dos times pela versão abreviada
    return regex.sub(abreviar, texto)

import pandas as pd
import re

# Define the function to format the time strings
def formatar_hora(hora_str):
    # Verifica se hora_str é uma string
    if isinstance(hora_str, str):
        # Esta expressão regular tenta capturar ambos os formatos
        match = re.match(r'(\d{2})\'|(\d{2}/\d{2}\s+\d{2}:\d{2})', hora_str)
        if match:
            # Se o formato for 'XX'', retorna como está
            if match.group(1):
                return match.group(1) + "'"
            # Se o formato for 'MM/DD HH:MM', retorna apenas a parte da hora
            elif match.group(2):
                return match.group(2)[-5:]  # Retorna os últimos 5 caracteres, que seriam 'HH:MM'
    return None  # Retorna None se nenhum formato corresponder

# # Create a sample dataframe to simulate the user's data
data = {
    'Hora': ["06'", "05'", "02/21 21:30", "02/21 21:30", "02/21 22:00",
             "02/21 22:15", "02/21 22:30", "02/21 22:45", "02/21 23:15",
             "02/21 23:30", "02/21 23:45", "02/22 00:00"],
    'Casa vs Visitante': ["Netherlands (Felix) vs Spain (Obelix)", "Belgium (Cleo) vs Portugal (Iron)",
                          "Croatia (Liam) vs Portugal (Iron)", "Belgium (Cleo) vs Spain (Obelix)",
                          "PSG (Felix) vs Barcelona (Iron)", "Bayern (Cleo) vs PSG (Felix)",
                          "Real Madrid (Liam) vs PSG (Felix)", "Nautico Capibaribe Women vs PSG (Felix)",
                          "Barcelona (Iron) vs PSG (Felix)", "PSG (Felix) vs Bayern (Cleo)",
                          "PSG (Felix) vs Real Madrid (Liam)", "PSG (Felix) vs Man City (Obelix)"],
    'GxG': ["2-1", "1-1", "View", "View", "View", "View", "View", "View", "View", "View", "View", "View"]
}

df = pd.DataFrame(data)
print (df)
1

def retorna_partidas(league_url):
    print(league_url)
    hoje = datetime.now()
    hoje_str = hoje.strftime("%d-%m-%Y %H-%M-%S")

    # Mapping league names to URLs for readability and maintainability.
    league_names = {
        'https://pt.betsapi.com/l/23118/Esoccer-GT-Leagues--12-mins-play': 'E-Soccer Liga GT - 12 minutos',
        'https://betsapi.com/l/33440/Esoccer-Adriatic-League--10-mins-play': 'E-Soccer Liga Adriatic - 10 minutos',
        'https://pt.betsapi.com/l/22614/Esoccer-Battle--8-mins-play': 'E-Soccer Liga Battle - 8 minutos'
    }

    #every key valeu from itens from the dictionary league_names
    for key, value in league_names.items():
        print("se_liga")




    df_return = []
    # Determine the league name based on the URL.
    league_name = league_names.get(league_url, 'Unknown League')
    page_name = f'{league_name}_{hoje_str}.html'

    response = requests.get(league_url)
    response_content = response.content

    # Check if the request was successful (HTTP status code 200).
    if response.status_code == 200:
        df_list = pd.read_html(response_content, attrs={'class': 'table'})
        #print(df_list)
        if len(df_list) >= 2:
            for i, table in enumerate(df_list):

                table.rename(columns={'Date': 'Hora', '-': 'GxG', 'Home vs Away': 'Casa vs Visitante'}, inplace=True)
                if 'R' in table.columns:
                    table = table.drop(columns=['R'])
                if 'Casa vs Visitante' in table.columns:
                    table['Casa vs Visitante'] = table['Casa vs Visitante'].str.replace('Esports', '', case=False, regex=True)
                if 'Hora' in table.columns:
                    table['Hora'] = table['Hora'].apply(formatar_hora)

                table.reset_index(drop=True, inplace=True)

                print(f"Tabela {i}:")
                df_return.append(table)
                #print(add_printer(table))
                print(table, '\n')  # Print each table

                if i == 0:
                    table.to_excel(f'TABELA-{i}{value}.xlsx',index=False)

                elif i == 1:
                    table.to_excel(f'TABELA-{i}{value}.xlsx',index=False)

            print(f'{hoje_str} Página capturada com sucesso.')
        elif len(df_list) < 2:
            print("Foi identificado apenas uma tabela.")

    else:
        print('Falha ao baixar a página. Código de status:', response.status_code)


# teste de input para validar retorno
try:
    input_user = int(input(f'Escolha uma das ligas para retornar informação:\n\n [1]-E-Soccer Liga Battle - 8 minutos\n [2]-E-Soccer Liga Adriatic - 10 minutos\n [3]-E-Soccer Liga GT - 12 minutos\n'))
    sleep(1)

    urls = {
        1: 'https://pt.betsapi.com/l/22614/Esoccer-Battle--8-mins-play',
        2: 'https://betsapi.com/l/33440/Esoccer-Adriatic-League--10-mins-play',
        3: 'https://pt.betsapi.com/l/23118/Esoccer-GT-Leagues--12-mins-play'
    }

    league_url = urls.get(input_user)
    print(league_url)
    if league_url:
        retorna_partidas(league_url)
    else:
        print('Por favor, escolha uma das opções corretas.')

except ValueError:
    # This captures cases where the input is not an integer.
    print('Por favor, insira um número válido.')
