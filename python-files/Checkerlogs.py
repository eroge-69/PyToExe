import sys
dire=sys.argv[0]
stk=[0]
stat={}
dire.replace('\\','/')
print(dire)
def ifnew(a):
    if not a in stat:
        stat[a]=[0,0]
with open(dire,'r') as file:
    for i in file.readlines():
        m=i.split()
        if m[0]=='LOGOUT':
            if stk[-1]==0 or not m[1] in stk:
                ifnew(m[1])
                stat[m[1]][1]=stat[m[1]][1]+1
                print(f"Ошибка: выход пользователя {m[1]} без входа")
            else:
                stk.pop(-1)
                ifnew(m[1])
                stat[m[1]][0]=stat[m[1]][0]+1
                print(f"Сессия {m[1]} закрыта")
        if m[0]=='LOGIN':
            if m[1] in stk:
                print(f"Ошибка: попытка открыть вторую сессию для пользователя {m[1]}")
                ifnew(m[1])
                stat[m[1]][1]=stat[m[1]][1]+1
            else:
                stk.append(m[1])
                print(f"Сессия {m[1]} открыта")
    if stk[-1]!=0:
        str1=''
        for i in stk[1:]:
            ifnew(m[1])
            stat[i][1]=stat[i][1]+1
            str1+=i+' '
        print(f"Ошибка, незакрытые сессии: {str1}")
    print('\nСтатистика:')
    for i in stat.items():
        print(f"{i[0]} - сессий: {i[1][0]}, ошибок:{i[1][1]}")
    input("Enter чтобы выйти")
        
