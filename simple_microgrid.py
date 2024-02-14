"""
Author: Wesley da Silva Rodrigues
Source: https://github.com/ahalev/python-microgrid/tree/master
Date: 2024/01/20
Description: This code simulates a simple microgrid
"""

import time
import numpy as np
import pandas as pd

# Modbus
from pyModbusTCP.client import ModbusClient



class Battery():
    def __init__(self) -> None:
        # Technical specification constans
        self.Q_BAT = int(12000)
        self.COST_BAT = 50000
        self.CC_BAT = self.COST_BAT/self.Q_BAT
        self.N_BAT = 6000
        self.COST_DEGR_BAT = 5*10^(-9)
        self.SOC_BAT_MIN = 0.2
        self.SOC_BAT_MAX = float(0.95)
        self.P_BAT_MAX = int(200)
        self.P_BAT_MIN = int(- 200)
        
        # Varibles
        self.SOC = 0.5
        self.ts = 0.2
        
    def charge(self, P_charge):
        self.SOC = self.SOC + P_charge*self.ts/self.Q_BAT

    def discharge(self, P_discharge):
        self.SOC = self.SOC - P_discharge*self.ts/self.Q_BAT


class Supercapacitor():
    def __init__(self) -> None:
        # Technical specification constans
        self.Q_SC = int(12000)
        self.COST_SC = 50000
        self.CC_SC = self.COST_SC/self.Q_SC
        self.N_SC = 6000
        self.COST_DEGR_SC = 5*10^(-9)
        self.SOC_SC_MIN = 0.2
        self.SOC_SC_MAX = float(0.95)
        self.P_SC_MAX = int(200)
        self.P_SC_MIN = int(- 200)
        
        # Varibles
        self.SOC = 0.5
        self.ts = 0.2

    def charge(self, P_charge):
        self.SOC = self.SOC + P_charge*self.ts/self.Q_SC

    def discharge(self, P_discharge):
        self.SOC = self.SOC - P_discharge*self.ts/self.Q_SC




class Microgrid():
    def __init__(self) -> None:
        
        self.battery = Battery()
        self.supercap = Supercapacitor()
        
        # Constants
        self.P_GRID_MAX = int(150)
        self.P_GRID_MIN = int(- 150)
        self.stop = 0
        self.PV = pd.read_csv('PV_1_sec.csv', index_col=['timestamp'],sep=",")
        self.load = pd.read_csv('load_1_sec.csv', index_col=['timestamp'],sep=",")
        self.delta_bat_max = 20
        
        # Variables
        self.operation_mode = "CONNECTED" # 'CONNECTED' or 'SLANDED'
        self.last_time_measurement = 0
        
        # Microgrid status variable
        self.p_bat = 0
        self.p_bat_last = 0
        self.p_sc = 0
        self.p_grid = 0
        self.p_pv = 0
        self.p_load = 0
        
        # Control variables
        self.last_time_control = 0
        self.has_control_signal = False
        self.p_bat_ref = 0
        self.p_sc_ref = 0
        
        # Config variables
        self.start_point = 0
        
        # Modbus
        self.host = 'localhost'
        self.port = 502
        self.client_ID = 3
        try:
            self.modbus_client = ModbusClient(host = self.host, port = self.port, 
                                              unit_id = self.client_ID, debug=False,
                                              auto_open=True)
        except Exception as e:
            print("Erros connecting Modbus Client: {}".format(e))
            self.modbus_client.close()
        
        
        
    def run(self) -> None:
        step = self.start_point

        while not self.stop:
            
            # Check times
            if (self.is_it_time_to_take_measurements()):
                pass
                # Get mensurements
                self.p_pv = self.PV[step, 'data']
                self.p_load = self.load[step, 'data']
                
                if (self.operation_mode == 'CONNECTED'):
                    # Power balance - Controle baseado em regras
                    # p_balance = pv - load
                    
                    if (self.has_control_signal):
                        self.p_bat = self.p_bat_ref
                        self.p_sc = self.p_sc_ref
                        # grid + bat + sc + pv = load
                        self.p_grid = self.p_load - self.p_bat - self.p_sc - self.p_pv
                        self.balance = (self.p_grid + self.p_bat + self.p_sc + self.p_pv
                                        - self.p_load)
                    else:
                        # grid + pv = load. Don't use sc
                        self.p_grid = self.p_load - self.p_pv
                        self.balance = self.p_grid + self.p_pv - self.p_load
                    
                elif (self.operation_mode == 'SLANDED'):
                    if (self.has_control_signal):
                        self.p_bat = self.p_bat_ref
                        # bat + sc + pv = load
                        self.p_sc = self.p_load - self.p_bat - self.p_pv
                        self.balance = self.p_bat + self.p_pv + self.p_sc - self.p_load
                    else:
                        # Aqui tem que ir o controle baseado em regras
                         if (abs(self.p_bat_last - (self.p_pv - self.p_load)) > self.delta_bat_max):
                            if (self.p_pv > self.p_load):
                                # Check SOC_MAX
                                if (self.battery.SOC >= self.battery.SOC_BAT_MAX):
                                    self.p_bat = 0
                                else:
                                    self.p_bat = - self.delta_bat_max
                            elif (self.p_pv < self.p_load):
                                # Check SOC_MIN
                                if (self.battery.SOC <= self.battery.SOC_BAT_MAX):
                                    self.p_bat = 0
                                else:
                                    self.p_bat = + self.delta_bat_max
                            else:
                                self.p_bat = 0

                            # remaining = bat + pv - load
                            remaining = - self.p_bat + self.p_pv - self.p_load
                            
                            
                            # bat + sc + pv - load = 0
                            self.p_sc = - self.p_bat - self.p_pv + self.p_load
                        else:
                            # bat + pv = load       e não usa o SC (Escolha minha)
                            self.p_bat = self.p_load - self.p_pv
                        
                        self.balance = self.p_sc + self.p_bat + self.p_pv - self.p_load
                        self.p_bat_last = self.p_bat
                        
                if (self.balance != 0):
                    print("Error: Power balance")
                
            if (self.is_it_time_to_take_control_signals()):
                pass
                # Get control signals
                
                # Power balance
                    # Controle baseado em regras
                
                # Calculate new SOCs
    
        
    
    def is_it_time_to_take_measurements(self) -> bool:
        current_time = time.time()
        
        if (current_time - self.last_time_measurement >= self.Datas.TS_MEASUREMENT):
            print("It's time to measurement")
            self.last_time_measurement = current_time
            return True
        else:
            return False



    def is_it_time_to_take_control_signals(self) -> bool:
        current_time = time.time()
        
        if (current_time - self.last_time_control >= self.Datas.TS_CONTROL):
            print("It's time to measurement")
            self.last_time_control = current_time
            return True
        else:
            return False

