import hashlib
dic = {}
for I in range(0 , 10000) :
    tran = f"{I:04}"
    dic[tran] = hashlib.sha256(tran.encode()).hexdigest()
z = input ("Hashcode:")
for key, value in dic.items() :
    if value == z :
        print (key)