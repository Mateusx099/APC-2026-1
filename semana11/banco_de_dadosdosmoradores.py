import pandas as pd

moradores = pd.read_csv("moradores.csv", sep=";")

ra_alvo = int(input("Digite o codigo da RA (ex: 5320): "))

filtro_ra = moradores[moradores["localidade"] == ra_alvo]

idades = []
rendas = []

for _, linha in filtro_ra.iterrows():
    idade = linha["idade_calculada"]
    renda = linha["renda_ind"]
    
    if idade != 99999:
        idades.append(idade)
        
    if renda != 99999 and renda != 88888 and renda > 0:
        rendas.append(renda)

print("\n--- Resultados da Busca ---")
print("Total de moradores na RA:", len(filtro_ra))

if len(idades) > 0:
    soma_id = 0
    for id in idades:
        soma_id = soma_id + id
    media_id = soma_id / len(idades)
    print("Idade media da RA:", media_id)

if len(rendas) > 0:
    soma_re = 0
    for re in rendas:
        soma_re = soma_re + re
    media_re = soma_re / len(rendas)
    print("Renda media da RA: R$", media_re)
else:
    print("Nenhum morador com renda declarada.")