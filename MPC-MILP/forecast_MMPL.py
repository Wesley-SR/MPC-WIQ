# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 18:27:54 2023

@author: L08652
"""

import pandas as pd


def run_forecast_MMPL(P):
    
    future_data = pd.DataFrame({'PV_previsao': [0]*96})
    
    # K = 0
    future_data.loc[0, 'PV_previsao'] = (3*P.loc[96, 'PV_real'] +
                                         2*P.loc[0, 'PV_real'] +
                                         2*P.loc[95, 'PV_real'])

    # k = 1
    future_data.loc[1, 'PV_previsao'] = (P.loc[1, 'PV_real']*3 + 
                                          P.loc[0, 'PV_real']*2 +
                                          1*0) / (3+2+1)

    # k = 2
    future_data.loc[2, 'PV_previsao'] = (P.loc[2, 'PV_real']*3 + 
                                          P.loc[1, 'PV_real']*2 +
                                          P.loc[0, 'PV_real']*1) / (3+2+1)

    # k > 3
    for x in range(3,96):
        future_data.loc[x, 'PV_previsao'] = (P.loc[x, 'PV_real']*3 + 
                                              P.loc[x-1, 'PV_real']*2 +
                                              P.loc[x-2, 'PV_real']*1) / (3+2+1) 
    
    
    ''' WRITE RESULTS IN SCV'''
    # future_data.to_csv("online_forecast_pv.csv", index=False)
    
    return future_data