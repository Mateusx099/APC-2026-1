import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter


PASTA = Path(__file__).resolve().parent
SENTINELAS = [88888, 99999]

df_completo = pd.DataFrame()

janela = None
combo_ra = None
lbl_status = None
lbl_moradores = None
lbl_idade = None
lbl_pessoas = None
lbl_criancas = None

fig_piramide = None
fig_tamanho = None
fig_arranjos = None
canvas_piramide = None
canvas_tamanho = None
canvas_arranjos = None


def localizar_arquivo(palavra, extensoes):
    """Procura um arquivo na mesma pasta do sistema."""
    for arquivo in PASTA.iterdir():
        if palavra in arquivo.name.lower() and arquivo.suffix.lower() in extensoes:
            return arquivo
    raise FileNotFoundError(
        f"Não encontrei o arquivo de {palavra}. Coloque as planilhas na mesma pasta do sistema.py."
    )


def criar_mapa(dicionario, aba, variavel):
    """Cria um mapa de códigos e descrições do dicionário."""
    tabela = pd.read_excel(dicionario, sheet_name=aba)
    tabela.columns = tabela.columns.str.strip()
    tabela["Coluna"] = tabela["Coluna"].ffill()

    linhas = tabela[tabela["Coluna"] == variavel].copy()
    linhas["Valor"] = pd.to_numeric(linhas["Valor"], errors="coerce")
    linhas = linhas.dropna(subset=["Valor", "Descrição do valor"])

    mapa = {}
    for _, linha in linhas.iterrows():
        mapa[int(linha["Valor"])] = str(linha["Descrição do valor"]).strip()
    return mapa


def criar_mapa_ras(dicionario):
    """Lê os códigos e os nomes das Regiões Administrativas."""
    tabela = pd.read_excel(dicionario, sheet_name="anexo_1")
    tabela.columns = tabela.columns.str.strip()
    tabela["Valor"] = pd.to_numeric(tabela["Valor"], errors="coerce")
    tabela = tabela.dropna(subset=["Valor", "Descrição do valor"])

    mapa = {}
    for _, linha in tabela.iterrows():
        mapa[int(linha["Valor"])] = str(linha["Descrição do valor"]).strip()
    return mapa


def simplificar_arranjo(nome):
    """Agrupa os diferentes casais com filhos em uma categoria."""
    if pd.isna(nome):
        return "Não informado"
    nome = str(nome)
    if nome.startswith("Casal com") and "sem filhos" not in nome.lower():
        return "Casal com filho"
    return nome


def limpar_colunas(df, colunas):
    """Converte colunas numéricas e remove valores sentinela."""
    for coluna in colunas:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

        # 88888 significa não declarado e 99999 significa não se aplica.
        df.loc[df[coluna].isin(SENTINELAS), coluna] = pd.NA


def carregar_dados():
    """Lê, limpa e junta moradores e domicílios."""
    arq_moradores = localizar_arquivo("moradores", [".csv"])
    arq_domicilios = localizar_arquivo("domicilios", [".xlsx", ".xls"])
    arq_dicionario = localizar_arquivo("dicionario", [".xlsx", ".xls"])

    moradores = pd.read_csv(arq_moradores, sep=";", low_memory=False)
    domicilios = pd.read_excel(arq_domicilios)

    moradores.columns = moradores.columns.str.strip()
    domicilios.columns = domicilios.columns.str.strip()

    colunas_moradores = [
        "A01nficha", "A01uf", "localidade", "idade_calculada",
        "E03", "E05", "id_genero"
    ]
    colunas_domicilios = [
        "A01nficha", "A01uf", "A01npessoas", "A01ncriancas", "arranjos"
    ]

    moradores = moradores[colunas_moradores].copy()
    domicilios = domicilios[colunas_domicilios].copy()

    limpar_colunas(moradores, colunas_moradores)
    limpar_colunas(domicilios, colunas_domicilios)

    moradores = moradores.dropna(
        subset=["A01nficha", "localidade", "idade_calculada"]
    )
    domicilios = domicilios.dropna(subset=["A01nficha"])

    moradores["A01nficha"] = moradores["A01nficha"].astype(int)
    domicilios["A01nficha"] = domicilios["A01nficha"].astype(int)

    mapa_uf = criar_mapa(arq_dicionario, "moradores", "A01uf")
    codigo_df = None

    for codigo, nome in mapa_uf.items():
        if nome == "Distrito Federal":
            codigo_df = codigo

    if codigo_df is None:
        raise ValueError("Distrito Federal não encontrado no dicionário.")

    moradores = moradores[moradores["A01uf"] == codigo_df].copy()
    domicilios = domicilios[domicilios["A01uf"] == codigo_df].copy()

    mapa_ras = criar_mapa_ras(arq_dicionario)
    mapa_arranjos = criar_mapa(arq_dicionario, "domicilios", "arranjos")

    moradores["ra_nome"] = moradores["localidade"].map(mapa_ras)
    domicilios["arranjo_nome"] = domicilios["arranjos"].map(mapa_arranjos)
    domicilios["arranjo_nome"] = domicilios["arranjo_nome"].apply(
        simplificar_arranjo
    )

    # Uma ficha representa um domicílio.
    domicilios = domicilios.drop_duplicates(subset=["A01nficha"])

    dados = pd.merge(
        moradores,
        domicilios[
            ["A01nficha", "A01npessoas", "A01ncriancas", "arranjo_nome"]
        ],
        on="A01nficha",
        how="inner"
    )

    return dados.dropna(subset=["ra_nome"])


def filtrar_ra():
    """Retorna os dados da RA escolhida."""
    return df_completo[df_completo["ra_nome"] == combo_ra.get()].copy()


def calcular_estatisticas(dados):
    """Calcula quatro estatísticas da RA."""
    casas = dados.drop_duplicates(subset=["A01nficha"])
    return (
        len(dados),
        dados["idade_calculada"].mean(),
        casas["A01npessoas"].mean(),
        casas["A01ncriancas"].sum()
    )


def criar_piramide(dados):
    """Agrupa moradores em faixas etárias de cinco anos."""
    dados = dados.dropna(subset=["idade_calculada", "E03"]).copy()
    maior_idade = int(dados["idade_calculada"].max())
    limite = ((maior_idade // 5) + 1) * 5
    faixas = list(range(0, limite + 5, 5))
    nomes = [f"{inicio}-{inicio + 4}" for inicio in faixas[:-1]]

    dados["faixa"] = pd.cut(
        dados["idade_calculada"],
        bins=faixas,
        labels=nomes,
        right=False
    )

    tabela = pd.crosstab(dados["faixa"], dados["E03"])
    tabela = tabela.reindex(nomes, fill_value=0)

    if 1 not in tabela.columns:
        tabela[1] = 0
    if 2 not in tabela.columns:
        tabela[2] = 0

    return tabela


def formatar_eixo(valor, posicao):
    """Mostra valores positivos nos dois lados da pirâmide."""
    return str(abs(int(valor)))


def atualizar_graficos(dados):
    """Redesenha os gráficos conforme a RA escolhida."""
    ra = combo_ra.get()
    casas = dados.drop_duplicates(subset=["A01nficha"])

    fig_piramide.clear()
    ax1 = fig_piramide.add_subplot(111)
    tabela = criar_piramide(dados)
    ax1.barh(tabela.index, -tabela[1], label="Masculino")
    ax1.barh(tabela.index, tabela[2], label="Feminino")
    ax1.axvline(0, color="black", linewidth=0.8)
    ax1.xaxis.set_major_formatter(FuncFormatter(formatar_eixo))
    ax1.set_title(f"Pirâmide etária - {ra}")
    ax1.set_xlabel("Quantidade de moradores")
    ax1.set_ylabel("Faixa etária")
    ax1.legend()
    fig_piramide.tight_layout()
    canvas_piramide.draw()

    fig_tamanho.clear()
    ax2 = fig_tamanho.add_subplot(111)
    tamanhos = casas["A01npessoas"].dropna().astype(int)

    if not tamanhos.empty:
        menor = int(tamanhos.min())
        maior = int(tamanhos.max())
        bins = [valor - 0.5 for valor in range(menor, maior + 2)]
        ax2.hist(tamanhos, bins=bins, rwidth=0.85)
        ax2.set_xticks(range(menor, maior + 1))

    ax2.set_title(f"Tamanho dos domicílios - {ra}")
    ax2.set_xlabel("Número de pessoas")
    ax2.set_ylabel("Quantidade de domicílios")
    fig_tamanho.tight_layout()
    canvas_tamanho.draw()

    fig_arranjos.clear()
    ax3 = fig_arranjos.add_subplot(111)
    arranjos = casas["arranjo_nome"].value_counts()

    if not arranjos.empty:
        partes, _, _ = ax3.pie(
            arranjos.values,
            autopct="%1.1f%%",
            startangle=90
        )
        ax3.legend(
            partes,
            arranjos.index,
            loc="center left",
            bbox_to_anchor=(1, 0.5)
        )

    ax3.set_title(f"Arranjos familiares - {ra}")
    fig_arranjos.tight_layout()
    canvas_arranjos.draw()


def atualizar_interface(evento=None):
    """Atualiza estatísticas e gráficos."""
    dados = filtrar_ra()
    moradores, idade, pessoas, criancas = calcular_estatisticas(dados)

    lbl_moradores.config(text=f"Moradores: {moradores}")
    lbl_idade.config(text=f"Idade média: {idade:.1f} anos")
    lbl_pessoas.config(text=f"Média por domicílio: {pessoas:.1f} pessoas")
    lbl_criancas.config(text=f"Crianças de 0 a 12 anos: {int(criancas)}")

    atualizar_graficos(dados)


def exportar_txt():
    """Exporta as informações da RA para um arquivo TXT."""
    dados = filtrar_ra()
    ra = combo_ra.get()

    caminho = filedialog.asksaveasfilename(
        title="Salvar relatório",
        initialfile="relatorio_pdad.txt",
        defaultextension=".txt",
        filetypes=[("Arquivo de texto", "*.txt")]
    )

    if caminho == "":
        return

    moradores, idade, pessoas, criancas = calcular_estatisticas(dados)
    casas = dados.drop_duplicates(subset=["A01nficha"])
    arranjos = casas["arranjo_nome"].value_counts()
    total = arranjos.sum()

    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("RELATÓRIO PDAD 2024 - RECORTE F\n")
        arquivo.write(f"Região Administrativa: {ra}\n\n")
        arquivo.write(f"Moradores: {moradores}\n")
        arquivo.write(f"Idade média: {idade:.1f} anos\n")
        arquivo.write(f"Média de pessoas por domicílio: {pessoas:.1f}\n")
        arquivo.write(f"Crianças de 0 a 12 anos: {int(criancas)}\n\n")
        arquivo.write("Arranjos familiares:\n")

        for nome, quantidade in arranjos.items():
            percentual = quantidade / total * 100
            arquivo.write(
                f"- {nome}: {quantidade} ({percentual:.1f}%)\n"
            )

    messagebox.showinfo("Concluído", "Relatório salvo com sucesso.")


def carregar_bases():
    """Carrega os dados e preenche a lista de RAs."""
    global df_completo

    lbl_status.config(text="Carregando dados...")
    janela.update_idletasks()

    try:
        df_completo = carregar_dados()
    except Exception as erro:
        lbl_status.config(text="Erro ao carregar.")
        messagebox.showerror("Erro", str(erro))
        return

    lista_ras = sorted(df_completo["ra_nome"].unique())
    combo_ra["values"] = lista_ras
    lbl_status.config(text="Dados carregados com sucesso.")

    if lista_ras:
        combo_ra.set(lista_ras[0])
        atualizar_interface()


def construir_janela():
    """Cria a interface gráfica."""
    global janela, combo_ra, lbl_status
    global lbl_moradores, lbl_idade, lbl_pessoas, lbl_criancas
    global fig_piramide, fig_tamanho, fig_arranjos
    global canvas_piramide, canvas_tamanho, canvas_arranjos

    janela = tk.Tk()
    janela.title("PDAD 2024 - Recorte F")
    janela.geometry("1000x700")

    ttk.Label(
        janela,
        text="Perfil demográfico e composição domiciliar",
        font=("Arial", 14, "bold")
    ).pack(pady=(10, 2))

    ttk.Label(
        janela,
        text="Exploração dos dados da PDAD 2024 por Região Administrativa"
    ).pack()

    lbl_status = ttk.Label(janela, text="Aguardando carregamento...")
    lbl_status.pack(pady=5)

    frame_filtro = ttk.Frame(janela)
    frame_filtro.pack(fill="x", padx=15, pady=5)

    ttk.Label(frame_filtro, text="Região Administrativa:").pack(side="left")

    combo_ra = ttk.Combobox(frame_filtro, state="readonly", width=35)
    combo_ra.pack(side="left", padx=8)
    combo_ra.bind("<<ComboboxSelected>>", atualizar_interface)

    ttk.Button(
        frame_filtro,
        text="Exportar TXT",
        command=exportar_txt
    ).pack(side="right")

    frame_info = ttk.LabelFrame(janela, text="Estatísticas", padding=8)
    frame_info.pack(fill="x", padx=15, pady=5)

    lbl_moradores = ttk.Label(frame_info, text="Moradores: -")
    lbl_idade = ttk.Label(frame_info, text="Idade média: -")
    lbl_pessoas = ttk.Label(frame_info, text="Média por domicílio: -")
    lbl_criancas = ttk.Label(frame_info, text="Crianças de 0 a 12 anos: -")

    lbl_moradores.grid(row=0, column=0, padx=15, pady=3)
    lbl_idade.grid(row=0, column=1, padx=15, pady=3)
    lbl_pessoas.grid(row=1, column=0, padx=15, pady=3)
    lbl_criancas.grid(row=1, column=1, padx=15, pady=3)

    abas = ttk.Notebook(janela)
    abas.pack(fill="both", expand=True, padx=15, pady=8)

    aba1 = ttk.Frame(abas)
    aba2 = ttk.Frame(abas)
    aba3 = ttk.Frame(abas)

    abas.add(aba1, text="Pirâmide etária")
    abas.add(aba2, text="Tamanho dos domicílios")
    abas.add(aba3, text="Arranjos familiares")

    fig_piramide = Figure(figsize=(7, 4), dpi=100)
    fig_tamanho = Figure(figsize=(7, 4), dpi=100)
    fig_arranjos = Figure(figsize=(7, 4), dpi=100)

    canvas_piramide = FigureCanvasTkAgg(fig_piramide, master=aba1)
    canvas_tamanho = FigureCanvasTkAgg(fig_tamanho, master=aba2)
    canvas_arranjos = FigureCanvasTkAgg(fig_arranjos, master=aba3)

    canvas_piramide.get_tk_widget().pack(fill="both", expand=True)
    canvas_tamanho.get_tk_widget().pack(fill="both", expand=True)
    canvas_arranjos.get_tk_widget().pack(fill="both", expand=True)


def main():
    """Inicia o programa."""
    construir_janela()
    janela.after(100, carregar_bases)
    janela.mainloop()


if __name__ == "__main__":
    main()