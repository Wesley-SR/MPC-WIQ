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

if __name__ == '__main__':

    caminho_do_arquivo = "datas.csv"
    
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
    Np_2th = 288
    counter_mb = 0
    last_counter_mb = 0
    cmd_to_send_new_data = 0
    run = 0

    # Wait for EMS_main command to start
    # The control system will send new_mb_data = 0 to start communication
    # while new_mb_data == 1:
    #     registers = client.read_holding_registers(0, 2)
    #     new_mb_data = int(registers[1])
    #     time.sleep(0.5)
    
    
    # counter_mb = int(registers[0])
    # new_mb_data = 1
    # p_pv = int((medidas_csv.loc[counter_mb, 'p_pv'])*1000)
    # p_load = int((medidas_csv.loc[counter_mb, 'p_load'])*1000)
    # data_to_write = [new_mb_data, p_pv, p_load]
    # print("Send first data: {}  {}  {}".format(data_to_write[0], data_to_write[1], data_to_write[2]))
    # # Write first new data
    # client.write_multiple_registers(1, data_to_write)
    
    run = 1
    #except Exception as e:
    #    print("Erro de conexao devido: {}".format(e))
    #    client.close()
    
    while run:
        
        number_of_register_to_read = 9
        time.sleep(0.5)
        #try:
        print(".")
        registers = client.read_holding_registers(0, 2)
        counter_mb = int(registers[0])
        cmd_to_send_new_data = int(registers[1])
        if (counter_mb != last_counter_mb) and (cmd_to_send_new_data == 1):                 
            last_counter_mb = counter_mb
            cmd_to_send_new_data = 0
            p_pv = int((medidas_csv.loc[counter_mb, 'p_pv'])*1000)
            p_load = int((medidas_csv.loc[counter_mb, 'p_load'])*1000)
            data_to_write = [cmd_to_send_new_data, p_pv, p_load]
            print("Send data: cmd_to_send_new_data: {}, p_pv: {}, p_load: {}".format(data_to_write[0], data_to_write[1], data_to_write[2]))
            client.write_multiple_registers(1, data_to_write) # mg2bm doesn't touch the counter_mb
            
            
        
        #except Exception as e:
        #    print("Erro de conexao devido: {}".format(e))
        #    client.close()
        #    break

    print("Cliente encerrado")