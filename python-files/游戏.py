import random

# 简单平仄字典（P: 平声, Z: 仄声；基于常见汉字，实际可扩展）
tone_dict = {
    '春': 'P', '风': 'P', '花': 'P', '鸟': 'Z', '月': 'Z', '江': 'P', '山': 'P', '天': 'P',
    '地': 'Z', '人': 'P', '海': 'Z', '河': 'P', '树': 'Z', '叶': 'Z', '雨': 'Z', '雪': 'Z',
    # 添加更多字根据需要
}

# 简单韵母字典（模拟押韵，基于末字拼音韵母）
rhyme_dict = {
    '花': 'ua', '家': 'ia', '山': 'an', '天': 'ian', '江': 'ang', '风': 'eng',
    '月': 'ue', '雪': 'ue', '雨': 'u', '树': 'u',
    # 添加更多
}

# 五言绝句基本格律模板（平仄：Z P Z P P；P Z P Z Z 等简化）
jueju_pattern = ['Z', 'P', 'Z', 'P', 'P']  # 示例第一行

# 玩家天梯排名：列表 of (name, score)
ladder = []

def get_tone(char):
    return tone_dict.get(char, random.choice(['P', 'Z']))  # 默认随机

def get_rhyme(char):
    return rhyme_dict.get(char, '')  # 默认空

def score_poem(poem):
    if len(poem) != 4:
        return 0  # 必须4行
    score = 0
    # 长度检查：每行5字 (40分)
    for line in poem:
        if len(line) == 5:
            score += 10
    # 押韵检查：第2、4行末字韵相同 (30分)
    if get_rhyme(poem[1][-1]) == get_rhyme(poem[3][-1]) and get_rhyme(poem[1][-1]) != '':
        score += 30
    # 平仄检查：简化匹配第一行模板 (20分)
    match_count = 0
    for i, char in enumerate(poem[0]):
        if get_tone(char) == jueju_pattern[i]:
            match_count += 1
    score += (match_count / 5) * 20
    # 原创/情感：随机模拟 (10分)
    score += random.randint(0, 10)
    return min(score, 100)  # 上限100

def create_poem():
    print("创作五言绝句（4行，每行5汉字）：")
    poem = []
    for i in range(4):
        line = input(f"输入第{i+1}行: ").strip()
        poem.append(line)
    return poem

def add_to_ladder(name, score):
    global ladder
    # 更新或添加
    for i, (pname, pscore) in enumerate(ladder):
        if pname == name:
            ladder[i] = (name, pscore + score)
            break
    else:
        ladder.append((name, score))
    # 排序降序
    ladder.sort(key=lambda x: x[1], reverse=True)

def show_ladder():
    print("\n天梯排名：")
    for i, (name, score) in enumerate(ladder, 1):
        print(f"{i}. {name}: {score} 分")

def pk_mode():
    print("事实PK：两位玩家创作诗词（主题：随意）")
    p1_name = input("玩家1姓名: ")
    p1_poem = create_poem()
    p1_score = score_poem(p1_poem)
    print(f"{p1_name} 诗词：\n" + '\n'.join(p1_poem))
    print(f"分数: {p1_score}")

    p2_name = input("玩家2姓名: ")
    p2_poem = create_poem()
    p2_score = score_poem(p2_poem)
    print(f"{p2_name} 诗词：\n" + '\n'.join(p2_poem))
    print(f"分数: {p2_score}")

    if p1_score > p2_score:
        print(f"{p1_name} 胜出！")
        add_to_ladder(p1_name, 20)
        add_to_ladder(p2_name, -10)
    elif p2_score > p1_score:
        print(f"{p2_name} 胜出！")
        add_to_ladder(p2_name, 20)
        add_to_ladder(p1_name, -10)
    else:
        print("平局！")
        add_to_ladder(p1_name, 5)
        add_to_ladder(p2_name, 5)

def main():
    while True:
        print("\n诗词天梯游戏菜单：")
        print("1. 自由创作并打分")
        print("2. 查看天梯排名")
        print("3. 事实PK")
        print("4. 退出")
        choice = input("选择: ")
        if choice == '1':
            name = input("您的姓名: ")
            poem = create_poem()
            score = score_poem(poem)
            print("您的诗词：\n" + '\n'.join(poem))
            print(f"AI分数: {score}")
            add_to_ladder(name, score)
        elif choice == '2':
            show_ladder()
        elif choice == '3':
            pk_mode()
        elif choice == '4':
            break
        else:
            print("无效选择！")

if __name__ == "__main__":
    main()