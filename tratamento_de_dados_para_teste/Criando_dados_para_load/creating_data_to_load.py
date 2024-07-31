# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 12:36:40 2024

@author: Wesley
"""


import pandas as pd
import numpy as np

caminho = ""  # Por a barra "/" no caminho
arquivo = "load_900_sec"

# Gerando um dataframe de exemplo com 96 linhas (dados de um dia)
np.random.seed(0)  # Para reprodutibilidade

# Ler o arquivo original com a coluna de tempo como timestamp e definir como índice
df = pd.read_csv("{}{}.csv".format(caminho, arquivo), parse_dates=['time'], index_col='time')

# Função para gerar dados de um ano adicionando ruído
def gerar_dados_ano(df, seed=0):
    np.random.seed(seed)
    # Repetir os dados para 365 dias
    df_ano = pd.concat([df]*365, ignore_index=True)
    
    # Adicionar ruído para variação diária
    ruido_diario = np.random.normal(0, 0.5, size=len(df_ano))
    df_ano['data'] = df_ano['data'] + ruido_diario
    
    
    # Ajustar o índice de tempo para cobrir um ano e definir como índice
    df_ano['time'] = pd.date_range(start='2023-01-01', periods=len(df_ano), freq='15T')
    df_ano.set_index('time', inplace=True)
    

    
    return df_ano

# Gerar os dados de um ano
df_ano = gerar_dados_ano(df)

# Exibir as primeiras linhas do dataframe resultante
#print(df_ano.head())

df_ano.to_csv("load.csv", index=True)

