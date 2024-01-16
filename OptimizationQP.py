# -*- coding: utf-8 -*-
"""
Created on Saturday August 19 18:23:10 2023

@author: Wesley Rodrigues
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
        # 3th
        self.WEIGHTING_K_PV_3TH = 1
        self.WEIGHTING_DELTA_BAT_3TH = 0.45
        # 2th
        self.WEIGHTING_K_PV_2TH = 0.45
        self.WEIGHTING_REF_BAT_2TH = 0.45
        self.WEIGHTING_SOC_SC_2TH = 0.001
        
        
        

    ''' ------------------------------------------------------------------------------- 
    Islanded Optimization 3th
    --------------------------------------------------------------------------------'''
    
    def islanded_optimization_3th(self):
        
        print("Islanded Optimization in 3th")
        
        # Optimization variables
        p_bat = cp.Variable(self.Datas.NP_3TH)
        soc_bat = cp.Variable(self.Datas.NP_3TH)
        k_pv = cp.Variable(self.Datas.NP_3TH)
        
        # Optimization problem
        objective = cp.Minimize(cp.sum_squares(k_pv - self.Datas.K_PV_REF_3TH)*self.WEIGHTING_K_PV_3TH +
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
        
        # Results
        for t in range(0, self.Datas.NP_3TH):
            self.Datas.R_3th.loc[t, 'p_bat_3th'] = p_bat.value[t]
            self.Datas.R_3th.loc[t, 'p_grid_3th'] = 0
            self.Datas.R_3th.loc[t, 'soc_bat_3th'] = soc_bat.value[t]
            self.Datas.R_3th.loc[t, 'k_pv_3th'] = k_pv.value[t]
        
        self.Datas.R_3th.loc[0, 'FO'] = problem.value





    ''' ------------------------------------------------------------------------------- 
    Connected Optimization 3th
    --------------------------------------------------------------------------------'''
    def connected_optimization_3th(self):
        
        # Optimization variables
        p_bat_ch = cp.Variable(self.Datas.NP_3TH)
        p_bat_dis = cp.Variable(self.Datas.NP_3TH)     
        soc_bat = cp.Variable(self.Datas.NP_3TH)
        p_sale = cp.Variable(self.Datas.NP_3TH)
        p_pur = cp.Variable(self.Datas.NP_3TH)

        switching_bat = cp.Variable(self.Datas.NP_3TH, boolean=False)
        switching_grid = cp.Variable(self.Datas.NP_3TH, boolean=False)



        # Optimization problem
        objective = cp.Minimize(cp.sum(cp.multiply(p_sale, self.Datas.I_3th['tariff_sale'].values)
                                + self.Datas.CC_BAT/(2*self.Datas.N_BAT)*self.Datas.TS_3TH*(p_bat_ch + p_bat_ch)
                                + self.Datas.COST_DEGR_BAT*(p_bat_ch + p_bat_dis)))
        constraints = []


        # MPC LOOP
        for t in range(0, self.Datas.NP_3TH):

            # Power balance
            constraints.append(self.Datas.I_3th.loc[t, 'pv_forecast'] + p_bat_ch[t] + p_pur[t] + self.Datas.I_3th.loc[t, 'load_forecast'] == 
                               p_bat_dis[t] + p_sale[t])
            
            
            # Battery SOC
            if t == 0:
                constraints.append(soc_bat[t] == self.Datas.soc_bat)
            else:
                constraints.append(soc_bat[t] == soc_bat[t-1] + (p_bat_dis[t-1] - p_bat_ch[t-1])*self.Datas.TS_3TH/self.Datas.Q_BAT)

            # Technical constrains
            # GRID
            constraints.append(p_pur[t] >= 0)
            constraints.append(p_pur[t] <= (1-switching_grid[t])*self.Datas.P_GRID_MAX)
            constraints.append(p_sale[t] >= 0)
            constraints.append(p_sale[t] <= switching_grid[t]*self.Datas.P_GRID_MAX)
            
            # BAT
            constraints.append(soc_bat[t] >= self.Datas.SOC_BAT_MIN)
            constraints.append(soc_bat[t] <= self.Datas.SOC_BAT_MAX)
            constraints.append(p_bat_ch[t] >= 0)
            constraints.append(p_bat_ch[t] <= (1-switching_bat[t])*self.Datas.P_BAT_MAX)
            constraints.append(p_bat_dis[t] >= 0)
            constraints.append(p_bat_dis[t] <= switching_bat[t]*self.Datas.P_BAT_MAX)
            



        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS)
        
        # Optimization Result
        for t in range(0, self.Datas.NP_3TH):
            self.Datas.R_3th.loc[t, 'p_bat_3th'] = p_bat_dis.value[t] - p_bat_ch.value[t]
            self.Datas.R_3th.loc[t, 'p_grid_3th'] = p_sale.value[t] - p_pur.value[t]
            self.Datas.R_3th.loc[t, 'soc_bat_3th'] = soc_bat.value[t]
            self.Datas.R_3th.loc[t, 'k_pv_3th'] = 0
        
        self.Datas.R_3th.loc[0, 'FO'] = problem.value





    ''' ------------------------------------------------------------------------------- 
    Islanded Optimization 2th
    --------------------------------------------------------------------------------'''
    def islanded_optimization_2th(self):
        # Simula a otimização secundária
        print("Otimização secundária da classe OptimizationQP...")
        print("Islanded Optimization in 2th")
        
        # Optimization variables
        p_bat = cp.Variable(self.Datas.NP_2TH)
        soc_bat = cp.Variable(self.Datas.NP_2TH)
        k_pv = cp.Variable(self.Datas.NP_2TH)
        p_sc = cp.Variable(self.Datas.NP_2TH)
        soc_sc = cp.Variable(self.Datas.NP_2TH)
                
        # Optimization problem
        objective = cp.Minimize(cp.sum_squares(k_pv - self.Datas.R_3th.loc[t, 'k_pv_3th'])*self.WEIGHTING_K_PV_2TH 
                                + cp.sum_squares(soc_bat - self.Datas.R_3th.loc[t, 'soc_bat_3th'])*self.WEIGHTING_REF_BAT_2TH
                                + cp.sum_squares(soc_sc - self.Datas.SOC_SC_REF)*self.WEIGHTING_SOC_SC_2TH
                                )
        # TODO: Test wigh battery degradation
        
        constraints = []
        
        # MPC LOOP
        for t in range(0, self.Datas.NP_2TH):

            # Power balance
            constraints.append(k_pv[t]*self.Datas.I_2th.loc[t, 'pv_forecast'] + p_bat[t] + self.Datas.I_2th.loc[t, 'load_forecast'] == 0)
            # TODO: Insert variable k_pv

            # Battery SOC
            if t == 0: # Now
                constraints.append(soc_bat[t] == self.Datas.soc_bat)
                constraints.append(soc_sc[t] == self.Datas.soc_sc)
            else:
                constraints.append(soc_bat[t] == soc_bat[t-1] - p_bat[t-1]*self.Datas.TS_2TH/self.Datas.Q_BAT)
                constraints.append(soc_sc[t] == soc_sc[t-1] - p_sc[t-1]*self.Datas.TS_2TH/self.Datas.Q_SC)
            
            # Technical constrains
            constraints.append(soc_bat[t] >= self.Datas.SOC_BAT_MIN)
            constraints.append(soc_bat[t] <= self.Datas.SOC_BAT_MAX)
            constraints.append(p_bat[t] >= self.Datas.P_BAT_MIN)
            constraints.append(p_bat[t] <= self.Datas.P_BAT_MAX)
            
            constraints.append(soc_sc[t] >= self.Datas.SOC_SC_MIN)
            constraints.append(soc_sc[t] <= self.Datas.SOC_SC_MAX)
            constraints.append(p_sc[t] >= self.Datas.P_SC_MIN)
            constraints.append(p_sc[t] <= self.Datas.P_SC_MAX)
            
            constraints.append(k_pv[t] >= 0)
            constraints.append(k_pv[t] <= 1)
            

      

        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS)
        
        # Optimization Result
        for t in range(0, self.Datas.NP_3TH):
            self.Datas.R_2th.loc[t, 'p_bat_2th'] = p_bat.value[t]
            self.Datas.R_2th.loc[t, 'p_sc_2th'] = p_sc.value[t]
            self.Datas.R_2th.loc[t, 'p_grid_2th'] = 0
            self.Datas.R_2th.loc[t, 'soc_bat_2th'] = soc_bat.value[t]
            self.Datas.R_2th.loc[t, 'soc_sc_2th'] = soc_sc.value[t]
            self.Datas.R_2th.loc[t, 'k_pv_2th'] = k_pv.value[t]

        self.Datas.R_2th.loc[0, 'FO'] = problem.value




    ''' ------------------------------------------------------------------------------- 
    Islanded Optimization 2th
    --------------------------------------------------------------------------------'''
    def connected_optimization_2th(self):
        # Simula a otimização secundária
        print("Otimização secundária da classe OptimizationQP...")
        return [[10, 20], [30, 40], [50, 60]]
