# converter_timestamp
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 07:27:00 2024

@author: Wesley
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

IS_PV = 0
IS_LOAD = 1

dado_a_ser_tratado = IS_PV

# Intervalo de amostragem desejado em segundos
ts_segundos_desejado = 1

# Nome para arquivos e caminho
arquivo = "p_pv_1_s_SNPTEE" # Caminho do arquivo base
caminho = ""  # Por a barra "/" no caminho. Deixe vazio se estive na mesma pasta
novo_arquivo = "p_pv_1_s_SNPTEE_com_ruido" # Nome pro novo arquivo

# Ler o arquivo original com a coluna de tempo como timestamp e definir como índice
df_original = pd.read_csv("{}{}.csv".format(caminho, arquivo), parse_dates=['time'], index_col='time')
data_com_ruido = df_original.copy()

# Gerar intervalos aleatórios entre 50 e 800 segundos
# Vamos gerar ruído em intervalos de tempo aleatórios
intervalos_ruido = np.random.randint(50, 800, size=len(df_original) // 200)

# Índices onde o ruído será aplicado
indices_com_ruido = np.random.choice(df_original.index, size=len(intervalos_ruido), replace=False)

# Adicionar o ruído somente nos intervalos definidos
desvio_padrao = 0.06
ruido_min = 0.001
for indice in indices_com_ruido:
    ruido = np.random.normal(0, desvio_padrao)  # Ruído com média 0 e desvio padrão 0.02
    if (abs(ruido) > ruido_min):
        data_com_ruido.at[indice, 'data'] += ruido  # Adiciona ruído ao valor correspondente

diferenca = 0
for index, row in df_original.iterrows():
    if (data_com_ruido.at[index, 'data'] >= df_original.at[index, 'data'] + ruido_min) or (data_com_ruido.at[index, 'data'] <= df_original.at[index, 'data'] - ruido_min) :
        diferenca = data_com_ruido.at[index, 'data'] - df_original.at[index, 'data']
    else:
        # print(f"{data_com_ruido.at[index, 'data']} to {data_com_ruido.at[index, 'data']} + {diferenca} = {data_com_ruido.at[index, 'data'] + diferenca}")
        data_com_ruido.at[index, 'data'] = data_com_ruido.at[index, 'data'] + diferenca
    
    if dado_a_ser_tratado == IS_PV:
        if df_original.at[index, 'data'] >= 0 and df_original.at[index, 'data'] <= 0.01:
            data_com_ruido.at[index, 'data'] = 0
        
        if df_original.at[index, 'data'] < 0 or data_com_ruido.at[index, 'data'] < 0:
            df_original.at[index, 'data'] = 0
            data_com_ruido.at[index, 'data'] = 0


# Fazendo com que os dados do vetor com ruído sejam identico aos dados originais 
# para intervalos de 100 segundos antes e 100 segundos depois de multiplos de 900 segundos
# Dessa forma, a medida do terciário (a cada 15 min = 900 s) será identica a medida do secundário nesse mesmo instante
contador = 0
resto_divisoes = pd.DataFrame({'data': [0.0]*len(df_original)})
for index, row in df_original.iterrows():
    resto = contador%900
    resto_divisoes.loc[contador, 'data'] = resto
    if resto < 100 or resto > 800:
        data_com_ruido.at[index, 'data'] = df_original.at[index, 'data']
    contador += 1


# Salvar o DataFrame interpolado em um novo arquivo CSV
data_com_ruido.to_csv("{}{}.csv".format(caminho, novo_arquivo), index=True)

print(f"tamanho do original: {len(df_original)}")
print(f"tamanho com ruido: {len(data_com_ruido)}")

# Plotar o gráfico de linha
plt.figure(figsize=(10, 5))
plt.plot(data_com_ruido['data'], label = 'com ruido', linewidth = 0.5)
plt.plot(df_original['data'], label = 'original')
plt.xlabel('Time')
plt.ylabel('Data')
plt.title('Gráfico de Linha')
plt.grid(True)

# Plot para entender como funciona o resto da divisão e identificar em volta do 900 s
# plt.figure(figsize=(10, 5))
# plt.plot(resto_divisoes['data'])

plt.show()