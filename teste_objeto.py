import pandas as pd
from Datas import Datas





class ClasseExterna:
    def __init__(self):
        self.Dados = Datas()
        
        print(self.Dados.I_3th['pv_forecast'])
        print(self.Dados.I_3th.loc[0, 'pv_forecast'])
        
        # Aqui está a cereja do bolo. Passa com o "self" o argumento para as outras classes
        self.edita1 = Edita1(self.Dados)  # Passando o objeto Dados para Edita1
        self.edita2 = Edita2(self.Dados)  # Passando o objeto Dados para Edita2
        
        self.edita1 = Edita1(self.Dados)  # Passando o objeto Dados para Edita1
        self.edita2 = Edita2(self.Dados)  # Passando o objeto Dados para Edita2





class Edita1:
    def __init__(self, Dados):
        self.Dados = Dados  # Passando o objeto Dados como argumento

    def editar_valor(self, novo_valor):
        self.Dados.valor = novo_valor
        self.Dados.I_3th.loc[3,'pv_forecast'] = 133.58

    def imprimir_valor(self):
        print(f"Valor atual: {self.Dados.valor}")
        print(self.Dados.I_3th['pv_forecast'])





class Edita2:
    def __init__(self, Dados):
        self.Dados = Dados  # Passando o objeto Dados como argumento

    def imprimir_valor(self):
        print(f"Valor atual: {self.Dados.valor}")
 
        print(self.Dados.I_3th['pv_forecast'])

    def editar_valor(self, novo_valor):
        self.Dados.valor = novo_valor
        self.Dados.I_3th.loc[15,'pv_forecast'] = 958.45
        self.Dados.I_3th.loc[15,'pv_forecast'] = self.Dados.p_pv









# Criando uma instância da ClasseExterna
classe_externa = ClasseExterna()

# Edita1 altera o valor
classe_externa.edita1.editar_valor(42)

# Edita2 imprime o valor definido pelo Edita1
classe_externa.edita2.imprimir_valor()

# Edita2 altera o valor novamente
classe_externa.edita2.editar_valor(100)

# Edita1 imprime o valor atualizado pelo Edita2
classe_externa.edita1.imprimir_valor()

print(classe_externa.Dados.I_3th['pv_forecast'])

classe_externa.Dados.I_3th.loc[16,'pv_forecast'] = 785.33
print(classe_externa.Dados.I_3th.loc[16,'pv_forecast'])

print(classe_externa.Dados.I_3th['pv_forecast'])
