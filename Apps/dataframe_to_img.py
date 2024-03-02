import dataframe_image as dfi
import pandas as pd

def df_to_image(file, league_name):

    df = pd.read_excel(f'{file}')

    # Salvar o DataFrame como uma imagem
    dfi.export(df, f'{league_name}.png')
