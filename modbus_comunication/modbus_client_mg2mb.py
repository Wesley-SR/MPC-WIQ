#!/usr/bin/env python3

# Esse client código lê os dados de um CSV e escreve na rede Modbus
# Fonte:
    # https://www.youtube.com/watch?v=FYPQgnQE9fk&ab_channel=Johannes4GNU_Linux
    # https://github.com/Johannes4Linux/Simple-ModbusTCP-Server/blob/master/Simple_ModbusServer.py
    # https://pymodbustcp.readthedocs.io/en/latest/examples/server.html?highlight=server
    # https://pymodbustcp.readthedocs.io/en/latest/package/class_ModbusServer.html?highlight=server#class-modbusserver

# read_register
# read 10 registers and print result on stdout

import time

from pyModbusTCP.client import ModbusClient
import pandas as pd

if __name__ == '__main__':

    # caminho = "C:\Users\wesle\Dropbox\Lactec\DADOS\MPC_MATLAB_Peak_shaving_Suavizacao_Regulacao\Curva_carga_dia_08_11_17.csv"
    caminho_do_arquivo = "Dados_medidos.csv"
    
    # Faz a leitura do arquivo
    medidas_csv = pd.read_csv(caminho_do_arquivo)
    
    # init modbus client
    host = 'localhost'
    # host = '127.1.0.0'
    port = 502
    client_ID = 2
    
    try:
        client = ModbusClient(host = host, port=port, unit_id = client_ID, debug=False, auto_open=True)
        # print("Client info: {}".format())
    except ValueError:
        print("Error with host or port params")
    
    # main read loop
    Np_2th = 96
    contador = Np_2th
    
    # Alimentador das medições do p_pv_carga (P), p_load_carga (Q) e P_pv (PV)
    while True:
        
        # Lê a linha atual a partir da linha 0 (substituir por medições online)
        N = medidas_csv.iloc[contador].values
        M = [int(N[0]), int(N[1]), int(N[2]), int(N[3])] # Amostra, P, Q e PV
        amostra = M[0]
        p_pv = M[1]
        p_load = M[2]
        address = 5
        time.sleep(1)
        try:
            
            # Leitura
            print("\n\n")
            registers = client.read_holding_registers(address, 6)
            # if success display registers
            if registers:
                print("Read: Amostra = {amostra}, P = {P},   Q = {Q},   PV = {PV}".format(amostra=registers[0], P=registers[1], Q=registers[2], PV=registers[3]))
            else:
                print('unable to read registers \n')            

            # Escrita
            print("Write: Amostra = {amostra}, P = {P},   Q = {Q},   PV = {PV}".format(amostra=amostra, P=p_pv, Q=p_load, PV=P_pv))
            client.write_multiple_registers(address,M)
            
            # Leitura
            registers = client.read_holding_registers(address, 6)
            # if success display registers
            if registers:
                print("Read: Amostra = {amostra}, P = {P},   Q = {Q},   PV = {PV}".format(amostra=registers[0], P=registers[1], Q=registers[2], PV=registers[3]))
            else:
                print('unable to read registers \n')

            contador += 1
            if contador > 2*Np_2th:
                contador = 1
        except:
            print("Erro de conexao")
            client.close()
            break

    
    print("Cliente encerrado")