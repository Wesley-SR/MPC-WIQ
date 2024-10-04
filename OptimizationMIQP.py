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

class OptimizationMIQP:

    def __init__(self, Datas): # With Datas like a enter parameter, we can edit the object EMS's Data
        
        self.Datas = Datas    
        
        

    ''' ------------------------------------------------------------------------------- 
    isolated Optimization 3th
    --------------------------------------------------------------------------------'''
    
    def isolated_optimization_3th(self):
        
        print("isolated Optimization in 3th")
        
        # Optimization variables
        p_bat   = cp.Variable(self.Datas.NP_3TH)
        p_bat_dis = cp.Variable(self.Datas.NP_3TH)
        p_bat_ch = cp.Variable(self.Datas.NP_3TH)
        flag_p_bat_dis = cp.Variable(self.Datas.NP_3TH, boolean = True)
        flag_p_bat_ch = cp.Variable(self.Datas.NP_3TH, boolean = True)
        soc_bat = cp.Variable(self.Datas.NP_3TH)
        k_pv    = cp.Variable(self.Datas.NP_3TH)
        
        
        # Objective function
        objective = cp.Minimize(cp.sum_squares(k_pv[1:self.Datas.NP_3TH] - self.Datas.K_PV_REF_3TH)*self.Datas.WEIGHT_K_PV_3TH +
                                cp.sum_squares(p_bat[1:self.Datas.NP_3TH] - p_bat[0:self.Datas.NP_3TH - 1]) +
                                cp.sum_squares(soc_bat[1:self.Datas.NP_3TH] - self.Datas.SOC_BAT_REF)
                                )
        constraints = []
        
        # MPC LOOP
        for k in range(0, self.Datas.NP_3TH):
            
            # Power balance
            constraints.append(p_bat[k] + k_pv[k]*self.Datas.I_3th.loc[k, 'pv_forecast'] - self.Datas.I_3th.loc[k, 'load_forecast'] == 0)

            # Battery SOC
            if k == 0:
                constraints.append(soc_bat[k] == self.Datas.soc_bat) # Now
            else:
                constraints.append(soc_bat[k] == soc_bat[k-1] - p_bat[k-1]*self.Datas.TS_3TH/self.Datas.Q_BAT)
            
            # Technical constrains
            # SOC bat
            constraints.append(soc_bat[k] >= self.Datas.SOC_BAT_MIN)
            constraints.append(soc_bat[k] <= self.Datas.SOC_BAT_MAX)
            # P_bat
            constraints.append(p_bat_ch[k] >= 0)
            constraints.append(p_bat_ch[k] <= self.Datas.P_BAT_MAX)
            constraints.append(p_bat_dis[k] >= 0)
            constraints.append(p_bat_dis[k] <= self.Datas.P_BAT_MAX)
            
            constraints.append(p_bat[k] >= - self.Datas.P_BAT_MAX)
            constraints.append(p_bat[k] <= self.Datas.P_BAT_MAX)
            constraints.append(p_bat[k] == p_bat_dis[k] - p_bat_ch[k])
            # k_pv
            constraints.append(k_pv[k] >= 0)
            constraints.append(k_pv[k] <= 1)

        # SOLVER
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS)
        
        # Results
        for k in range(0, self.Datas.NP_3TH):
            self.Datas.R_3th.loc[k, 'p_bat_3th'] = p_bat.value[k]
            self.Datas.R_3th.loc[k, 'p_grid_3th'] = 0
            self.Datas.R_3th.loc[k, 'soc_bat_3th'] = soc_bat.value[k]
            self.Datas.R_3th.loc[k, 'k_pv_3th'] = k_pv.value[k]
        
        self.Datas.R_3th.loc[0, 'FO'] = problem.value





    ''' ------------------------------------------------------------------------------- 
    Connected Optimization 3th
    --------------------------------------------------------------------------------'''
    def connected_optimization_3th(self):
        
        # Optimization variables
        p_bat = cp.Variable(self.Datas.NP_3TH) 
        soc_bat = cp.Variable(self.Datas.NP_3TH)
        p_grid = cp.Variable(self.Datas.NP_3TH)

        switching_bat = cp.Variable(self.Datas.NP_3TH, boolean=False)
        switching_grid = cp.Variable(self.Datas.NP_3TH, boolean=False)


        # Optimization problem
        objective = cp.Minimize(cp.sum_squares(p_grid[0:self.Datas.NP_3TH] - self.Datas.P_GRID_MAX)
                                + cp.sum_squares(p_bat[1:self.Datas.NP_3TH] - p_bat[0:self.Datas.NP_3TH - 1])
                                + cp.sum_squares(soc_bat[1:self.Datas.NP_3TH] - self.Datas.SOC_BAT_REF))
        constraints = []

        # MPC for K = 0
        constraints.append(soc_bat[k] == self.Datas.soc_bat)
        constraints.append(soc_bat[k] == self.Datas.soc_bat)

        # MPC LOOP
        for k in range(0, self.Datas.NP_3TH):

            # Power balance
            constraints.append(self.Datas.I_3th.loc[k, 'pv_forecast'] + self.Datas.I_3th.loc[k, 'load_forecast']
                               + p_bat[k] + p_grid[k] == 0)
            
            # Battery SOC
            if k == 0:
                constraints.append(soc_bat[k] == self.Datas.soc_bat - (p_bat[k-1])*self.Datas.TS_3TH/self.Datas.Q_BAT)
            else:
                constraints.append(soc_bat[k] == soc_bat[k-1] - (p_bat[k-1])*self.Datas.TS_3TH/self.Datas.Q_BAT)
            
            # Technical constrains
            # GRID
            constraints.append(p_grid[k] <= self.Datas.P_GRID_MAX)
            constraints.append(p_grid[k] >= self.Datas.P_GRID_MIN)
            
            # BAT
            constraints.append(soc_bat[k] >= self.Datas.SOC_BAT_MIN)
            constraints.append(soc_bat[k] <= self.Datas.SOC_BAT_MAX)
            constraints.append(p_bat[k] >= self.Datas.P_BAT_MIN)
            constraints.append(p_bat[k] <= self.Datas.P_BAT_MAX)
            

        # SOLVER
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS)
        
        # Optimization Result
        for k in range(0, self.Datas.NP_3TH):
            self.Datas.R_3th.loc[k, 'p_bat_3th'] = p_bat.value[k]
            self.Datas.R_3th.loc[k, 'p_grid_3th'] = p_grid.value[k]
            self.Datas.R_3th.loc[k, 'soc_bat_3th'] = soc_bat.value[k]
            self.Datas.R_3th.loc[k, 'k_pv_3th'] = 0
        
        self.Datas.R_3th.loc[0, 'FO'] = problem.value





    ''' ------------------------------------------------------------------------------- 
    isolated Optimization 2th
    --------------------------------------------------------------------------------'''
    def isolated_optimization_2th(self):
        # Simula a otimização secundária
        print("Otimização secundária da classe OptimizationMIQP...")
        print("isolated Optimization in 2th")
        
        # Optimization variables
        p_bat = cp.Variable(self.Datas.NP_2TH)
        soc_bat = cp.Variable(self.Datas.NP_2TH)
        k_pv = cp.Variable(self.Datas.NP_2TH)
        p_sc = cp.Variable(self.Datas.NP_2TH)
        soc_sc = cp.Variable(self.Datas.NP_2TH)
                
        # Optimization problem
        objective = cp.Minimize(cp.sum_squares(k_pv - self.Datas.R_3th.loc[k, 'k_pv_3th'])*self.Datas.WEIGHT_DELTA_BAT_3TH 
                                + cp.sum_squares(soc_bat - self.Datas.R_3th.loc[k, 'soc_bat_3th'])*self.Datas.WEIGHT_REF_BAT_2TH
                                + cp.sum_squares(soc_sc - self.Datas.SOC_SC_REF)*self.Datas.WEIGHT_SOC_SC_2TH
                                )
        
        constraints = []
        
        # MPC LOOP
        for k in range(0, self.Datas.NP_2TH):

            # Power balance
            constraints.append(k_pv[k]*self.Datas.I_2th.loc[k, 'pv_forecast'] + p_bat[k] + self.Datas.I_2th.loc[k, 'load_forecast'] == 0)
            # TODO: Insert variable k_pv

            # Battery SOC
            if k == 0: # Now
                constraints.append(soc_bat[k] == self.Datas.soc_bat)
                constraints.append(soc_sc[k] == self.Datas.soc_sc)
            else:
                constraints.append(soc_bat[k] == soc_bat[k-1] - p_bat[k-1]*self.Datas.TS_2TH/self.Datas.Q_BAT)
                constraints.append(soc_sc[k] == soc_sc[k-1] - p_sc[k-1]*self.Datas.TS_2TH/self.Datas.Q_SC)
            
            # Technical constrains
            constraints.append(soc_bat[k] >= self.Datas.SOC_BAT_MIN)
            constraints.append(soc_bat[k] <= self.Datas.SOC_BAT_MAX)
            constraints.append(p_bat[k] >= self.Datas.P_BAT_MIN)
            constraints.append(p_bat[k] <= self.Datas.P_BAT_MAX)
            
            constraints.append(soc_sc[k] >= self.Datas.SOC_SC_MIN)
            constraints.append(soc_sc[k] <= self.Datas.SOC_SC_MAX)
            constraints.append(p_sc[k] >= self.Datas.P_SC_MIN)
            constraints.append(p_sc[k] <= self.Datas.P_SC_MAX)
            
            constraints.append(k_pv[k] >= 0)
            constraints.append(k_pv[k] <= 1)
            

      
        # SOLVER
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS)
        
        # Optimization Result
        for k in range(0, self.Datas.NP_3TH):
            self.Datas.R_2th.loc[k, 'p_bat_2th'] = p_bat.value[k]
            self.Datas.R_2th.loc[k, 'p_sc_2th'] = p_sc.value[k]
            self.Datas.R_2th.loc[k, 'p_grid_2th'] = 0
            self.Datas.R_2th.loc[k, 'soc_bat_2th'] = soc_bat.value[k]
            self.Datas.R_2th.loc[k, 'soc_sc_2th'] = soc_sc.value[k]
            self.Datas.R_2th.loc[k, 'k_pv_2th'] = k_pv.value[k]

        self.Datas.R_2th.loc[0, 'FO'] = problem.value




    ''' ------------------------------------------------------------------------------- 
    isolated Optimization 2th
    --------------------------------------------------------------------------------'''
    def connected_optimization_2th(self):
        # Simula a otimização secundária
        print("Otimização secundária da classe OptimizationMIQP...")
        return [[10, 20], [30, 40], [50, 60]]
