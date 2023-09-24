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
        self.K_PV_REF = 1
        self.WEIGHTING_K_PV = 1
        self.WEIGHTING_DELTA_BAT = 0.45
        self.WEIGHTING_REF_BAT = 0.45
        self.WEIGHTING_REF_SC =0.45
        



    def islanded_optimization_3th(self):
        
        print("Islanded Optimization in 3th")
        
        # Optimization variables
        p_bat = cp.Variable(self.Datas.NP_3TH)
        soc_bat = cp.Variable(self.Datas.NP_3TH)
        k_pv = cp.Variable(self.Datas.NP_3TH)
        
        
        # Optimization problem
        objective = cp.Minimize(cp.sum_squares(k_pv - self.K_PV_REF)*self.WEIGHTING_K_PV +
                                cp.sum_squares(p_bat))
        constraints = []
        
        # MPC LOOP
        for t in range(0, self.Datas.NP_3TH):

            # Power balance
            constraints.append(self.Datas.I_3th.loc[t, 'pv_forecast'] + p_bat[t] + self.Datas.I_3th.loc[t, 'load_forecast'] == 0)
            # TODO: Insert variable k_pv

            # Battery SOC
            if t == 0:
                constraints.append(soc_bat[t] == self.Datas.soc_bat) # Now
            else:
                constraints.append(soc_bat[t] == soc_bat[t-1] - p_bat[t-1]*self.Datas.TS_3TH/self.Datas.Q_BAT)
            
            # Technical constrains
            constraints.append(soc_bat[t] >= self.Datas.SOC_BAT_MIN)
            constraints.append(soc_bat[t] <= self.Datas.SOC_BAT_MAX)
            constraints.append(p_bat[t] >= self.Datas.P_BAT_MIN)
            constraints.append(p_bat[t] <= self.Datas.P_BAT_MAX)
            constraints.append(k_pv[t] >= 0)
            constraints.append(k_pv[t] <= 1)
            

      

        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS)
        
        # Optimization Result
        for i in range(0, self.Datas.NP_3TH):
            self.Datas.R_3th.loc[i, 'p_bat_3th'] = p_bat.value[i]
            self.Datas.R_3th.loc[i, 'p_grid_3th'] = 0
            self.Datas.R_3th.loc[i, 'soc_bat_3th'] = soc_bat.value[i]
            self.Datas.R_3th.loc[i, 'k_pv_3th'] = k_pv.value[i]
        
        self.Datas.R_3th.loc[0, 'FO'] = problem.value






    def connected_optimization_3th(self):
        
        # Optimization variables
        p_bat = cp.Variable(self.Datas.NP_3TH)
        soc_bat = cp.Variable(self.Datas.NP_3TH)
        p_grid = cp.Variable(self.Datas.NP_3TH)
        
        # Optimization problem
        objective = cp.Minimize(cp.sum_squares(p_grid) + cp.sum_squares(p_bat))
        constraints = []
        

        # MPC LOOP
        for t in range(0,self.Datas.NP_3TH):

            # Power balance
            constraints.append(self.Datas.I_3th.loc[t, 'pv_forecast'] + p_bat[t] + p_grid[t] + self.Datas.I_3th.loc[t, 'load_forecast'] == 0)

            # Battery SOC
            if t == 0:
                constraints.append(soc_bat[t] == self.Datas.soc_bat)
            else:
                constraints.append(soc_bat[t] == soc_bat[t-1] - p_bat[t-1]*self.Datas.TS_3TH/self.Datas.Q_BAT)

            # Technical constrains
            constraints.append(p_grid[t] >= self.Datas.P_GRID_MIN)
            constraints.append(p_grid[t] <= self.Datas.P_GRID_MAX)
            constraints.append(soc_bat[t] >= self.Datas.SOC_BAT_MIN)
            constraints.append(soc_bat[t] <= self.Datas.SOC_BAT_MAX)
            constraints.append(p_bat[t] >= self.Datas.P_BAT_MIN)
            constraints.append(p_bat[t] <= self.Datas.P_BAT_MAX)

      

        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS)
        
        # Optimization Result
        for i in range(0, self.Datas.NP_3TH):
            self.Datas.R_3th.loc[i, 'p_bat_3th'] = p_bat.value[i]
            self.Datas.R_3th.loc[i, 'p_grid_3th'] = p_grid.value[i]
            self.Datas.R_3th.loc[i, 'soc_bat_3th'] = soc_bat.value[i]
            self.Datas.R_3th.loc[i, 'k_pv_3th'] = 0
        
        self.Datas.R_3th.loc[0, 'FO'] = problem.value






    def islanded_optimization_2th(self):
        # Simula a otimização secundária
        print("Otimização secundária da classe OptimizationQP...")
        return [[10, 20], [30, 40], [50, 60]]






    def connected_optimization_2th(self):
        # Simula a otimização secundária
        print("Otimização secundária da classe OptimizationQP...")
        return [[10, 20], [30, 40], [50, 60]]
