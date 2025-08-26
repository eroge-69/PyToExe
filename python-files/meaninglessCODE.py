while True:
    code_esolang = input("")
    if code_esolang == "code()":
        break
    elif code_esolang == "":
        continue
    else:
        print("SYNTAX ERROR")
        break
if code_esolang == "code()":
  print("this is all this esolang does")