s = int(input ("請輸入數字"))
a = 2

while s > a:
      r = s % a
      if r == 0:
         print(s, "是合成數。")
         break
      a += 1
            
else:
      print(s, "是質數。")
