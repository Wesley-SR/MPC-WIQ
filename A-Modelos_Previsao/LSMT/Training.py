# Video that I used to build this code:
# https://www.youtube.com/watch?v=c0k-YLQGKjY


import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import *
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.metrics import RootMeanSquaredError
from tensorflow.keras.optimizers import Adam

# Function to convert dataframe to X and y
def df_to_X_y(df, window_size):
    df_as_np = df.to_numpy()
    X = []
    y = []
    for i in range(len(df_as_np)-window_size):
        row = [[a] for a in df_as_np[i:i+window_size]]
        X.append(row)
        label = df_as_np[i+window_size]
        y.append(label)
    return np.array(X), np.array(y)

# Read data
''' PV '''
# path = "A-Modelos_Previsao\LSMT\Dados_PV_15_min_1ano_timestamp.csv" # VS CODE
path = "Dados_PV_15_min_1ano_timestamp.csv" # Spyder

''' Load '''
# path = "A-Modelos_Previsao\LSMT\Dados_load_15_min_1ano_timestamp.csv" # VS CODE
# path = "Dados_load_15_min_1ano_timestamp.csv" # Spyder



df = pd.read_csv(path)
df.index = pd.to_datetime(df['timestamp'])

# Prepare data
''' PV '''
power = df['p_pv']

''' Load '''
#power = df['p_load']


WINDOW_SIZE = 5
X, y = df_to_X_y(power, WINDOW_SIZE)
X_train, y_train = X[:25000], y[:25000]
X_val, y_val = X[25000:30000], y[25000:30000]

# Define model architecture
model = Sequential()
model.add(InputLayer((WINDOW_SIZE, 1)))
model.add(LSTM(64))
model.add(Dense(8, activation='relu'))
model.add(Dense(1, activation='linear'))

# Compile the model
model.compile(loss=MeanSquaredError(), optimizer=Adam(learning_rate=0.0001), metrics=[RootMeanSquaredError()])

# Train the model in VS code
# model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=10, callbacks=[ModelCheckpoint('A-Modelos_Previsao/LSMT/PV_model/', save_best_only=True)])

# Train the model in Spyder
model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=10, callbacks=[ModelCheckpoint('./PV_model/', save_best_only=True)])
# model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=10, callbacks=[ModelCheckpoint('/Load_model/', save_best_only=True)])
