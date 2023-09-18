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

    def __init__(self, Datas):
        self.Datas = Datas
        
        # Weightings for objective function
        self.K_PV_REF = 0.05
        self.WEIGHTING_DELTA_BAT = 0.45
        self.WEIGHTING_REF_BAT = 0.45
        self.WEIGHTING_REF_SC =0.45
        
        # Optimization variables
        self.p_bat = cp.Variable(self.Np_3th)
        self.soc_bat = cp.Variable(self.Np_3th)
        self.p_grid = cp.Variable(self.Np_3th)
        self.soc_bat = cp.Variable(self.Np_3th)





    def islanded_optimization_3th(self):
        # Simula a otimização terciária
        print("Otimização terciária da classe OptimizationQP...")
        return [[1, 2], [3, 4], [5, 6]]






    def islanded_optimization_2th(self):
        # Simula a otimização secundária
        print("Otimização secundária da classe OptimizationQP...")
        return [[10, 20], [30, 40], [50, 60]]






    def connected_optimization_3th(self):
        
        # Problema de otimização
        objective = cp.Minimize(cp.sum_squares(self.p_grid) + cp.sum_squares(self.p_bat))
        constraints = []
        
        for t in time_steps:

            # Balanço de potência
            constraints.append(self.Datas.I_3th[t, 'pv_forecast'] + self.p_bat[t] + self.p_grid[t] + self.Datas.I_3th[t, 'load_forecast'] == 0)

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
 
 
 
 
 
 
    def connected_optimization_2th(self):
        # Simula a otimização secundária
        print("Otimização secundária da classe OptimizationQP...")
        return [[10, 20], [30, 40], [50, 60]]
