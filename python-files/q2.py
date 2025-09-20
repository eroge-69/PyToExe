import random
import sympy
import time

        
def correctness_check(k_1, k_2)-> bool:
    if (k_1 == k_2):
        return True
    else:
        return False
    


# using p and g from the Reference
p = 898846567431157953854195783968937265989301480243783420555165923800167437681267498321228388839564102546198423597101336410666468834111713556904492294748479777844382830870763301843657378425949779355866142709546265053025135405421453846466009564097233813503
g = 5


a = int(input("Input a: "))
b = int(input("Input b: "))

A = (g ** a) % p
B = (g ** b) % p

start_time_k1 = time.time()
k_1 = B ** a
end_time_k1 = time.time()

start_time_k2 = time.time()
k_2 = A ** b
end_time_k2 = time.time()

correct = correctness_check(k_1=k_1, k_2=k_2)


print("A = ", A)
print("B = ", B)
print("K = ", k_1)
print("k_1==k_2: ", correct)
print(f"Time taken to compute k_1: {end_time_k1 - start_time_k1:.6f} seconds")
print(f"Time taken to compute k_2: {end_time_k2 - start_time_k2:.6f} seconds")


