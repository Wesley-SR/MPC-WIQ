# -*- coding: utf-8 -*-
"""
Created on 20230902

@author: Wesley
"""

import pandas as pd


class Datas:
    def __init__(self):
        
        # Time constants
        self.NP_2TH = 9000
        self.NP_3TH = 24
        self.TS_2TH = 60
        self.TS_3TH = 60
        self.TS_MEASUREMENT = 60
        self.TS_FORECAST = 60
        self.TIME_SLEEP = 20
         
        # Technical specification constans
        self.Q_BAT = 12
        self.SOC_BAT_MIN = 0.95
        self.SOC_BAT_MAX = 0.2
        self.SOC_BAT_INI = 0.5
        self.P_BAT_MAX = 12
        self.P_GRID_MAX = 20
        
        self.soc_bat = 0
        self.soc_sc = 0
        self.p_pv = 0
        self.p_load = 0

        self.I_3th = pd.DataFrame({'pv_forecast': [0]*self.NP_3TH,
                                   'energy_tariff_purchase': [0]*self.NP_3TH,
                                   'energy_tariff_sales': [0]*self.NP_3TH,
                                   'load_forecast': [0]*self.NP_3TH,
                                   })
        
        self.I_2th = pd.DataFrame({'pv_forecast': [0]*self.NP_2TH,
                                   'energy_tariff_purchase': [0]*self.NP_2TH,
                                   'energy_tariff_sales': [0]*self.NP_2TH,
                                   'load_forecast': [0]*self.NP_2TH,
                                   })
        
