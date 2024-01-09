import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import timedelta
import matplotlib.pyplot as plt

def treinar_modelo_arimax(dados_treino):
    # Criar features adicionais, como hora do dia
    dados_treino['HoraDoDia'] = dados_treino.index.hour

    # Treinar modelo ARIMAX
    modelo_arimax = SARIMAX(dados_treino['potencia_PV'], exog=dados_treino['HoraDoDia'], order=(1, 1, 1), seasonal_order=(0, 0, 0, 0))
    modelo_arimax_treinado = modelo_arimax.fit(disp=False)

    return modelo_arimax_treinado

def prever_proximo_dia(modelo, entrada_teste):
    entrada_teste['HoraDoDia'] = entrada_teste.index.hour
    previsao_arimax = modelo.get_forecast(steps=len(entrada_teste), exog=entrada_teste['HoraDoDia']).predicted_mean

    return previsao_arimax

# Carregar o arquivo CSV
# Suponha que o arquivo CSV tenha colunas 'timestamp' e 'potencia_PV'
# Certifique-se de ajustar o nome das colunas de acordo com seu conjunto de dados
dados = pd.read_csv('Dados_PV_15_min_1ano_timestamp.csv')
dados['timestamp'] = pd.to_datetime(dados['timestamp'])
dados = dados.set_index('timestamp')

# Definir o período de treino
periodo_treino = pd.date_range(start='2024-01-01', end='2024-08-01')  # Ajuste conforme necessário

# Filtrar dados de treino
dados_treino = dados.loc[periodo_treino]

# Treinar o modelo inicial
modelo_arimax_treinado = treinar_modelo_arimax(dados_treino)

# Selecionar um dia para entrada de teste
dia_teste = '2024-08-02'  # Ajuste conforme necessário
entrada_teste = dados.loc[dia_teste]

# Fazer previsões para o próximo dia
previsao_proximo_dia = prever_proximo_dia(modelo_arimax_treinado, entrada_teste)

# Imprimir a previsão
print("Previsão para o próximo dia:")
print(previsao_proximo_dia)

# Plotar resultados
plt.figure(figsize=(12, 6))
plt.plot(dados_treino.index, dados_treino['potencia_PV'], label='Treino', color='blue')
plt.plot(entrada_teste.index, entrada_teste['potencia_PV'], label='Real - Dia de Teste', color='green')
plt.plot(entrada_teste.index, previsao_proximo_dia, label='Previsto - Dia de Teste', linestyle='dashed', color='orange')
plt.xlabel('Tempo')
plt.ylabel('Potência Ativa')
plt.title('Previsão ARIMAX para o Próximo Dia')
plt.legend()
plt.show()