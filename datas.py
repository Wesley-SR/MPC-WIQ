# -*- coding: utf-8 -*-
"""
Created on 20230902

@author: Wesley Rodrigues
"""

import pandas as pd
import matplotlib.pyplot as plt



class Datas:
    def __init__(self):
        
        self.caminho_do_arquivo = "datas_1_s_completo_SNPTEE_3_dias.csv"
        self.M = pd.read_csv(self.caminho_do_arquivo)
        print(f"colunas: {self.M.columns}")

        self.M['p_grid'] = self.M['p_grid'].astype('float64')
        self.M['p_bat'] = self.M['p_bat'].astype('float64')
        self.M['p_sc'] = self.M['p_sc'].astype('float64')
        self.M['soc_bat'] = self.M['soc_bat'].astype('float64')
        self.M['soc_sc'] = self.M['soc_sc'].astype('float64')
        self.M['p_bat_ref'] = self.M['p_bat_ref'].astype('float64')
        self.M['p_sc_ref'] = self.M['p_sc_ref'].astype('float64')
        self.M['p_grid_ref'] = self.M['p_grid_ref'].astype('float64')
        self.M['k_pv_ref'] = self.M['k_pv_ref'].astype('float64')
        self.M['power_balance'] = self.M['power_balance'].astype('float64')

        # Operation mode
        self.ISOLATED = 0
        self.CONNECTED = 1
        # self.operation_mode = CONNECTED
        self.operation_mode = self.ISOLATED
        
        # Optmization method
        # self.optimization_method = "QP"
        self.optimization_method = "MILP"
        
        # Time constants
        self.NP_2TH         = 15 # seconds
        self.NP_3TH         = 96 # minutes
        self.TS_2TH         = 1 # seconds
        self.TS_3TH         = 900 # seconds, 900 s = 15 m
        self.TS_MEASUREMENT = 1 # seconds
        self.TS_FORECAST    = 1 # minutes
        self.TIME_SLEEP     = 0.3 # seconds

        # Technical specification constants
        # bat
        self.Q_BAT         = int(120) # kWh
        self.SOC_BAT_MIN   = float(0.2)
        self.SOC_BAT_MAX   = float(0.95)
        self.P_BAT_MAX     = int(20) # kW
        self.P_BAT_MIN     = int(-20) # kW
        self.P_BAT_VAR_MAX = int(50) # kW
        self.P_BAT_VAR_MIN = int(50) # kW
        # sc
        self.Q_SC         = float(0.289) # kWh
        self.SOC_SC_MIN = float(0.2)
        self.SOC_SC_MAX = float(0.95)
        self.P_SC_MAX   = int(50) # kW
        self.P_SC_MIN   = int(-50) # kW
        self.P_SC_VAR_MAX = int(50) # kW
        self.P_SC_VAR_MIN = int(50) # kW
        # grid
        self.P_GRID_MAX = int(150) # kW
        self.P_GRID_MIN = int(-150) # kW

        # Constansts references for optimization
        self.SOC_SC_REF  = 0.5
        self.SOC_BAT_REF = 0.8
        self.K_PV_REF    = 1
           
        # Measurements (Init values)
        self.soc_bat = 0.8
        self.soc_sc  = 0.5
        self.k_pv    = 1
        self.p_pv    = 0
        self.p_load  = 0
        self.p_grid  = 0
        self.p_bat   = 0
        self.p_sc    = 0
        
        # Tell us if is negative value
        self.p_bat_neg = 0
        self.p_sc_neg = 0
        
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
        
        self.MB_MULTIPLIER = 1000
        
        
        
        ''' ------------------- Matrices for 3th ------------------- '''
       
        # # Input for optimization
        # self.I_3th = pd.DataFrame({'p_pv': [0.0]*self.NP_3TH,
        #                            'tariff_pur': [0.5]*self.NP_3TH,
        #                            'tariff_sale': [0.5]*self.NP_3TH,
        #                            'p_load': [0.0]*self.NP_3TH,
        #                            })
        
        # # Result of optimization
        # self.R_3th = pd.DataFrame({'p_bat_3th': [0.0]*self.NP_3TH,
        #                            'p_grid_3th': [0.0]*self.NP_3TH,
        #                            'soc_bat_3th': [0.0]*self.NP_3TH,
        #                            'k_pv_3th': [0.0]*self.NP_3TH,
        #                            'FO_3th': [0.0]*self.NP_3TH})
        
        # Main
        # self.M_3th = pd.DataFrame({'p_pv': [0.0]*self.NP_3TH,
        #                            'tariff_pur': [0.5]*self.NP_3TH,
        #                            'tariff_sale': [0.5]*self.NP_3TH,
        #                            'p_load': [0.0]*self.NP_3TH,
        #                            })
        
        
        ''' ------------------- Matrices for 2th ------------------- '''
        # self.P_2th = pd.DataFrame({'p_pv': [0.0]*self.NP_2TH,
        #                            'p_load': [0.0]*self.NP_2TH})
        
        # self.F_2th = pd.DataFrame({'p_pv': [0.0]*self.NP_2TH,
        #                            'p_load': [0.0]*self.NP_2TH})
        
        # # Input for optimization
        # self.I_2th = pd.DataFrame({'p_pv': [0.0]*self.NP_2TH,
        #                            'p_load': [0.0]*self.NP_2TH,
        #                            'tariff_pur': [0.0]*self.NP_2TH,
        #                            'tariff_sale': [0.0]*self.NP_2TH,
        #                            'p_bat_ref': [0.0]*self.NP_2TH
        #                            })
        
        # Result of optimization
        self.R_2th = pd.DataFrame({'p_bat_ref': [0.0]*self.NP_2TH,
                                   'p_sc_ref': [0.0]*self.NP_2TH,
                                   'p_grid_ref': [0.0]*self.NP_2TH,
                                   'soc_bat_2th': [0.0]*self.NP_2TH,
                                   'k_pv_ref': [0.0]*self.NP_2TH,
                                   'FO_2th': [0.0]*self.NP_2TH})
        
        # self.update_past_datas()


    # def update_past_datas(self) -> None:
    #     # print(self.M)
        
    #     self.P_3th.loc[0:self.NP_3TH-1, 'p_pv'] = self.M.loc[0:self.NP_3TH-1, 'p_pv']
    #     self.P_3th.loc[0:self.NP_3TH-1, 'p_load'] = self.M.loc[0:self.NP_3TH-1, 'p_load']
        # plt.figure(figsize=(10, 5))
        # time_steps = list(range(self.NP_3TH))
        # plt.plot(time_steps, self.P_3th['p_pv'].values)
        # plt.plot(time_steps, self.P_3th['p_load'].values)
        # plt.show()
                