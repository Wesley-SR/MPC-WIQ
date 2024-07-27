import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt

# Function to convert dataframe to X and y
def df_to_X_y(df, window_size=5):
    df_as_np = df.to_numpy()
    X = []
    y = []
    for i in range(len(df_as_np)-window_size):
        row = [[a] for a in df_as_np[i:i+window_size]]
        X.append(row)
        label = df_as_np[i+window_size]
        y.append(label)
    return np.array(X), np.array(y)

# Get previous data
df = pd.read_csv("A-Modelos_Previsao\LSMT\\test_new.csv")
df.index = pd.to_datetime(df['timestamp'])

# 
power = df['potencia_PV']
WINDOW_SIZE = 5
X, y = df_to_X_y(power, WINDOW_SIZE)
X_test, y_test = X[0:96], y[0:96]

# Load trained model
model = load_model('A-Modelos_Previsao/LSMT/PV_model/')

# Make predictions
# X is the previous data. That is, yesterday's data.
predictions = model.predict(X_test).flatten()

# Plot predictions vs actuals
plt.plot(predictions[:300], color='blue', label='Predictions')
plt.plot(y_test[:300], color='red', label='Actuals')
plt.legend()
plt.show()
