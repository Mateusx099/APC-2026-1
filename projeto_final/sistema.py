import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

df_completo = pd.DataFrame()

def carregar_dados():
    """Lê as planilhas, limpa os dados sentinelas e realiza o merge relacional das bases."""
    global df_completo
    try:
        df_m = pd.read_csv("moradores.csv", sep=";", low_memory=False)
        df_d = pd.read_excel("domicilios.xlsx")
        df_dict = pd.read_excel("dicionario_de_variaveis_pdada_2024_público.xlsx", sheet_name="anexo_1")
        
        df_m.columns = df_m.columns.str.strip()
        df_d.columns = df_d.columns.str.strip()
        df_dict.columns = df_dict.columns.str.strip()
        
        ra_mapping = dict(zip(df_dict['Valor'], df_dict['Descrição do valor']))
        e05_mapping = {1: "Unipessoal", 2: "Casal sem filhos", 3: "Casal com filhos", 4: "Mãe solo", 5: "Pai solo", 6: "Outros"}
        
        df_m['A01nficha'] = df_m['A01nficha'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        df_d['A01nficha'] = df_d['A01nficha'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
        for c in df_m.columns:
            if c.lower() in ['idade_calculada', 'localidade', 'e04', 'c04', 'sexo', 'id_genero', 'e05']:
                df_m[c] = pd.to_numeric(df_m[c], errors='coerce')
        for c in df_d.columns:
            if c.lower() in ['a01npessoas', 'a01ncriancas', 'e05']:
                df_d[c] = pd.to_numeric(df_d[c], errors='coerce')
        
        df_m = df_m[(df_m['idade_calculada'] != 99999) & (df_m['idade_calculada'] != 88888)]
        df_d = df_d[(df_d['A01npessoas'] != 99999) & (df_d['A01npessoas'] != 88888)]
        df_d = df_d[(df_d['A01ncriancas'] != 99999) & (df_d['A01ncriancas'] != 88888)]
        
        if 'E05' in df_m.columns:
            df_m = df_m[(df_m['E05'] != 99999) & (df_m['E05'] != 88888)]
        elif 'E05' in df_d.columns:
            df_d = df_d[(df_d['E05'] != 99999) & (df_d['E05'] != 88888)]
            
        cols_d = ['A01nficha', 'A01npessoas', 'A01ncriancas']
        if 'E05' in df_d.columns:
            cols_d.append('E05')
            
        df_d_simplificado = df_d[cols_d].drop_duplicates(subset=['A01nficha'])
        df_completo = pd.merge(df_m, df_d_simplificado, on="A01nficha")
        
        df_completo['ra_nome'] = df_completo['localidade'].map(ra_mapping)
        
        if 'E05' in df_completo.columns:
            df_completo['arranjo_nome'] = df_completo['E05'].map(e05_mapping).fillna(df_completo['E05'].astype(str))
        else:
            df_completo['arranjo_nome'] = "Não informado"
            
        col_gen = None
        for c in df_completo.columns:
            if c.lower() in ['e04', 'c04', 'sexo', 'id_genero']:
                col_gen = c
                break
        if col_gen:
            df_completo['id_genero_calc'] = pd.to_numeric(df_completo[col_gen], errors='coerce')
        else:
            df_completo['id_genero_calc'] = None

        lbl_status.config(text=f"Sucesso! {len(df_completo)} registros processados.")
        
        lista_ras = sorted([str(name) for name in df_completo['ra_nome'].dropna().unique()])
        combo_ra['values'] = lista_ras
        if lista_ras:
            combo_ra.set(lista_ras[0])
            atualizar_interface()
    except Exception as e:
        messagebox.showerror("Erro Crítico", f"Falha ao carregar:\n{str(e)}")

def calcular_metricas(df_ra):
    """Calcula estatísticas descritivas (média, soma, moda) isoladas da interface visual."""
    if df_ra.empty:
        return 0, 0, 0, "N/A"
    med_idade = df_ra['idade_calculada'].mean()
    med_pessoas = df_ra['A01npessoas'].mean()
    tot_criancas = df_ra['A01ncriancas'].sum()
    m_res = df_ra['arranjo_nome'].mode()
    arranjo_topo = str(m_res.iloc[0]) if not m_res.empty else "N/A"
    return med_idade, med_pessoas, tot_criancas, arranjo_topo

def atualizar_interface(event=None):
    """Filtra dados pela RA ativa no menu, atualiza indicadores e redesenha os gráficos."""
    ra_sel = combo_ra.get()
    df_ra = df_completo[df_completo['ra_nome'] == ra_sel]
    
    m_idade, m_pessoas, t_criancas, a_topo = calcular_metricas(df_ra)
    lbl_idade.config(text=f"Idade Média da População: {m_idade:.1f} anos")
    lbl_pessoas.config(text=f"Média de Pessoas por Domicílio: {m_pessoas:.1f} pessoas")
    lbl_criancas.config(text=f"Total de Crianças: {int(t_criancas)} | Arranjo Comum: {a_topo}")
    
    fig_m.clear()
    fig_f.clear()
    fig_a.clear()
    
    ax_m = fig_m.add_subplot(111)
    ax_f = fig_f.add_subplot(111)
    ax_a = fig_a.add_subplot(111)
    
    # Aba 1 e 2: Histogramas de Idade
    if 'id_genero_calc' in df_ra.columns and df_ra['id_genero_calc'].notna().any():
        m_mask = df_ra['id_genero_calc'] == 1.0
        f_mask = df_ra['id_genero_calc'] == 2.0
        
        if not f_mask.any():
            f_mask = (df_ra['id_genero_calc'].notna()) & (df_ra['id_genero_calc'] != 1.0)
            
        m_ages = df_ra[m_mask]['idade_calculada'].dropna()
        f_ages = df_ra[f_mask]['idade_calculada'].dropna()
        
        ax_m.hist(m_ages, bins=15, color="#2b5c8f", edgecolor='black')
        ax_f.hist(f_ages, bins=15, color="#d95f02", edgecolor='black')
    else:
        ax_m.hist(df_ra['idade_calculada'].dropna(), bins=15, color="#6c3483", edgecolor='black')
        ax_f.hist(df_ra['idade_calculada'].dropna(), bins=15, color="#6c3483", edgecolor='black')
        
    ax_m.set_title(f"Composição Etária Masculina — {ra_sel}", fontsize=10, fontweight='bold')
    ax_m.set_xlabel("Idade (Anos)", fontsize=8)
    ax_m.set_ylabel("Quantidade de Moradores (Amostra)", fontsize=8)
    ax_m.grid(axis='y', linestyle='--', alpha=0.5)
    
    ax_f.set_title(f"Composição Etária Feminina — {ra_sel}", fontsize=10, fontweight='bold')
    ax_f.set_xlabel("Idade (Anos)", fontsize=8)
    ax_f.set_ylabel("Quantidade de Moradores (Amostra)", fontsize=8)
    ax_f.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Aba 3: Gráfico de Pizza de Arranjos Familiares
    contagem_arranjos = df_ra['arranjo_nome'].value_counts()
    if not contagem_arranjos.empty:
        ax_a.pie(contagem_arranjos, labels=contagem_arranjos.index, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 8})
        ax_a.set_title(f"Perfil de Arranjos Familiares — {ra_sel}", fontsize=10, fontweight='bold')
    
    fig_m.tight_layout()
    fig_f.tight_layout()
    fig_a.tight_layout()
    
    canvas_m.draw()
    canvas_f.draw()
    canvas_a.draw()

def exportar_relatorio():
    """Gera um arquivo .txt formatado com os indicadores calculados da RA selecionada."""
    ra_sel = combo_ra.get()
    df_ra = df_completo[df_completo['ra_nome'] == ra_sel]
    m_idade, m_pessoas, t_criancas, a_topo = calcular_metricas(df_ra)
    
    arquivo = filedialog.asksaveasfilename(
        initialfile=f"relatorio_{ra_sel.lower().replace(' ', '_')}.txt",
        defaultextension=".txt",
        filetypes=[("Documento de Texto", "*.txt")]
    )
    
    if arquivo:
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(f"PDAD 2024\n")
            f.write(f"Região Administrativa Analisada: {ra_sel}\n")
            f.write(f"Amostras Individuais: {len(df_ra)} registros\n\n")
            f.write(f"Métricas Descritivas Calculadas:\n")
            f.write(f"* Idade Média dos Habitantes: {m_idade:.2f} anos\n")
            f.write(f"* Densidade Domiciliar Média: {m_pessoas:.2f} pessoas/casa\n")
            f.write(f"* População Infantil Estimada: {int(t_criancas)} crianças\n")
            f.write(f"* Arranjo Familiar Predominante: {a_topo}\n")

janela = tk.Tk()
janela.title("PDAD 2024 - Sistema de Inteligência Demográfica")
janela.geometry("800x650") 
janela.state('zoomed') # Abre o sistema maximizado em tela cheia
janela.resizable(True, True)

tk.Label(janela, text="Análise Demográfica PDAD 2024", font=("Arial", 12, "bold")).pack(pady=5)
tk.Label(janela, text="Recorte F: Análise de composição etária, adensamento e arranjos familiares.", font=("Arial", 10, "italic")).pack(pady=2)

lbl_status = tk.Label(janela, text="")
lbl_status.pack(pady=3)

frame_filtro = tk.Frame(janela)
frame_filtro.pack(pady=5, fill="x", padx=15)

tk.Label(frame_filtro, text="Selecione a RA:").pack(side="left", padx=5)
combo_ra = ttk.Combobox(frame_filtro, state="readonly", width=40)
combo_ra.pack(side="left", padx=5)
combo_ra.bind("<<ComboboxSelected>>", atualizar_interface)

frame_stats = tk.LabelFrame(janela, text=" Indicadores Demográficos (Tempo Real) ", padx=10, pady=5)
frame_stats.pack(pady=5, fill="x", padx=15)

lbl_idade = tk.Label(frame_stats, text="Idade media da população:", font=("Arial", 10, "bold"))
lbl_idade.pack(anchor="w", pady=2)

lbl_pessoas = tk.Label(frame_stats, text="Média de pessoas por domicilio: ", font=("Arial", 10, "bold"))
lbl_pessoas.pack(anchor="w", pady=2)

lbl_criancas = tk.Label(frame_stats, text="Total de crianças na localidade:", font=("Arial", 10, "bold"))
lbl_criancas.pack(anchor="w", pady=2)

# Sistema de Abas
notebook = ttk.Notebook(janela)
notebook.pack(pady=5, fill="both", expand=True, padx=15)

aba_homens = ttk.Frame(notebook)
notebook.add(aba_homens, text="Distribuição Etária (Masculino)")

aba_mulheres = ttk.Frame(notebook)
notebook.add(aba_mulheres, text="Distribuição Etária (Feminino)")

aba_arranjos = ttk.Frame(notebook)
notebook.add(aba_arranjos, text="Estrutura Familiar (Arranjos)")

# Canvas Masculino
fig_m = plt.Figure(figsize=(5, 3), dpi=100)
canvas_m = FigureCanvasTkAgg(fig_m, master=aba_homens)
canvas_m.get_tk_widget().pack(pady=5, fill="both", expand=True)

# Canvas Feminino
fig_f = plt.Figure(figsize=(5, 3), dpi=100)
canvas_f = FigureCanvasTkAgg(fig_f, master=aba_mulheres)
canvas_f.get_tk_widget().pack(pady=5, fill="both", expand=True)

# Canvas Pizza (Arranjos)
fig_a = plt.Figure(figsize=(5, 3), dpi=100)
canvas_a = FigureCanvasTkAgg(fig_a, master=aba_arranjos)
canvas_a.get_tk_widget().pack(pady=5, fill="both", expand=True)

# Rodapé
frame_rodape = tk.Frame(janela)
frame_rodape.pack(fill="x", side="bottom", pady=10)

tk.Button(frame_rodape, text="Exportar Relatório (.txt)", font=("Arial", 9, "bold"), command=exportar_relatorio).pack(pady=5)
tk.Label(frame_rodape, text="Mateus de Lima — 232021937 — Projeto Final APC", fg="black", font=("Arial", 8)).pack(pady=2)

janela.after(100, carregar_dados)
janela.mainloop()