# -*- coding: utf-8 -*-
"""
Created on 20240728

@author: Wesley Rodrigues
"""

import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
import time

# Function to convert dataframe to arrays of float with shape (lenght, window, 1)
def df_to_array(df, window_size=5):
    df_as_np = df.to_numpy()
    X = []
    # y = []
    for i in range(len(df_as_np)-window_size):
        row = [[a] for a in df_as_np[i:i+window_size]]
        X.append(row)
        label = df_as_np[i+window_size]
        # y.append(label)
    return np.array(X) #, np.array(y)



class ForecastingModel:
    def __init__(self, path_pv, path_load):
        
        self.pv_model = load_model(f'{path_load}/')
        self.load_model = load_model(f'{path_pv}/')
        
        print("Initialized forecast models \n")
        
    def predict_pv(self, past):
        x = df_to_array(past)
        return self.load_model.predict(x).flatten()
    
    def predict_load(self, past):
        x = df_to_array(past)
        return self.load_model.predict(x).flatten()  