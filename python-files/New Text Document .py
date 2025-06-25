memolist = [["🌷","🌷","🌷","🌷"],["🌷","🌷","🌷","🌷"],["🌷","🌷","🌷","🌷"]]
print(f"{memolist [0]} \n{memolist [1]} \n{memolist [2]}")

mum = input("whene do you want insart the monkey 🙈")
row = int(mum[0]) 
pos = int(mum[1]) 

memolist[row-1] [pos-1] = "🙈"

print(f"{memolist [0]} \n{memolist [1]} \n{memolist [2]}")

