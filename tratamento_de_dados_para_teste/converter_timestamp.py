# converter_timestamp
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 16:12:18 2023

@author: Wesley
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Intervalo de amostragem desejado em segundos
ts_segundos_desejado = 1

# Nome para arquivos e caminho
arquivo = "load_5_min"
novo_arquivo = "load_{}_sec".format(ts_segundos_desejado)
caminho = ""  # Por a barra "/" no caminho

# Ler o arquivo original com a coluna de tempo como timestamp e definir como índice
df_original = pd.read_csv("{}{}.csv".format(caminho, arquivo), parse_dates=['time'], index_col='time')

# Criar um novo DataFrame com o intervalo desejado
df_resampled = df_original.resample('{}s'.format(ts_segundos_desejado)).interpolate()

# Resetar o índice antes de salvar o arquivo, se necessário
df_resampled = df_resampled.reset_index()

# Salvar o DataFrame interpolado em um novo arquivo CSV
df_resampled.to_csv("{}{}.csv".format(caminho, novo_arquivo), index=False)

# Plotar o gráfico de linha
plt.plot(df_resampled['data'])
plt.xlabel('Time')
plt.ylabel('Data')
plt.title('Gráfico de Linha')
plt.grid(True)
plt.show()