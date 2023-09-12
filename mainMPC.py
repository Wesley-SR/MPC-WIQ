"""
Created on Sat Aug 22 21:39:00 2023

@author: Wesley
"""

import time
import pandas as pd
from optimization_QP import OptimizationQP

class mainClass( ):
    def __init__(self, constants):
        super().__init__(constants)
        self.stop_mpc = False
        self.time_sleep = constants.loc[0, 'time_sleep']
        
        self.sampling_time_measurement = constants.loc[0, 'sampling_time_measurement']
        self.sampling_time_forecast = constants.loc[0, 'sampling_time_forecast']
        self.sampling_time_2th = constants.loc[0, 'sampling_time_2th']
        self.sampling_time_3th = constants.loc[0, 'sampling_time_3th']
        
        self.Np_2th = constants.loc[0, 'Np_2th']
        self.Np_3th = constants.loc[0, 'Np_3th']
        
        self.last_time_measurement = 0
        self.last_time_forecast = 0
        self.last_time_secundary = 0
        self.last_time_terciary = 0
        
        self.operation_mode = 0
        # 0 -> QP.   Connected mode.
        # 1 -> QP.   Islanded mode.
        # 2 -> MILP. Connected mode.
        # 3 -> MILP. Islanded mode.
        
        self.pv_forecast_2th = pd.DataFrame([0]* self.Np_2th)
        self.pv_forecast_3th = pd.DataFrame([0]* self.Np_3th)
        
        self.qp_otimization = OptimizationQP(constants)



    def run(self):

        while not self.stop_mpc:

            time.sleep(self.time_sleep)

            # Check if staying in island mode or connected mode

            # Take measurements
            if (self.is_it_time_to_take_measurements()):
                self.get_measurements()

            # Forecast PV and Load
            if (self.is_it_time_to_make_a_forecast()):
                self.get_measurements()

            # Run terciary optmization
            if (self.is_it_time_to_run_the_terciary()):
                self.run_terciary()

            # Run secundary optmization
            if (self.is_it_time_to_run_the_secundary()):
                self.run_secundary()

            # Check if it's time to stop the code
            if self.stop():
                self.stop_mpc = True 





    def is_it_time_to_take_measurements(self):
        current_time = time.time()
        if (current_time - self.last_time_measurement >= self.sampling_time_measurement):
            self.last_time_measurement = current_time
            return True
        else:
            return False





    def is_it_time_to_make_a_forecast(self):
        current_time = time.time()
        if (current_time - self.last_time_forecast >= self.sampling_time_measurement):
            self.last_time_forecast = current_time
            return True
        else:
            return False





    def is_it_time_to_run_the_terciary(self):
        current_time = time.time()
        if (current_time - self.sampling_time_terciary >= self.sampling_time_terciary):
            self.last_time_terciary = current_time
            return True
        else:
            return False





    def is_it_time_to_run_the_secundary(self):
        current_time = time.time()
        if (current_time - self.sampling_time_secondary >= self.sampling_time_secondary):
            self.last_time_secundary = current_time
            return True
        else:
            return False





    def run_secundary():
        pass
        # self.qp_otimization.connected_tertiary_optimization(self.operation_mode, soc_bat_current, p_pv, p_load)





    def run_terciary():
        pass




    
    def get_measurements(self):
        # Simula a captura de dados
        print("Capturando medidas...")
        return [1, 2, 3, 4, 5]




    def get_forecast_pv(self):
        pass




    def get_forecast_load(self):
        pass





    def stop(self):
        self.stop_mpc = True





    def start(self):
        self.stop_mpc = False