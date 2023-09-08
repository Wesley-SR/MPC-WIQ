# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 18:23:10 2023

@author: Wesley
"""

import cvxpy as cp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time

class QPOptimization:
    
    def __init__(self, constants):
        # Parâmetros da microrrede
        self.ts = constants.loc[0, 'ts']
        self.Np = constants.loc[0, 'Np']
        self.time_steps = list(range(Np))

        self.q_bat = constants.loc[0, 'q_bat']
        self.p_bat_max = constants.loc[0, 'p_bat_max']
        self.soc_bat_max = constants.loc[0, 'soc_bat_max']
        self.soc_bat_min = constants.loc[0, 'soc_bat_min']
        self.soc_bat_ini = constants.loc[0, 'soc_bat_ini']
        
        # Variáveis de otimização
        self.p_bat = cp.Variable(Np)
        self.soc_bat = cp.Variable(Np)
        self.p_grid = cp.Variable(Np)
    
    def islanded_tertiary_optimization(self, data):
        # Simula a otimização terciária
        print("Otimização terciária da classe OptimizationQP...")
        return [[1, 2], [3, 4], [5, 6]]

    def islanded_secondary_optimization(self, data):
        # Simula a otimização secundária
        print("Otimização secundária da classe OptimizationQP...")
        return [[10, 20], [30, 40], [50, 60]]

    def connected_tertiary_optimization(self, data):
        # Simula a otimização terciária
        print("Otimização terciária da classe OptimizationQP...")
        return [[1, 2], [3, 4], [5, 6]]
 
    def connected_secondary_optimization(self, data):
        # Simula a otimização secundária
        print("Otimização secundária da classe OptimizationQP...")
        return [[10, 20], [30, 40], [50, 60]]
