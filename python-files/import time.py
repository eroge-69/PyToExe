import time
import os
import sys

print('System initialization in progress...')

time.sleep(2)
os.system('cls')

trueenter1 = 0
trueenter2 = 0
trueenter3 = 0
jf = 0
uin1 = 0
uin2 = 0
uin3 = 0
uin4 = 0
kp1name = 1
kp1price = 50
kp2name = 2
kp2price = 75
kp3name = 0
kp3price = 0
kp4name = 0
kp4price = 0
kp5name = 0
kp5price = 0
kp1quantity = 0
kp2quantity = 0
kp3quantity = 0
kp4quantity = 0
kp5quantity = 0

print('欢迎')
print('v1.0')
time.sleep(0.75)
os.system('cls')
print('主页')
os.system('cls')
trueenter1 = 0
while trueenter1 == 0:
    print('剩余积分',jf)
    time.sleep(0.1)
    print('您想做什么？')
    time.sleep(0.1)
    print('输入1以打开积分商城')
    time.sleep(0.1)
    print(' ')
    print('输入2以打开卡牌商城')
    time.sleep(0.1)
    print(' ')
    print('输入3以打开卡包')
    time.sleep(0.1)
    print(' ')
    print('输入0以退出程序')
    time.sleep(0.1)
    print('请输入...')
    uin1 = input()
    if uin1 == '0':
        sys.exit()
    elif uin1 == '1':
        os.system('cls')
        print('请输入增加积分的数量... ps：必须是阿拉伯数字，否则会报错！！！')
        uin2 = input()
        jf += int(uin2)
        print(jf)
        os.system('cls')
        
        
#增加积分部分完成
    elif uin1 == '2':
        os.system('cls')
        trueenter2 = 0
        while trueenter2 == 0:
            os.system('cls')
            print('输入1以购买',kp1name,'需要',kp1price,'积分')
            time.sleep(0.1)
            print(' ')
            print('输入2以购买',kp2name,'需要',kp2price,'积分')
            time.sleep(0.1)
            print(' ')
            print('输入3以购买',kp3name,'需要',kp3price,'积分')
            time.sleep(0.1)
            print(' ')
            print('输入4以购买',kp4name,'需要',kp4price,'积分')
            time.sleep(0.1)
            print(' ')
            print('输入5以购买',kp5name,'需要',kp5price,'积分')
            time.sleep(0.1)
            print(' ')
            print('输入0以返回上一级')
            print(' ')
            print('请输入... ps：必须是阿拉伯数字，否则会报错！！！')
            uin3 = input()
            os.system('cls')
            if uin3 == '1':
                if jf >= kp1price:
                    jf -= int(kp1price)
                    kp1quantity += 1
                    print(kp1name,'购买成功，已扣积分',kp1price)
                    time.sleep(3)
                    os.system('cls')
                else:
                    print('余额不足，购买失败')
                    time.sleep(3)
                    os.system('cls')
            elif uin3 == '2':
                if jf >= kp2price:
                    jf -= int(kp2price)
                    kp2quantity += 1
                    print(kp2name,'购买成功，已扣积分',kp2price)
                    time.sleep(3)
                    os.system('cls')
                else:
                    print('余额不足，购买失败')
                    time.sleep(3)
                    os.system('cls') 
            elif uin3 == '3':
                if jf >= kp3price:
                    jf -= int(kp3price)
                    kp3quantity += 1
                    print(kp3name,'购买成功，已扣积分',kp3price)
                    time.sleep(3)
                    os.system('cls')
                else:
                    print('余额不足，购买失败')
                    time.sleep(3)
                    os.system('cls')    
            elif uin3 == '4':
                if jf >= kp4price:
                    jf -= int(kp4price)
                    kp4quantity += 1
                    print(kp4name,'购买成功，已扣积分',kp4price)
                    time.sleep(3)
                    os.system('cls')
                else:
                    print('余额不足，购买失败')
                    time.sleep(3)
                    os.system('cls')
            elif uin3 == '5':
                if jf >= kp5price:
                    jf -= int(kp5price)
                    kp5quantity += 1
                    print(kp5name,'购买成功，已扣积分',kp5price)
                    time.sleep(3)
                    os.system('cls')
                else:
                    print('余额不足，购买失败')
                    time.sleep(3)
                    os.system('cls')
            elif uin3 == '0':
                trueenter2 += 1
            else:
                print('输入错误')
                
                
                
#购买卡牌部分完成
    elif uin1 == '3':
        os.system('cls')
        trueenter3 = 0
        while trueenter3 == 0:
            if kp1quantity >= 0:
                print('有',kp1quantity,'张',kp1name)
                print('输入1以使用')
                time.sleep(0.1)
  
            if kp2quantity >= 0:
                print('有',kp2quantity,'张',kp2name)
                print('输入2以使用')
            if kp3quantity >= 0:
                print('有',kp3quantity,'张',kp3name)
                print('输入3以使用')
            if kp4quantity >= 0:
                print('有',kp4quantity,'张',kp4name)
                print('输入4以使用')
            if kp5quantity >= 0:
                print('有',kp5quantity,'张',kp5name)
                print('输入5以使用')
            if kp1quantity == 0 and kp2quantity == 0 and kp3quantity == 0 and kp4quantity == 0 and kp5quantity == 0:
                print('你还没有卡牌，快去购买吧')
            print('请输入... ps：必须是阿拉伯数字，否则会报错！！！')
            uin4 = input()
            if uin4 =='0':
                trueenter3 += 1
            elif uin4 == 1 or 2 or 3 or 4 or 5:
                print('此部分还没完成，即将返回上一级')
                time.sleep(5)
                trueenter3 += 1
            else:
                print('输入错误')
    else:
        print('输入错误')

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
input()
