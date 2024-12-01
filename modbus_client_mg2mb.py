#!/usr/bin/env python3

# Esse client código lê os dados de um CSV e escreve na rede Modbus
# Fonte:
    # https://www.youtube.com/watch?v=FYPQgnQE9fk&ab_channel=Johannes4GNU_Linux
    # https://github.com/Johannes4Linux/Simple-ModbusTCP-Server/blob/master/Simple_ModbusServer.py
    # https://pymodbustcp.readthedocs.io/en/latest/examples/server.html?highlight=server
    # https://pymodbustcp.readthedocs.io/en/latest/package/class_ModbusServer.html?highlight=server#class-modbusserver

# read_register

import time

from pyModbusTCP.client import ModbusClient
import pandas as pd
from datas import Datas


if __name__ == '__main__':

    caminho_do_arquivo = "datas_1_s_completo_SNPTEE.csv"
    Datas = Datas()
    # Faz a leitura do arquivo
    medidas_csv = pd.read_csv(caminho_do_arquivo)
    
    # init modbus client
    host = 'localhost'
    port = 502
    client_ID = 1
    try:
        client = ModbusClient(host = host, port=port, unit_id = client_ID, auto_open=True)
    except ValueError:
        print("Error with host or port params")
    
    # Execution variables
    counter_mb = 0
    last_counter_mb = - 1
    updated_data_switch = 0
    got_reference_signals = False

    run = 1
    #except Exception as e:
    #    print("Erro de conexao devido: {}".format(e))
    #    client.close()
    
    
    soc_bat = 0
    soc_sc  = 0
    k_pv    = 0
    p_sc    = 0
    p_bat   = 0
    p_grid  = 0
    
    print("-----------------------------------")
    print("MODBUS MG - MODBUS MG - MODBUS MG - MODBUS MG")
    while run:
        
        
        # Check reset need
        reset = client.read_holding_registers(100, 1)[0]
        if reset == 1:
            print("\n\n\n\n\n\n")
            print("RESET \n\n\n\n\n\n")
            counter_mb = 0
            last_counter_mb = - 1
            updated_data_switch = 0
            got_reference_signals = False
            client.write_single_register(100,0)
        
        number_of_register_to_read = 18
        
        #try:
        registers = client.read_holding_registers(0, number_of_register_to_read)
        counter_mb = int(registers[0])
        updated_data_switch = int(registers[1])
        
        
        # -------------------- MEDIDAS --------------------
        if (counter_mb != last_counter_mb) and (updated_data_switch == 1):
            print(f"\ncounter_mb: {counter_mb}")
            print("Request for mensurements received")       
            print(f"registers: {registers}")
            last_counter_mb = counter_mb
            updated_data_switch = 0
            
            p_pv = medidas_csv.loc[counter_mb, 'p_pv']
            p_load = medidas_csv.loc[counter_mb, 'p_load']
            print(f"counter_mb: {counter_mb}, updated_data_switch: {updated_data_switch}, p_pv: {p_pv}, p_load: {p_load}")
            if counter_mb == 0:
                if (Datas.operation_mode == Datas.ISOLATED):
                    soc_bat = Datas.soc_bat
                    soc_sc  = Datas.soc_sc
                    k_pv    = Datas.k_pv
                    p_sc    = Datas.p_sc
                    # Power balance
                    # k_pv*p_pv + p_bat + p_sc - p_load = 0
                    p_bat = - k_pv*p_pv - p_sc + p_load
                    p_grid = 0
                else: # (Datas.operation_mode == Datas.CONNECTED):
                    pass
            else:
                if (got_reference_signals):
                    if (Datas.operation_mode == Datas.ISOLATED):
                        p_bat = p_bat_ref
                        p_sc_power_balance = - k_pv_ref*p_pv - p_bat + p_load
                        p_sc = p_sc_power_balance
                        p_grid = 0
                        soc_bat = soc_bat - p_bat*(Datas.TS_2TH/60/60)/Datas.Q_BAT
                        soc_sc = soc_sc - ((p_sc+p_sc_ref)/2)*(Datas.TS_2TH/60/60)/Datas.Q_SC
                        
                        power_balance = p_bat + k_pv*p_pv + p_sc - p_load
                        if power_balance >= -0.0001 and power_balance <= 0.0001:
                            pass
                        else:
                            print("DEU CHABU!!!!!!!!!!!!!!!!!!!!!")
                            print(f"power_balance: {power_balance} = {p_bat} + {k_pv*p_pv} + {p_sc} - {p_load}")
                            break
                    else: # (Datas.operation_mode == Datas.CONNECTED):
                        pass
                        
                    got_reference_signals = False
                        
            p_pv_to_send    = int(p_pv * Datas.MB_MULTIPLIER)
            p_load_to_send  = int(p_load * Datas.MB_MULTIPLIER)
            p_grid_to_send  = int(p_grid * Datas.MB_MULTIPLIER)
            
            p_bat_to_send   = int(p_bat * Datas.MB_MULTIPLIER)
            if p_bat_to_send < 0:
                p_bat_to_send = - p_bat_to_send
                p_bat_neg = 1
            else:
                p_bat_neg = 0
                
            p_sc_to_send    = int(p_sc * Datas.MB_MULTIPLIER)
            if p_sc_to_send < 0:
                p_sc_to_send = - p_sc_to_send
                p_sc_neg = 1
            else:
                p_sc_neg = 0
            soc_bat_to_send = int(soc_bat * Datas.MB_MULTIPLIER)
            soc_sc_to_send  = int(soc_sc * Datas.MB_MULTIPLIER)
            # 0	1	2	3	4	5	6	7	8	9	10	11
            # counter_mb	new_mb_data	operation_mode	p_pv	p_load	p_grid	p_bat	p_sc	soc_bat	soc_sc	p_bat_neg	p_sc_neg
            data_to_write = [updated_data_switch, Datas.operation_mode, p_pv_to_send, p_load_to_send, p_grid_to_send, p_bat_to_send, p_sc_to_send, soc_bat_to_send, soc_sc_to_send, p_bat_neg, p_sc_neg]
            print(f"Medidas -  p_pv: {p_pv_to_send}, p_load: {p_load_to_send}, p_grid: {p_grid_to_send}, p_bat: {p_bat_to_send}, p_sc: {p_sc_to_send}, soc_bat: {soc_bat_to_send}, soc_sc: {soc_sc_to_send}, p_bat_neg: {p_bat_neg}, p_sc_neg: {p_sc_neg}")
            
            # print(f"Send data: updated_data_switch: {data_to_write[0]}, operation_mode: {data_to_write[1]}, p_pv: {data_to_write[2]}, p_load: {data_to_write[3]}")
            # print(f"data_to_write: {data_to_write}")
            client.write_multiple_registers(1, data_to_write) # mg2bm doesn't touch the counter_mb (register[0])
        
        
        # -------------------- CONTROLE --------------------
        if (updated_data_switch == 2):
            print("Contrl signal received")
            print(f"registers: {registers}")
            got_reference_signals = True
            updated_data_switch = 0
            # 12        13          14          15          16              17
            # p_bat_ref	p_sc_ref	p_grid_ref	k_pv_ref	p_bat_ref_neg	p_sc_ref_neg
            p_bat_ref  = float(registers[12] / Datas.MB_MULTIPLIER)
            p_sc_ref   = float(registers[13] / Datas.MB_MULTIPLIER)
            p_grid_ref = float(registers[14] / Datas.MB_MULTIPLIER)
            k_pv_ref = float(registers[15] / Datas.MB_MULTIPLIER)
            p_bat_ref_neg = registers[16]
            p_sc_ref_neg = registers[17]
            
            if p_bat_ref_neg == 1:
                p_bat_ref = - p_bat_ref
            if p_sc_ref_neg == 1:
                p_sc_ref = - p_sc_ref
            
            print(f"Referencias recebidas - p_bat_ref: {p_bat_ref}, p_sc_ref: {p_sc_ref}, p_grid_ref: {p_grid_ref}, k_pv_ref: {k_pv_ref}")
            client.write_single_register(1, 3)
        
        #except Exception as e:
        #    print("Erro de conexao devido: {}".format(e))
        #    client.close()
        #    break
        time.sleep(0.01)

    print("Cliente encerrado")