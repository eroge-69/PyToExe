# -*- coding: utf-8 -*-
import random
import time
import os

# --- 辅助函数 ---
def print_slow(text, delay=0.05):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# --- 角色定义 ---
class Character:
    def __init__(self, name, max_hp, abilities, items, gifts, is_player=False):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.abilities = abilities
        self.items = items
        self.gifts = gifts
        self.is_player = is_player
        self.is_stunned = False
        self.is_desperate = False
        self.in_dying_burst = False
        self.in_meikyo = False
        self.internal_injury_damage = 0
        self.meikyo_turns = 0
        self.stim_turns = 0
        self.first_aid_immune_turns = 0
        self.milk_heal_turns = 0
        self.gift_used = False
        self.actions_per_turn = 1

    def take_damage(self, damage, attacker):
        if self.in_dying_burst and self.name == "Marilyn":
            damage += 1
            print_slow(f"（濒死爆发：Marilyn受到的伤害+1）")
        self.hp -= damage
        print_slow(f"💥 {self.name} 受到了 {damage} 点伤害！")
        if damage > self.max_hp * 0.5:
            print_slow(f"‼️ {self.name} 受到重创，进入【架势崩溃】状态！下一回合无法攻击！")
            self.is_stunned = True
        if not self.in_dying_burst and self.hp <= self.max_hp * 0.5:
            self.trigger_dying_burst()
        if self.hp <= 0:
            self.hp = 0
            self.is_desperate = True
            print_slow(f"生死一线！{self.name} 的生命值归零，进入【绝命】状态！")

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
        print_slow(f"💚 {self.name} 恢复了 {amount} 点生命值。")

    def trigger_dying_burst(self):
        self.in_dying_burst = True
        print_slow(f"\n--- 状态激活：【濒死爆发】 ---")
        if self.name == "Marilyn":
            print_slow("Marilyn的速度激增，掌法伤害提升，使用道具不再消耗回合！但每次受伤会更痛。")
        else:
            print_slow("Lifeng的速度激增，奥义不再消耗生命，并且每回合可以行动两次！")
            if "预存乳汁" in self.items and self.items["预存乳汁"] > 0:
                self.items["预存乳汁"] -= 1
                self.milk_heal_turns = 6
                print_slow("\n--- 回忆闪回：生命之泉 ---", 0.06)
                print_slow(
                    "Lifeng的胸前衣物被乳汁浸湿，那熟悉的、甜美的香气瞬间唤醒了她的记忆。她想起了那个雨夜，在温暖的被褥里，女友将她紧紧抱在怀中。",
                    0.06,
                )
                print_slow(
                    "她记得女友柔软的嘴唇是如何吻遍她的全身，记得她丰满的胸部在自己身上磨蹭时的触感，记得女友在她耳边轻语：‘我的身体……我的一切，都是属于你的。’",
                    0.06,
                )
                print_slow(
                    "‘把这个喝下去，’女友将这生命之源渡到她的口中，‘这是我们爱的证明。无论你身在何处，无论多么危险，我的爱都会像这样，治愈你，保护你。答应我，一定要回来。’",
                    0.06,
                )
                print_slow(
                    "（Lifeng内心独白：是啊……我答应过她的。这份温暖……这份爱……就是我战斗的意义！我绝不能在这里倒下！）", 0.06
                )

    def apply_turn_effects(self):
        print(f"\n--- {self.name} 回合效果结算 ---")
        if self.is_stunned:
            print(f"{self.name} 从【架势崩溃】中恢复，但本回合依然无法攻击。")
            self.is_stunned = False
        if self.in_dying_burst:
            self.hp -= 1
            print(f"（濒死爆发：{self.name} 因透支生命而失去1点HP）")
        if self.internal_injury_damage > 0:
            self.hp -= self.internal_injury_damage
            print(f"（内伤：{self.name} 因内伤流失了 {self.internal_injury_damage} 点HP）")
        if self.meikyo_turns > 0:
            self.hp -= 3
            self.meikyo_turns -= 1
            print(f"（命驱：剩余{self.meikyo_turns}回合）")
        if self.stim_turns > 0:
            self.stim_turns -= 1
            print(f"（性奋剂：效果持续中，剩余{self.stim_turns}回合）")
            if self.stim_turns == 0:
                print_slow("\n--- 回忆闪回：极乐的烙印 ---", 0.06)
                print_slow(
                    "药效如潮水般退去，随之而来的是深入骨髓的空虚。Marilyn的脑海中不受控制地浮现出那夜的残像——她被密友压在华丽的丝绸床单上，双手被皮带缚于头顶。",
                    0.06,
                )
                print_slow(
                    "她记得密友那比男人更具侵略性的目光，以及那炙热的、不属于女性的器官是如何一次又一次地贯穿自己，带来毁灭般的快感。她记得自己在高潮中哭喊着求饶，却只换来对方更深的占有。",
                    0.06,
                )
                print_slow(
                    "最后，在一阵滚烫的洪流中，她被彻底填满。密友在她耳边用沙哑的声音说：‘记住这种感觉。这是你属于我的证明。’", 0.06
                )
                print_slow(
                    "那份灼热和满足感，此刻化为巨大的失落和心痛，仿佛灵魂被抽走了一块。Marilyn忍不住弯下腰，心口一阵剧痛。", 0.06
                )
                self.hp -= 10
                print_slow(f"（性奋剂：效果结束，{self.name} 因巨大的失落感而心口剧痛，受到10点伤害！）")
        if self.first_aid_immune_turns > 0:
            self.first_aid_immune_turns -= 1
        if self.milk_heal_turns > 0:
            self.heal(5)
            self.milk_heal_turns -= 1
            print(f"（预存乳汁：恢复5点HP，剩余{self.milk_heal_turns}回合）")
        if self.hp <= 0 and not self.is_desperate:
            self.hp = 0
            self.is_desperate = True
            print_slow(f"生死一线！{self.name} 因持续伤害耗尽生命，进入【绝命】状态！")

    def update_actions_per_turn(self):
        if self.stim_turns > 0:
            self.actions_per_turn = 3
            return
        actions = 1
        if self.in_dying_burst and self.name == "Lifeng":
            actions += 1
        if self.in_meikyo:
            actions += 1
        self.actions_per_turn = actions


# --- 游戏主类 ---
class Game:
    def __init__(self):
        self.marilyn = Character(
            name="Marilyn",
            max_hp=60,
            abilities={
                "三连掌": {"total": 4, "effect_chance": 15},
                "连环踢": {"total": 5},
                "八卦掌": {"damage": 15, "heal": 5, "recoil": 15},
            },
            items={"急救喷雾": 5, "性奋剂": 1},
            gifts={"密友的馈赠": {"threshold": 90, "heal": 45}},
            is_player=True,
        )
        self.lifeng = Character(
            name="Lifeng",
            max_hp=20,
            abilities={
                "百華繚乱": {"total": 5, "stagger_chance": 20, "bleed_chance": 50},
                "飞燕突": {"damage": 6},
                "莲华踢": {"total": 5, "stagger_chance": 20, "bleed_chance": 50},
                "奥义·红莲开华": {"damage": 18, "cost": 5, "bleed_chance": 50},
                "命驱": {"cost": 5, "duration": 3},
            },
            items={"预存乳汁": 1},
            gifts={"女友的馈赠": {"threshold": 90, "heal": 10}},
        )
        self.turn = 1
        self.game_over = False

        self.marilyn_taunts = [
            "就这点本事吗，小妹妹？你的莲华之舞，就像小孩子过家家。",
            "你的身体已经跟不上你的战意了。放弃吧。",
            "看看你这狼狈的样子，真可怜。",
        ]
        self.lifeng_taunts = [
            "你的动作变慢了，老女人。岁月不饶人啊。",
            "就这点程度吗？连给我热身都不够。",
            "你的死相已经清清楚楚地浮现出来了。",
        ]

        self.marilyn_dialogue_pool = ["你的招数，我看穿了。", "到此为止了。", "为了她，我不能输！", "觉悟吧！"]
        self.lifeng_dialogue_pool = [
            "我的莲华，将在此地盛开！",
            "你的死相已经出现了。",
            "这就是你我之间的觉悟之差！",
            "消失吧！",
        ]
        self.marilyn_executions = [
            self.execution_marilyn_death_kiss,
            self.execution_marilyn_crushing_embrace,
            self.execution_marilyn_final_lesson,
        ]
        self.lifeng_executions = [
            self.execution_lifeng_life_drain,
            self.execution_lifeng_crimson_lotus,
            self.execution_lifeng_serene_death,
        ]

    def check_and_handle_desperate(self, attacker, defender):
        if defender.is_desperate:
            print_slow(f"\n\n--- 生死检定：【致命技】 vs 【反击检定】 ---", 0.06)
            print_slow(
                f"{attacker.name} 看准时机，对已无防备的 {defender.name} 发动了终结一切的【致命技】！", 0.06
            )
            threshold = 40
            if not defender.gift_used:
                gift_name = list(defender.gifts.keys())[0]
                threshold = defender.gifts[gift_name]["threshold"]
                defender.gift_used = True
                print_slow(
                    f"{defender.name} 在绝望中，激活了最后的底牌——【{gift_name}】！反击检定成功率大幅提升至 {threshold}！",
                    0.06,
                )
                if defender.is_player:
                    print_slow("\n--- 回忆闪回：所有权的烙印 ---", 0.06)
                    print_slow("（Marilyn内心独白：要死了吗……不！我不能死！）濒死的瞬间，无数与密友交缠的画面涌入脑海。", 0.06)
                    print_slow(
                        "她想起密友那张雌雄莫辨的俊美脸庞，想起她用手指抬起自己下巴时那充满占有欲的眼神。想起她们在落地窗前交合，城市的灯火成为背景，自己的倒影印在玻璃上，淫靡又美丽。",
                        0.06,
                    )
                    print_slow(
                        "她想起密友在自己体内留下烙印后，舔舐着自己的耳垂，用命令的口吻说：‘你是我的所有物，你的身体、你的胜利、你的生命，都属于我。没有我的允许，你不准被任何人破坏，听到了吗？’）",
                        0.06,
                    )
                    print_slow("（Marilyn内心独白：没错……我是她的……在回去见她之前，我绝不能……死在这里！）", 0.06)
                else:
                    print_slow("\n--- 回忆闪回：未来的约定 ---", 0.06)
                    print_slow("（Lifeng内心独白：结束了……？骗人！）绝望的黑暗中，一束光照了进来——那是她女友的笑脸。", 0.06)
                    print_slow(
                        "她想起女友为她梳理长发时指尖的温柔，想起她们在樱花树下接吻，花瓣落在她们的唇间。想起她们挤在一张小床上，规划着战斗结束后要去哪里旅行，要养一只猫，要开一家小小的茶馆。",
                        0.06,
                    )
                    print_slow(
                        "她想起女友在自己出征前，含泪抱着自己说：‘答应我，一定要活着回来。我们的未来，不能没有你。我等你。’）", 0.06
                    )
                    print_slow("（Lifeng内心独白：未来……我们约好的未来……我怎么能……我怎么能在这里违背约定！）", 0.06)
            print_slow(f"d100投掷... 需要小于等于 {threshold} 才能成功。")
            input("【按Enter进行反击检定...】")
            roll = random.randint(1, 100)
            print_slow(f"投掷结果是... {roll}！")
            time.sleep(1)
            if roll <= threshold:
                print_slow("【检定成功：死里逃生】！", 0.06)
                print_slow(f"爱人的誓言化作奇迹，{defender.name} 在最后一刻爆发出了超越极限的求生意志！", 0.06)
                heal_amount = defender.gifts[list(defender.gifts.keys())[0]]["heal"]
                defender.hp = heal_amount
                defender.is_desperate = False
                attacker.is_stunned = True
                print_slow(
                    f"{defender.name} 的生命值恢复到 {heal_amount}，并造成攻击方僵直1回合！战斗继续！", 0.06
                )
                time.sleep(3)
                return False
            else:
                print_slow("【检定失败：劫数难逃】。", 0.06)
                time.sleep(1)
                if attacker.name == "Marilyn":
                    random.choice(self.marilyn_executions)()
                elif attacker.name == "Lifeng":
                    random.choice(self.lifeng_executions)()
                self.game_over = True
                if defender.is_player:
                    print_slow("\nGAME OVER", 0.1)
                else:
                    print_slow("\nYOU WIN", 0.1)
                return True
        return False

    def describe_initial_scene(self):
        clear_screen()
        print_slow("--- 序幕：月下死斗 ---", 0.06)
        print_slow("夜凉如水，月色如霜。在一座精心修剪的枯山水庭院中，两道身影在白沙之上对峙，空气中弥漫着肃杀之气。", 0.06)

        print_slow(
            "\n你，Marilyn，28岁。一头鲜艳的粉红色长发在夜风中微微飘动。你身着一件明黄色的丝绸旗袍，紧紧包裹着你成熟丰腴的肉体。旗袍侧面的开叉高得惊人，几乎开到腰际，将你修长结实的大腿完全暴露出来，黑色丝袜上的吊带若隐若现。覆盖到手肘的黑色长手套和同色的尖头高跟鞋，为你增添了一抹危险而高贵的气质。",
            0.06,
        )

        print_slow(
            "\n你的对手，Lifeng，年仅18岁。她那亮丽的紫色长发扎成一个干练的高马尾，由两个可爱的白色包子头饰固定。然而，她的穿着却与可爱毫不沾边。那是一件经过大胆解构的粉色旗袍，上衣短得只能堪堪遮住乳房的上半部分，圆润饱满的下乳和紧致平坦、带着马甲线的小腹则完全暴露在空气中。下身的裙摆同样采用了延伸到腰际的超高开叉，随着她的呼吸，腰臀间惊心动魄的曲线一览无遗。金色的镶边勾勒出她青春而火辣的轮廓。",
            0.06,
        )

        print_slow("\n你看着眼前这个年轻的对手，嘴角勾起一抹轻蔑的微笑，缓缓开口：", 0.06)
        print_slow('Marilyn: "真是大胆的穿着……是急着来送死，连衣服都来不及穿好吗？"', 0.06)

        print_slow("\nLifeng的眼神冰冷如刀，完全没有少女应有的羞涩，她用清脆但毫无感情的声音回应：", 0.06)
        print_slow('Lifeng: "很快，你就会知道，我这身打扮是为了方便……在你温热的尸体上，跳完我的莲华之舞。"', 0.06)
        print_slow("\n死斗，正式开始。", 0.06)
        input("\n【按Enter键继续...】")

    def describe_battle_status(self):
        print("\n" + "—" * 20 + " 战况速写 " + "—" * 20)

        hp_percent_m = self.marilyn.hp / self.marilyn.max_hp
        if hp_percent_m > 0.75:
            print_slow("Marilyn的姿态依旧优雅，但明黄色的旗袍上已沾染了些许尘土，呼吸略显急促。")
        elif 0.5 < hp_percent_m <= 0.75:
            print_slow("一道划痕出现在Marilyn修长的大腿上，鲜血从撕裂的黑丝中渗出。她白皙的脸颊上带着一丝红晕，不知是激战所致，还是愤怒。")
        elif 0.25 < hp_percent_m <= 0.5:
            print_slow(
                "Marilyn的嘴角溢出一丝血迹，旗袍的肩头被撕开一个大口子，露出浑圆的肩膀和内衣的肩带。她的眼神变得更加危险，像一头被激怒的母豹。"
            )
        else:
            print_slow(
                "Marilyn狼狈地单膝跪地，用手撑着地面才能勉强维持平衡。黄色的旗袍已是褴褛不堪，大片雪白的肌肤暴露在外，混杂着血污和汗水，让她看起来既凄美又脆弱。"
            )

        hp_percent_l = self.lifeng.hp / self.lifeng.max_hp
        if hp_percent_l > 0.75:
            print_slow("Lifeng那暴露在外的紧致腹部上，出现了一道浅浅的红痕，但她的动作依旧迅捷如电。")
        elif 0.5 < hp_percent_l <= 0.75:
            print_slow("Lifeng的紫色马尾有些散乱，一缕发丝贴在汗湿的脸颊上。她裸露的下乳边缘，能看到一片青紫色的瘀伤，让她忍不住皱了皱眉。")
        elif 0.25 < hp_percent_l <= 0.5:
            print_slow("一道狰狞的伤口从Lifeng的侧腰划过，鲜血染红了粉色旗袍的下摆。她的呼吸变得沉重，每次起伏都牵动着伤口，带来剧痛。")
        else:
            print_slow(
                "Lifeng的身体摇摇欲坠，仿佛随时都会倒下。她用手捂着不断渗血的腹部，汗水浸透了她的短上衣，让她看起来楚楚可怜，但眼中的杀意却未曾减退分毫。"
            )

        if hp_percent_m > hp_percent_l + 0.3 and hp_percent_l < 0.5:
            print_slow(f'\nMarilyn (冷笑): "{random.choice(self.marilyn_taunts)}"', 0.06)
        elif hp_percent_l > hp_percent_m + 0.3 and hp_percent_m < 0.5:
            print_slow(f'\nLifeng (轻蔑): "{random.choice(self.lifeng_taunts)}"', 0.06)

        print("—" * 52 + "\n")

    def start_game(self):
        self.describe_initial_scene()
        self.game_loop()

    def game_loop(self):
        while not self.game_over:
            clear_screen()
            print(f"\n【回合 {self.turn}】")
            self.marilyn.apply_turn_effects()
            if self.check_and_handle_desperate(self.lifeng, self.marilyn):
                break
            self.lifeng.apply_turn_effects()
            if self.check_and_handle_desperate(self.marilyn, self.lifeng):
                break
            self.print_status()
            self.lifeng_turn()
            if self.game_over:
                break
            self.print_status()
            self.marilyn_turn()
            if self.game_over:
                break
            self.turn += 1
            input("\n【按Enter键进入下一回合...】")
        print_slow("\n游戏结束。")

    def print_status(self):
        print("\n" + "=" * 50)
        print(
            f"❤️ 生命值: Marilyn [{self.marilyn.hp}/{self.marilyn.max_hp}] | Lifeng [{self.lifeng.hp}/{self.lifeng.max_hp}]"
        )
        marilyn_status = [
            s
            for s, v in [
                ("濒死", self.marilyn.in_dying_burst),
                ("性奋剂", self.marilyn.stim_turns > 0),
                ("内伤", self.marilyn.internal_injury_damage > 0),
            ]
            if v
        ]
        lifeng_status = [
            s
            for s, v in [
                ("濒死", self.lifeng.in_dying_burst),
                ("命驱", self.lifeng.in_meikyo),
                ("内伤", self.lifeng.internal_injury_damage > 0),
                ("恢复", self.lifeng.milk_heal_turns > 0),
            ]
            if v
        ]
        print(
            f"🌟 状态: Marilyn {marilyn_status if marilyn_status else ['正常']} | Lifeng {lifeng_status if lifeng_status else ['正常']}"
        )
        print("=" * 50)
        self.describe_battle_status()

    def use_stimulant(self):
        if self.marilyn.items["性奋剂"] > 0:
            self.marilyn.items["性奋剂"] -= 1
            self.marilyn.stim_turns = 3
            print_slow("\n--- 道具使用：性奋剂 ---", 0.06)
            print_slow("你毫不犹豫地打开那个精致的小瓶，将里面的液体一饮而尽。一股辛辣又甘甜的味道在口中散开，瞬间点燃了你的神经。", 0.06)
            print_slow(
                "（Marilyn回忆：你想起了密友在把这个交给你时的场景。她将你按在梳妆台上，从背后抱住你，让你看着镜中的自己。她将小瓶凑到你唇边，用充满挑逗的语气说：‘喝下去，我的女孩。’）",
                0.06,
            )
            print_slow(
                "（‘这是我用爱意为你调制的甘露，它会让你忘记疼痛，化身无情的女武神。’她吻着你的脖颈，‘去为我带来胜利……然后，带着胜利的果实，回来接受我的奖赏。’）",
                0.06,
            )
            self.marilyn.update_actions_per_turn()
            print_slow("你的感官变得无比敏锐，心跳加速，全身充满了力量！接下来3回合内每回合能行动3次！", 0.06)
        else:
            print_slow("【性奋剂】已经用完了！")

    def use_first_aid_spray(self):
        if self.marilyn.items["急救喷雾"] > 0:
            print_slow("你使用了【急救喷雾】！")
            self.marilyn.items["急救喷雾"] -= 1
            self.marilyn.heal(30)
            self.marilyn.internal_injury_damage, self.marilyn.is_stunned = 0, False
            self.marilyn.first_aid_immune_turns = 3
            print_slow("伤痛和异常状态一扫而空，并免疫负面效果3回合！")
        else:
            print_slow("【急救喷雾】已经用完了！")

    def lifeng_turn(self):
        print("\n--- Lifeng的行动 ---")
        self.lifeng.update_actions_per_turn()
        if self.lifeng.is_stunned:
            print_slow("Lifeng处于【架势崩溃】状态，无法组织有效的进攻！")
            self.lifeng.is_stunned = False
            return
        for i in range(self.lifeng.actions_per_turn):
            if self.lifeng.hp <= 0:
                break
            print_slow(f"Lifeng发动第 {i+1} 次行动...")
            action, ability_data = self.lifeng_ai_decision()
            if action == "命驱":
                self.lifeng.in_meikyo, self.lifeng.meikyo_turns = True, 3
                cost = 5 if not self.lifeng.in_dying_burst else 0
                self.lifeng.hp -= cost
                print_slow(f"Lifeng眼神一凛，发动了【命驱】！她燃烧生命（{-cost}HP），进入了3回合的爆发状态！")
                self.lifeng.update_actions_per_turn()
                continue
            print_slow(f"Lifeng发动了【{action}】！")
            if "开华" in action:
                self.lifeng.hp -= 5 if not self.lifeng.in_dying_burst else 0
            damage = ability_data.get("damage", ability_data.get("total", 0))
            self.marilyn.take_damage(damage, self.lifeng)
            if (
                "stagger_chance" in ability_data
                and random.randint(1, 100) <= ability_data["stagger_chance"]
            ):
                print_slow("最后一击正中要害，Marilyn陷入短暂的【硬直】！")
                self.marilyn.is_stunned = True
            if (
                "bleed_chance" in ability_data
                and random.randint(1, 100) <= ability_data["bleed_chance"]
            ):
                print_slow("掌劲穿透防御，Marilyn陷入【内伤】状态！")
                self.marilyn.internal_injury_damage += 5 if "开华" in action else 1
            if self.check_and_handle_desperate(self.lifeng, self.marilyn):
                return

    def lifeng_ai_decision(self):
        if self.lifeng.hp > 10 and not self.lifeng.in_meikyo and random.random() < 0.5:
            return "命驱", self.lifeng.abilities["命驱"]
        if self.lifeng.hp > 15 and random.random() < 0.4:
            action = "奥义·红莲开华"
        else:
            action = random.choice(["百華繚乱", "飞燕突", "莲华踢"])
        return action, self.lifeng.abilities[action]

    def marilyn_turn(self):
        print("\n--- Marilyn的行动 ---")
        self.marilyn.update_actions_per_turn()
        if self.marilyn.is_stunned:
            print_slow("你处于【硬直】或【架势崩溃】状态，无法行动！")
            self.marilyn.is_stunned = False
            return
        for i in range(self.marilyn.actions_per_turn):
            if self.marilyn.hp <= 0:
                break
            if self.marilyn.in_dying_burst and self.marilyn.actions_per_turn == 1:
                choice = input("💡 濒死爆发中，免费使用道具？('喷雾'/'性奋剂'/Enter跳过): ").lower()
                if choice == "喷雾":
                    self.use_first_aid_spray()
                elif choice == "性奋剂":
                    self.use_stimulant()
            print_slow(f"\n你发动第 {i+1} 次行动...")
            self.present_player_options()
            valid_choice = False
            while not valid_choice:
                choice = input("请选择你的行动 (A, B, C): ").upper()
                if choice in ["A", "B", "C"]:
                    self.execute_player_choice(choice)
                    valid_choice = True
                else:
                    print("无效的输入，请输入 A, B, 或 C。")
            if self.check_and_handle_desperate(self.marilyn, self.lifeng):
                return

    def present_player_options(self):
        print("\n【Marilyn的选项】")
        print_slow("[选项A: 激进猛攻] 使用【三连掌】或【连环踢】。")
        print_slow("[选项B: 终极一击] 赌上一切，使用高风险高回报的【八卦掌】。")
        print_slow("[选项C: 恢复/强化] 使用【急救喷雾】或【性奋剂】。")

    def execute_player_choice(self, choice):
        if choice == "A":
            action = random.choice(["三连掌", "连环踢"])
            ability = self.marilyn.abilities[action]
            print_slow(f"你决定速攻，使出了【{action}】！")
            self.lifeng.take_damage(ability["total"], self.marilyn)
            if action == "三连掌" and random.randint(1, 100) <= ability["effect_chance"]:
                print_slow("你的掌力穿透了Lifeng的防御，她陷入【内伤】状态！")
                self.lifeng.internal_injury_damage += 1
        elif choice == "B":
            action = "八卦掌"
            print_slow("你深吸一口气，架起【八卦掌】的架势！")
            if random.random() < 0.5:
                print_slow("命中！沉重的掌击撼动了Lifeng！")
                ability = self.marilyn.abilities[action]
                self.lifeng.take_damage(ability["damage"], self.marilyn)
                self.marilyn.heal(ability["heal"])
            else:
                print_slow("攻击失手！你露出了巨大的破绽！")
                self.marilyn.take_damage(
                    self.marilyn.abilities[action]["recoil"], self.marilyn
                )
        elif choice == "C":
            if self.marilyn.in_dying_burst and self.marilyn.actions_per_turn == 1:
                print_slow("你已经利用濒死爆发的优势使用过道具了，请选择其他行动。")
                self.marilyn_turn()
                return
            item_choice = input(
                f"选择道具：[1] 急救喷雾 ({self.marilyn.items['急救喷雾']}), [2] 性奋剂 ({self.marilyn.items['性奋剂']}): "
            )
            if item_choice == "1":
                self.use_first_aid_spray()
            elif item_choice == "2":
                self.use_stimulant()
            else:
                print_slow("取消使用道具。")

    def execution_marilyn_death_kiss(self):
        print_slow("\n【处决：绝顶之吻】", 0.06)
        print_slow("你无视了Lifeng眼中的惊恐，一步步向她走近。她想后退，双腿却因力竭而颤抖，最终跌坐在地。", 0.06)
        print_slow("你抓住她的手臂，将她娇小的身体粗暴地拉入怀中，禁锢住她的所有反抗。她的挣扎在你面前，如同幼猫的抓挠，毫无意义。", 0.06)
        print_slow(
            "“不……放开我……” Lifeng的声音带着哭腔。（为什么……会输……我还没有……和她一起去看海……）她的脑海中闪过女友在沙滩上奔跑的笑脸，那份温暖的回忆此刻却成了最锋利的刀，刺得她心痛欲裂。",
            0.06,
        )
        print_slow(
            "“嘘。” 你用一种近乎残忍的温柔，吻上了她的唇。这不是一个吻，而是一场掠夺。你的舌头霸道地侵入，带着征服者的气息，在她口中肆虐，将她所有不成调的悲鸣尽数吞下。",
            0.06,
        )
        print_slow(
            "你的吻技太过高超，那不容拒绝的快感，让她身体的抵抗逐渐瓦解。她的腿开始发软，下体传来一阵阵可耻的湿热，让她感到无比的屈辱和不甘。这陌生的、被强迫的快感，甚至比和女友做爱时还要强烈，这个认知让她彻底崩溃了。",
            0.06,
        )
        print_slow(
            "“感觉到了吗？这就是你我之间，觉悟的差距。” 你在她耳边低语，加深了这个致命的吻。伴随着一声悠长而尖锐、混杂着痛苦与极乐的悲鸣，Lifeng的身体猛地抽搐，高潮的洪流带走了她最后一丝生命力。她死在了这场由你赐予的、无法承受的极乐地狱中。",
            0.07,
        )

    def execution_marilyn_crushing_embrace(self):
        print_slow("\n【处决：碎心拥抱】", 0.06)
        print_slow(
            "你没有给她任何喘息的机会。你像捕食的猛兽，用双腿缠住Lifeng的腰，将她完全锁在身前，形成一个无法挣脱的十字固。她的身体被你强行拉伸，发出痛苦的呻吟。",
            0.06,
        )
        print_slow(
            "“放开！你这个怪物！” Lifeng用尽最后的力气捶打你的后背，但你的身体如钢铁般纹丝不动。（不甘心……我不想死……我还没有告诉她，我爱她……）",
            0.06,
        )
        print_slow(
            "“太弱了。” 你冷酷地评价，仿佛在审视一件有瑕疵的艺术品。你将掌心贴在她因剧烈呼吸而起伏的胸口，那里是她心脏的位置。“你的爱，你的觉悟，都太脆弱，太天真了。”",
            0.06,
        )
        print_slow(
            "“就让我来告诉你，什么是真正的力量！” 八卦掌的内劲毫无保留地瞬间爆发。Lifeng的身体剧烈一震，骨骼碎裂和内脏破裂的声音清晰可闻。她猛地喷出一口鲜血，溅在你的脸上。",
            0.06,
        )
        print_slow(
            "但奇异的是，这股毁灭性的冲击力让她的大脑产生了错乱的信号，一股前所未有的、贯穿脊髓的剧烈快感淹没了痛楚。她的身体在你怀中弓起，下体不受控制地收缩、痉挛。",
            0.06,
        )
        print_slow(
            "她的眼中同时流露出极致的痛苦、刻骨的不甘和迷离的性奋，最后在你怀中失去了所有神采，身体因死后的神经反射而轻微颤抖，仿佛还在回味那最后的绝命高潮。",
            0.07,
        )

    def execution_marilyn_final_lesson(self):
        print_slow("\n【处决：最终课程】", 0.06)
        print_slow(
            "你一记扫堂腿将遍体鳞伤的Lifeng踢倒，她像个破布娃娃一样滚落在地。你缓步上前，用你那沾满尘土的高跟鞋，精准地踩在了她的手腕上，碾碎了她的骨头和反抗的希望。",
            0.06,
        )
        print_slow(
            "“啊——！” Lifeng发出凄厉的惨叫。（为什么……会这样……她教我的招式……我的一切……为什么都赢不了你……）她屈辱地趴在地上，泪水和泥土混在一起，让她美丽的脸庞狼狈不堪。",
            0.06,
        )
        print_slow(
            "你优雅地蹲下身，像女王一样捏住她的下巴，强迫她看着你。“看着我，”你命令道，声音不大，却带着不容置疑的威严，“我的密友教过我，真正的强大，不是天真的守护，而是连绝望和痛苦都能品尝、都能支配的从容。”",
            0.06,
        )
        print_slow(
            "你俯身，在她耳边用舌尖描绘着轮廓，这本该是情人间的亲昵动作，此刻却让她感受到刺骨的寒意。一股热流从下腹涌起，身体在本能地战栗，既因为恐惧，也因为这陌生的、带着施虐意味的刺激。",
            0.06,
        )
        print_slow(
            "“你的爱太渺小了，只懂得给予和守护。而我的爱，懂得掠夺和支配。” 你说完，手指在她脖颈的动脉处轻轻一划，锋利的指甲切开了皮肤和血管。“就让你在无尽的悔恨和这背德的快感中死去吧，这是我给你的，最后一课。”",
            0.06,
        )
        print_slow(
            "Lifeng的呼吸戛然而止，鲜血从脖颈涌出。她的身体僵直，双眼圆睁，永远定格在了那副混杂着屈辱、不解、痛苦与亢奋的表情上。", 0.07
        )

    def execution_lifeng_life_drain(self):
        print_slow("\n【处决：生命吸收】", 0.06)
        print_slow(
            "Lifeng如一道粉色的闪电欺身而上，你甚至来不及反应，就被她娇小却充满爆发力的身体压倒在地。你的后脑勺撞在碎石上，一阵眩晕。", 0.06
        )
        print_slow(
            "你奋力挣扎，试图用双臂推开她，但她的关节技死死地锁住了你。“别动。”她冰冷地说着，一手按住你的双手，另一只手粗暴地撕开了你胸前本就破损的旗袍，让你傲人的双峰暴露在冰冷的夜气中。",
            0.06,
        )
        print_slow(
            "“不……不要……”你想起了密友也曾这样对你，但那是充满爱欲的抚弄，而眼前的，是纯粹的掠夺。她俯下身，毫不犹豫地将你的乳房整个含入口中。", 0.06
        )
        print_slow(
            "一股无法抗拒的、带着妖异力量的吸力传来，你感觉自己的生命力、体温、甚至意识，都正从胸口被源源不断地抽走。你眼前的世界开始褪色，变得灰白。", 0.06
        )
        print_slow(
            "（不甘心……我还没有……让她在我身下哭着求饶……）绝望中，身体却背叛了你的意志。乳头在对方口中被吸吮得又硬又麻，一股羞耻的、尖锐的快感竟从下腹直冲脑髓，与生命流逝的空虚感交织在一起，让你几欲疯狂。",
            0.06,
        )
        print_slow(
            "“嗯……啊……住……住手……”无意识的呻吟从你口中溢出。Lifeng抬起头，她的脸颊因吸入生命力而泛着异样的潮红，嘴角挂着一丝你的奶水，眼神却冰冷如初。“你的生命……很甜美。它将成为我莲华之道绽放的养料。”",
            0.06,
        )
        print_slow("在这矛盾的绝望与性奋中，你的意识迅速沉入黑暗，身体最后一次因为那致命的快感而剧烈痉挛，随即彻底冰冷。", 0.07)

    def execution_lifeng_crimson_lotus(self):
        print_slow("\n【处决：红莲奈落】", 0.06)
        print_slow(
            "你倒在地上，每一次呼吸都牵动着全身的伤口。你挣扎着想爬起来，（我不能……死在这里……我还没有征服她……还没有让她承认我是最强的……）但Lifeng已经像幽灵一样站在了你的面前，她的手掌上凝聚着不祥的、仿佛有生命的绯红光芒。",
            0.06,
        )
        print_slow(
            "她没有攻击你的头颅或心脏，而是将那只燃烧着红光的手掌，轻轻地、带着一丝诡异的仪式感，按在了你的小腹上，那是女性生命之源的宫殿。", 0.06
        )
        print_slow(
            "“你的强大，充满了欲望和攻击性，但也因此，充满了破绽。”她轻声说，声音里没有胜利的喜悦，只有一种执行天命般的平静。“就让我的红莲，在你这片欲望的沃土上，盛开吧。”",
            0.06,
        )
        print_slow(
            "一股灼热到极致的能量猛地注入你的身体！你感觉仿佛有无数根烧红的针从子宫向四肢百骸疯狂扩散，剧痛让你发出不似人声的惨叫。但这股暴虐的能量同时点燃了你最深处的欲望，你的身体不受控制地弓起，在极致的痛苦中迎来了前所未有的、撕心裂肺的高潮。",
            0.06,
        )
        print_slow(
            "你感觉有什么东西在你体内爆开了，像是最绚烂的烟花，也像是生命的终结。你最后看到的，是自己的小腹上，一个血红色的、妖艳的莲花印记透过旗袍浮现出来，仿佛烙印在你的灵魂之上。随即眼前一黑，彻底死去。",
            0.07,
        )

    def execution_lifeng_serene_death(self):
        print_slow("\n【处决：寂静莲华】", 0.06)
        print_slow(
            "你用尽最后一丝力气，挥出疲软的一掌，却被Lifeng一记精准的手刀砍在颈侧。你眼前金星乱冒，世界天旋地转，最终无力地瘫软在地。", 0.06
        )
        print_slow(
            "（可恶……竟然会……输给这种天真的家伙……）你的意识开始模糊，准备迎接最后的痛击。但出乎意料，Lifeng没有继续攻击。她只是静静地跪坐在你身边，将你的头抬起，枕在她的腿上。她的大腿柔软而温暖，与你预想的冰冷结局截然不同。",
            0.06,
        )
        print_slow(
            "她的动作很轻柔，像是在照顾一个受伤的姐妹。她从怀中掏出手帕，为你擦去脸上的血污。她开始哼唱一段你从未听过的、温柔又悲伤的摇篮曲。你想起了你的密友，如果她在此刻，是会愤怒地为你复仇，还是会……像这样抱着你？这个念头让你感到一阵迷茫。",
            0.06,
        )
        print_slow(
            "在这诡异的、不合时宜的安详中，你的杀意和反抗意志被一点点瓦解。你甚至感到了一丝困意和久违的温暖。你试图张嘴说些什么，但她只是用手指轻轻按住你的嘴唇。“睡吧，”她轻声说，眼神中带着一丝怜悯，“战斗已经结束了。不用再痛苦了。”",
            0.06,
        )
        print_slow(
            "她慢慢地、但却无比坚定地加大了手指的力道，封住了你的口鼻，切断了你的呼吸。你本能地想挣扎，但身体却不听使唤。在这片刻的温柔中，你的身体彻底放松下来，甚至因为这份临终的亲密而微微湿润。你安详地闭上了眼睛，如同一个在母亲怀中睡去的婴儿，迎来了永恒的寂静。",
            0.07,
        )


# --- 游戏启动 ---
if __name__ == "__main__":
    game = Game()
    game.start_game()
