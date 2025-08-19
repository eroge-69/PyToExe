# Listas para armazenar os dados
codigos = []
nomes = []
precos = []

print("=== Cadastro de Produtos ===")

# Cadastro de 3 produtos
for i in range(3):
    print(f"\nProduto {i+1}:")
    codigo = input("Digite o código de barras: ")
    nome = input("Digite o nome do produto: ")
    preco = float(input("Digite o preço do produto (ex: 23.90): "))

    codigos.append(codigo)
    nomes.append(nome)
    precos.append(preco)

# Exibição dos produtos cadastrados
print("\n=== Produtos Cadastrados ===")
for i in range(3):
    print(f"Produto: {nomes[i]} | Código: {codigos[i]} | Preço: R$ {precos[i]:.2f}")
