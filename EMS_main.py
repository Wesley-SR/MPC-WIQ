"""
Created on Sat Aug 22 21:39:00 2023

@author: Wesley
"""

import time
import pandas as pd
from OptimizationQP import OptimizationQP
from Datas import Datas
import numpy as np
import matplotlib.pyplot as plt


class EMS():
    def __init__(self):

        self.Datas = Datas()
        print(self.Datas.I_3th.loc[0, 'pv_forecast'])
        
        self.stop_mpc = False
        # Last Time
        self.last_time_measurement = 0
        self.last_time_forecast = 0
        self.last_time_2th = 0
        self.last_time_3th = 0
        
        self.operation_mode = 1
        # 0 -> QP.   Connected mode.
        # 1 -> QP.   Islanded mode.
        # 2 -> MILP. Connected mode.
        # 3 -> MILP. Islanded mode.
        
        self.qp_otimization = OptimizationQP(self.Datas)
        




    def run(self):

        while not self.stop_mpc:
            print("EMS init")
            
            time.sleep(self.Datas.TIME_SLEEP)

            # Check if staying in island mode or connected mode

            # Take measurements
            if (self.is_it_time_to_take_measurements()):
                self.get_measurements()

            # Forecast PV and Load
            if (self.is_it_time_to_make_a_forecast()):
                self.get_forecast_pv()
                self.get_forecast_load()

            # Run terciary optmization
            if (self.is_it_time_to_run_the_terciary()):
                self.run_3th_optimization()

            # Run 2th optmization
            # if (self.is_it_time_to_run_the_2th()):
            #    self.run_2th_optimization()

            # Check if it's time to stop the code
            self.stop_mpc = True # Test for now
            if self.stop():
                break
            
        
        self.plot_result()
        return self.Datas.I_3th, self.Datas.R_3th




    def is_it_time_to_take_measurements(self):
        current_time = time.time()
        print("Check if is time to measurement")
        print("current_time = {}".format(current_time))
        print("last_time_measurement = {}".format(self.last_time_measurement))
        print("TS_MEASUREMENT = {}".format(self.Datas.TS_MEASUREMENT))
        
        if (current_time - self.last_time_measurement >= self.Datas.TS_MEASUREMENT):
            print("It's time to measurement")
            self.last_time_measurement = current_time
            return True
        else:
            return False





    def is_it_time_to_make_a_forecast(self):
        current_time = time.time()
        if (current_time - self.last_time_forecast >= self.Datas.TS_FORECAST):
            print("It's time to forecast")
            self.last_time_forecast = current_time
            return True
        else:
            return False





    def is_it_time_to_run_the_terciary(self):
        current_time = time.time()
        if (current_time - self.last_time_3th >= self.Datas.TS_3TH):
            print("It's time to 3th")
            self.last_time_terciary = current_time
            return True
        else:
            return False





    def is_it_time_to_run_the_2th(self):
        current_time = time.time()
        if (current_time - self.last_time_2th >= self.Datas.TS_2TH):
            print("It's time to 2th")
            self.last_time_2th = current_time
            return True
        else:
            return False





    def run_2th_optimization():
        pass
        # self.qp_otimization.connected_tertiary_optimization(self.operation_mode, soc_bat_current, p_pv, p_load)





    def run_3th_optimization(self):
        if self.operation_mode == 0:
            self.qp_otimization.connected_optimization_3th()
        elif self.operation_mode == 1:
            self.qp_otimization.islanded_optimization_3th()




    
    def get_measurements(self):
        # Simula a captura de dados
        self.Datas.p_pv = float(0.1)
        self.Datas.p_load = float(-79.5)
        



    def get_forecast_pv(self):
        p_pv = np.array([0, 0, 0, 0, 0, 0, 3, 12, 25, 35, 40, 45, 50, 60, 50, 40, 10, 7, 0, 0, 0, 0, 0, 0])  # Exemplo de geração do PV em kWh
        self.Datas.I_3th.loc[:, 'pv_forecast'] = p_pv[:]
        self.Datas.I_3th.loc[0, 'pv_forecast'] = float(self.Datas.p_pv)
        



    def get_forecast_load(self):
        p_load = np.array([-0, -5, -13, -20, -40, -45, -65, -35, -38, -20, -18, -40, -48, -56, -70, -50, -40, -40, -35, -32, -27, -25, -20, -15])  # Exemplo de demanda em kWh
        self.Datas.I_3th.loc[:, 'load_forecast'] = p_load[:]
        self.Datas.I_3th.loc[0, 'load_forecast'] = float(self.Datas.p_load)
        




    def stop(self):
        return self.stop_mpc





    def plot_result(self):
        time_steps = list(range(self.Datas.NP_3TH))
        
        plt.figure(figsize=(10, 5))
        
        if self.operation_mode == 0:
            print("Plot p_grid")
            plt.plot(time_steps, self.Datas.R_3th.loc[:, 'p_grid_3th'], marker='o', linestyle='-', color='r', label='Grid')
        
        plt.plot(time_steps, self.Datas.R_3th.loc[:, 'p_bat_3th'], marker='o', linestyle='-', color='b', label='Battery')
        plt.plot(time_steps, self.Datas.I_3th.loc[:, 'pv_forecast'], marker='o', linestyle='-', color='orange', label='PV')
        plt.plot(time_steps, self.Datas.I_3th.loc[:, 'load_forecast'], marker='o', linestyle='-', color='g', label='Load')
        plt.plot(time_steps, self.Datas.I_3th.loc[:, 'pv_forecast']*self.Datas.R_3th.loc[:, 'k_pv_3th'], linestyle='-', color='orange', label='Load')
        plt.axhline(0, color='black', linestyle='--')
        plt.xlabel('Time (h)')
        plt.ylabel('Power (kW)')
        plt.title('Microgrid power')
        plt.legend()
        plt.grid()

        plt.figure(figsize=(10, 5))
        if self.operation_mode == 1:
            plt.plot(time_steps, self.Datas.R_3th.loc[:, 'k_pv_3th'], marker='o', linestyle='-', color='r', label='k_pv_3th')
        
        plt.plot(time_steps, self.Datas.R_3th.loc[:, 'soc_bat_3th'], marker='o', linestyle='-', color='b', label='soc_bat')
        plt.axhline(0, color='black', linestyle='--')
        plt.xlabel('Hora')
        plt.ylabel('SOC (%)')
        plt.title('Estado de Carga da Bateria')
        plt.legend()
        plt.grid()
        plt.show()
        print("Custo Total:", self.Datas.R_3th.loc[0, 'FO'])
        
        
        
if __name__ == "__main__":
    EMS_instance = EMS()
    
    I_3th, R_3th = EMS_instance.run()