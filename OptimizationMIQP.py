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

class OptimizationMIQP():


    ''' ------------------------------------------------------------------------------- 
    isolated Optimization 3th
    --------------------------------------------------------------------------------'''
    @staticmethod
    def isolated_optimization_3th(Datas, pv_forecasted, load_forecasted):
        print("isolated Optimization in 3th")
        
        # WEIGHTs for objective function
        # 3th
        WEIGHT_K_PV      = 1
        WEIGHT_DELTA_BAT = 0.45
        WEIGHT_SOC_BAT   = 0.45
        
        # Optimization variables
        # Bat
        p_bat          = cp.Variable(Datas.NP_3TH)
        p_bat_ch       = cp.Variable(Datas.NP_3TH)
        p_bat_dis      = cp.Variable(Datas.NP_3TH)
        flag_p_bat_ch  = cp.Variable(Datas.NP_3TH, boolean = True)
        flag_p_bat_dis = cp.Variable(Datas.NP_3TH, boolean = True)
        soc_bat        = cp.Variable(Datas.NP_3TH)
        delta_p_bat    = cp.Variable(Datas.NP_3TH)
        # PV
        k_pv           = cp.Variable(Datas.NP_3TH)
        
        # Objective function
        objective = cp.Minimize(cp.sum_squares(k_pv[0:Datas.NP_3TH] - Datas.K_PV_REF)       * WEIGHT_K_PV       +
                                cp.sum_squares(delta_p_bat[0:Datas.NP_3TH])                 * WEIGHT_DELTA_BAT  +
                                cp.sum_squares(soc_bat[1:Datas.NP_3TH] - Datas.SOC_BAT_REF) * WEIGHT_SOC_BAT)
        
        # Constraints
        constraints = []
        # MPC LOOP
        for k in range(0, Datas.NP_3TH):
            
            # Power balance
            constraints.append(p_bat[k] + k_pv[k]*pv_forecasted.loc[k, 'data'] - load_forecasted.loc[k, 'data'] == 0)
            
            # Battery SOC
            if k == 0:
                constraints.append(soc_bat[k]     == Datas.soc_bat) # SOC now
                constraints.append(delta_p_bat[k] == p_bat[k] - Datas.p_bat)
            else: 
                constraints.append(soc_bat[k]     == soc_bat[k-1] - p_bat[k-1]*Datas.TS_3TH/Datas.Q_BAT)
                constraints.append(delta_p_bat[k] == p_bat[k] - p_bat[k-1])
            
            # Technical constrains
            # SOC bat
            constraints.append(soc_bat[k] >= Datas.SOC_BAT_MIN)
            constraints.append(soc_bat[k] <= Datas.SOC_BAT_MAX)
            # P_bat
            constraints.append(p_bat_ch[k]                          >= 0)
            constraints.append(p_bat_ch[k]       <= Datas.P_BAT_MAX * flag_p_bat_ch[k])
            constraints.append(p_bat_dis[k]                         >= 0)
            constraints.append(p_bat_dis[k]     <= Datas.P_BAT_MAX * flag_p_bat_dis[k])
            constraints.append(p_bat[k]                             >= Datas.P_BAT_MIN)
            constraints.append(p_bat[k]                             <= Datas.P_BAT_MAX)
            constraints.append(p_bat[k]                             == p_bat_dis[k] - p_bat_ch[k])
            constraints.append(flag_p_bat_ch[k] + flag_p_bat_dis[k] <= 1)
            # k_pv
            constraints.append(k_pv[k] >= 0)
            constraints.append(k_pv[k] <= 1)

        # SOLVER
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.CBC)
        
        if problem.status == cp.OPTIMAL:
            print("OTIMO")
            # Results
            results_3th = pd.DataFrame(index=range(Datas.NP_3TH), columns=['p_bat_sch', 'k_pv_sch'])
            OF_3th      = 0
            for k in range(0, Datas.NP_3TH):
                results_3th.loc[k, 'p_bat_sch']   = p_bat.value[k]
                results_3th.loc[k, 'k_pv_sch']    = k_pv.value[k]
                # results_3th.loc[0, 'p_grid_sch']  = p_grid.value[k]
            OF_3th = problem.value
            print(type(results_3th))
            return results_3th, OF_3th
        else:
            print("ENGASGOU")
            return None, None




    ''' ------------------------------------------------------------------------------- 
    Connected Optimization 3th
    --------------------------------------------------------------------------------'''
    @staticmethod
    def connected_optimization_3th(Datas):
        
        # Optimization variables
        p_bat = cp.Variable(Datas.NP_3TH) 
        soc_bat = cp.Variable(Datas.NP_3TH)
        p_grid = cp.Variable(Datas.NP_3TH)

        # Optimization problem
        objective = cp.Minimize(cp.sum_squares(p_grid[0:Datas.NP_3TH] - Datas.P_GRID_MAX)
                                + cp.sum_squares(p_bat[1:Datas.NP_3TH] - p_bat[0:Datas.NP_3TH - 1])
                                + cp.sum_squares(soc_bat[1:Datas.NP_3TH] - Datas.SOC_BAT_REF))
        constraints = []

        # MPC for K = 0
        constraints.append(soc_bat[k] == Datas.soc_bat)
        constraints.append(soc_bat[k] == Datas.soc_bat)

        # MPC LOOP
        for k in range(0, Datas.NP_3TH):

            # Power balance
            constraints.append(Datas.I_3th.loc[k, 'pv_forecasted'] + Datas.I_3th.loc[k, 'load_forecasted']
                               + p_bat[k] + p_grid[k] == 0)
            
            # Battery SOC
            if k == 0:
                constraints.append(soc_bat[k] == Datas.soc_bat - (p_bat[k-1])*Datas.TS_3TH/Datas.Q_BAT)
            else:
                constraints.append(soc_bat[k] == soc_bat[k-1] - (p_bat[k-1])*Datas.TS_3TH/Datas.Q_BAT)
            
            # Technical constrains
            # GRID
            constraints.append(p_grid[k] <= Datas.P_GRID_MAX)
            constraints.append(p_grid[k] >= Datas.P_GRID_MIN)
            
            # BAT
            constraints.append(soc_bat[k] >= Datas.SOC_BAT_MIN)
            constraints.append(soc_bat[k] <= Datas.SOC_BAT_MAX)
            constraints.append(p_bat[k] >= Datas.P_BAT_MIN)
            constraints.append(p_bat[k] <= Datas.P_BAT_MAX)

        # SOLVER
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS)
        
        # Optimization Result
        for k in range(0, Datas.NP_3TH):
            Datas.R_3th.loc[k, 'p_bat_3th'] = p_bat.value[k]
            Datas.R_3th.loc[k, 'p_grid_3th'] = p_grid.value[k]
            Datas.R_3th.loc[k, 'soc_bat_3th'] = soc_bat.value[k]
            Datas.R_3th.loc[k, 'k_pv_3th'] = 0
        
        Datas.R_3th.loc[0, 'FO'] = problem.value





    ''' ------------------------------------------------------------------------------- 
    isolated Optimization 2th
    --------------------------------------------------------------------------------'''
    @staticmethod
    def isolated_optimization_2th(Datas):
        
        WEIGHT_DELTA_BAT = 1
        WEIGHT_REF_BAT = 1
        WEIGHT_REF_SC = 1
        WEIGHT_SOC_SC = 1
        WEIGHT_REF_K_PV = 1
              
        # Simula a otimização secundária
        print("Otimização secundária da classe OptimizationMIQP...")
        print("isolated Optimization in 2th")
        
        # Optimization variables
        p_bat          = cp.Variable(Datas.NP_2TH)
        # Bat
        p_bat_ch       = cp.Variable(Datas.NP_2TH)
        p_bat_dis      = cp.Variable(Datas.NP_2TH)
        flag_p_bat_ch  = cp.Variable(Datas.NP_2TH, boolean = True)
        flag_p_bat_dis = cp.Variable(Datas.NP_2TH, boolean = True)
        soc_bat        = cp.Variable(Datas.NP_2TH)
        delta_p_bat    = cp.Variable(Datas.NP_2TH)
        # PV
        k_pv           = cp.Variable(Datas.NP_2TH)
        # SC
        p_sc           = cp.Variable(Datas.NP_2TH)
        p_sc_ch        = cp.Variable(Datas.NP_2TH)
        p_sc_dis       = cp.Variable(Datas.NP_2TH)
        flag_p_sc_ch   = cp.Variable(Datas.NP_2TH, boolean = True)
        flag_p_sc_dis  = cp.Variable(Datas.NP_2TH, boolean = True)
        soc_sc         = cp.Variable(Datas.NP_2TH)
        delta_p_sc     = cp.Variable(Datas.NP_2TH)
        
        # Optimization problem
        objective = cp.Minimize(cp.sum_squares(k_pv[0:Datas.NP_2TH] - Datas.k_pv_sch)     * WEIGHT_REF_K_PV +
                                cp.sum_squares(p_bat[0:Datas.NP_2TH] - Datas.p_bat_sch)   * WEIGHT_REF_BAT +
                                cp.sum_squares(delta_p_bat[0:Datas.NP_2TH])               * WEIGHT_DELTA_BAT +
                                cp.sum_squares(delta_p_sc[0:Datas.NP_2TH])                * WEIGHT_REF_SC +
                                cp.sum_squares(soc_sc[0:Datas.NP_2TH] - Datas.SOC_SC_REF) * WEIGHT_SOC_SC
                                )
        
        constraints = []
        
        # MPC LOOP
        for k in range(0, Datas.NP_2TH):

            # Power balance
            constraints.append(k_pv[k]*Datas.p_pv + p_bat[k] + p_sc[k] + Datas.p_load == 0)

            # Battery SOC
            if k == 0: # Now
                constraints.append(soc_bat[k]     == Datas.soc_bat)
                constraints.append(soc_sc[k]      == Datas.soc_sc)
                constraints.append(delta_p_bat[k] == p_bat[k] - Datas.p_bat)
                constraints.append(delta_p_sc[k]  == p_sc[k]  - Datas.p_sc)
            else:
                constraints.append(soc_bat[k]     == soc_bat[k-1] - p_bat[k-1]*Datas.TS_2TH/Datas.Q_BAT)
                constraints.append(soc_sc[k]      == soc_sc[k-1] - p_sc[k-1]*Datas.TS_2TH/Datas.Q_SC)
                constraints.append(delta_p_bat[k] == p_bat[k] - p_bat[k-1])
                constraints.append(delta_p_sc[k]  == p_sc[k]  - p_sc[k-1])
            
            # Technical constrains
            # SOC bat
            constraints.append(soc_bat[k] >= Datas.SOC_BAT_MIN)
            constraints.append(soc_bat[k] <= Datas.SOC_BAT_MAX)
            # p_bat
            constraints.append(p_bat_ch[k]                          >= 0)
            constraints.append(p_bat_ch[k]*flag_p_bat_ch[k]         <= Datas.P_BAT_MAX)
            constraints.append(p_bat_dis[k]                         >= 0)
            constraints.append(p_bat_dis[k]*flag_p_bat_dis[k]       <= Datas.P_BAT_MAX)
            constraints.append(p_bat[k]                             >= Datas.P_BAT_MAX * (-1))
            constraints.append(p_bat[k]                             <= Datas.P_BAT_MAX)
            constraints.append(p_bat[k]                             == p_bat_dis[k] - p_bat_ch[k])
            constraints.append(flag_p_bat_ch[k] + flag_p_bat_dis[k] <= 1)
            # SOC sc
            constraints.append(soc_sc[k]                            >= Datas.SOC_SC_MIN)
            constraints.append(soc_sc[k]                            <= Datas.SOC_SC_MAX)
            # p_sc
            constraints.append(p_sc_ch[k]                           >= 0)
            constraints.append(p_sc_ch[k]*flag_p_sc_ch[k]           <= Datas.P_SC_MAX)
            constraints.append(p_sc_dis[k]                          >= 0)
            constraints.append(p_sc_dis[k]*flag_p_sc_dis[k]         <= Datas.P_SC_MAX)
            constraints.append(p_sc[k]                              >= Datas.P_SC_MAX * (-1))
            constraints.append(p_sc[k]                              <= Datas.P_SC_MAX)
            constraints.append(p_sc[k]                              == p_sc_dis[k] - p_sc_ch[k])
            constraints.append(flag_p_sc_ch[k] + flag_p_sc_dis[k]   <= 1)
            # pv
            constraints.append(k_pv[k]                              >= 0)
            constraints.append(k_pv[k]                              <= 1)
        
        # SOLVER
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS)
        
        # Results
        Results_2th = pd.DataFrame(index=range(Datas.NP_3TH), columns=['p_bat_ref', 'p_sc_ref', 'k_pv_ref'])
        
        # Optimization Result
        for k in range(0, Datas.NP_3TH):
            Results_2th.loc[k, 'p_bat_ref']  = p_bat.value[k]
            Results_2th.loc[k, 'p_sc_ref']   = p_sc.value[k]
            Results_2th.loc[k, 'k_pv_ref']   = k_pv.value[k]

        OF_2th = problem.value

        return Results_2th, OF_2th



    ''' ------------------------------------------------------------------------------- 
    isolated Optimization 2th
    --------------------------------------------------------------------------------'''
    @staticmethod
    def connected_optimization_2th():
        # Simula a otimização secundária
        print("Otimização secundária da classe OptimizationMIQP...")
        return [[10, 20], [30, 40], [50, 60]]
