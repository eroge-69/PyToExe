playermoney = 100
playerinv = ["sword"]
buy_dict = {
    "sword": 10,
    "advanced sword": 15 ,
    "mega sword": 20,
    "bow": 15,
    "sigma gun": 20,
}


sell_dict = {
    "sword": 9,
    "advanced sword": 12 ,
    "mega sword": 17,
    "bow": 14,
    "sigma gun": 14,
}
def shop_my(playermoney,playerinv):
    print('Hi, welcome to the shop. What do you want to do?')
    cycleshop = False
    while cycleshop == False:
        buysell = input('1-Buy\n2-Sell\n3-Exit\nType here:  ')
        print('')
        if buysell == "1":
            for item, price in buy_dict.items():
                print(f"{item} : {price} $")
            print('')
            print('What do you want to buy?')
            buy = input('Type:   ').strip().lower()
            if buy in buy_dict:
                print('You want to buy',buy,'?')
                print('')
                choise = input('1-Yes\n2-No\nType here:  ')
                if choise == '1':
                    print('')
                    print('You have',playermoney,'$')
                    print("You bought",buy,f"for {buy_dict[buy]}$")
                    if playermoney >= buy_dict[buy]:
                        playermoney -= buy_dict[buy]
                        playerinv.append(buy)
                        print('Now you have',playerinv,'and',playermoney,'$')
                        print('')
                    elif playermoney < buy_dict[buy]:
                        print('You dont have enough money')
                elif choise == '2':
                    print('Do you want to buy or sell something else?')
                    print('')
            else:
                print('Item not found')
                print('')
        elif buysell == '2':
            print('What do you want so you want to sell?')
            sell = input(f'You have {playerinv}\nType here:  ')
            if sell in sell_dict and playerinv:
                print('You want to sell',sell,'?')
                selltrue = input('1-Yes\n2-No\nType here:  ')
                if selltrue == '1':
                    print(f"You sold {sell} for {sell_dict[sell]}$")
                    playermoney += sell_dict[sell]
                    playerinv.remove(sell)
                    print('Now you have',playerinv,'and',playermoney,'$')
            else:
                print('You dont have this item!')
        
        
        
        
        
        
        
        
        
        
        
        
        
        else:
            buysell == '3'
            break




































































































shop_my(playermoney,playerinv)
   