alt = float(input("Insira a altura do objeto (em metros): ").replace(',', '.'))
larg = float(input("Insira a largura do objeto (em metros): ").replace(',', '.'))
valm2 = float(input("Insira o valor do produto por m²: ").replace(',', '.'))
units = int(input("Insira a quantidade de adesivos: "))

# área de uma unidade
m2_unit = alt * larg

# área total real do pedido
qtdm2_real = m2_unit * units

# aplicar mínimo de 0.5m² sobre a ÁREA TOTAL (não por unidade)
qtdm2_cobrado = qtdm2_real if qtdm2_real >= 0.5 else 0.5

# preço final
precofim = qtdm2_cobrado * valm2

print(f"\nÁrea por unidade: {m2_unit:.6f} m²")
print(f"Área total real: {qtdm2_real:.3f} m²")
if qtdm2_real < 0.5:
    print(f"Área cobrada (mínimo aplicado): {qtdm2_cobrado:.3f} m²")
else:
    print(f"Área cobrada: {qtdm2_cobrado:.3f} m²")
print(f"Valor total: R$ {precofim:.2f}")
