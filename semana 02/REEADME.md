# Semana 02 - Simulador de CPU e Memória

## O que foi feito
Criamos um projeto no OctoStudio para simular o funcionamento básico de uma CPU e da memória, fazendo um paralelo com o LMC (Little Man Computer) e o modelo de arquitetura de Von Neumann. 

## Conceitos e Ciclo de Execução (Fetch-Decode-Execute)
- **Fetch (Busca):** O programa busca a instrução (o bloco que vem a seguir na sequência ou o evento de clique).
- **Decode (Decodificação):** O sistema processa o comando para entender o que ele pede (se é para mover, somar ou mudar de cor).
- **Execute (Execução):** O robô realiza a ação na tela.

## Diferença entre LMC e OctoStudio
No simulador do LMC, a gente consegue ver a memória e os registradores guardando os números de forma explícita por endereços. No OctoStudio, isso fica escondido por trás da interface visual. A memória acaba sendo representada pelas variáveis que guardam os valores (como a quantidade de passos) e a CPU é o próprio ator interpretando os blocos.

## Algoritmo base do robô
1. Iniciar o simulador.
2. Definir a variável de passos como 10.
3. Perguntar a direção para o usuário.
4. Se a resposta for "frente", andar o valor da variável (10) e mudar o traje do robô.
5. Se não, manter o robô parado em standby.
