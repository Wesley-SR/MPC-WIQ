import pandas as pd
import numpy as np

# Carregar o arquivo CSV
# Suponha que o arquivo CSV tenha uma coluna chamada 'potencia_ativa'
# Certifique-se de ajustar o nome da coluna de acordo com seu conjunto de dados
dados = pd.read_csv('Dados_PV_15_min_1ano.csv')

# Criar uma coluna de timestamp com intervalos de 15 minutos
intervalo_tempo = pd.date_range(start='2024-01-01', periods=len(dados), freq='15T')
dados['timestamp'] = intervalo_tempo

# Reorganizar as colunas para ter 'timestamp' na primeira posição
dados = dados[['timestamp', 'potencia_PV']]

# Salvar o DataFrame de volta como um novo arquivo CSV, se desejar
dados.to_csv('Dados_PV_15_min_1ano_timestamp.csv', index=False)
