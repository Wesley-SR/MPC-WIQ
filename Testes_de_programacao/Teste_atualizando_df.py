import pandas as pd



P_3th = pd.DataFrame({'p_pv': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                            'p_load': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]})

Np = len(P_3th)
novo_pv = 11.5
novo_load = 3.43

P_3th.iloc[0:Np-1] = P_3th.iloc[1:Np]

P_3th.at[Np, 'p_pv'] = novo_pv
P_3th.at[Np, 'p_load'] = novo_load


print(P_3th.loc[:, 'p_pv'])