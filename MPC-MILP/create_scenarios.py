# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 15:47:34 2023

@author: L08652
"""


import pandas as pd
import random

def run_generate_scenario():
    
    df = pd.DataFrame(1, index=range(96), columns=['time',
                                                   'cx_bike_0', 
                                                   'cx_bike_1',
                                                   'cx_bike_2',
                                                   'cx_bike_3',
                                                   'cx_bike_4',
                                                   'cx_bike_5',
                                                   'cx_bike_6',
                                                   'cx_bike_7',
                                                   'cx_bike_8',
                                                   'cx_bike_9'])
    
    # MONTAR VETOR TEMPO
    cont = 0
    h = 0
    m = 0
    for k in range(0,96):
        if m == 0:
            df.loc[k,'time'] = str('{hour}:00'.format(hour = h))
        else:    
            df.loc[k,'time'] = str('{hour}:{minute}'.format(hour = h, minute = m))
        cont += 1
        m += 15
        if cont > 3:
            m = 0
            h += 1
            cont = 0
    
    # Períodos de tempo
    # 6:30 até 7:30, range(26,30+1):
    # 7:45 até 9:30, range(31,38+1):
    # 9:45 até 11:45, range(39,47+1):
    # 12:00 até 14:30, range(48,58+1):
    # 14:45 até 17:00, range(59, 68+1):
    # 17:15 até 20:00, range(69, 80)+1:
    # 20:15 até 23:45, range(81, 95+1):
    
    
    for bike in range(0, 10):
        for iteracao in range(0, 5):
            time = random.randint(26,80)
            cx = random.randint(0,1)
            cx_time = random.randint(0,80-time)
            # print('time = {}'.format(time))
            # print('cx = {}'.format(cx))
            # print('cx_time = {}'.format(cx_time))
            for k in range(0,cx_time):
                df.loc[time+k,'cx_bike_{}'.format(bike)] = cx
    
    
    return df
    
if __name__ == "__main__":
    
    cenario = run_generate_scenario()
    cenario.to_csv('Cenario.csv',sep=';')
    