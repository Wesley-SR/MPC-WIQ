#!/usr/bin/env python3

# Modbus/TCP server

# run this as root to listen on TCP priviliged ports (<= 1024)
# add "--host 0.0.0.0" to listen on all available IPv4 addresses of the host

# import argparse
from pyModbusTCP.server import ModbusServer, DataBank
from time import sleep
from random import uniform

if __name__ == '__main__':

    # parse args
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-H', '--host', type=str, default='localhost', help='Host (default: localhost)')
    # parser.add_argument('-p', '--port', type=int, default=502, help='TCP port (default: 502)')
    # args = parser.parse_args()
    # IP_server = '127.1.0.0'
    IP_server = 'localhost'
    port =  502

    print("host= {}".format(IP_server))
    print("port= {}".format(port))
    
    server = ModbusServer(IP_server, port, no_block=True)
    
    print(server.ServerInfo())
    try:
        print("Start server...")
        server.start()
        
        print("Server is online")
        cont_mb = [0]
        cont = 1
        address = 0
        sleep(0.05)
        print("databank = {}".format(server.data_bank.get_holding_registers(address)))
        while True:
            # The server keeps track of changes
            if cont_mb != server.data_bank.get_holding_registers(address): # old -> databank.get_words(address):
                cont_mb = server.data_bank.get_holding_registers(address)
                print("cont_mb = {}".format(cont_mb[0]))
            else:
                pass
                #print("databank = {}".format(server.data_bank.get_holding_registers(address))) # (databank.get_words(address)))
                # print(".")

            sleep(0.05)
            cont = cont + 1
    
    except Exception as error:
        print(error)
        
    finally:
        server.stop()
        print("Server is offline 2")
        