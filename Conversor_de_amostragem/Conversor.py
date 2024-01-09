# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 16:12:18 2023

@author: Wesley
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Nome para arquivos e camiho
arquivo = "Carga_5min"
novo_arquivo = "Carga_30sec"
caminho = "" # Por a barra "/" no caminho

df_original = pd.read_csv("{}{}.csv".format(caminho,arquivo))

# Os dados originais estão em horas, minutos ou segundo?
original_esta_em_horas = 0
original_esta_em_minutos = 1
original_esta_em_segundos = 0

# Intervalo de amostragem desejado em segundos
ts_segundos_desejado = 30

if original_esta_em_minutos:

    # Extrair as colunas "hora" e "PV" do DataFrame original
    hora_original = df_original['time']
    dados_original = df_original['data']
    
    # Converter as horas para segundos
    vetor_minuto_antigo = [int(hora.split(':')[0]) * 60 + int(hora.split(':')[1]) for hora in hora_original]
    vetor_segundo_antigo = [(minuto * 60) for minuto in vetor_minuto_antigo]

    # Criar matriz de tempo com intervalo da amostragem nova
    novo_tempo_segundos = np.arange(vetor_segundo_antigo[0], 
                           vetor_segundo_antigo[-1] + ts_segundos_desejado,
                           ts_segundos_desejado)

    # Interpolar os valores usando interpolação linear
    dados_novos = np.interp(novo_tempo_segundos, vetor_segundo_antigo, dados_original)

    # Converter os minutos de volta para o formato de hora
    novo_hora = [f"{segundos // 3600:02d}:{(segundos % 3600) // 60:02d}:{(segundos % 3600) % 60:02d}" for segundos in novo_tempo_segundos]

    # Criar um novo DataFrame com os dados interpolados
    df_interp = pd.DataFrame({'time': novo_hora, 'data': dados_novos})
    
    # Salvar o DataFrame interpolado em um novo arquivo CSV
    df_interp.to_csv("{}{}.csv".format(caminho,novo_arquivo), index=False)


# Plotar o gráfico de linha
plt.plot(df_interp['data'])
plt.xlabel('Time')
plt.ylabel('Data')
plt.title('Gráfico de Linha')
plt.grid(True)
plt.show()