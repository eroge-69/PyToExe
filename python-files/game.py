import random

print("\n\n\n【猜数字游戏】") # "\": escape; "n": newline
print("规则很简单，每局随机1~100中的一个数字，你猜是几！")

# 成功次数
wins = 0
# 是否退出
q = True

# 一轮游戏循环
while q:
    # print("【本轮开始】")
    print(f"\n【第{wins+1}轮】")

    # 生成答案
    answer = random.randint(1,100)

    guess = int(input("请输入猜想："))

    # 猜错循环
    while guess!=answer:
        if guess<1 or guess>100:
            guess=int(input("请输入1~100的数字"))
        elif guess<answer:
            guess = int(input("太小了，再猜："))
        elif guess>answer:
            guess = int(input("太大了，再猜："))
    
    # 跳出循环说明猜对了
    wins += 1
    print("🎉🎉🎉 恭喜猜中 🎉🎉🎉")
    print("以下指令")
    print("  > 直接回车再来一把；\n  > 输入q退出程序；\n  > 输入s查询成功次数。")
    
    # 处理指令循环
    while True:
        command = input("请输入指令：")
        if command=='':
            break
        elif command=='q':
            q=False
            break
        elif command=='s':
            print(f'~~~ 目前已成功猜中{wins}次 ~~~')
            continue
        else:
            continue

print("\n拜拜~\n")