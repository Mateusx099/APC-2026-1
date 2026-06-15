def calcular_media(lista):
    """Calcula a média de uma lista de números"""
    if len(lista) == 0:
        return 0
    return sum(lista) / len(lista)

def calcular_mdc(a, b):
    """Calcula o MDC de dois números inteiros"""
    while b != 0:
        a, b = b, a % b
    return a

def verificar_primo(n):
    """Verifica se um número é primo (retorna True ou False)"""
    if n <= 1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

# === TESTES PARA VER O CÓDIGO FUNCIONAR NO TELA ===
print("=== TESTANDO A BIBLIOTECA MATEMÁTICA ===")

# Testando a média
minhas_notas = [10.0, 8.0, 6.0]
print(f"A média das notas é: {calcular_media(minhas_notas)}")

# Testando o MDC
print(f"O MDC de 24 e 36 é: {calcular_mdc(24, 36)}")

# Testando se é primo
numero = 7
if verificar_primo(numero):
    print(f"O número {numero} é primo!")
else:
    print(f"O número {numero} NÃO é primo.")
