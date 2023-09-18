# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 08:56:02 2022

@author: wesley
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import AutoMinorLocator, FormatStrFormatter
from matplotlib.ticker import FixedLocator, FixedFormatter

# import seaborn as sns
# sns.set()


# OFFLINE_OUT = pd.read_csv('RESULTATO_M.csv', index_col=['tempo'], sep=";")



def run_offline_plot_charts(R_offline_out, pesos):
    
    
    
    dpi = 600 # 1200 para apresentações
    
    
    peso_imp = pesos.loc[0, 'peso_imp']
    peso_exp = pesos.loc[0, 'peso_exp']
    peso_est = pesos.loc[0, 'peso_est']
    peso_bike = pesos.loc[0, 'peso_bike']
    
    
    
    
    
    OFFLINE_OUT = R_offline_out
    # ============================================================================#
    # MONTAR VETOR TEMPO
    cont = 0
    h = 0
    m = 0
    dia = ' '
    for k in range(0,3*96):
        if m == 0:
            OFFLINE_OUT.loc[k,'time_plot'] = str('{dia}{hour}:00'.format(dia=dia, hour=h))
        else:    
            OFFLINE_OUT.loc[k,'time_plot'] = str('{dia}{hour}:{minute}'.format(dia=dia, hour=h, minute=m))
        cont += 1
        m += 15
        if cont > 3:
            m = 0
            h += 1
            cont = 0
        if h > 23:
            h = 0
            dia += ' '
    
    
    
    
    
    
    
    # ============================================================================#
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(3, 1)
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[0, 0])
    ax.set_title(r'Otimização OFFline, pesos: $\alpha_{{IMP}}={peso_imp}$, $\alpha_{{EXP}}={peso_exp}$, $\alpha_{{est}}={peso_est}$, $\alpha_{{bike}}={peso_bike}$'.format(peso_imp=peso_imp, peso_exp=peso_exp, peso_est=peso_est, peso_bike = peso_bike),fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    ax.plot(OFFLINE_OUT.loc[:,'time_plot'], -OFFLINE_OUT.loc[:,'p_rede_imp_ref'], label = r'$P_{IMP}^{REF}$ [kW]', linestyle='dashed', drawstyle="steps", linewidth=0.8, c = 'green')
    ax.plot(OFFLINE_OUT.loc[:,'p_rede_exp_ref'], label = r'$P_{EXP}^{REF}$ [kW]', linestyle='dashed', drawstyle="steps", linewidth=0.8, c = 'dodgerblue')
    ax.plot(OFFLINE_OUT.loc[:,'PV_real'], label = r'$PV_{real}$ [kW]', drawstyle="steps", linewidth=0.8, c = 'grey')
    ax.plot(OFFLINE_OUT.loc[:,'PV_previsao'], label = r'$P_{previsao}$ [kW]',drawstyle="steps", linewidth=0.8, c = 'red')
    ax.plot(OFFLINE_OUT.loc[:,'load_previsao'], label = 'load previsao [kW]', drawstyle="steps", linestyle='dashed', linewidth=0.8, c = 'darkred')

    ax.axvline(x = 95, color = 'gray', label = 'Tempo inicial', linewidth=0.3)
    
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
    ax.yaxis.set_major_locator(plt.MaxNLocator(10))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[1, 0])
    
    ax.set_title(r'Estado de Carga das Baterias e a Tarifa de Energia',fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    # Colocar aqui o plot das bikes
    # ax.plot(OFFLINE_OUT.loc[:,'time_plot'], OFFLINE_OUT.loc[:,'soc_bike'], label = r'$SOC_{bike}$ [%]', drawstyle="steps", linewidth=0.8, c = 'green')
    # ax.plot(OFFLINE_OUT.loc[:,'time_plot'], OFFLINE_OUT.loc[:,'soc_est'], label = r'$SOC_{Est}$ [%]',drawstyle="steps", linestyle="dashed", linewidth=0.8, c = 'blue')
    # ax.plot(OFFLINE_OUT.loc[:,'time_plot'], OFFLINE_OUT.loc[:,'custo_energia_imp'], label = 'Tarifa [R$/(kWh)]',drawstyle="steps", linewidth=0.8, c = 'orange')
    ax.axvline(x = 95, color = 'gray', label = 'Tempo inicial', linewidth=0.3)
    
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
    ax.yaxis.set_major_locator(plt.MaxNLocator(10))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[2, 0])
    ax.set_title(r'Receita Estimada',fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    ax.plot(OFFLINE_OUT.loc[:,'time_plot'], OFFLINE_OUT.loc[:,'somatorio_p_rede'], label = 'Energia da Rede (+ é exportação) [R\$=(kWh).(R\$/kWh)]', drawstyle="steps", linewidth=0.8, c = 'green')
    ax.axvline(x = 95, color = 'gray', label = 'Tempo inicial', linewidth=0.3)

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
    ax.yaxis.set_major_locator(plt.MaxNLocator(10))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    '''SALVAR FIGURA'''
    name_figure = "Results/OFFLINE_01_ref_SoCs_receita.png"
    fig.set_size_inches(10, 5)
    plt.savefig(name_figure, format="png", dpi=dpi) 
    
    
    
    
    
    
    
    # ============================================================================#
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(2, 1)
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[0, 0])
    ax.set_title(r'Otimização OFFline: $\alpha_{{IMP}}={peso_imp}$, $\alpha_{{EXP}}={peso_exp}$, $\alpha_{{est}}={peso_est}$, $\alpha_{{bike}}={peso_bike}$'.format(peso_imp=peso_imp, peso_exp=peso_exp, peso_est=peso_est, peso_bike = peso_bike),fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    # Aqui são as potências das bikes
    # ax.plot(OFFLINE_OUT.loc[:,'time_plot'], -OFFLINE_OUT.loc[:,'p_ch_bike_bs'], label = 'Pot. carga bike 1 [kW]', drawstyle="steps", linewidth=0.8, c = 'red')
    # ax.plot(OFFLINE_OUT.loc[:,'p_dc_bike_bs'], label = 'Pot. descarga bike 1 [kW]', drawstyle="steps", linewidth=0.8, c = 'darkred')
    # ax.plot(-OFFLINE_OUT.loc[:,'p_ch_bike_cps'], label = 'Pot. carga bike 2 [kW]', drawstyle="steps", linestyle='dashed', linewidth=0.8, c = 'red')
    # ax.plot(OFFLINE_OUT.loc[:,'p_dc_bike_cps'], label = 'Pot. descarga bike 2 [kW]', drawstyle="steps", linestyle='dashed', linewidth=0.8, c = 'darkred')
    # ax.axvline(x = 95, color = 'gray', label = 'Tempo inicial', linewidth=0.3)
    
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
    ax.yaxis.set_major_locator(plt.MaxNLocator(10))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[1, 0])
    ax.set_title("Potência da Bateria Estacionária",fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    # Aqui são as potências das bikes
    # ax.plot(OFFLINE_OUT.loc[:,'time_plot'], -OFFLINE_OUT.loc[:,'p_ch_bat_est_bs'], label = 'Pot. carga est. [kW]', drawstyle="steps", linewidth=0.8, c = 'orange')
    # ax.plot(OFFLINE_OUT.loc[:,'time_plot'], OFFLINE_OUT.loc[:,'p_dc_bat_est_bs'], label = 'Pot. descarga est [kW]',drawstyle="steps", linewidth=0.8, c = 'green')
    # ax.axvline(x = 95, color = 'gray', label = 'Tempo inicial', linewidth=0.3)

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
    ax.yaxis.set_major_locator(plt.MaxNLocator(10))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    '''SALVAR FIGURA'''
    name_figure = "Results/OFFLINE_02_potencias_bikes_est_e_eficiencia.png"
    fig.set_size_inches(10, 5)
    plt.savefig(name_figure, format="png", dpi=dpi)
    
    
    
    
    
    
    # ============================================================================#
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(1, 1)
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[0, 0])
    ax.set_title(r'Otimização OFFline, pesos: $\alpha_{{IMP}}={peso_imp}$, $\alpha_{{EXP}}={peso_exp}$, $\alpha_{{est}}={peso_est}$, $\alpha_{{bike}}={peso_bike}$'.format(peso_imp=peso_imp, peso_exp=peso_exp, peso_est=peso_est, peso_bike = peso_bike),fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    ax.plot(OFFLINE_OUT.loc[:,'time_plot'], -OFFLINE_OUT.loc[:,'p_rede_imp_ref'], label = r'$P_{IMP}^{REF}$ [kW]', linestyle='dashed', drawstyle="steps", linewidth=0.8, c = 'green')
    ax.plot(OFFLINE_OUT.loc[:,'p_rede_exp_ref'], label = r'$P_{EXP}^{REF}$ [kW]', linestyle='dashed', drawstyle="steps", linewidth=0.8, c = 'dodgerblue')
    ax.plot(OFFLINE_OUT.loc[:,'PV_real'], label = r'$PV_{real}$ [kW]', drawstyle="steps", linewidth=0.8, c = 'grey')
    ax.plot(OFFLINE_OUT.loc[:,'PV_previsao'], label = r'$P_{previsao}$ [kW]',drawstyle="steps", linewidth=0.8, c = 'red')
    ax.axvline(x = 95, color = 'gray', label = 'Tempo inicial', linewidth=0.3)
    
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
    ax.yaxis.set_major_locator(plt.MaxNLocator(10))
    ax.grid(color = 'lightgray', linewidth = 0.03)
    
    '''SALVAR FIGURA'''
    name_figure = "Results/OFFLINE_03_referencia.png"
    fig.set_size_inches(10, 5)
    plt.savefig(name_figure, format="png", dpi=dpi)






    # ============================================================================#
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(1, 1)
    
    # Escolhe as posição
    ax = fig.add_subplot(gs[0, 0])
    ax.set_title(r'Otimização OFFline',fontsize = 10)
    ax.set_xlabel("Tempo [horas]", fontsize= 8)
    ax.set_ylabel("Amplitude", fontsize= 8)
    
    ax.plot(OFFLINE_OUT.loc[:,'time_plot'], -OFFLINE_OUT.loc[:,'p_rede_imp_ref'], label = r'$P_{IMP}^{REF}$ [kW]', linestyle='dashed', drawstyle="steps", linewidth=0.8, c = 'green')
    ax.plot(OFFLINE_OUT.loc[:,'p_rede_exp_ref'], label = r'$P_{EXP}^{REF}$ [kW]', linestyle='dashed', drawstyle="steps", linewidth=0.8, c = 'dodgerblue')
    ax.plot(OFFLINE_OUT.loc[:,'PV_previsao'], label = r'$P_{previsao}$ [kW]',drawstyle="steps", linewidth=0.8, c = 'red')
    ax.plot(OFFLINE_OUT.loc[:,'p_ch_bat_est_bs'], label = 'Pot. carga est. [kW]', drawstyle="steps", linewidth=0.8, c = 'orange')
    ax.plot(OFFLINE_OUT.loc[:,'p_dc_bat_est_bs'], label = 'Pot. descarga est [kW]',drawstyle="steps",linestyle='dashed', linewidth=0.8, c = 'orange')
    # ax.plot(-OFFLINE_OUT.loc[:,'p_ch_bike_cps'], label = 'Pot. carga bike 2 [kW]', drawstyle="steps", linewidth=0.8, c = 'blue')
    # ax.plot(OFFLINE_OUT.loc[:,'p_dc_bike_cps'], label = 'Pot. descarga bike 2 [kW]', drawstyle="steps", linestyle='dashed', linewidth=0.8, c = 'blue')
    ax.plot(OFFLINE_OUT.loc[:,'load_previsao'], label = 'load previsao [kW]', drawstyle="steps", linestyle='dashed', linewidth=0.8, c = 'darkred')


    ax.axvline(x = 95, color = 'gray', label = 'Tempo inicial', linewidth=0.3)
    
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
    name_figure = "Results/OFFLINE_04_potencias.png"
    fig.set_size_inches(10, 5)
    plt.savefig(name_figure, format="png", dpi=dpi)
    
    
    
    
    
    # ============================================================================#
    # Save all OFFLINE_OUT
    OFFLINE_OUT.to_csv('output_OFFLINE.csv', index=True)


if __name__ == "__main__":
    
    R_offline_out = pd.read_csv('Matrizes_for_charts/OFFLINE_OUTPUT.csv', index_col=['tempo'], sep=";")
    pesos = pd.read_csv('Matrices_for_offline_optimization/pesos.csv',sep=",")
    
    run_offline_plot_charts(R_offline_out, pesos)
    
    
    