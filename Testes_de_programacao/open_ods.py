import pyexcel_ods
import pandas as pd
import matplotlib.pyplot as plt

# Especifique o caminho para o seu arquivo .ods
ods_file_path = "Testes_de_programacao/p_load.ods"

# Leia os dados do arquivo .ods
data = pyexcel_ods.get_data(ods_file_path)

# Extraia os dados da primeira coluna (supondo que é a única coluna)
sheet_name = list(data.keys())[0]
sheet_data = data[sheet_name]

# Crie um DataFrame pandas com os dados
df = pd.DataFrame(sheet_data, columns=["Dados"])

# Converte os dados da coluna em números (se necessário)
df["Dados"] = pd.to_numeric(df["Dados"], errors="coerce")

# Crie um gráfico de linha simples
plt.plot(df["Dados"])

# Adicione rótulos aos eixos e um título ao gráfico (opcional)
plt.xlabel("Eixo X")
plt.ylabel("Eixo Y")
plt.title("Gráfico dos Dados do Arquivo .ods")

# Exiba o gráfico
plt.show()
