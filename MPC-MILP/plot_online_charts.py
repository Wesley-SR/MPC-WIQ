# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 08:56:02 2022

@author: wesley
"""


import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import seaborn as sns


# import seaborn as sns
# sns.set()




def run_online_plot_charts(ONLINE_OUT, pesos):
    
    
    dpi = 1200 # Para apresentações
    # dpi = 120 # Para visualização rápida
    
    peso_imp = pesos.loc[0, 'peso_imp']
    peso_exp = pesos.loc[0, 'peso_exp']
    peso_est = pesos.loc[0, 'peso_est']
    peso_bikes = pesos.loc[0, 'peso_bikes']
    
    valor_aluguel_por_hora = 2 # [R$]
    ts = 0.25 # [Hora]
    aluguel_por_amostra = valor_aluguel_por_hora*ts
    
    
    
    # ============================================================================#
    # MONTAR VETOR TEMPO
    cont = 0
    h = 0
    m = 0
    for k in range(0,96):
        if m == 0:
            ONLINE_OUT.loc[k,'time_plot'] = str('{hour}:00'.format(hour = h))
        else:    
            ONLINE_OUT.loc[k,'time_plot'] = str('{hour}:{minute}'.format(hour = h, minute = m))
        cont += 1
        m += 15
        if cont > 3:
            m = 0
            h += 1
            cont = 0
    
    
    # ============================================================================#
    # CALCULA POTÊNCIA TOTAL DAS BIKES E CONEXÃO TOTAL DAS BIKES
    # CALCULA O VALOR GANHO COM ALUGUEL
    # CALCULA O VALOR GANHO COM ENERGIA EXPORTADA
    
    ONLINE_OUT.loc[0,'SOC_bike_previsao_total'] = 0
    ONLINE_OUT.loc[0,'cx_bike_previsao_total'] = 0
    ONLINE_OUT.loc[0,'SOC_bike_real_total'] = 0
    ONLINE_OUT.loc[0,'cx_bike_real_total'] = 0
    
    ONLINE_OUT.loc[0,'p_ch_bike_total'] = 0
    ONLINE_OUT.loc[0,'p_dc_bike_total'] = 0
    
    ONLINE_OUT.loc[0,'ganho_aluguel'] = 0
    ONLINE_OUT.loc[0,'ganho_pot_exp'] = (ONLINE_OUT.loc[0,'p_rede_exp']*ONLINE_OUT.loc[0,'custo_energia_exp'] - ONLINE_OUT.loc[0,'p_rede_imp']*ONLINE_OUT.loc[0,'custo_energia_imp'])*ts # Ganho com potência exportada
    ONLINE_OUT.loc[0,'ganho_total'] = 0
    
    ONLINE_OUT.loc[0,'p_rede'] = 0
    ONLINE_OUT.loc[0,'p_rede_ref'] = 0
    
    ONLINE_OUT.loc[k,'p_bike_total'] = 0
    ONLINE_OUT.loc[:,'p_est_total'] = 0
    
       
    for k in range(0,96):
        soc_total_real = 0
        cx_total_real = 0
        soc_total_previsao = 0
        cx_total_previsao = 0
        P_ch_bike_total = 0
        P_dc_bike_total = 0
        
        for b in range(0,10):
            soc_total_real += ONLINE_OUT.loc[k,'soc_bike_real_{}'.format(b)]
            cx_total_real += ONLINE_OUT.loc[k,'cx_bike_real_{}'.format(b)]
            soc_total_previsao += ONLINE_OUT.loc[k,'soc_bike_previsao_{}'.format(b)]
            cx_total_previsao += ONLINE_OUT.loc[k,'cx_bike_previsao_{}'.format(b)]
            
            P_ch_bike_total += ONLINE_OUT.loc[k,'p_ch_bike_{}'.format(b)]
            P_dc_bike_total += ONLINE_OUT.loc[k,'p_dc_bike_{}'.format(b)]
        if cx_total_real > 0:        
            ONLINE_OUT.loc[k,'SOC_bike_real_total'] = soc_total_real/cx_total_real
            ONLINE_OUT.loc[k,'SOC_bike_previsao_total'] = soc_total_previsao/cx_total_previsao
        elif cx_total_real == 0:
            ONLINE_OUT.loc[k,'SOC_bike_real_total'] = 1
            ONLINE_OUT.loc[k,'SOC_bike_previsao_total'] = 1
        
        ONLINE_OUT.loc[k,'cx_bike_real_total'] = cx_total_real/10
        ONLINE_OUT.loc[k,'cx_bike_previsao_total'] = cx_total_previsao/10
        ONLINE_OUT.loc[k,'p_ch_bike_total'] = P_ch_bike_total
        ONLINE_OUT.loc[k,'p_dc_bike_total'] = P_dc_bike_total
        
        ONLINE_OUT.loc[k,'p_bike_total'] = P_dc_bike_total - P_ch_bike_total
        ONLINE_OUT.loc[:,'p_est_total'] = ONLINE_OUT.loc[:,'p_dc_est'] - ONLINE_OUT.loc[:,'p_ch_est']
        
        if k > 0:
            ONLINE_OUT.loc[k,'ganho_aluguel'] = ONLINE_OUT.loc[k-1,'ganho_aluguel'] + (10-cx_total_real)*aluguel_por_amostra
            ONLINE_OUT.loc[k,'ganho_pot_exp'] = ONLINE_OUT.loc[k-1,'ganho_pot_exp'] + (ONLINE_OUT.loc[k,'p_rede_exp']*ONLINE_OUT.loc[k,'custo_energia_exp'] - ONLINE_OUT.loc[k,'p_rede_imp']*ONLINE_OUT.loc[k,'custo_energia_imp'])*ts
            ONLINE_OUT.loc[k,'ganho_total'] = ONLINE_OUT.loc[k,'ganho_aluguel'] + ONLINE_OUT.loc[k,'ganho_pot_exp']
        
        ONLINE_OUT.loc[k,'p_rede'] = ONLINE_OUT.loc[k,'p_rede_imp'] - ONLINE_OUT.loc[k,'p_rede_exp']
        ONLINE_OUT.loc[k,'p_rede_ref'] = ONLINE_OUT.loc[k,'p_rede_imp_ref'] - ONLINE_OUT.loc[k,'p_rede_exp_ref']
    
    
    
    
    # ============================================================================#
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(1, 1)
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[:, :])
    ax.set_title(r'Otimização ONline, pesos: $\alpha_{{IMP}}={peso_imp}$, $\alpha_{{EXP}}={peso_exp}$, $\alpha_{{est}}={peso_est}$, $\alpha_{{bike}}={peso_bikes}$'.format(peso_imp=peso_imp, peso_exp=peso_exp, peso_est=peso_est, peso_bikes = peso_bikes),fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    ax.plot(ONLINE_OUT.loc[:,'p_rede_imp_ref'], label = 'Pot. Imp. referência [kW]', linestyle='dashed', drawstyle="steps", linewidth=1, c = 'red')
    ax.plot(ONLINE_OUT.loc[:,'p_rede_imp'], label = 'Pot. Imp. [kW]', drawstyle="steps", linewidth=0.8, c = 'darkred')
    ax.plot(ONLINE_OUT.loc[:,'p_rede_exp_ref'], label = 'Pot. Exp. referência [kW]', linestyle='dashed', drawstyle="steps", linewidth=1, c = 'dodgerblue')
    ax.plot(ONLINE_OUT.loc[:,'p_rede_exp'], label = 'Pot. Exp. [kW]', drawstyle="steps", linewidth=0.3, c = 'navy')
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'PV_real'], label = 'PV real [kW]', drawstyle="steps", linewidth=0.8, c = 'orange')
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'PV_previsao'], label = 'Previsão do PV em tempo real [kW]',drawstyle="steps", linestyle="dashed", linewidth=0.3, c = 'green')
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'PV_previsao_off'], label = 'Previsão offline do PV [kW]',drawstyle="steps", linewidth=0.3, c = 'hotpink')
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'load_real'], label = 'Demanda [kW]',drawstyle="steps", linewidth=0.3)
    
    ax.plot(ONLINE_OUT.loc[:,'p_ch_bike_total'], label = 'Pot. carga bike total [kW]', drawstyle="steps", linewidth=0.8, c = 'y')
    ax.plot(ONLINE_OUT.loc[:,'p_dc_bike_total'], label = 'Pot. descarga bike total [kW]', drawstyle="steps", linewidth=0.8, c = 'black')
    ax.plot(ONLINE_OUT.loc[:,'p_ch_est'], label = 'Pot. carga est [kW]', drawstyle="steps", linewidth=0.8, c = 'green')
    ax.plot(ONLINE_OUT.loc[:,'p_dc_est'], label = 'Pot. descarga est [kW]', drawstyle="steps",linestyle='dashed', linewidth=0.8, c = 'green')
    
    # Altera o estilo do gráfico
    ax.tick_params(axis='x', which='major', labelsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.legend(loc='upper left',prop={'size': 8})
    ax.tick_params(axis='x', rotation=0)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    '''SALVAR FIGURA'''
    name_figure = "Results/MPC_seguimento_tragetoria_e_todas_potencias.png"
    fig.set_size_inches(10, 5)
    plt.savefig(name_figure, format="png", dpi=dpi)






    # ============================================================================#
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(1, 1)
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[:, :])
    ax.set_title(r'Otimização ONline, pesos: $\alpha_{{IMP}}={peso_imp}$, $\alpha_{{EXP}}={peso_exp}$, $\alpha_{{est}}={peso_est}$, $\alpha_{{bike}}={peso_bikes}$'.format(peso_imp=peso_imp, peso_exp=peso_exp, peso_est=peso_est, peso_bikes = peso_bikes),fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'p_rede_ref'], label = 'Pot. referência [kW]', drawstyle="steps", linewidth=1)
    ax.plot(ONLINE_OUT.loc[:,'p_rede'], label = 'Pot. rede [kW]', drawstyle="steps", linewidth=0.3, c = 'navy')
    ax.plot(ONLINE_OUT.loc[:,'PV_real'], label = 'PV real [kW]', drawstyle="steps", linewidth=0.8)
    ax.plot(ONLINE_OUT.loc[:,'load_real'], label = 'Demanda real [kW]',drawstyle="steps", linewidth=0.3)
    ax.plot(ONLINE_OUT.loc[:,'p_bike_total'], label = 'Pot. bike total [kW]', drawstyle="steps", linewidth=0.8)
    ax.plot(ONLINE_OUT.loc[:,'p_est_total'], label = 'Pot. est [kW]', drawstyle="steps", linewidth=0.8)
    
    # Altera o estilo do gráfico
    ax.tick_params(axis='x', which='major', labelsize=5)
    ax.tick_params(axis='y', which='major', labelsize=5)
    ax.legend(loc='upper left',prop={'size': 8})
    ax.tick_params(axis='x', rotation=0)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(30))
    ax.yaxis.set_major_locator(plt.MaxNLocator(40))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    '''SALVAR FIGURA'''
    name_figure = "Results/MPC_todas_as_potencias.png"
    fig.set_size_inches(10, 5)
    plt.savefig(name_figure, format="png", dpi=dpi)

    
    
    
    
    
    # ============================================================================#
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(2, 2)
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[0, :])
    ax.set_title("Seguimento de trajetória",fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], -ONLINE_OUT.loc[:,'p_rede_imp_ref'], label = 'Pot. Imp. referência [kW]', linestyle='dashed', drawstyle="steps", linewidth=1, c = 'red')
    ax.plot(-ONLINE_OUT.loc[:,'p_rede_imp'], label = 'Pot. Imp. [kW]', drawstyle="steps", linewidth=0.8, c = 'darkred')
    ax.plot(ONLINE_OUT.loc[:,'p_rede_exp_ref'], label = 'Pot. Exp. referência [kW]', linestyle='dashed', drawstyle="steps", linewidth=1, c = 'dodgerblue')
    ax.plot(ONLINE_OUT.loc[:,'p_rede_exp'], label = 'Pot. Exp. [kW]', drawstyle="steps", linewidth=0.8, c = 'navy')
    ax.plot(ONLINE_OUT.loc[:,'custo_energia_imp'], label = 'Tarifa [R\$/kW]', drawstyle="steps", linewidth=0.3, c = 'orange')

    # Altera o estilo do gráfico
    ax.tick_params(axis='x', which='major', labelsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.legend(loc='upper left',prop={'size': 8})
    ax.tick_params(axis='x', rotation=0)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[1, :])
    ax.set_title("PV real, previsão do Online e Offline",fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'PV_real'], label = 'PV real [kW]', drawstyle="steps", linewidth=0.8, c = 'orange')
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'PV_previsao'], label = 'Previsão do PV em tempo real [kW]',drawstyle="steps", linestyle="dashed", linewidth=0.3, c = 'green')
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'PV_previsao_off'], label = 'Previsão offline do PV [kW]',drawstyle="steps", linewidth=0.15, c = 'hotpink')
    
    # Altera o estilo do gráfico
    ax.tick_params(axis='x', which='major', labelsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.legend(loc='upper left',prop={'size': 8})
    ax.tick_params(axis='x', rotation=0)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    '''SALVAR FIGURA'''
    name_figure = "Results/MPC_seguimento_trajetoria_previsao_PV.png"
    fig.set_size_inches(10, 5)
    plt.savefig(name_figure, format="png", dpi=dpi)

    



    # ============================================================================#
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(2, 2)
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[0, :])
    ax.set_title("Rede e demanda",fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'p_rede'], label = 'Pot. rede [kW]', drawstyle="steps", linewidth=1)
    ax.plot(ONLINE_OUT.loc[:,'p_rede_ref'], label = 'Pot. rede referência [kW]', drawstyle="steps", linestyle='dashed', linewidth=0.8)
    # ax.plot(ONLINE_OUT.loc[:,'custo_energia_imp'], label = 'Tarifa [R\$/kW]', drawstyle="steps", linewidth=0.3)
    ax.plot(ONLINE_OUT.loc[:,'load_real'], label = 'Demanda [kW]',drawstyle="steps", linewidth=0.3)



    # Altera o estilo do gráfico
    ax.tick_params(axis='x', which='major', labelsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.legend(loc='upper left',prop={'size': 8})
    ax.tick_params(axis='x', rotation=0)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[1, :])
    ax.set_title("SAE",fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    ax.plot(ONLINE_OUT.loc[:,'p_bike_total'], label = 'Pot. carga bike total [kW]', drawstyle="steps", linewidth=0.8)
    ax.plot(ONLINE_OUT.loc[:,'p_est_total'], label = 'Pot. carga est [kW]', drawstyle="steps", linewidth=0.8)
       
    
    # Altera o estilo do gráfico
    ax.tick_params(axis='x', which='major', labelsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.legend(loc='upper left',prop={'size': 8})
    ax.tick_params(axis='x', rotation=0)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    '''SALVAR FIGURA'''
    name_figure = "Results/MPC_seguimento_trajetoria_potencia_SAE.png"
    fig.set_size_inches(10, 5)
    plt.savefig(name_figure, format="png", dpi=dpi)
    
    
    
    
    # ============================================================================#
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(2, 2)

    # Escolhe as posição
    ax = fig.add_subplot(gs[0, :])
    ax.set_title("Estado de Carga (SOC) das bikes e da estacionária",fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    # Plota os gráficos
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'SOC_bike_real_total'], label = 'Somatório dos SOC das bikes [%]',drawstyle="steps", linewidth=0.8, c = 'y')
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'cx_bike_real_total'], label = 'Somatório das cx das bikes [%]', linestyle='dashed', drawstyle="steps", linewidth=0.8, c = 'y')
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'soc_est'], label = 'SOC bat. est. [%]',drawstyle="steps", linewidth=0.8, c = 'g')
    
    # Altera o estilo
    ax.legend(loc='upper left',prop={'size': 8})
    ax.tick_params(axis='x', which='major', labelsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[1, :])
    ax.set_title("Potência de carga e descarga das bikes e da estacionária",fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'p_ch_bike_total'], label = 'Pot. carga bike total [kW]', drawstyle="steps", linewidth=0.8, c = 'darkblue')
    ax.plot(ONLINE_OUT.loc[:,'p_dc_bike_total'], label = 'Pot. descarga bike total [kW]', drawstyle="steps", linewidth=0.8, c = 'r')
    ax.plot(ONLINE_OUT.loc[:,'p_ch_est'], label = 'Pot. carga est [kW]', drawstyle="steps", linewidth=0.8, c = 'green')
    ax.plot(ONLINE_OUT.loc[:,'p_dc_est'], label = 'Pot. descarga est [kW]', drawstyle="steps",linestyle='dashed', linewidth=0.8, c = 'green')
    
    # Altera o estilo do gráfico
    ax.tick_params(axis='x', which='major', labelsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.legend(loc='upper left',prop={'size': 8})
    ax.tick_params(axis='x', rotation=0)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    '''SALVAR FIGURA'''
    name_figure = "Results/MPC_SoC_CX_total_bikes_real_e_est_e_potencias.png"
    fig.set_size_inches(10, 5)
    plt.savefig(name_figure, format="png", dpi=dpi)
    
    
    
    
    
    # ============================================================================#
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(2, 2)

    # Escolhe as posição
    ax = fig.add_subplot(gs[0, :])
    ax.set_title("Seguimento de trajetória",fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], -ONLINE_OUT.loc[:,'p_rede_imp_ref'], label = 'Pot. Imp. referência [kW]', linestyle='dashed', drawstyle="steps", linewidth=1, c = 'red')
    ax.plot(-ONLINE_OUT.loc[:,'p_rede_imp'], label = 'Pot. Imp. [kW]', drawstyle="steps", linewidth=0.8, c = 'darkred')
    ax.plot(ONLINE_OUT.loc[:,'p_rede_exp_ref'], label = 'Pot. Exp. referência [kW]', linestyle='dashed', drawstyle="steps", linewidth=1, c = 'dodgerblue')
    ax.plot(ONLINE_OUT.loc[:,'p_rede_exp'], label = 'Pot. Exp. [kW]', drawstyle="steps", linewidth=0.8, c = 'navy')
    ax.plot(ONLINE_OUT.loc[:,'custo_energia_imp'], label = 'Tarifa [R\$/kW]', drawstyle="steps", linewidth=0.3, c = 'orange')

    # Altera o estilo do gráfico
    ax.tick_params(axis='x', which='major', labelsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.legend(loc='upper left',prop={'size': 8})
    ax.tick_params(axis='x', rotation=0)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    ax = fig.add_subplot(gs[1, :])
    ax.set_title("Estado de Carga (SOC) das bikes e da estacionária",fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    # Plota os gráficos
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'SOC_bike_real_total'], label = 'Somatório dos SOC das bikes [%]',drawstyle="steps", linewidth=0.8, c = 'y')
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'cx_bike_real_total'], label = 'Somatório das cx das bikes [%]', linestyle='dashed', drawstyle="steps", linewidth=0.8, c = 'y')
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'soc_est'], label = 'SOC bat. est. [%]',drawstyle="steps", linewidth=0.8, c = 'g')
    
    # Altera o estilo
    ax.legend(loc='upper left',prop={'size': 8})
    ax.tick_params(axis='x', which='major', labelsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    '''SALVAR FIGURA'''
    name_figure = "Results/MPC_seguimento_trajetoria_SoC_CX_total_bikes_e_est.png"
    fig.set_size_inches(10, 5)
    plt.savefig(name_figure, format="png", dpi=dpi)
    
    
    
    
    
    # ============================================================================#
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(2, 2)
    # Escolhe as posição
    ax = fig.add_subplot(gs[0, :])
    ax.set_title("Estado de Carga (SOC) das bikes e da estacionária",fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    # Plota os gráficos
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'SOC_bike_real_total'], label = 'Somatório dos SOC das bikes [%]',drawstyle="steps", linewidth=0.8, c = 'y')
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'cx_bike_real_total'], label = 'Somatório das cx das bikes [%]', linestyle='dashed', drawstyle="steps", linewidth=0.8, c = 'y')
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'soc_est'], label = 'SOC bat. est. [%]',drawstyle="steps", linewidth=0.8, c = 'g')
    
    # Altera o estilo
    ax.legend(loc='upper left',prop={'size': 8})
    ax.tick_params(axis='x', which='major', labelsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    ax = fig.add_subplot(gs[1, :])
    ax.set_title("Estado de Carga (SOC) das bikes",fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    for bike in range(0,10):
        ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'soc_bike_real_{}'.format(bike)], label = 'SOC real da bike {} [%]'.format(bike), drawstyle="steps", linewidth=0.8)
    
    ax.legend(loc='upper left',prop={'size': 3})
    ax.tick_params(axis='x', which='major', labelsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))    
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    '''SALVAR FIGURA'''
    name_figure = "Results/MPC_SoC_bike_a_bike.png"
    fig.set_size_inches(10, 5)
    plt.savefig(name_figure, format="png", dpi=dpi)
    
    
    
    
    
    # ============================================================================#
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(12, 1)
    
    # Bikes, uma por uma
    for bike in range(0,10):
        ax = fig.add_subplot(gs[bike, 0])
        
        if bike == 0:     
            ax.set_title("Carga e descarga de todas as bicicletas + somatório total",fontsize = 4)
            
        ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'p_ch_bike_{}'.format(bike)], label = 'P. carga da bike {} [kW]'.format(bike), drawstyle="steps", linewidth=0.8)
        ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'p_dc_bike_{}'.format(bike)], label = 'P. desc. da bike {} [kW]'.format(bike), drawstyle="steps", linewidth=0.8)
        ax.legend(loc='upper left',prop={'size': 3})
        ax.tick_params(axis='x', which='major', labelsize=4)
        ax.tick_params(axis='y', which='major', labelsize=4)
        ax.set_facecolor("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_linewidth(0.1)
        ax.spines["bottom"].set_linewidth(0.1)
        ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
        ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
        ax.xaxis.set_major_locator(plt.MaxNLocator(15))    
        ax.grid(color = 'lightgray', linewidth = 0.03)
    
    # Somatório das bikes
    ax = fig.add_subplot(gs[10:, 0])
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'p_ch_bike_total'], label = 'Pot. de carga de todas as bikes [kW]', drawstyle="steps", linewidth=0.8, c = 'darkblue')
    ax.plot(ONLINE_OUT.loc[:,'p_dc_bike_total'], label = 'Pot. de descarga de todas as bikes [kW]', drawstyle="steps", linewidth=0.8, c = 'red')
    ax.legend(loc='upper left',prop={'size': 8})
    ax.tick_params(axis='x', which='major', labelsize=4)
    ax.tick_params(axis='y', which='major', labelsize=4)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))    
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    '''SALVAR FIGURA'''
    name_figure = "Results/MPC_Potencia_bike_a_bike.png"
    fig.set_size_inches(10, 5)
    plt.savefig(name_figure, format="png", dpi=dpi)
    
    
    
    
    
    # ============================================================================#
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(2, 1)
    

    # Escolhe as posição
    ax = fig.add_subplot(gs[0, 0])
    ax.set_title("Uso das bicicletas e a energia exportada para a rede",fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
        
    # Plota os gráficos
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'cx_bike_real_total'], label = 'Somatório das cx das bikes [%]', drawstyle="steps", linewidth=0.8, c = 'darkorange')
    ax.plot(ONLINE_OUT.loc[:,'p_rede_exp'], label = 'Pot. Exp. [kW]', drawstyle="steps", linewidth=0.8, c = 'green')
    ax.plot(-ONLINE_OUT.loc[:,'p_rede_imp'], label = 'Pot. Exp. [kW]', drawstyle="steps", linewidth=0.8, c = 'red')
    ax.plot(ONLINE_OUT.loc[:,'custo_energia_imp'], label = 'Tarifa [R\$/kW]', drawstyle="steps", linewidth=0.8, c = 'yellow')
    
    # Altera o estilo
    ax.legend(loc='upper left',prop={'size': 8})
    ax.tick_params(axis='x', which='major', labelsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.3, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.3, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[1, 0])
    ax.set_title("Ganho em reais",fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    # Plota os gráficos
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'ganho_aluguel'], label = 'Acumulado em aluguel [R\$]',  drawstyle="steps", linewidth=0.8, c = 'orange')
    ax.plot(ONLINE_OUT.loc[:,'ganho_pot_exp'], label = 'Acumulado com a exportação de energia [R\$]', drawstyle="steps", linewidth=0.8, c = 'green')
    ax.plot(ONLINE_OUT.loc[:,'ganho_total'], label = 'Ganho total [R\$]', drawstyle="steps", linewidth=0.8, c = 'navy')
    
    # Altera o estilo
    ax.legend(loc='upper left',prop={'size': 8})
    # ax.set_xlabel("Tempo [horas]")
    ax.tick_params(axis='x', which='major', labelsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    

    '''SALVAR FIGURA'''
    name_figure = "Results/MPC_Uso_bikes_pot_exp_lucro_total.png"
    fig.set_size_inches(10, 5)
    plt.savefig(name_figure, format="png", dpi=dpi)
    
    
    
    
    # ============================================================================#
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(1, 1)
    # Escolhe as posição
    ax = fig.add_subplot(gs[0, :])
    ax.set_title("CS e SoC real e previsto para as bikes",fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    # Plota os gráficos
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'SOC_bike_real_total'], label = 'Soma SOC bikes real [%]',drawstyle="steps", linewidth=0.8, c = 'y')
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'cx_bike_real_total'], label = 'Soma CX bikes real [%]', linestyle='dashed', drawstyle="steps", linewidth=2, c = 'y')
    # ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'SOC_bike_previsao_total'], label = 'Soma SOC bikes previsto [%]',drawstyle="steps", linewidth=0.8, c = 'r')
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'cx_bike_previsao_total'], label = 'Soma CX bikes previsto [%]', drawstyle="steps", linewidth=0.4, c = 'r')
    
    # Altera o estilo
    ax.legend(loc='upper left',prop={'size': 8})
    ax.tick_params(axis='x', which='major', labelsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    
    '''SALVAR FIGURA'''
    name_figure = "Results/MPC_SoC_bike_a_bike_previsao_e_real.png"
    fig.set_size_inches(10, 5)
    plt.savefig(name_figure, format="png", dpi=dpi)
    
    
    
    
    
    # ============================================================================#
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(2, 2)
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[0, :])
    ax.set_title("SOC bike: ONLINE e OFFLINE",fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'SOC_bike_offline'], label = 'Offline: Uma bateria representando todas [%]', linewidth=1)
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'SOC_bike_real_total'], label = 'Online: Somatório dos SOC das bikes [%]', linewidth=1)
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'cx_bike_real_total'], label = 'Online: Somatório das conexões [%]', linewidth=0.4)
    
    
    # Altera o estilo do gráfico
    ax.tick_params(axis='x', which='major', labelsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.legend(loc='upper left',prop={'size': 8})
    ax.tick_params(axis='x', rotation=0)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[1, :])
    ax.set_title("SOC estacionária: ONLINE e OFFLINE",fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    # Plota os gráficos
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'SOC_est_offline'], label = 'Offline [%]', linewidth=1)
    ax.plot(ONLINE_OUT.loc[:,'time_plot'], ONLINE_OUT.loc[:,'soc_est'], label = 'Online [%]', linewidth=1)
    
    
    # Altera o estilo do gráfico
    ax.tick_params(axis='x', which='major', labelsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.legend(loc='upper left',prop={'size': 8})
    ax.tick_params(axis='x', rotation=0)
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.1)
    ax.spines["bottom"].set_linewidth(0.1)
    ax.tick_params(axis="x", direction="in", length=1, width=0.5, color="black")
    ax.tick_params(axis="y", direction="in", length=1, width=0.5, color="black")
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    '''SALVAR FIGURA'''
    name_figure = "Results/Comparando_MPC_e_OFFline.png"
    fig.set_size_inches(10, 5)
    plt.savefig(name_figure, format="png", dpi=dpi)
    
    
    
    
    # ============================================================================#
    # Save all data
    print('Antes de salvar')
    ONLINE_OUT.to_csv('output_ONLINE.csv', index=True)
    print('Depois de salvar')
    return ONLINE_OUT
    
    
if __name__ == "__main__":
    
    on_out_to_chart = pd.read_csv('Matrizes_for_charts/ONLINE_OUTPUT.csv', index_col=['tempo'], sep=";")
    pesos_mpc = pd.read_csv('Matrizes_for_MPC/pesos.csv',sep=";")
    
    run_online_plot_charts(on_out_to_chart, pesos_mpc)