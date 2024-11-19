# -*- coding: utf-8 -*-
"""
Created on 20230902

@author: Wesley Rodrigues
"""

import pandas as pd
import matplotlib.pyplot as plt


class Datas:
    def __init__(self):
        
        self.M = pd.read_csv("datas.csv", index_col='t')
        
        # Operation mode
        # self.operation_mode = "CONNECTED"
        self.operation_mode = "ISOLATED"
        
        # Optmization method
        self.optimization_method = "QP"
        # self.optimization_method = "MILP"
        
        # Paths for files
        self.pv_path = "PV_model"
        self.load_path = "Load_model"
        
        # Time constants
        self.NP_2TH         = 15 # seconds
        self.NP_3TH         = 96 # minutes
        self.TS_2TH         = 1 # seconds
        self.TS_3TH         = 1 # seconds
        self.TS_MEASUREMENT = 1 # seconds
        self.TS_FORECAST    = 1 # minutes
        self.TIME_SLEEP     = 0.3 # seconds

        # Technical specification constants
        # bat
        self.Q_BAT         = int(120)
        self.SOC_BAT_MIN   = 0.2
        self.SOC_BAT_MAX   = float(0.95)
        self.P_BAT_MAX     = int(20)
        self.P_BAT_MIN     = int(-20)
        self.P_BAT_VAR_MAX = int(50)
        self.P_BAT_VAR_MIN = int(50)
        # sc
        self.Q_SC         = int(0.289)
        self.SOC_SC_MIN = 0.2
        self.SOC_SC_MAX = float(0.95)
        self.P_SC_MAX   = int(50)
        self.P_SC_MIN   = int(-50)
        self.P_SC_VAR_MAX = int(50)
        self.P_SC_VAR_MIN = int(50)
        # grid
        self.P_GRID_MAX = int(150)
        self.P_GRID_MIN = int(-150)

        # Constansts references for optimization
        self.SOC_SC_REF  = 0.5
        self.SOC_BAT_REF = 0.8
        self.K_PV_REF    = 1
              
        # Measurements (Init values)
        self.soc_bat = 0.65
        self.soc_sc  = float(0.5)
        self.p_pv    = float(0)
        self.p_load  = float(0.5)
        self.p_grid  = float(0)
        self.p_bat   = float(0)
        self.p_sc    = float(0)
        
        # Scheduled (Calculated by 3th)
        self.p_bat_sch     = 0
        self.p_bat_ch_sch  = 0
        self.p_bat_dis_sch = 0
        self.p_grid_sch    = 0
        self.k_pv_sch      = 0
        
        # References (Calculated by 2th)
        self.p_bat_ref  = 0
        self.p_grid_ref = 0
        self.k_pv_ref   = 0
        
        
        
        ''' ------------------- Matrices for 3th ------------------- '''
        self.P_3th = pd.DataFrame({'p_pv': [0.0]*self.NP_3TH,
                                   'p_load': [0.0]*self.NP_3TH})
        
        # Forecast
        self.F_3th = pd.DataFrame({'p_pv': [0.0]*self.NP_3TH,
                                   'p_load': [0.0]*self.NP_3TH})
        
        # Input for optimization
        self.I_3th = pd.DataFrame({'p_pv': [0.0]*self.NP_3TH,
                                   'tariff_pur': [0.5]*self.NP_3TH,
                                   'tariff_sale': [0.5]*self.NP_3TH,
                                   'p_load': [0.0]*self.NP_3TH,
                                   })
        
        # Result of optimization
        self.R_3th = pd.DataFrame({'p_bat_3th': [0.0]*self.NP_3TH,
                                   'p_grid_3th': [0.0]*self.NP_3TH,
                                   'soc_bat_3th': [0.0]*self.NP_3TH,
                                   'k_pv_3th': [0.0]*self.NP_3TH,
                                   'FO_3th': [0.0]*self.NP_3TH})
        
        # Main
        # self.M_3th = pd.DataFrame({'p_pv': [0.0]*self.NP_3TH,
        #                            'tariff_pur': [0.5]*self.NP_3TH,
        #                            'tariff_sale': [0.5]*self.NP_3TH,
        #                            'p_load': [0.0]*self.NP_3TH,
        #                            })
        
        
        ''' ------------------- Matrices for 2th ------------------- '''
        self.P_2th = pd.DataFrame({'p_pv': [0.0]*self.NP_2TH,
                                   'p_load': [0.0]*self.NP_2TH})
        
        self.F_2th = pd.DataFrame({'p_pv': [0.0]*self.NP_2TH,
                                   'p_load': [0.0]*self.NP_2TH})
        
        # Input for optimization
        self.I_2th = pd.DataFrame({'p_pv': [0.0]*self.NP_2TH,
                                   'p_load': [0.0]*self.NP_2TH,
                                   'tariff_pur': [0.0]*self.NP_2TH,
                                   'tariff_sale': [0.0]*self.NP_2TH,
                                   'p_bat_ref': [0.0]*self.NP_2TH
                                   })
        
        # Result of optimization
        self.R_2th = pd.DataFrame({'p_bat_2th': [0.0]*self.NP_2TH,
                                   'p_sc_2th': [0.0]*self.NP_2TH,
                                   'p_grid_2th': [0.0]*self.NP_2TH,
                                   'soc_bat_2th': [0.0]*self.NP_2TH,
                                   'k_pv_2th': [0.0]*self.NP_2TH,
                                   'FO_2th': [0.0]*self.NP_2TH})
        
        self.update_past_datas()


    def update_past_datas(self) -> None:
        # print(self.M)
        
        self.P_3th.loc[0:self.NP_3TH-1, 'p_pv'] = self.M.loc[0:self.NP_3TH-1, 'p_pv']
        self.P_3th.loc[0:self.NP_3TH-1, 'p_load'] = self.M.loc[0:self.NP_3TH-1, 'p_load']
            
        
        # plt.figure(figsize=(10, 5))
        # time_steps = list(range(self.NP_3TH))
        # plt.plot(time_steps, self.P_3th['p_pv'].values)
        # plt.plot(time_steps, self.P_3th['p_load'].values)
        # plt.show()
                