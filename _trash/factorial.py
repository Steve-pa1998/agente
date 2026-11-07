def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

if __name__ == '__main__':
    # Casos de prueba
    print(factorial(5))  # Debería imprimir 120
    print(factorial(0))  # Debería imprimir 1
    print(factorial(1))  # Debería imprimir 1