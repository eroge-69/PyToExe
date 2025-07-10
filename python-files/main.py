def calculate_volume_by_centimeters(length_in_cm):
    return 209 / 85 * length_in_cm

def calculate_weight_by_buckets(bucket_count):
    return bucket_count * 18  

def main():
    while True:
        print("MENU")
        print("1. Calcular tambor")
        print("2. Calcular balde")
        print("3. Sair")

        choice = input("Escolha uma opção (1-3): ")

        if choice == "1":
            try:
                length_cm = float(input("Digite o comprimento em centímetros: ").replace(",", "."))
                volume = calculate_volume_by_centimeters(length_cm)
                print(f"Resultado: {volume:.2f} unidades")
            except ValueError:
                print("Por favor, digite um número válido.")
        elif choice == "2":
            try:
                buckets = int(input("Digite a quantidade de baldes: "))
                weight = calculate_weight_by_buckets(buckets)
                print(f"Peso total: {weight} kg")
            except ValueError:
                print("Por favor, digite um número inteiro válido.")
        elif choice == "3":
            print("Encerrando a calculadora.")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
