import re

stroka = """38088  10  100  0
115709  0  100  0
144  -1  100  0
59  -3  100  0
3171  10  300  0
1  2  300  0
2  1  300  0
9060  0  300  0
600  -1  300  0
52  1  400  0
161  0  400  0
2  -1  400  0
2  1  402  0"""

def get_info(text):
    
    my_dict = {
        "Pallet": [0,0,0], # 1,402,VIRTUAL
        "Case": [0,0], # 1,10
        "Bottle": [0,0,0] # 1,10,-1
    }

    mas = stroka.splitlines()
    mas_ad = []
    otvet = ''
    for i in mas:
        mas_ad.append(i.split())
    
    for i in mas_ad:
        Counter = int(i[0])
        Status = int(i[1])
        Type = int(i[2])
        NotificationStatus = int(i[3])
        
        if Type == 100 and Status != 0:
            if Status == 1:
                my_dict['Bottle'][0] += Counter
            if Status == 10:
                my_dict['Bottle'][1] += Counter
                
        if Type == 300 and Status != 0:
            if Status == 1:
                my_dict['Case'][0] += Counter
            if Status == 10:
                my_dict['Case'][1] += Counter
        
        if Type == 400 and Status != 0:
            if Status == 1:
                my_dict['Pallet'][0] += Counter
        
        if Type == 402 and Status != 0:
            if Status == 1:
                my_dict['Pallet'][1] += Counter
        
        if Type == 405 and Status != 0:
            my_dict['Pallet'][2] += Counter
                
    for i in my_dict:
        num = 0
        if i == 'Pallet':
            num = my_dict[i][0] + my_dict[i][1] + my_dict[i][2]
            otvet += 'Паллеты - Всего(' + str(num) + '): '
            if int(my_dict[i][0]) != 0 :
                otvet +=  str(my_dict[i][0]) + ' полные'
            if int(my_dict[i][1]) != 0 :
                otvet +=  ' + ' + str(my_dict[i][1]) + ' неполные '
            if int(my_dict[i][2]) != 0 :
                otvet += ' + ' + str(my_dict[i][2]) + ' виртуальные '
            
        if i == 'Case':
            num = my_dict[i][0] + my_dict[i][1]
            otvet += '\nКейсы: Всего(' + str(num) + '): '
            if int(my_dict[i][0]) != 0 :
                otvet +=  str(my_dict[i][0]) + ' упакованные'
            if int(my_dict[i][1]) != 0 :
                otvet +=  ' + ' + str(my_dict[i][1]) + ' не агрег. в паллеты '
        
        if i == 'Bottle':
            num = my_dict[i][0] + my_dict[i][1]
            otvet += '\nБутылки: Всего(' + str(num) + '): '
            if int(my_dict[i][0]) != 0 :
                otvet +=  ' + ' + str(my_dict[i][0]) + ' упакованные '
            if int(my_dict[i][1]) != 0 :
                otvet +=  str(my_dict[i][1]) + ' не упакованные '
                
    return otvet
    
            
    