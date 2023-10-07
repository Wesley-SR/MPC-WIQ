# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 16:12:18 2023

@author: Wesley
"""

import pandas as pd
import numpy as np

# Nome para arquivos e camiho
arquivo = "Carga_5min"
novo_arquivo = "Carga_nova"
caminho = ""

print("{}{}".format(caminho,arquivo))
df_original = pd.read_csv("{}{}.csv".format(caminho,arquivo))


# Extrair as colunas "hora" e "PV" do DataFrame original
hora_original = df_original['time']
PV_original = df_original['data']

# Intervalo de amostragem desejado
intervalo_amostragem_desejado = 3

# Converter as horas para segundos
hora_minutos = [int(hora.split(':')[0]) * 60 + int(hora.split(':')[1]) for hora in hora_original]

# # Criar matriz de tempo com intervalo da amostragem nova
# novo_tempo = np.arange(hora_minutos[0], hora_minutos[-1] + intervalo_amostragem_desejado, intervalo_amostragem_desejado)

# # Interpolar os valores usando interpolação linear
# novo_PV = np.interp(novo_tempo, hora_minutos, PV_original)

# # Converter os minutos de volta para o formato de hora
# novo_hora = [f"{minutos // 60:02d}:{minutos % 60:02d}" for minutos in novo_tempo]

# # Criar um novo DataFrame com os dados interpolados
# df_interp = pd.DataFrame({'time': novo_hora, 'data': novo_PV})

# # Salvar o DataFrame interpolado em um novo arquivo CSV
# df_interp.to_csv("{}/{}.csv".format(caminho,novo_arquivo), index=False)
