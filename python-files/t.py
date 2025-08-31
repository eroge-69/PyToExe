import random
t=0
f=0
while True:
#STOCK

    st_1=[1,2,3,4,5,6,7,8,9,0]
    st_2=[1,2,3,4,5,6,7,8,9]
    r_st1=random.choice(st_1)
    r_st2=random.choice(st_2)
    stock_0 = str('6'+str(r_st1)+'-000'+str(r_st2)+'-00')

#SHILF

    sh_1=[1,2,3,4,5,6,7,8,9,0]
    sh_2=['C','D','E','F','G','H','J','L']
    sh_3=[1,2,3,4,5,6,7]
    sh_4=['10','20','30','40']
    r_sh1=random.choice(sh_1)
    r_sh2=random.choice(sh_2)
    r_sh3=random.choice(sh_3)
    r_sh4=random.choice(sh_4)
    shilf_0=str('08-6'+str(r_sh1)+r_sh2+str(r_sh3)+'-'+r_sh4)
    st_sh=[shilf_0,stock_0]
    st_or_sh=random.choice(st_sh)

#PRINT STOCK,SHILF

    print('STOCK or SHILF: '+ st_or_sh)

#ITEM

    it_1=[5,6]
    it_2=[1,2,3,4,5,6,7,8,9,0]
    r_it1=random.choice(it_1)
    r_it2=random.choice(it_2)
    r_it3=random.choice(it_2)
    r_it4=random.choice(it_2)
    r_it5=random.choice(it_2)
    r_it6=random.choice(it_2)
    item=str(r_it1)+str(r_it2)+str(r_it3)+str(r_it4)+str(r_it5)+str(r_it6)
    print('Item          : '+ item)

#QTY

    Q_1= [1,2,3,4,5,6,7,8,9]
    Q_2= [1,2,3,4,5,6,7,8,9,0]
    r_q1=random.choice(Q_1)
    r_q2=random.choice(Q_2)
    r_q3=random.choice(Q_2)
    r_q4=random.choice(Q_2)
    r_q5=random.choice(Q_2)
    rr0=str(0)
    rr1=str(r_q1)
    rr2=str(r_q1)+str(r_q2)
    rr3=str(r_q1)+str(r_q2)+str(r_q3)
    rr4=str(r_q1)+str(r_q2)+str(r_q3)+str(r_q4)
    rr5=str(r_q1)+str(r_q2)+str(r_q3)+str(r_q4)+str(r_q5)
    rr=[rr0,rr1,rr2,rr3,rr4,rr5]
    QRRR=random.choice(rr)
    print('QTY           : '+QRRR)

#INPUT

    inp_sh_st=str(input('ENTER SHILF or STOCK : ').upper())
    inp_it=str(input('ENTER Item : '))
    inp_q=str(input('ENTER QTY : '))
    
#IF
    if  (inp_sh_st == st_or_sh) and (inp_it == item) and ( inp_q == QRRR) :
        t=t+1
        
        print ('_____ SYSTEM CONNECT ✔ _____' + str(t))
    else : 
        f=f+1
        print ('_____INVALID❌ ____'+  str(f))
        
        
        
        
        
        
        
        