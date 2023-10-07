# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 21:38:56 2023

@author: wesley.r
"""

from scipy import io
import numpy as np
import matplotlib.pyplot as plt


# Carrega o arquivo MAT
mat = io.loadmat('Testes_de_programacao/Geracao_SNPTEE_ensolarado.mat')

# Agora você pode acessar as variáveis dentro do arquivo MAT
minha_variavel = mat['__function_workspace__']
minha_variavel = np.transpose(minha_variavel)

plt.plot(minha_variavel[0:48])
plt.xlabel('Índice')
plt.ylabel('Valor')
plt.title('Gráfico do vetor transformado')
plt.show()