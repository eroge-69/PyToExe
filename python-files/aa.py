
cache: list = []

def square(num):
    return num*num

def step(number):
    if number in cache:
        return "sad"
    cache.append(number)
    digits = list(str(number))
    digits = [int(digit) for digit in digits]
    number = sum(map(square, digits))
    step(number)