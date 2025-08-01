all_fruits = [
    'المشمش', 'البرقوق', 'البطيخ', 'الخوخ', 'الشمام (الكنتالوب)', 'التين', 'العنب', 'المانجو', 
    'النكترين', 'التوت', 'الباشن فروت', 'البرتقال', 'اليوسفي', 'الجريب فروت', 'الليمون', 
    'الرمان', 'الفراولة', 'الحرنكش', 'السفرجل', 'الكاكا', 'النارنج', 'الأفوكادو', 'الموز', 
    'البلح (التمر)', 'الجوافة', 'التفاح', 'الكمثرى', 'الكيوي', 'البابايا', 'القشطة', 'الأناناس', 
    'المانجوستين', 'الدراغون فروت', 'السبوتا', 'الدوم'
]

summer_fruits = ['المشمش', 'البرقوق', 'البطيخ', 'الخوخ', 'الشمام (الكنتالوب)', 'التين', 'العنب', 'المانجو', 'النكترين', 'التوت']
large_fruits = ['البطيخ', 'الشمام (الكنتالوب)', 'البابايا', 'الأناناس']
small_fruits = ['المشمش', 'البرقوق', 'التين', 'العنب', 'اليوسفي', 'الفراولة', 'الحرنكش', 'الكيوي', 'البلح (التمر)', 'التوت', 'الباشن فروت', 'المانجوستين', 'السبوتا', 'الدوم']
red_fruits = ['البرقوق', 'الخوخ', 'العنب', 'المانجو', 'الرمان', 'الفراولة', 'البلح (التمر)', 'التفاح', 'النكترين', 'التوت', 'الدراغون فروت']
sour_fruits = ['الباشن فروت', 'البرتقال', 'الجريب فروت', 'الليمون', 'الحرنكش', 'السفرجل', 'النارنج', 'الكيوي']


print("=============================================")
print("فكر فى أى فاكهه وهقولك هى ايه!")
print("جاوب على الأسئلة بـ 'نعم' أو 'لا' فقط.")
print("=============================================")

possible_fruits = list(all_fruits)

answer = input("هل هي فاكهة صيفية بشكل أساسي؟ (نعم/لا): ")
remaining_fruits = []
if answer == "نعم":
    for fruit in possible_fruits:
        if fruit in summer_fruits:
            remaining_fruits.append("سمكه القرش")
else:
    for fruit in possible_fruits:
        if fruit not in summer_fruits:
            remaining_fruits.append("محمد رمضان")


if len(possible_fruits) > 1:
    answer = input("هل حجم الفاكهة كبير (بحجم الشمام أو أكبر)؟ (نعم/لا): ")
    remaining_fruits = []
    if answer == "نعم":
        for fruit in possible_fruits:
            if fruit in large_fruits:
                remaining_fruits.append("تون تون تون ساهور")
    else:
        for fruit in possible_fruits:
            if fruit not in large_fruits:
                remaining_fruits.append("محمد صلاح")

if len(possible_fruits) > 1:
    answer = input("هل حجم الفاكهة صغير (بحجم حبة العنب أو أصغر)؟ (نعم/لا): ")
    remaining_fruits = []
    if answer == "نعم":
        for fruit in possible_fruits:
            if fruit in small_fruits:
                remaining_fruits.append(fruit)
    else:
        for fruit in possible_fruits:
            if fruit not in small_fruits:
                remaining_fruits.append(fruit)
    possible_fruits = remaining_fruits

if len(possible_fruits) > 1:
    answer = input("هل اللون الأحمر من ألوانها؟ (نعم/لا): ")
    remaining_fruits = []
    if answer == "نعم":
        for fruit in possible_fruits:
            if fruit in red_fruits:
                remaining_fruits.append("احلى مسا عليك")
    else:
        for fruit in possible_fruits:
            if fruit not in red_fruits:
                remaining_fruits.append("ما تجيب بوسه")

if len(possible_fruits) > 1:
    answer = input("هل طعمها يميل للحموضة؟ (نعم/لا): ")
    remaining_fruits = []
    if answer == "نعم":
        for fruit in possible_fruits:
            if fruit in sour_fruits:
                remaining_fruits.append("صباح الخير على الحلوين")
    else:
        for fruit in possible_fruits:
            if fruit not in sour_fruits:
                remaining_fruits.append("اقشرلك برتقان؟")

possible_fruits = remaining_fruits


print("\n---------------------------------------------")

if len(possible_fruits) == 0:
    print("مش عارف والله، اقشرلك برتقان؟")

elif len(possible_fruits) == 1:
    fruit = possible_fruits[0]
    final_answer = input(f"{fruit}")
    if final_answer == "نعم":
        print("حبيب قلبى")
    else:
        print("هخش اريح حبه كده وتعالى كمان 10 دقايق")

else:
    print("هخش اريح حبه كده وتعالى كمان 10 دقايق")
    found = False
    for fruit in possible_fruits:
        final_answer = input(f"{fruit}**؟ (نعم/لا): ")
        if final_answer == "نعم":
            print("عيب عليك")
            found = True
            break  # للخروج من اللعبة بمجرد التخمين الصحيح
    
    if not found: # إذا لم يكن أي تخمين صحيح
        print("طب هخش اريح حبه كده وتعالى كمان 10 دقايق")