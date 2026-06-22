import streamlit as st
st.title("Simulador cruzamento genético: Cor dos olhos")

st.markdown("Escolha as características do pai e da mãe para calcular a probabilidades para os filhos")

col1, col2 = st.columns(2)

opcoes = [
    "Preto/Castanho Escuro Puro (NN)",
    "Preto/Castanho Escuro (NB)",
    "Preto/Castanho Escuro (NG)",
    "Preto/Castanho Escuro (Nb)",
    "Castanho Claro Puro (BB)",
    "Castanho Claro (BG)",
    "Castanho Claro (Bb)",
    "Verde Puro (GG)",
    "Verde Misto (Gb)",
    "Azul Puro (bb)"
]

with col1:
    st.write("Pai")
    pai_escolha = st.selectbox("Características do pai:", opcoes, key="pai")

with col2:
    st.write("Mãe")
    mae_escolha = st.selectbox("Características da mãe:", opcoes, key="mae")

if "NN" in pai_escolha: pai = "NN"
elif "NB" in pai_escolha: pai = "NB"
elif "NG" in pai_escolha: pai = "NG"
elif "Nb" in pai_escolha: pai = "Nb"
elif "BB" in pai_escolha: pai = "BB"
elif "BG" in pai_escolha: pai = "BG"
elif "Bb" in pai_escolha: pai = "Bb"
elif "GG" in pai_escolha: pai = "GG"
elif "Gb" in pai_escolha: pai = "Gb"
else: pai = "bb"

if "NN" in mae_escolha: mae = "NN"
elif "NB" in mae_escolha: mae = "NB"
elif "NG" in mae_escolha: mae = "NG"
elif "Nb" in mae_escolha: mae = "Nb"
elif "BB" in mae_escolha: mae = "BB"
elif "BG" in mae_escolha: mae = "BG"
elif "Bb" in mae_escolha: mae = "Bb"
elif "GG" in mae_escolha: mae = "GG"
elif "Gb" in mae_escolha: mae = "Gb"
else: mae = "bb"

st.markdown("---")

if st.button("Calcular", use_container_width=True):
    filhos = []
    for g1 in pai:
        for g2 in mae:
        
            if g1 == "N" or g2 == "N":
                comb = "N" + (g2 if g1 == "N" else g1)
            elif g1 == "B" or g2 == "B":
                comb = "B" + (g2 if g1 == "B" else g1)
            elif g1 == "G" or g2 == "G":
                comb = "G" + (g2 if g1 == "G" else g1)
            else:
                comb = g1 + g2
            filhos.append(comb)
    
    st.write("Quadro das características")
    quadro = f"""
           MAE: {mae[0]}      MAE: {mae[1]}
        -------------------------
    PAI {pai[0]}: |   {filhos[0]}   |   {filhos[1]}   |
        -------------------------
    PAI {pai[1]}: |   {filhos[2]}   |   {filhos[3]}   |
        -------------------------
    """
    st.code(quadro, language='text')

    st.write("Probabilidade")
    
    c_preto = 0
    c_castanho = 0
    c_verde = 0
    c_azul = 0
    
    for x in filhos:
        if "N" in x: c_preto += 1
        elif "B" in x: c_castanho += 1
        elif "G" in x: c_verde += 1
        else: c_azul += 1
        
    if c_preto > 0: st.info(f"**{(c_preto / 4) * 100}%** de chance: **Preto/Castanho Escuro**")
    if c_castanho > 0: st.warning(f"**{(c_castanho / 4) * 100}%** de chance: **Castanho Claro**")
    if c_verde > 0: st.success(f"**{(c_verde / 4) * 100}%** de chance: **Verde**")
    if c_azul > 0: st.error(f"**{(c_azul / 4) * 100}%** de chance: **Azul**")

st.caption("Mateus de Lima - 232021937 - Projeto final APC")