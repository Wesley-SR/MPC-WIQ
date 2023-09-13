class Dados:
    def __init__(self):
        self.valor = 0  # Variável que deseja ser editada

class Edita1:
    def __init__(self, dados):
        self.dados = dados  # Passando o objeto Dados como argumento

    def editar_valor(self, novo_valor):
        self.dados.valor = novo_valor

    def imprimir_valor(self):
        print(f"Valor atual: {self.dados.valor}")


class Edita2:
    def __init__(self, dados):
        self.dados = dados  # Passando o objeto Dados como argumento

    def imprimir_valor(self):
        print(f"Valor atual: {self.dados.valor}")

    def editar_valor(self, novo_valor):
        self.dados.valor = novo_valor

class ClasseExterna:
    def __init__(self):
        self.dados = Dados()
        self.edita1 = Edita1(self.dados)  # Passando o objeto Dados para Edita1
        self.edita2 = Edita2(self.dados)  # Passando o objeto Dados para Edita2

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
