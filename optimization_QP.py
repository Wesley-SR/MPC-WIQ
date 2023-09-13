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

class OptimizationQP:

    def __init__(self, constants, Datas):
        self.Datas = Datas
        
        # Parâmetros da microrrede
        self.ts_2th = constants.loc[0, 'ts_2th']
        self.ts_3th = constants.loc[0, 'ts_3th']
        self.Np_2th = constants.loc[0, 'Np_2th']
        self.Np_3th = constants.loc[0, 'Np_3th']

        self.time_steps = list(range(self.Np_3th))

        self.q_bat = constants.loc[0, 'q_bat']
        self.p_bat_max = constants.loc[0, 'p_bat_max']
        self.soc_bat_max = constants.loc[0, 'soc_bat_max']
        self.soc_bat_min = constants.loc[0, 'soc_bat_min']
        
        # Variáveis de otimização
        self.p_bat = cp.Variable(self.Np_3th)
        self.soc_bat = cp.Variable(self.Np_3th)
        self.p_grid = cp.Variable(self.Np_3th)
        self.soc_bat = cp.Variable(self.Np_3th)





    def islanded_tertiary_optimization(self, data):
        # Simula a otimização terciária
        print("Otimização terciária da classe OptimizationQP...")
        return [[1, 2], [3, 4], [5, 6]]






    def islanded_secondary_optimization(self, data):
        # Simula a otimização secundária
        print("Otimização secundária da classe OptimizationQP...")
        return [[10, 20], [30, 40], [50, 60]]






    def connected_tertiary_optimization(self, soc_bat_current, p_pv, p_load):
        
        # Problema de otimização
        objective = cp.Minimize(cp.sum_squares(self.p_grid) + cp.sum_squares(self.p_bat))
        constraints = []
        
        for t in time_steps:

            # Balanço de potência
            constraints.append(p_pv[t] + self.p_bat[t] + self.p_grid[t] + p_load[t] == 0)

            # SOC da bateria
            if t == 0:
                constraints.append(self.Np_3th[t] == soc_bat_current)
            else:
                constraints.append(self.Np_3th[t] == self.Np_3th[t-1] - self.p_bat[t]*self.ts_3th/self.q_bat)
            
            constraints.append(self.Np_3th[t] <= self.soc_bat_max)
            constraints.append(self.Np_3th[t] >= self.soc_bat_min)

        problem = cp.Problem(objective, constraints)
        problem.solve()
        return [[1, 2], [3, 4], [5, 6]]
 
 
 
 
 
 
    def connected_secondary_optimization(self, data):
        # Simula a otimização secundária
        print("Otimização secundária da classe OptimizationQP...")
        return [[10, 20], [30, 40], [50, 60]]
