#!/usr/bin/env python
# coding: utf-8

# In[2]:


print("escribe un numero")
dato = input()
print("el numero escrito es: ", int(dato)*12)


# In[15]:


def mifuncion(a):
    print(int(a)


mifuncion(5)    


# In[14]:


miDiccionario={}
miDiccionario = {"nombre": "Juan", "edad": 30, "ciudad": "Madrid"}

a="hola mundo"
b="pues muy bien"
print(f"{a} {b}")
print(a, b)
for clave, valor in miDiccionario.items():
    print(clave,":", valor) 
    print("O tambien se podria--------->")
    print(f"{clave}: {valor}")

    


# In[22]:


import hashlib

def generar_clave_128bits(dato_entrada: str) -> str:
    # Calcular hash SHA-256 del dato de entrada
    hash_obj = hashlib.sha256(dato_entrada.encode())
    hash_digest = hash_obj.digest()
    
    # Tomar los primeros 16 bytes (128 bits)
    clave_128_bits = hash_digest[:16]

    
    # Convertir a hexadecimal para representación legible
    return clave_128_bits.hex()

def hex_a_binario(hexadecimal):
    # Convertir hexadecimal a decimal
    decimal = int(hexadecimal, 16)
    # Convertir decimal a binario y retirar el prefijo '0b'
    binario = bin(decimal)[2:]
    return binario


# Ejemplo de uso
dato = "mi dato de entrada1"
clave = generar_clave_128bits(dato)
print("Clave 128 bits (hex):", clave)
print("clave en binario: ", hex_a_binario(clave))


# In[27]:


def or_binarios(bin1, bin2):
    # Convertir a enteros
    int1 = int(bin1, 2)
    int2 = int(bin2, 2)
    
    print("Valor de int1", int1)
    print("Valor de int2", int2)
    
    # Operación OR bit a bit
    resultado_int = int1 | int2
    
    # Convertir resultado a binario y rellenar a 128 bits
    resultado_bin = bin(resultado_int)[2:].zfill(128)
    
    return resultado_bin

# Ejemplo de uso con dos cadenas binarias de 128 bits
binario1 = '0' * 127 + '1'  # Ejemplo: 127 ceros y un 1 al final
binario2 = '1' + '0' * 127  # Ejemplo: 1 al principio y 127 ceros

print("binarios2", binario2)

resultado = or_binarios(binario1, binario2)
print(resultado)



# In[47]:


from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# Generar un par de claves RSA (clave pública y privada)
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

public_key = private_key.public_key()

print(private_key)
print(public_key)


# In[44]:


def operador_or(texto_binario, clave_binario):
    global resultado
    resultado=""
    for t1, c2 in zip(texto_binario, clave_binario):    
        if t1 == c2:
            resultado = resultado + "0"
        else:
            resultado = resultado + "1"
            
    return resultado


texto = "hola"
print(texto.encode())
binarios_texto = [format(b, '08b') for b in texto.encode()]
print("Este texto es: ", texto, " en binario -->",binarios_texto)
print("Y la longitud del texto es: ",len(binarios_texto))

# Unir para ver toda la cadena en binario
binario_texto = ''.join(binarios_texto)
print("Este es el texto en binario: ",binario_texto)

clave = "123455555"
print(clave.encode())
binarios_clave =  [format(b, '08b') for b in clave.encode()]
print("Esta es la clave ", clave, "en binario -->",binarios_clave)
print("La longitud de la clave es: ", len(clave))

# Unir para ver toda la cadena en binario
binarios_clave = ''.join(binarios_clave)
print("Este es la clave en binario: ",binarios_clave)

if len(binarios_clave) > len(binario_texto):
    dif = len(binarios_clave) - len(binario_texto)
    binario_texto = binario_texto.ljust(len(binario_texto) + dif, '0')
    print("El resultado de binario_texto añadiendo 0 por la derecha",binario_texto )


# Unir para ver toda la cadena en binario
print("Este es el resultado: ",operador_or(binario_texto,binarios_clave))


# In[1]:


def operador_or(texto_binario, clave_binario):
    global resultado
    resultado=""
    for t1, c2 in zip(texto_binario, clave_binario):    
        if t1 == c2:
            resultado = resultado + "0"
        else:
            resultado = resultado + "1"
            
    return resultado

def binario_a_texto(binario):
    texto = ""
    for i in range(0, len(binario), 8):
        byte = binario[i:i+8]
        texto += chr(int(byte, 2))
    return texto

def decodificador(resultado_binario, clave):
    #1º Pasar la clave a binario:
    clave_binaria = [format(b, '08b') for b in clave.encode()]
    clave_binaria = ''.join(clave_binaria)
    
    #comprobar el tamaño de la clave con el resultado_binario:
    if(len(clave_binaria) > len(resultado_binario)):
        dif = len(clave_binaria) - len(resultado_binario)
        resultado_binario = resultado_binario.ljust(len(resultado_binario) + dif, '0')
    elif(len(clave_binaria) < len(resultado_binario)):
        dif = len(resultado_binario) - len(clave_binaria)
        clave_binaria = clave_binaria.ljust(len(clave_binaria) + dif, '0')
    
    #2º descodificamos
    respuesta_decodificada_binario = operador_or(resultado_binario, clave_binaria)
    return binario_a_texto(respuesta_decodificada_binario)

def codificar(texto_binario, clave_binario):
    return operador_or(texto_binario, clave_binario)

texto = input("Introduce un Texto para codificar: ")
#texto = "hola"
print(texto.encode())
binarios_texto = [format(b, '08b') for b in texto.encode()]
print("Este texto es: ", texto, " en binario -->",binarios_texto)
print("Y la longitud del texto es: ",len(binarios_texto))
# Unir para ver toda la cadena en binario
binario_texto = ''.join(binarios_texto)
print("Este es el texto en binario: ",binario_texto)

clave = input("Introduce una contraseña: ")
#clave = "12345678910611111111111111111"
print(clave.encode())
binarios_clave =  [format(b, '08b') for b in clave.encode()]
print("Esta es la clave ", clave, "en binario -->",binarios_clave)
print("La longitud de la clave es: ", len(clave))
# Unir para ver toda la cadena en binario
binarios_clave = ''.join(binarios_clave)
print("Este es la clave en binario: ",binarios_clave)

if len(binarios_clave) > len(binario_texto):
    dif = len(binarios_clave) - len(binario_texto)
    binario_texto = binario_texto.ljust(len(binario_texto) + dif, '0')
    print("El resultado de binario_texto añadiendo 0 por la derecha",binario_texto)
elif len(binarios_clave) < len(binario_texto):
    dif = len(binario_texto) - len(binarios_clave)
    binarios_clave = binarios_clave.ljust(len(binarios_clave) + dif, '0')
    print("El resultado de binario_clave añadiendo 0 por la derecha",binarios_clave)

# Unir para ver toda la cadena en binario
texto_codificado = codificar(binario_texto,binarios_clave)

print(decodificador(texto_codificado,clave))

#print(binario_a_texto("00110001001100100011001100110100"))
    


# In[64]:


def operador_or(texto_binario, clave_binario):
    global resultado
    resultado=""
    for t1, c2 in zip(texto_binario, clave_binario):    
        if t1 == c2:
            resultado = resultado + "0"
        else:
            resultado = resultado + "1"
            
    return resultado

def binario_a_texto(binario):
    texto = ""
    for i in range(0, len(binario), 8):
        byte = binario[i:i+8]
        texto += chr(int(byte, 2))
    return texto

print(binario_a_texto("0011000100110010001100110011010000110101001101100011011100111000001110010011000100110000001101100000000000000000000000000000000000000000000000000000000000000000"))

#print(operador_or("01101000011011110110110001100001","00110001001100100011001100110100"))


# In[ ]:




