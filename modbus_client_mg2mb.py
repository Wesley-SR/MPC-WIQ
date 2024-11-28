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
        client = ModbusClient(host = host, port=port, unit_id = client_ID, debug=False, auto_open=True)
    except ValueError:
        print("Error with host or port params")
    
    # Execution variables
    counter_mb = 0
    last_counter_mb = - 1
    cmd_to_send_new_data = 0
    run = 0
    operation_mode = Datas.operation_mode
  
    run = 1
    #except Exception as e:
    #    print("Erro de conexao devido: {}".format(e))
    #    client.close()
    
    while run:
        
        number_of_register_to_read = 13
        time.sleep(0.5)
        #try:
        print(".")
        registers = client.read_holding_registers(0, number_of_register_to_read)
        counter_mb = int(registers[0])
        cmd_to_send_new_data = int(registers[1])
        if (counter_mb != last_counter_mb) and (cmd_to_send_new_data == 1):                 
            last_counter_mb = counter_mb
            cmd_to_send_new_data = 0
            
            # Read p_pv
            p_pv = int((medidas_csv.loc[counter_mb, 'p_pv'])*1000)
            # Read p_load
            p_load = int((medidas_csv.loc[counter_mb, 'p_load'])*1000)
            # Read p_bat
            # Read p_sc
            # Read p_grid
            # Read soc_bat
            # Read soc_sc
            # Battery SOC
            if counter_mb == 0:
                p_bat = Datas.p_bat
                p_sc = Datas.p_sc
                p_grid = Datas.p_grid
                soc_bat     = Datas.soc_bat
                delta_p_bat = p_bat - Datas.p_bat
            else: 
                soc_bat     = soc_bat - p_bat*Datas.TS_3TH/Datas.Q_BAT
                delta_p_bat = p_bat - p_bat
            
            
            data_to_write = [cmd_to_send_new_data, operation_mode, p_pv, p_load]
            print(f"Send data: cmd_to_send_new_data: {data_to_write[0]}, operation_mode: {data_to_write[1]}, p_pv: {data_to_write[2]}, p_load: {data_to_write[3]}")
            client.write_multiple_registers(1, data_to_write) # mg2bm doesn't touch the counter_mb (register[0])
            
            
        
        #except Exception as e:
        #    print("Erro de conexao devido: {}".format(e))
        #    client.close()
        #    break

    print("Cliente encerrado")