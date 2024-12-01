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
        self.enable_run_2th = True
        
        # Timers
        self.t = 0 # Time that start in matrix M (in simulation)
        # Last Timers
        self.last_time_measurement = -1
        self.last_time_2th = -1
        self.last_time_3th = -900

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
        self.modbus_client.write_single_register(100, 1)
        reset = 1
        while reset == 1:
            time.sleep(0.50)
            reset = self.modbus_client.read_holding_registers(100, 1)[0]
            print(f"reset: {reset}")

        # Create DataFrame for forecast
        self.pv_forecasted_3th = pd.DataFrame(index=range(self.Datas.NP_3TH), columns=['data'])
        self.load_forecasted_3th = pd.DataFrame(index=range(self.Datas.NP_3TH), columns=['data'])
        # Create DataFrame for past datas
        self.p_pv_past_3th = pd.read_csv("data_pv_15_min_past.csv", index_col='time')
        self.p_load_past_3th = pd.read_csv("data_load_15_min_past.csv", index_col='time')
        plt.figure(figsize=(10, 5))
        time_steps = list(range(self.Datas.NP_3TH))
        plt.plot(time_steps, self.p_pv_past_3th['data'].values, label = 'p_pv_past_3th')
        plt.plot(time_steps, self.p_load_past_3th['data'].values, label = 'p_load_past_3th')
        plt.title('Passado')
        plt.legend()
        plt.grid()
        
        # Create DataFrame for forecast
        self.pv_forecasted_2th = pd.DataFrame(index=range(self.Datas.NP_2TH), columns=['data'])
        self.load_forecasted_2th = pd.DataFrame(index=range(self.Datas.NP_2TH), columns=['data'])
        
        self.results_3th = pd.DataFrame(index=range(self.Datas.NP_3TH), columns=['p_bat_sch', 'k_pv_sch', 'p_grid_sch','soc_bat'])
        self.results_2th = pd.DataFrame(index=range(self.Datas.NP_2TH), columns=['p_bat_ref', 'k_pv_ref', 'p_sc_ref', 'p_grid_ref','soc_bat', 'soc_sc'])
        self.OF_3th = 0
        self.OF_2th = 0




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
                self.p_pv_past_3th.iloc[0:self.Datas.NP_3TH-1] = self.p_pv_past_3th.iloc[1:self.Datas.NP_3TH] # Discart the oldest sample
                self.p_load_past_3th.iloc[0:self.Datas.NP_3TH-1] = self.p_load_past_3th.iloc[1:self.Datas.NP_3TH] # Discart the oldest sample
                
                self.p_pv_past_3th.at[self.Datas.NP_3TH, 'data'] = self.Datas.p_pv # Update the new PV sample with the actual data
                self.p_load_past_3th.at[self.Datas.NP_3TH, 'data'] = self.Datas.p_load # Update the new load sample with the actual data
                
                print(f"p_pv mensuremented: {self.p_pv_past_3th.at[self.Datas.NP_3TH, 'data']}")
                print(f"p_load mensuremented: {self.p_load_past_3th.at[self.Datas.NP_3TH, 'data']}")
                
                # Update the first row of the forecast DataFrames
                ## The first row of the forecast DataFrames is a measurement.
                self.pv_forecasted_3th.loc[0, 'data'] = self.Datas.p_pv
                self.load_forecasted_3th.loc[0, 'data'] = self.Datas.p_load

                # Run 3th forecast
                self.pv_forecasted_3th.iloc[1:]   = mmpw(self.p_pv_past_3th, self.Datas.NP_3TH)
                self.load_forecasted_3th.iloc[1:] = mmpw(self.p_load_past_3th, self.Datas.NP_3TH)
                
                plt.figure(figsize=(10, 5))
                time_steps = list(range(self.Datas.NP_3TH))
                plt.plot(time_steps, self.pv_forecasted_3th['data'].values, label = 'pv_forecasted_3th')
                plt.plot(time_steps, self.load_forecasted_3th['data'].values, label = 'load_forecasted_3th')
                plt.title("Forecast")
                plt.legend()
                plt.grid()

                self.run_3th_optimization()
                self.Datas.k_pv_sch     = self.results_3th.loc[0, 'k_pv_sch']
                self.Datas.p_bat_sch    = self.results_3th.loc[0, 'p_bat_sch']
                if self.Datas.p_bat_sch >= 0:
                    self.Datas.p_bat_dis_sch = self.Datas.p_bat_sch
                    self.Datas.p_bat_ch_sch  = 0
                else:
                    self.Datas.p_bat_dis_sch = 0
                    self.Datas.p_bat_ch_sch  = self.Datas.p_bat_sch
                # self.Datas.p_grid_sch = self.results_3th.loc[0, 'p_grid_sch'] # Not used
                print(f"OF_3th: {self.OF_3th}")
                plt.figure(figsize=(10, 5))
                time_steps = list(range(self.Datas.NP_3TH))
                plt.plot(time_steps, self.results_3th['p_bat_sch'].values, label = 'p_bat_sch')
                plt.plot(time_steps, self.results_3th['k_pv_sch'].values, label = 'k_pv_sch')
                plt.title("Schedule")
                plt.legend()
                plt.grid()
                
            # Run 2th optmization
            if (self.is_it_time_to_run_2th() and self.enable_run_2th):

                # Run optimization 2th
                self.run_2th_optimization()
                self.send_control_signals()
                
                print(f"OF_2th: {self.OF_2th}")
                plt.figure(figsize=(10, 5))
                time_steps = list(range(self.Datas.NP_2TH))
                plt.plot(time_steps, self.results_2th['p_bat_ref'].values, label = 'p_bat_ref')
                plt.plot(time_steps, self.results_2th['k_pv_ref'].values, label = 'k_pv_ref')
                plt.plot(time_steps, self.results_2th['p_sc_ref'].values, label = 'p_sc_ref')
                plt.title("Reference")
                plt.legend()
                plt.grid()
                

            # Check if it's time to stop the code
            self.enable_run_EMS = bool(input("Pressione 1 para continuar e 0 para finalizar: "))
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
        # current_time = time.time()
        current_time = self.t
        if (current_time - self.last_time_measurement >= self.Datas.TS_MEASUREMENT):
            print("It's time to take measurement")
            self.last_time_measurement = current_time
            return True
        else:
            print("It`s not time to take measurement")
            return False



    def is_it_time_to_run_3th(self) -> bool:
        # current_time = time.time() # For real control
        current_time = self.t # For simulation
        if (current_time - self.last_time_3th >= self.Datas.TS_3TH):
            print("It's time to 3th")
            self.last_time_3th = current_time
            return True
        else:
            return False



    def is_it_time_to_run_2th(self) -> bool:
        # current_time = time.time() # For real control
        current_time = self.t # For simulation
        if (current_time - self.last_time_2th >= self.Datas.TS_2TH):
            print("It's time to 2th")
            self.last_time_2th = current_time
            return True
        else:
            return False



    def run_3th_optimization(self) -> None:
        print("run_3th_optimization")
        # Call optimization
        if (self.Datas.operation_mode == self.Datas.CONNECTED):
            if (self.Datas.optimization_method == "QP"):
                self.results_3th, self.OF_3th = self.qp_optimization.connected_optimization_3th(self.Datas, self.pv_forecasted_3th, self.load_forecasted_3th)
            elif(self.Datas.optimization_method == "MILP"):
                # self.milp_optimization.connected_optimization_3th()
                print("Dont have connected MILP")

        elif (self.Datas.operation_mode == self.Datas.ISOLATED):
            if (self.Datas.optimization_method == "QP"):
                self.results_3th, self.OF_3th = self.qp_optimization.isolated_optimization_3th(self.Datas, self.pv_forecasted_3th, self.load_forecasted_3th)
            elif (self.Datas.optimization_method == "MILP"):
                self.results_3th, self.OF_3th = self.milp_optimization.isolated_optimization_3th(self.Datas, self.pv_forecasted_3th, self.load_forecasted_3th)
            else:
                print("Don't have optimization method")
                
        else:
            print("Don't have optimization method")


    def run_2th_optimization(self) -> None:
        self.pv_forecasted_2th['data'] = self.Datas.p_pv
        self.load_forecasted_2th['data'] = self.Datas.p_load
        
        # Call optimization
        if (self.Datas.operation_mode == self.Datas.CONNECTED):
            if (self.Datas.optimization_method == "QP"):
                self.results_2th, self.OF_2th = self.qp_optimization.connected_optimization_2th(self.Datas, self.pv_forecasted_2th, self.load_forecasted_2th)
            elif (self.Datas.optimization_method == "MILP"):
                print("TODO: MILP Optimization")
                pass
        elif (self.Datas.operation_mode == self.Datas.ISOLATED):
            if (self.Datas.optimization_method == "QP"):
                self.results_2th, self.OF_2th = self.qp_optimization.isolated_optimization_2th(self.Datas, self.pv_forecasted_2th, self.load_forecasted_2th)
            elif (self.Datas.optimization_method == "MILP"):
                self.results_2th, self.OF_2th = self.milp_optimization.isolated_optimization_2th(self.Datas, self.pv_forecasted_2th, self.load_forecasted_2th)

    
    def get_measurements(self) -> None:
        print("3) get_measurements")
        wait_for_new_data = 1
        
        updated_data_switch = 1
        self.modbus_client.write_multiple_registers(0, [self.counter_mb, updated_data_switch])
        send_request_time = time.time()
        time.sleep(0.100)
        
        while wait_for_new_data == 1:
            print("Waiting for datas")
            registers = self.modbus_client.read_holding_registers(0, 15)
            # Check if we have new data
            updated_data_switch = int(registers[1])
            if updated_data_switch == 0:
                print(f"[updated_data_switch = {updated_data_switch}] registers: {registers}")
                self.counter_mb += 1
                wait_for_new_data = 0
                
                # Operation mode
                if (registers[2] == 1):
                    print("CONECTADO lido do MODBUS")
                    self.Datas.operation_mode = self.Datas.CONNECTED
                else:
                    self.Datas.operation_mode = self.Datas.ISOLATED
                
                # Datas from microgrid
                self.Datas.p_pv         = registers[3]/self.Datas.MB_MULTIPLIER
                self.Datas.p_load       = registers[4]/self.Datas.MB_MULTIPLIER
                self.Datas.p_grid       = registers[5]/self.Datas.MB_MULTIPLIER
                self.Datas.p_bat        = registers[6]/self.Datas.MB_MULTIPLIER
                self.Datas.p_sc         = registers[7]/self.Datas.MB_MULTIPLIER
                self.Datas.soc_bat      = registers[8]/self.Datas.MB_MULTIPLIER
                self.Datas.soc_sc       = registers[9]/self.Datas.MB_MULTIPLIER
                
                print("Measurements")
                print(f'updated_data_switch:    {updated_data_switch}')
                print(f'operation_mode: {self.Datas.operation_mode}')
                print(f'p_pv:    {self.Datas.p_pv}')
                print(f'p_load:  {self.Datas.p_load}')
                print(f'p_grid:  {self.Datas.p_grid}')
                print(f'p_bat:   {self.Datas.p_bat}')
                print(f'p_sc:    {self.Datas.p_sc}')
                print(f'soc_bat: {self.Datas.soc_bat}')
                print(f'soc_sc:  {self.Datas.soc_sc} \n')
                
            time.sleep(0.1)
            if (send_request_time - time.time() > 0.6):
                self.get_measurements()



    def send_control_signals(self) -> None:
        print("Send control signals")
        is_signal_reference = 2
        existe_nan = self.results_2th.isna().any().any()
        if existe_nan:
            print(f"existe_nan ---------------")
            print(self.results_2th)
        
        p_bat_ref  = int((self.results_2th.loc[0, 'p_bat_ref']) * self.Datas.MB_MULTIPLIER)
        p_sc_ref   = int((self.results_2th.loc[0, 'p_sc_ref']) * self.Datas.MB_MULTIPLIER)
        p_grid_ref = int((self.results_2th.loc[0, 'p_grid_ref']) * self.Datas.MB_MULTIPLIER)
        k_pv_ref   = int((self.results_2th.loc[0, 'k_pv_ref']) * self.Datas.MB_MULTIPLIER)
        control_signals = [p_bat_ref,
                           p_sc_ref,
                           p_grid_ref,
                           k_pv_ref]
        
        self.modbus_client.write_multiple_registers(10, control_signals)
        time.sleep(0.1)
        wait_for_confirmation = 1
        confirmation = 0
        waint = 1
        while (wait_for_confirmation == 1):
            confirmation = self.modbus_client.read_holding_registers(1,1)[0]
            if confirmation == 3:
                wait_for_confirmation = 0
                print("Veio a confirmacao que recebeu o controle")
            else:
                time.sleep(0.1)
                waint += 1
                if waint > 10:
                    self.modbus_client.write_single_register(1, is_signal_reference)
                    waint = 0




    def plot_result(self) -> None:
        time_steps = list(range(self.Datas.NP_3TH))
        
        plt.figure(figsize=(10, 5))
        
        if (self.Datas.operation_mode == "CONNECTED"):
            print("Plot p_grid")
            plt.plot(time_steps, self.Datas.R_3th.loc[:, 'p_grid_3th'], marker='o', linestyle='-', color='r', label='Grid')
        
        plt.plot(time_steps, self.Datas.R_3th.loc[:, 'p_bat_3th'], marker='o', linestyle='-', color='b', label='Battery')
        plt.plot(time_steps, self.pv_forecasted_3th.loc[:, 'pv_forecasted_3th'], marker='o', linestyle='-', color='orange', label='PV')
        plt.plot(time_steps, self.load_forecasted_3th.loc[:, 'load_forecasted_3th'], marker='o', linestyle='-', color='g', label='Load')
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