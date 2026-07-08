import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

df_completo = pd.DataFrame()

def carregar_dados():
    global df_completo
    try:
        print("... guenta ai") 
        

        df_m = pd.read_csv("moradores.csv", sep=";", low_memory=False)
        df_d = pd.read_excel("domicilios.xlsx")
        df_dict = pd.read_excel("dicionario_de_variaveis_pdada_2024_público.xlsx", sheet_name="anexo_1")
        
        ra_mapping = dict(zip(df_dict['Valor'], df_dict['Descrição do valor']))
        
        df_m = df_m[(df_m['idade_calculada'] != 99999) & (df_m['idade_calculada'] != 88888)]
        df_d = df_d[(df_d['A01npessoas'] != 99999) & (df_d['A01npessoas'] != 88888)]
        df_d = df_d[(df_d['A01ncriancas'] != 99999) & (df_d['A01ncriancas'] != 88888)]
        
        df_d_simplificado = df_d[['A01nficha', 'A01npessoas', 'A01ncriancas']]
        
        df_completo = pd.merge(df_m, df_d_simplificado, on="A01nficha")
        df_completo['ra_nome'] = df_completo['localidade'].map(ra_mapping)

        lbl_status.config(text=f"Registros: {len(df_m)} moradores / {len(df_d)} domicilios")
        
        lista_ras = sorted([str(name) for name in df_completo['ra_nome'].dropna().unique()])
        combo_ra['values'] = lista_ras
        if lista_ras:
            combo_ra.set(lista_ras[0])
            atualizar_interface()
    except Exception:
        pass



def calcular_metricas(df_ra):
    """Calcula estatísticas """
    if df_ra.empty:
        return 0, 0, 0
    med_idade = df_ra['idade_calculada'].mean()
    med_pessoas = df_ra['A01npessoas'].mean()
    tot_criancas = df_ra['A01ncriancas'].sum()
    return med_idade, med_pessoas, tot_criancas

def atualizar_interface(event=None):
    """Filtra os microdados pela RA selecionada e updates a janela."""
    ra_sel = combo_ra.get()
    
    df_ra = df_completo[df_completo['ra_nome'] == ra_sel]
    
    m_idade, m_pessoas, t_criancas = calcular_metricas(df_ra)
    lbl_idade.config(text=f"Idade Média da População: {m_idade:.1f} anos")
    lbl_pessoas.config(text=f"Média de Pessoas por Domicílio: {m_pessoas:.1f} pessoas")
    lbl_criancas.config(text=f"Total de Crianças na Localidade: {int(t_criancas)} crianças")
    
    fig.clear()
    ax = fig.add_subplot(111)
    ax.hist(df_ra['idade_calculada'], bins=15, color="#000000", edgecolor='black')
    ax.set_title(f"Distribuição Etária — {ra_sel}", fontsize=10, fontweight='bold')
    ax.set_xlabel("Idade (Anos)", fontsize=8)
    ax.set_ylabel("Quantidade de Moradores", fontsize=8)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    fig.tight_layout()
    canvas.draw()

def exportar_relatorio():
    ra_sel = combo_ra.get()
    print(f"--> Iniciando exportacao de dados de {ra_sel}") 
    df_ra = df_completo[df_completo['ra_nome'] == ra_sel]
    m_idade, m_pessoas, t_criancas = calcular_metricas(df_ra)
    
    arquivo = filedialog.asksaveasfilename(
        initialfile=f"relatorio_{ra_sel.lower().replace(' ', '_')}.txt",
        defaultextension=".txt",
        filetypes=[("Documento de Texto", "*.txt")]
    )
    
    if arquivo:
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(f"PDAD 2024")
            f.write(f"Região Administrativa Analisada: {ra_sel}\n")
            f.write(f"Amostras Individuais: {len(df_ra)} registros\n\n")
            f.write(f"Métricas Descritivas Calculadas:\n")
            f.write(f"* Idade Média dos Habitantes: {m_idade:.2f} anos\n")
            f.write(f"* Densidade Domiciliar Média: {m_pessoas:.2f} pessoas/casa\n")
            f.write(f"* População Infantil Estimada: {int(t_criancas)} crianças\n")

janela = tk.Tk()
janela.title("PDAD 2024")
janela.geometry("600x580")
janela.resizable(False, False)

tk.Label(janela, text="Análise Demográfica PDAD 2024", font=("Arial", 12,)).pack(pady=5)
tk.Label(janela, text="Recorte F: Análise de composição etária e tamanho familiar.", font=("Arial", 9, "italic")).pack(pady=2)

lbl_status = tk.Label(janela, text="")
lbl_status.pack(pady=3)

frame_filtro = tk.Frame(janela)
frame_filtro.pack(pady=5, fill="x", padx=15)

tk.Label(frame_filtro, text="Selecione a RA:").pack(side="left", padx=5)
combo_ra = ttk.Combobox(frame_filtro, state="readonly", width=40)
combo_ra.pack(side="left", padx=5)
combo_ra.bind("<<ComboboxSelected>>", atualizar_interface)

frame_stats = tk.LabelFrame(janela, text=" Indicadores", padx=10, pady=5)
frame_stats.pack(pady=5, fill="x", padx=15)

lbl_idade = tk.Label(frame_stats, text="Idade media da população:", font=("Arial", 9, "bold"))
lbl_idade.pack(anchor="w")

lbl_pessoas = tk.Label(frame_stats, text="Média de pessoas por domicilio: ", font=("Arial", 9, "bold"))
lbl_pessoas.pack(anchor="w")

lbl_criancas = tk.Label(frame_stats, text="Total de crianças na localidade:", font=("Arial", 9, "bold"))
lbl_criancas.pack(anchor="w")

fig = plt.Figure(figsize=(5, 2.5), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=janela)
canvas.get_tk_widget().pack(pady=5, fill="both", expand=True, padx=15)

tk.Button(janela, text="Exportar Dados (.txt)", command=exportar_relatorio).pack(pady=5)
tk.Label(janela, text="Mateus de Lima — 232021937 — Projeto Final APC", fg="black", font=("Arial", 8)).pack(side="bottom", pady=5)

janela.after(100, carregar_dados)
janela.mainloop()