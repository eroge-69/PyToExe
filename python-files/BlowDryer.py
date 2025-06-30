#   ____________________________
#  /                            \
# |         BlowDryer.py         |
#  \____________________________/
#

with open("BlowDryer.py", "r") as f:
    code = f.read()

with open("_.count", "r") as f:
    num = int(f.read())

with open("_.count", "w") as f:
    num += 1
    f.write(str(num))

with open("BlowDryer" + str(num) + ".py", "w") as f:
    f.write(code)
