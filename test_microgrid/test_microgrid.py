"""
Author: Wesley da Silva Rodrigues
Source: https://github.com/ahalev/python-microgrid/tree/master
Date: 2024/01/15
Description: This code simulates a microgrid
"""

import numpy as np
import pandas as pd

np.random.seed(0)

from pymgrid import Microgrid
from pymgrid.modules import (
    BatteryModule,
    LoadModule,
    RenewableModule,
    GridModule)

small_battery = BatteryModule(min_capacity=10, # Cmax
                              max_capacity=100, # Cmin
                              max_charge=50, # A or kW?
                              max_discharge=50, # A or kW?
                              efficiency=0.9,
                              init_soc=0.2)

large_battery = BatteryModule(min_capacity=10,
                              max_capacity=1000,
                              max_charge=10,
                              max_discharge=10,
                              efficiency=0.7,
                              init_soc=0.3)

# load_ts = 100+100*np.random.rand(7) # random load data in the range [100, 200].
# pv_ts = 200*np.random.rand(7) # random pv data in the range [0, 200].
load_ts = [20.3, 20, 20, 20, 20, 20, 20] # random load data in the range [100, 200].
pv_ts =   [10,  10, 10, 10, 10, 10, 10] # random pv data in the range [0, 200].

load = LoadModule(time_series=load_ts)

pv = RenewableModule(time_series=pv_ts)

grid_ts = [0.2, 0.1, 0.5] * np.ones((7, 3))

grid = GridModule(max_import=100,
                  max_export=100,
                  time_series=grid_ts)

modules = [
    small_battery, 
    large_battery,
    ('pv', pv),
    load,
    grid]

microgrid = Microgrid(modules)

microgrid.reset()
# microgrid.state_series.to_frame()

print("MICROGRID")
print("{}\n\n\n".format(microgrid))
print("PV")
print("{}\n\n\n".format(microgrid.modules.pv)) 
print("CONTROLLABLE")
print("{}\n\n\n".format(microgrid.controllable))
print("EMPTY ACTION")
print("{}\n\n\n".format(microgrid.get_empty_action()))
print("RESET")
print("{}\n\n\n".format(microgrid.reset()))
print("STATE SERIES")
print("{}\n\n\n".format(microgrid.state_series()))


load = -1.0 * microgrid.modules.load.item().current_load
pv = microgrid.modules.pv.item().current_renewable
net_load = load + pv # negative if load demand exceeds pv
if net_load > 0:
    net_load = 0.0

print("\n\n\n net_load = load + pv")
print("{} = {} + {}".format(net_load, load, pv))

battery_0_discharge = min(-1*net_load, microgrid.modules.battery[0].max_production)
net_load += battery_0_discharge

battery_1_discharge = min(-1*net_load, microgrid.modules.battery[1].max_production)
net_load += battery_1_discharge

grid_import = min(-1*net_load, microgrid.modules.grid.item().max_production)

control = {"battery" : [battery_0_discharge, battery_1_discharge],
           "grid": [grid_import]}

print("\n\n\n CONTROL")
print(control)

obs, reward, done, info = microgrid.run(control, normalized=False)
print("\n\n\n {} \n {} \n {} \n {}".format(obs, reward, done, info))

print("\n\n\n LOAD 0")
print(microgrid.log.loc[:, pd.IndexSlice['load', 0, :]])
print("\n\n\n PV")
print(microgrid.log.loc[:, pd.IndexSlice['pv', 0, :]])
print("\n\n\n BATTERY")
print(microgrid.log.loc[:, 'battery'])

# microgrid.reset()
for _ in range(6):
    microgrid.run(microgrid.sample_action(strict_bound=True))


print("\n\n\n LOAD 0")
print(microgrid.log.loc[:, pd.IndexSlice['load', 0, :]])
print("\n\n\n PV")
print(microgrid.log.loc[:, pd.IndexSlice['pv', 0, :]])
print("\n\n\n BATTERY")
print(microgrid.log.loc[:, 'battery'])

microgrid.log[[('load', 0, 'load_met'), 
               ('pv', 0, 'renewable_used'),
               ('grid', 0, 'grid_import'),
               ('balancing', 0, 'loss_load')]].droplevel(axis=1, level=1).plot()