"""
Created on Sat Aug 22 21:39:00 2023

@author: Wesley
"""

#TODO: To download and to test the PVLIB and PyBaMM libraries!

# Python libs
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pyModbusTCP.client import ModbusClient

# My libs
from OptimizationMIQP import OptimizationMIQP
from OptimizationMILP import OptimizationMILP
from datas import Datas
# from ForecastingModel import ForecastingModel

# Modbus
from pyModbusTCP.client import ModbusClient

from mmpw import mmpw


# *******************************************************
#      EMC CLASS                                        #
# *******************************************************
class EMS():
    def __init__(self):
        
        print("-------------------------")
        print("1) EMS Initialization")
        # Create a object of datas
        self.Datas = Datas()
        
        # Execution variables
        self.enable_run_EMS = True
        self.enable_run_3th = True
        self.enable_run_2th = False
        
        # Timers
        self.t = 96 # Time that start in matrix M (in simulation)
        # Last Timers
        self.last_time_measurement = 0
        self.last_time_2th = 0
        self.last_time_3th = 0

        # Create optimization object
        if self.Datas.optimization_method == "QP":
            self.qp_optimization = OptimizationMIQP()
        elif self.Datas.optimization_method == "MILP":
            self.milp_optimization = OptimizationMILP()
        
        # Create Modbus object
        print("2) Modbus initialization")
        self.host = 'localhost'
        self.port = 502
        self.client_ID = 2
        try:
            self.modbus_client = ModbusClient(host = self.host, port = self.port, unit_id = self.client_ID, auto_open=True)
        except Exception as e:
            print("[EMS Init] Error connecting Modbus Client: {}".format(e))
            self.modbus_client.close()
        self.counter_mb = 0

        # DataFrame for forecast
        
        self.pv_forecasted = pd.DataFrame(index=range(self.Datas.NP_3TH), columns=['data'])
        self.load_forecasted = pd.DataFrame(index=range(self.Datas.NP_3TH), columns=['data'])
        # DataFrame for past datas
        self.pv_past = pd.DataFrame(index=range(self.Datas.NP_3TH), columns=['data'])
        self.load_past = pd.DataFrame(index=range(self.Datas.NP_3TH), columns=['data'])
        
        # Get datas for first time
        self.pv_past.loc[0:self.Datas.NP_3TH-1, 'data'] = self.Datas.M.loc[0:self.Datas.NP_3TH-1, 'p_pv']
        self.load_past.loc[0:self.Datas.NP_3TH-1, 'data'] = self.Datas.M.loc[0:self.Datas.NP_3TH-1, 'p_load']

        plt.figure(figsize=(10, 5))
        time_steps = list(range(self.Datas.NP_3TH))
        plt.plot(time_steps, self.pv_past['data'].values, label = 'pv_past')
        plt.plot(time_steps, self.load_past['data'].values, label = 'load_past')
        plt.title('Inicio')
        plt.legend()
        plt.grid()




    # =======================================================
    #      Main loop of MPC                                 #
    # =======================================================
    def run(self) -> None:
        
        print("Run MPC")
        
        while self.enable_run_EMS:

            print(f"t = {self.t}")    

            # Take measurements
            if (self.is_it_time_to_take_measurements()):
                self.get_measurements()

            # Run terciary optmization
            if (self.is_it_time_to_run_3th() and self.enable_run_3th):
                print("Update 3th data")
                # Update past 3th data
                self.pv_past.iloc[0:self.Datas.NP_3TH-1] = self.pv_past.iloc[1:self.Datas.NP_3TH] # Discart the oldest sample
                self.load_past.iloc[0:self.Datas.NP_3TH-1] = self.load_past.iloc[1:self.Datas.NP_3TH] # Discart the oldest sample
                
                self.pv_past.at[self.Datas.NP_3TH, 'data'] = self.Datas.p_pv # Update the new PV sample with the actual data
                self.load_past.at[self.Datas.NP_3TH, 'data'] = self.Datas.p_load # Update the new load sample with the actual data
                
                print(f"p_pv mensuremented: {self.pv_past.at[self.Datas.NP_3TH, 'data']}")
                print(f"p_load mensuremented: {self.load_past.at[self.Datas.NP_3TH, 'data']}")
                
                # Update the first row of the forecast DataFrames
                ## The first row of the forecast DataFrames is a measurement.
                self.pv_forecasted.loc[0, 'data'] = self.Datas.p_pv
                self.load_forecasted.loc[0, 'data'] = self.Datas.p_load

                # Run 3th forecast
                # self.Datas.I_3th.loc[1:, 'pv_forecasted']   = self.forecast.predict_pv(self.Datas.P_3th[:, 'p_pv'])
                # self.Datas.I_3th.loc[1:, 'load_forecasted'] = self.forecast.predict_load(self.Datas.P_3th[:, 'p_load'])

                self.pv_forecasted.iloc[1:]   = mmpw(self.pv_past, self.Datas.NP_3TH)
                self.load_forecasted.iloc[1:] = mmpw(self.load_past, self.Datas.NP_3TH)
                
                print("[run] Forecas realized")
                # Run optmization 3th
                results_3th = pd.DataFrame(index=range(self.Datas.NP_3TH), columns=['p_bat_sch', 'k_pv_sch'])
                OF_3th      = 0
                
                
                plt.figure(figsize=(10, 5))
                time_steps = list(range(self.Datas.NP_3TH))
                plt.plot(time_steps, self.pv_forecasted['data'].values, label = 'pv_forecasted')
                plt.plot(time_steps, self.load_forecasted['data'].values, label = 'load_forecasted')
                plt.table("Forecast")
                plt.legend()
                plt.grid()
                
                results_3th, OF_3th = self.run_3th_optimization()
                self.Datas.k_pv_sch     = results_3th.loc[0, 'k_pv_sch']
                self.Datas.p_bat_sch    = results_3th.loc[0, 'p_bat_sch']
                # self.Datas.p_grid_sch = results_3th.loc[0, 'p_grid_sch'] # Not used
                
                plt.figure(figsize=(10, 5))
                time_steps = list(range(self.Datas.NP_3TH))
                plt.plot(time_steps, results_3th['p_bat_sch'].values, label = 'p_bat_sch')
                plt.plot(time_steps, results_3th['k_pv_sch'].values, label = 'k_pv_sch')
                plt.table("Schedule")
                plt.legend()
                plt.grid()
                
            # Run 2th optmization
            if (self.is_it_time_to_run_2th() and self.enable_run_2th):

                # Run optimization 2th
                self.run_2th_optimization(self.Datas)
                
                self.send_control_signals()

            # Check if it's time to stop the code
            self.enable_run_EMS = False # To run only a time
            if not self.enable_run_EMS:
                break
        
            self.t = self.t + 1
        
        plt.show()
            
        # self.plot_result() # Tem erro, analisar
        return self.Datas





    # =======================================================
    #    # Auxiliaries functions                            #
    # =======================================================

    # Check if is time to take new measumerements for microgrid via Mudbus
    def is_it_time_to_take_measurements(self) -> bool: 
        current_time = time.time()
        
        if (current_time - self.last_time_measurement >= self.Datas.TS_MEASUREMENT):
            print("It's time to measurement")
            self.last_time_measurement = current_time
            return True
        else:
            return False



    def is_it_time_to_run_3th(self) -> bool:
        current_time = time.time()
        if (current_time - self.last_time_3th >= self.Datas.TS_3TH):
            print("It's time to 3th")
            self.last_time_3th = current_time
            return True
        else:
            return False



    def is_it_time_to_run_2th(self) -> bool:
        current_time = time.time()
        if (current_time - self.last_time_2th >= self.Datas.TS_2TH):
            print("It's time to 2th")
            self.last_time_2th = current_time
            return True
        else:
            return False



    def run_3th_optimization(self) -> None:
        print("run_3th_optimization")
        results_3th = pd.DataFrame(index=range(self.Datas.NP_3TH), columns=['p_bat_sch', 'k_pv_sch'])
        OF_3th      = 0
        # Call optimization
        if (self.Datas.operation_mode == "CONNECTED"):
            if (self.Datas.optimization_method == "QP"):
                results_3th, OF_3th = self.qp_optimization.connected_optimization_3th(self.Datas, self.pv_forecasted, self.load_forecasted)
            elif(self.Datas.optimization_method == "MILP"):
                # self.milp_optimization.connected_optimization_3th()
                print("Dont have connected MILP")

        elif (self.Datas.operation_mode == "ISOLATED"):
            if (self.Datas.optimization_method == "QP"):
                results_3th, OF_3th = self.qp_optimization.isolated_optimization_3th(self.Datas, self.pv_forecasted, self.load_forecasted)
            elif (self.Datas.optimization_method == "MILP"):
                results_3th, OF_3th = self.milp_optimization.isolated_optimization_3th(self.Datas, self.pv_forecasted, self.load_forecasted)
            else:
                print("Don't have optimization method")
                
        else:
            print("Don't have optimization method")
    
        return results_3th, OF_3th


    def run_2th_optimization(self) -> None:
        # Update the first row of the I_2th matrix
        self.Datas.I_2th.loc[:, 'pv_forecasted'] = self.Datas.p_pv
        self.Datas.I_2th.loc[:, 'load_forecasted'] = self.Datas.p_load
        
        # Call optimization
        if (self.Datas.operation_mode == "CONNECTED"):
            if (self.Datas.optimization_method == "QP"):
                self.qp_optimization.connected_optimization_2th(self.Datas)
            elif (self.Datas.optimization_method == "MILP"):
                print("TODO: MILP Optimization")
                pass
        elif (self.Datas.operation_mode == "ISOLATED"):
            if (self.Datas.optimization_method == "QP"):
                self.qp_optimization.isolated_optimization_2th(self.Datas)
            elif (self.Datas.optimization_method == "MILP"):
                print("TODO: MILP Optimization")
                pass


    
    def get_measurements(self) -> None:
        print("get_measurements")
        wait_for_new_data = 1
        
        cmd_to_send_new_data = 1
        self.modbus_client.write_multiple_registers(0, [self.counter_mb, cmd_to_send_new_data])
        time.sleep(0.100)
        
        while wait_for_new_data == 0:
            print("Waiting for datas")
            registers = self.modbus_client.read_holding_registers(0, 9)
            
            # Check if we have new data
            cmd_to_send_new_data = int(registers[1])
            if cmd_to_send_new_data == 1:
                
                # Operation mode
                if (registers[2] == 1):
                    self.Datas.operation_mode = "CONNECTED"
                else:
                    self.Datas.operation_mode = "ISOLATED"
                
                # Datas from microgrid
                self.measurements["p_pv"]         = registers[3]/1000
                self.measurements["p_load"]       = registers[4]/1000
                self.measurements["p_grid"]       = registers[5]/1000
                self.measurements["p_bat"]        = registers[6]/1000
                self.measurements["p_sc"]         = registers[7]/1000
                self.measurements["soc_bat"]      = registers[8]/1000
                self.measurements["soc_sc"]       = registers[9]/1000
                
                print("Measurements")
                print(f'cmd_to_send_new_data:    {cmd_to_send_new_data}')
                print(f'operation_mode: {self.Datas.operation_mode}')
                print(f'p_pv:    {self.measurements["p_pv"]}')
                print(f'p_load:  {self.measurements["p_load"]}')
                print(f'p_grid:  {self.measurements["p_grid"]}')
                print(f'p_bat:   {self.measurements["p_bat"]}')
                print(f'p_sc:    {self.measurements["p_sc"]}')
                print(f'soc_bat: {self.measurements["soc_bat"]}')
                print(f'soc_sc:  {self.measurements["soc_sc"]} \n')
                
                self.counter_mb += 1
                wait_for_new_data = 0
                
            time.sleep(0.5)
        


    def send_control_signals(self) -> None:
        control_signals = [self.Datas.R_2th.loc['p_bat_2th', 0],
                           self.Datas.R_2th.loc['p_sc_2th', 0],
                           self.Datas.R_2th.loc['p_grid_2th', 0],
                           self.Datas.R_2th.loc['k_pv', 0]]
        # self.modbus_client.write_multiple_registers(10, control_signals)
    



    def plot_result(self) -> None:
        time_steps = list(range(self.Datas.NP_3TH))
        
        plt.figure(figsize=(10, 5))
        
        if (self.Datas.operation_mode == "CONNECTED"):
            print("Plot p_grid")
            plt.plot(time_steps, self.Datas.R_3th.loc[:, 'p_grid_3th'], marker='o', linestyle='-', color='r', label='Grid')
        
        plt.plot(time_steps, self.Datas.R_3th.loc[:, 'p_bat_3th'], marker='o', linestyle='-', color='b', label='Battery')
        plt.plot(time_steps, self.Datas.I_3th.loc[:, 'pv_forecasted'], marker='o', linestyle='-', color='orange', label='PV')
        plt.plot(time_steps, self.Datas.I_3th.loc[:, 'load_forecasted'], marker='o', linestyle='-', color='g', label='Load')
        plt.plot(time_steps, self.Datas.I_3th.loc[:, 'pv_forecasted']*self.Datas.R_3th.loc[:, 'k_pv_3th'], linestyle='-', color='orange', label='Load')
        plt.axhline(0, color='black', linestyle='--')
        plt.xlabel('Time (h)')
        plt.ylabel('Power (kW)')
        plt.title('Microgrid power')
        plt.legend()
        plt.grid()

        plt.figure(figsize=(10, 5))
        if (self.Datas.operation_mode == "CONNECTED"):
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
    
    data_results = EMS_instance.run()