import os
for i in range (0, 5):
    fo = open ( os.environ['USERPROFILE'] + f"\Desktop\ILY{i}.txt", "w" )
    for j in range (1000):
        fo.write ( "Я тя лю " )
    fo.read()    
    fo.close()
    
