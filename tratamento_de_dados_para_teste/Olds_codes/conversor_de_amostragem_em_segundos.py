# Importar bibliotecas
import pandas as pd
import numpy as np

# Nome do arquivo CSV de entrada e saída
arquivo_entrada = "PV_15_min.csv"
arquivo_saida = "PV_1_sec.csv"

# Carregar o arquivo CSV original em um DataFrame
df_original = pd.read_csv(arquivo_entrada)

# Intervalo de amostragem desejado em segundos
intervalo_amostragem_desejado = 1  # Altere para o intervalo desejado em segundos

# Converter a coluna de tempo para um objeto de data e hora
df_original['time'] = pd.to_datetime(df_original['time'])

# Definir o período de amostragem original em segundos
periodo_amostragem_original = (df_original['time'].iloc[1] - df_original['time'].iloc[0]).total_seconds()
print("periodo_amostragem_original = {}".format(periodo_amostragem_original))

# Calcular o fator de escala para a interpolação
fator_escala = int(intervalo_amostragem_desejado / periodo_amostragem_original)
print("fator_escala = {}".format(fator_escala))

# Criar uma lista de DataFrames com o período de amostragem desejado
novo_dfs = []
for index, row in df_original.iterrows():
    novo_dfs.append({'time': row['time'], 'data': row['data']})
    for i in range(1, fator_escala):
        novo_tempo = row['time'] + pd.Timedelta(seconds=i * periodo_amostragem_original)
        novo_dfs.append({'time': novo_tempo, 'data': np.nan})

# Concatenar os DataFrames em um novo DataFrame
novo_df = pd.DataFrame(novo_dfs)

# Interpolar os valores usando interpolação linear
novo_df['data'] = novo_df['data'].interpolate(method='linear')

# Salvar o DataFrame interpolado em um novo arquivo CSV
novo_df.to_csv(arquivo_saida, index=False)
