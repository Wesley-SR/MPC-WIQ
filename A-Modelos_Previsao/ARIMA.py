# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 15:50:37 2023

@author: L08652

ARIMA
AR: Autoregression
I: Integrated
MA: moving Average


AIMA(p,d,q)
p: Núumero de lags que devem ser incluídos no modelo.
d: Número de vezes que as observações serão diferenciadas.
q: Tamanho de uma janela de média móvel ou ordem da média móvel.
"""

import pandas as pd
import pandas.util.testing as tm

import warnings

from matplotlib import pyplot
from pandas.plotting import autocorrelation_plot

import pandas.util.testing as tm
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf

from statsmodels.tsa.arima.model import ARIMA

from pandas import DataFrame

from numpy import sqrt
from sklearn.metrics import mean_squared_error


# elimina os warnings das bibliotecas

warnings.filterwarnings("ignore")

original_series = pd.read_csv('Dados_PV_15_min_1ano.csv')
series = original_series.loc[1:7*96]

# autocorelation plot
# autocorrelation_plot(series)
# pyplot.savefig('books_read.png')


# Plot autocorrelation from statsmodel
plot_acf(series, lags=96)
pyplot.show()
     
# Treina com todos os dados, sem separar treino de teste
model = ARIMA(series, order=(7,1,1))
model_fit = model.fit()


# summary 
print(model_fit.summary())

# plot residuais
residuals = DataFrame(model_fit.resid)
residuals.plot()
pyplot.show()

# gráficos de densidade dos residuais
residuals.plot(kind='kde')
pyplot.show()

# estatística descritiva dos residuos
print(residuals.describe())


''' PREVENDO OS DADOS COM ARIMA UTILIZANDO WALK FORWARD'''
# a variável X recebe os dados da série
X = series.values
X = X.astype('float32')

# Separa os dados com 50% dos dados para treino e 50% dos dados para teste
size = int(len(X) * 0.50)

# Separa dados de treino e teste
train = X[0:size]
test =  X[size:]
     

# cria a variável history
history = [x for x in train]
     

# cria lista de previsões
predictions = list()
     

# Cria a função que faz a diferenciação
def difference(dataset, interval=1):
  diff = list() 
  for i in range(interval, len(dataset)):
    value = dataset[i] - dataset[i - interval]
    diff.append(value)
  return diff

# cria função que reverte o valor diferenciado para o original
def inverse_difference(history, previsao, interval=1):
  return previsao + history[-interval]
     



''' inicia Walk-Forward '''
for t in range(len(test)):
  
    # difference data
    meses_no_ano = 96
    diff = difference(history, meses_no_ano)
    
    # cria um modelo ARIMA com os dados de history
    model = ARIMA(diff, order=(0,0,1))
    
    # treina o modelo ARIMA
    # model_fit = model.fit( trend='nc', disp=0)
    model_fit = model.fit()
    
    # a variável valor_predito recebe o valor previsto pelo modelo
    valor_predito = model_fit.forecast()[0]
    
    # valor_predito recebe o valor revertido (escala original)
    valor_predito = inverse_difference(history, valor_predito, meses_no_ano)
     
    # adiciona o valor predito na lista de predicões
    predictions.append(valor_predito)
    
    # a variável valor_real recebe o valor real do teste
    valor_real = test[t]
    
    # adiciona o valor real a variável history
    history.append(valor_real)
    
    # imprime valor predito e valor real
    print('Valor predito=%.3f, Valor esperado=%3.f' % (valor_predito, valor_real))


# Avaliando os resultados
rmse = sqrt(mean_squared_error(test, predictions))
print('Test RMSE: %.3f' % rmse)
     
# Test RMSE: 785.401

# plot forecasts against actual outcomes 
pyplot.plot(test)
pyplot.plot(predictions, color='red')
pyplot.show()