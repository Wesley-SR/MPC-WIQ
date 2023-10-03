# -*- coding: utf-8 -*-
"""
Created on Sat Oct 30 20:17:00 2023

@author: Wesley Rodrigues
"""

import pandas as pd

class Comunication():
    def __init__(self, Q_BAT, Q_SC):
        
        M = pd.read_csv('M.csv', index_col=['tempo'], sep=",")
        
        self.p_pv = 0
        self.p_load = 0
        self.soc_bat = 0
        self.soc_sc = 0 
    
   
    def get_soc_bat(self, p, ts):
        return self.soc_bat
    
    def get_soc_sc(self, p, ts):
        return self.soc_sc
    
    def get_p_pv(self):
        return self.p_pv
    
    def get_p_load(self):
        return self.p_load
      