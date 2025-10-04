n = int(input())

for num in range(2, n + 1):
    if num <= 1:
        is_prime = False
    else:    
        is_prime = True
        d = 2 # initialize the divisor
        while d <= num-1:
            if num % d == 0:
                is_prime = False
            d += 1
        
    if is_prime == True:
        print(num, end=" ")
print("end")        