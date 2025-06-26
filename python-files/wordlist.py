import itertools

def w_l(length, charset):
    for word in itertools.product(charset, repeat=length):
        print("".join(word))

charset = "abcdefghijklmnopqrstuvwxyz"
length = 5
w_l(length, charset)