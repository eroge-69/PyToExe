def celsius_to_fahrenheit(c):
    return (c * 9/5) + 32

def celsius_to_kelvin(c):
    return c + 273.15

def fahrenheit_to_celsius(f):
    return (f - 32) * 5/9

def fahrenheit_to_kelvin(f):
    c = fahrenheit_to_celsius(f)
    return celsius_to_kelvin(c)

def kelvin_to_celsius(k):
    return k - 273.15

def kelvin_to_fahrenheit(k):
    c = kelvin_to_celsius(k)
    return celsius_to_fahrenheit(c)

def converter_temperatura():
    print("Conversor de Temperatura - Celsius, Fahrenheit e Kelvin")
    try:
        valor = float(input("Digite o valor da temperatura: "))
        unidade = input("Digite a unidade original (C, F ou K): ").strip().upper()

        if unidade == 'C':
            f = celsius_to_fahrenheit(valor)
            k = celsius_to_kelvin(valor)
            print(f"{valor}°C equivalem a {f:.2f}°F e {k:.2f} K.")
        elif unidade == 'F':
            c = fahrenheit_to_celsius(valor)
            k = fahrenheit_to_kelvin(valor)
            print(f"{valor}°F equivalem a {c:.2f}°C e {k:.2f} K.")
        elif unidade == 'K':
            c = kelvin_to_celsius(valor)
            f = kelvin_to_fahrenheit(valor)
            print(f"{valor} K equivalem a {c:.2f}°C e {f:.2f}°F.")
        else:
            print("Unidade inválida! Use C, F ou K.")
    except ValueError:
        print("Por favor, digite um número válido para a temperatura.")

if __name__ == "__main__":
    converter_temperatura()
