import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
import time






# Function to convert dataframe to arrays of float with shape (lenght, window, 1)
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




# With timestamp as a index
# df = pd.read_csv("test_new.csv", index_col='timestamp')

# Get previous data
# df = pd.read_csv("A-Modelos_Previsao\LSMT\\test_new.csv") # VS code
df = pd.read_csv("test_load.csv") # Spyder

#df = pd.read_csv("test_new.csv")
# df.index = pd.to_datetime(df['timestamp'])

# 
power = df['potencia_load']
WINDOW_SIZE = 5
start_time = time.time()
X, y = df_to_X_y(power, WINDOW_SIZE)
X_test, y_test = X[0:96], y[0:96]
end_time = time.time()
execution_time = end_time - start_time
print(f"convert_time: {execution_time}")

# Load trained model
# model = load_model('A-Modelos_Previsao/LSMT/PV_model/')  # VS code
model = load_model('Load_model/') # Spyder






''' Run a time '''
# Make predictions
# X is the previous data. That is, yesterday's data.
# start_time = time.time()
# predictions = model.predict(X_test).flatten()

# end_time = time.time()
# execution_time = end_time - start_time
# print(f"execution_time: {execution_time}")

# Plot predictions vs actuals
# plt.plot(predictions[:96], color='blue', label='Predictions')
# plt.plot(y_test[:96], color='red', label='Actuals')
# plt.legend()
# plt.show()





''' Run in loop '''
# begin = 53
# day_after = 96
# for i in range (1):
    
#     # Prepare the test data
#     X_test, y_test = X[begin + i : begin + i + 96], y[begin + i + day_after: begin + i + 96 + day_after]
    
#     # Predict
#     predictions = model.predict(X_test).flatten()
    
#     # Create a new figure for each iteration
#     plt.figure()
#     plt.plot(predictions[:96], label='Predictions')
#     plt.plot(y_test[:96], label='Actuals')
    
#     # Add legend
#     plt.legend()
#     # Plot
#     plt.show()


begin = 53
day_after = 0
figures = []  # List to store figure objects

for i in range(10):  # Changed to 10 iterations for the sake of example
    # Prepare the test data
    X_test, y_test = X[begin + i : begin + i + 96], y[begin + i + day_after: begin + i + 96 + day_after]
    
    # Predict
    predictions = model.predict(X_test).flatten()
    
    # Create a new figure for each iteration
    fig, ax = plt.subplots()
    figures.append(fig)
    
    # Plot predictions and actual values
    ax.plot(predictions[:96], label='Predictions')
    ax.plot(y_test[:96], label='Actuals')
    
    # Add legend
    ax.legend()
    
    # Show the plot
    plt.show()

# Now 'figures' list contains all the figure objects
 