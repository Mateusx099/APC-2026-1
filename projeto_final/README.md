# Projeto Final APC - Analise PDAD 2024 (Recorte F)

Este projeto apresenta uma interface grafica em Tkinter para analisar o perfil demografico e a composicao domiciliar do Distrito Federal com base nos microdados da PDAD 2024.

## Funcionalidades
- Carregamento e limpeza de dados (tratamento de valores sentinela).
- Cruzamento de dados (merge) entre as tabelas de moradores e domicilios.
- Filtro interativo por Regiao Administrativa (RA).
- Calculo de metricas: idade media, media de moradores por casa e total de criancas.
- Visualizacao grafica da distribuicao etaria via histograma do Matplotlib.
- Exportacao de relatorio estatistico em formato TXT.

## Requisitos
E necessario ter o Python instalado e as seguintes bibliotecas:
- pandas
- matplotlib
- openpyxl

Para instalar as dependencias, rode o comando:
pip install pandas matplotlib openpyxl

## Arquivos Necessarios
Para o programa rodar, os seguintes arquivos devem estar na mesma pasta do script:
- sistema.py
- moradores.csv
- domicilios.xlsx
- dicionario_de_variaveis_pdada_2024_público.xlsx

## Como Executar
Abra o terminal na pasta do projeto e execute:
python sistema.py

