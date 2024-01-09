import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Suponha que você já tenha um DataFrame chamado df_original com uma coluna de data e uma coluna de valores.
# Certifique-se de que a coluna de data seja do tipo datetime.

# Nome para arquivos e camiho
arquivo = "Carga_30sec"
novo_arquivo = "Carga_20T"
caminho = "" # Por a barra "/" no caminho

df_original = pd.read_csv("{}{}.csv".format(caminho,arquivo))



# Certifique-se de que a coluna de tempo seja do tipo datetime.
df_original['time'] = pd.to_datetime(df_original['time'], format='%H:%M:%S')

# Defina a coluna de tempo como o índice do DataFrame
df_original.set_index('time', inplace=True)

# Calcule a média móvel de 20 minutos
df_20min_avg = df_original.resample('20T').mean()

# Se você deseja manter apenas os registros com valores não nulos na média móvel:
df_20min_avg.dropna(inplace=True)

# Reponha a coluna de tempo como uma coluna no DataFrame resultante
df_20min_avg.reset_index(inplace=True)

# Exiba o DataFrame resultante
print(df_20min_avg)
