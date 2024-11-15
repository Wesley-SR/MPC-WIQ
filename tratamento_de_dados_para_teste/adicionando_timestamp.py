import pandas as pd
import numpy as np

# Carregar o arquivo CSV
# Suponha que o arquivo CSV tenha uma coluna chamada 'data'
# Certifique-se de ajustar o nome da coluna de acordo com seu conjunto de dados
dados = pd.read_csv('p_pv_5_min_SNPTEE.csv')

# Criar uma coluna de timestamp com intervalos de x minutos
x = 5
intervalo_tempo = pd.date_range(start='2024-01-01', periods=len(dados), freq='{}min'.format(x))
dados['time'] = intervalo_tempo

# Reorganizar as colunas para ter 'timestamp' na primeira posição
dados = dados[['time', 'data']]

# Salvar o DataFrame de volta como um novo arquivo CSV, se desejar
dados.to_csv('p_pv_5_min_SNPTEE.csv', index=False)
