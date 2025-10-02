import random
import json
import os

# =========================
# 游戏基础数据
# =========================
SAVE_FILE = "save.json"

# 地图大小
MAP_SIZE = 5

# 职业属性
CLASSES = {
    "战士": {"hp": 40, "atk": 6, "luck": 2},
    "盗贼": {"hp": 25, "atk": 4, "luck": 6},
    "法师": {"hp": 20, "atk": 8, "luck": 3},
}

# =========================
# 游戏核心类
# =========================
class Player:
    def __init__(self, name, job):
        self.name = name
        self.job = job
        self.hp = CLASSES[job]["hp"]
        self.atk = CLASSES[job]["atk"]
        self.luck = CLASSES[job]["luck"]
        self.gold = 0
        self.inventory = []
        self.x = 0
        self.y = 0
        self.explored = set()

    def status(self):
        print(f"\n--- {self.name} ({self.job}) 状态 ---")
        print(f"HP: {self.hp} | 攻击: {self.atk} | 幸运: {self.luck} | 金币: {self.gold}")
        print(f"位置: ({self.x}, {self.y})\n背包: {self.inventory if self.inventory else '空'}")
        print("----------------------------------")

class Enemy:
    def __init__(self, name, hp, atk):
        self.name = name
        self.hp = hp
        self.atk = atk

# =========================
# 游戏逻辑
# =========================
def save_game(player):
    data = player.__dict__.copy()
    data["explored"] = list(player.explored)
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print("✅ 游戏进度已保存！")

def load_game():
    if not os.path.exists(SAVE_FILE):
        print("⚠️ 没有找到存档。")
        return None
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    player = Player(data["name"], data["job"])
    player.__dict__.update(data)
    player.explored = set(data["explored"])
    print("✅ 存档已读取！")
    return player

def battle(player, enemy):
    print(f"⚔️ 遭遇 {enemy.name}！ (HP:{enemy.hp} ATK:{enemy.atk})")
    while player.hp > 0 and enemy.hp > 0:
        print("\n选择技能：1) 普通攻击  2) 重击  3) 防御  4) 魔法")
        choice = input("> ")

        if choice == "1":
            dmg = player.atk
            enemy.hp -= dmg
            print(f"你攻击了 {enemy.name}，造成 {dmg} 点伤害！")

        elif choice == "2":
            if random.random() < 0.5:
                dmg = player.atk * 2
                enemy.hp -= dmg
                print(f"重击成功！{enemy.name} 受到了 {dmg} 点伤害！")
            else:
                print("重击落空！")

        elif choice == "3":
            print("你进入防御姿态，本回合受到的伤害减半。")
            enemy_dmg = max(1, enemy.atk // 2)
            player.hp -= enemy_dmg
            print(f"{enemy.name} 攻击了你，造成 {enemy_dmg} 点伤害！")
            continue

        elif choice == "4":
            dmg = player.atk + random.randint(3, 6)
            enemy.hp -= dmg
            print(f"你释放了魔法，对 {enemy.name} 造成 {dmg} 点伤害！")

        if enemy.hp > 0:
            enemy_dmg = enemy.atk
            player.hp -= enemy_dmg
            print(f"{enemy.name} 攻击了你，造成 {enemy_dmg} 点伤害！")

    if player.hp > 0:
        gold_gain = random.randint(5, 15)
        player.gold += gold_gain
        print(f"🎉 你打败了 {enemy.name}，获得 {gold_gain} 金币！")
        return True
    else:
        print("💀 你被击败了！游戏结束。")
        exit()

def explore(player):
    coord = (player.x, player.y)
    if coord in player.explored:
        print("这里你已经探索过了，什么都没有发生。")
        return
    player.explored.add(coord)

    event = random.choice(["enemy", "treasure", "shop", "empty", "quest", "boss"])
    if event == "enemy":
        enemy = Enemy("史莱姆", 15, 3)
        battle(player, enemy)
    elif event == "treasure":
        gold = random.randint(10, 30)
        player.gold += gold
        print(f"💰 你发现了宝箱，获得 {gold} 金币！")
    elif event == "shop":
        print("🛒 你遇到一个流浪商人，他卖药草（回血10点，价格10金币）。")
        if player.gold >= 10 and input("要购买吗？(y/n) ") == "y":
            player.gold -= 10
            player.inventory.append("药草")
            print("你买下了药草。")
    elif event == "quest":
        print("📜 你遇到一个旅行者，他请求你击败附近的怪物。任务完成后或许会有奖励！")
    elif event == "boss" and len(player.explored) > (MAP_SIZE * MAP_SIZE) // 2:
        boss = Enemy("森林领主", 50, 8)
        print("⚠️ 你闯入了Boss的巢穴！")
        battle(player, boss)
        print("🎉 你打败了Boss，成为了冒险的英雄！")
        ending(player)
        exit()
    else:
        print("这里一片安静，什么都没有。")

def use_item(player):
    if not player.inventory:
        print("你的背包是空的。")
        return
    print("你的背包:", player.inventory)
    item = input("选择要使用的物品: ")
    if item in player.inventory:
        if item == "药草":
            player.hp += 10
            player.inventory.remove(item)
            print("你使用了药草，恢复了10点HP。")
    else:
        print("没有这个物品。")

def ending(player):
    print("\n=== 游戏结局 ===")
    if player.gold >= 100:
        print("💰 你带着满满的财富离开了森林，成为了传奇商人！")
    elif player.hp > 20:
        print("⚔️ 你走出了森林，带着荣耀与力量，成为了英雄。")
    else:
        print("🌌 你艰难地逃出了森林，这段冒险将成为你的秘密记忆。")

# =========================
# 主流程
# =========================
def main():
    print("=== 欢迎来到文字冒险游戏 ===")
    if os.path.exists(SAVE_FILE) and input("是否读取存档？(y/n) ") == "y":
        player = load_game()
        if not player:
            return
    else:
        name = input("请输入角色名字: ")
        print("选择职业: 战士 / 盗贼 / 法师")
        job = input("> ")
        if job not in CLASSES:
            job = "战士"
        player = Player(name, job)

    while True:
        player.status()
        print("行动选项：1) 上  2) 下  3) 左  4) 右  5) 使用物品  6) 存档  7) 退出")
        cmd = input("> ")
        if cmd == "1" and player.y > 0:
            player.y -= 1
            explore(player)
        elif cmd == "2" and player.y < MAP_SIZE - 1:
            player.y += 1
            explore(player)
        elif cmd == "3" and player.x > 0:
            player.x -= 1
            explore(player)
        elif cmd == "4" and player.x < MAP_SIZE - 1:
            player.x += 1
            explore(player)
        elif cmd == "5":
            use_item(player)
        elif cmd == "6":
            save_game(player)
        elif cmd == "7":
            print("👋 游戏结束，下次再见！")
            break
        else:
            print("无效指令。")

if __name__ == "__main__":
    main()
