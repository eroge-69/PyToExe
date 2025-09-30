import random
import datetime
import msvcrt
import sys

#                                                        PLAYER INTRODUCTION

def PlayerIntroduction():
    #                                                               Player Introduction
    Introduction= "\nNamaskar devio aur sajjano.\n"

    Hello = "Mera Naam Hai Amitabh Bhacchan. \nAur aapka swagat hai ek bahut hi adbhut khel mein. \nJiska naam hai kaun banega crorepati season 18."
    Sponsors = "\nSponsored by Maruti Suzuki, Aditya Birla Group, and HPCL.\n"
    print(Introduction.title())
    print(Hello.title())
    print(Sponsors)
    PlayerFName = input("Enter Your First Name: ")
    PlayerLName = input("Enter Your Last Name: ")
    while True:
        PlayerGender = input("Enter Your Gender(Male/Female): ").strip().capitalize()
        if PlayerGender in ["Male","Female"]:
            break
        else:
            print("Invalid Input")

    Greeting = "Aaj hamare saath hotseat par maujud hai "
    if PlayerGender == "Male":
        PlayerTitle = "Mr."
    else:
        PlayerTitle = "Ms."
    print("")
    print(Greeting.title(), PlayerTitle ," ", PlayerFName.title() , " ", PlayerLName.title() , " Ji." , "\nAapka Bahut Swagat Hai Kaun Banega Crorepati Season 18 Mein.\n", sep="")

    #                                                         Game Rules, Lifelines and Stages
    print("Yeh Khel Bahut hi Saral Hai.\n")
    Rules= "\"GAME RULES\""
    print(Rules.center(70))
    GameRules = """ 
    Aapko diye jayenge kuch prashn, aur har prashn ke 4 options.
    Aapko chunna hoga ek sahi uttar.

    Jaise-jaise aap sahi uttar dete jayenge, waise-waise 
    aapki prize money badhti jayegi.

    Dhyaan rahe – agar aap galat jawab dete hain, 
    toh aapko aapke stage ke mutaabiq dhanrashi milegi. 

    Lekin agar aap khel chhodna chahte hain, toh aap turant ‘Quit’ kehkar
    apne jeete hue paise le sakte hain.\n"""
    print(GameRules.title())
    Lifes="\"LIFELINES\""
    print(Lifes.center(70))
    LifeLines = """\nAur Iss safar Aapke paas hoge 4 lifelines:

    1. 50–50:
    Agar aapko jawab mein confusion ho, toh is lifeline 
    se computer chaar options mein se do galat options hata dege. 
    Sirf do options bacheinge – ek sahi aur ek galat.
    Iss lifeline ka istemaal karne ke baad bhi aap quit kar sakte hain.

    2. Double Dip:
    Iss lifeline ke saath aap ek nahin, balki do jawaab de sakte hain.
    Iss lifeline ka istemaal karne ke baad aap quit nahi kar sakte.
    Iss lifeline ko aap 50-50 ke saath istemaal nahi kar sakte hain.

    3. Switch the Question: 
    Agar koi sawaal aapko pasand na aaye ya mushkil lage, 
    toh is lifeline se aap us sawaal ko hata ke ek naya sawaal le sakte hain.

    4. Power Paplu:
    Ye ek khaas lifeline hai. Agar aapne apni koi lifeline pehle
    hi use kar li hai, toh is lifeline se aap us ek lifeline ko 
    wapis jeevit kar sakte hain.\n"""
    print(LifeLines.title())
    Stage = "\"GAME STAGES\""
    print(Stage.center(70))
    GameStages = """\nIs khel mein aapko diye jaayenge 16 sawaal, \naur har ek sahi jawab ke saath aapki inaam ki rashi badhati chali jaayegi:

        ₹ 1000
        ₹ 2000
        ₹ 3000
        ₹ 5000
        ₹ 10,000      STAGE 1
        
        ₹ 20,000
        ₹ 40,000
        ₹ 80,000
        ₹ 1,60,000
        ₹ 3,20,000    STAGE 2
        
        ₹ 6,40,000
        ₹ 12,50,000
        ₹ 25,00,000
        ₹ 50,00,000
        ₹ 1 Crore
        ₹ 7 Crore     JACKPOT"""
    print(GameStages.title())
    print("\nToh ", PlayerFName.title(), " Ji",sep="")
    x = input("Kya Aap Taiyar hai Kaun Banega Crorepati Season 18 \nke iss Safar ki Shuruat karne ke liye?\n\n",)
    No=["No", "Nahi", "Nhi", "Nah", "Bilkul nahi", "Not at all"]
    Reply = str(x)
    if Reply.strip().capitalize() in No:
        print("\nKoi Baat Nahi.\nAapse baat karke bahut Accha laga.\nHam kisi aur din bhi yeh Khel Continue kar sakte hai.")
        print("Press Any Key to Exit ")
        msvcrt.getch()
        sys.exit()
    else:
        print("\nToh Chaliye Shuru Karte Hai!\nKaun Banega Crorepati Season 18\nSponsored by Maruti Suzuki, Aditya Birla Group, and HPCL.\n")
        return PlayerFName, PlayerLName
IntroSign = "WELCOME TO KAUN BANEGA CROREPATI"
print("\n", IntroSign.center(70), "\n")
TutorialChoice = input("Would You Like to Skip Introduction and Game Rules? (Yes or No): ").strip().capitalize()
if TutorialChoice in ["Yes", "Skip it", "Haan", "Sure", "Yup", "Yea", "Yeah", "Of course", "Yes please", "Please skip it", "No need", "No need to explain", "No need of explanation", "No need of introduction", "No need to explain rules", "No need of rules", "Hn", "Ha", "Haa", "Hnn", "Haanji", "Haan Ji", "Haan Ji Bilkul", "Haan Bilkul", "Haanji Bilkul"]:
    PlayerFName = "Player"
    PlayerLName = ""
    print("\nChaliye! Shuru Karte hai Yeh Bahut hi Adbhut Khel!\nJiska Naam hai Kaun Banega Crorepati\n")
elif TutorialChoice == "Skip":
    PlayerFName = "Player"
    PlayerLName = ""
    print("\nChaliye! Shuru Karte hai Yeh Bahut hi Adbhut Khel!\nJiska Naam hai Kaun Banega Crorepati\n")
else: 
    PlayerFName, PlayerLName = PlayerIntroduction()
full_name = f"{PlayerFName} {PlayerLName}" 
#                                                       ALL IMPORTANT LISTS

MasterKey = "Sankalp_Is_Great"
QuestionNumber = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
PrizeMoney = [1000, 2000, 3000, 5000, 10000, 20000, 40000, 80000, 160000, 320000, 640000, 1250000, 2500000, 5000000, 10000000, 70000000]
PrizeMoneyString = ["1000", "2000", "3000", "5000", "10,000", "20,000", "40,000", "80,000", "1,60,000", "3,20,000", "6,40,000", "12,50,000", "25,00,000", "50,00,000", "1 Crore", "7 Crore"]
Options = ["A.", "B.", "C.", "D."]
Lifelines = ["50-50", "Double Dip", "Switch the Question", "Power Paplu"]
AvailableLifelines = ["50-50", "Double Dip", "Switch the Question", "Power Paplu"]
UsedLifelines = []
x = "                            QUESTION NUMBER "
EasyQuestions = [
    "Which color do you get by mixing red and blue?", # 1
    "Who wrote the famous book \"Gulliver's Travels\"?", # 2
    "Which Indian state is famous for the Sundarbans mangrove forest?", # 3
    "Which planet has the most moons in our solar system?", # 4
    "Which organ in the human body produces insulin?", # 5
    "Which city hosted the first modern Olympic Games in 1896?", # 6
    "Which planet rotates on its axis in the opposite direction compared to most planets in the solar system?", # 7
    "Which blood type is known as the \"Universal Donor\"?", # 8
    "Which river is called the \"Sorrow of Bihar\" due to frequent floods?", # 9
    "Who was the first woman to win a Nobel Prize?", # 10
    "Which country invented paper?", # 11
    "Which famous scientist is known as the \"Father of Genetics\"?", # 12
    "Which Indian river is called the \"Ganga of the South\"?", # 13
    "Which part of the human brain controls balance and coordination?", # 14
    "Which is the heaviest naturally occurring element by atomic number?", # 15
    "Who discovered penicillin?", # 16
    "Which Indian city is known as the \"Manchester of India\" because of its textile industry?", # 17
    "Which is the official language of Brazil?", # 18
    "Which part of the human body has the thickest skin?", # 19
    "Which gas is used in electric bulbs to prevent the filament from burning?", # 20
    "Which planet has the shortest day in the solar system?", # 21
    "Who wrote the famous book \"The Argumentative Indian\"?", # 22
    "Which Indian state is known as the \"Spice Garden of India\"?", # 23
    "Which country hosted the first FIFA World Cup?", # 24
    "Which is the only mammal capable of true flight?", # 25
    "Which Indian city is called the \"City of Joy\"?", # 26
    "Which planet has the longest day in the solar system?", # 27
    "Which is the smallest bone in the human body?", # 28
    "Which scientist discovered the neutron?", # 29
    "Which Indian river is known as the \"Sorrow of Bengal\" due to its floods?", # 30
    "Which Indian state is known as the \"Land of the Rising Sun\"?", # 31
    "Which is the largest freshwater lake in India?", # 32
    "Which planet has the most volcanoes in the solar system?", # 33
    "Which fuel gas is used in oxy-acetylene welding?", # 34
    "Which is the largest glacier in India?", # 35
    "Who is considered the \"Father of Modern Chemistry\"?", # 36
    "Which Indian mountain range is called the \"Water Tower of India\"?", # 37
    "Which planet is known for its extreme winds, the fastest in the solar system?", # 38
    "Who discovered the radioactivity of uranium?", # 39
    "Which is the world's highest waterfall?", # 40
    "Which river is known as the \"Yellow River\"?", # 41
    "Which is the tallest mountain in Antarctica?", # 42
    "Which is the tallest mountain in South America?", # 43
    "Which is the tallest mountain in Europe?", # 44
    "Which Indian state is famous for its handloom silk called \"Tussar Silk\"?", # 45
    "Which organ in the human body stores glycogen?", # 46
    "Which country is known as the \"Land of Thousand Lakes\"?", # 47
    "Which is the longest river in Europe?", # 48
    "Which part of the human eye controls the amount of light entering it?", # 49
    "Which country is known as the \"Land of Volcanoes\"?" # 50
]
EasyOptions = [ 
    ["Purple", "Orange", "Green", "Yellow"],   # 1
    ["Jonathan Swift", "William Shakespeare", "Charles Dickens", "Mark Twain"],  # 2 
    ["West Bengal", "Odisha", "Assam", "Kerala"],  # 3 
    ["Jupiter", "Saturn", "Neptune", "Mars"],  # 4 
    ["Pancreas", "Liver", "Kidney", "Heart"],  # 5 
    ["Athens", "Rome", "Paris", "London"],  # 6 
    ["Venus", "Mars", "Jupiter", "Mercury"],  # 7 
    ["O-", "A+", "AB+", "B+"],  # 8 
    ["Kosi", "Ganga", "Brahmaputra", "Yamuna"],  # 9 
    ["Marie Curie", "Mother Teresa", "Rosalind Franklin", "Indira Gandhi"],  # 10 
    ["China", "Egypt", "India", "Greece"],  # 11 
    ["Gregor Mendel", "Albert Einstein", "Charles Darwin", "Antoine Lavoisier"],  # 12 
    ["Mahanadi", "Krishna", "Kaveri", "Narmada"],  # 13 
    ["Cerebellum", "Cerebrum", "Medulla", "Thalamus"],  # 14 
    ["Uranium", "Lead", "Osmium", "Plutonium"],  # 15 
    ["Alexander Fleming", "Louis Pasteur", "Robert Koch", "Joseph Lister"],  # 16 
    ["Ahmedabad", "Surat", "Mumbai", "Delhi"],  # 17 
    ["Portuguese", "Spanish", "French", "English"],  # 18 
    ["Soles of feet", "Palm", "Back", "Thigh"],  # 19 
    ["Argon", "Helium", "Neon", "Oxygen"],  # 20 
    ["Jupiter", "Saturn", "Mars", "Mercury"],  # 21 
    ["Amartya Sen", "Chetan Bhagat", "Motilal Nehru", "Khushwant Singh"],  # 22 
    ["Kerala", "Tamil Nadu", "Assam", "Karnataka"],  # 23 
    ["Uruguay", "Brazil", "Italy", "Germany"],  # 24 
    ["Bat", "Flying Squirrel", "Bald Eagle", "Hummingbird"],  # 25 
    ["Kolkata", "Mumbai", "Delhi", "Bangaluru"],  # 26 
    ["Venus", "Mercury", "Mars", "Earth"],  # 27 
    ["Stapes", "Femur", "Radius", "Ulna"],  # 28 
    ["James Chadwick", "Enrico Fermi", "Niels Bohr", "Ernest Rutherford"],  # 29 
    ["Damodar", "Hooghly", "Teesta", "Mahananda"],  # 30 
    ["Arunachal Pradesh", "Assam", "Nagaland", "Manipur"],  # 31 
    ["Wular Lake", "Dal Lake", "Loktak Lake", "Vembanad Lake"],  # 32 
    ["Venus", "Mars", "Mercury", "Earth"],  # 33 
    ["Acetylene", "Oxygen", "Nitrogen", "Carbon dioxide"],  # 34 
    ["Siachen", "Lambert", "Biafo", "Baltoro"],  # 35 
    ["Antoine Lavoisier", "Dmitri Mendeleev", "Robert Boyle", "Joseph Priestley"],  # 36 
    ["Himalayas", "Western Ghats", "Aravallis", "Eastern Ghats"],  # 37 
    ["Neptune", "Uranus", "Saturn", "Mars"],  # 38 
    ["Henri Becquerel", "Marie Curie", "Pierre Curie", "Ernest Rutherford"],  # 39 
    ["Angel Falls", "Niagara Falls", "Victoria Falls", "Iguazu Falls"],  # 40 
    ["Huang He", "Yangtze", "Mekong", "Indus"],  # 41 
    ["Mount Vinson", "Mount Erebus", "Mount Tyree", "Mount Sidley"],  # 42 
    ["Aconcagua", "Mount Chimborazo", "Mount Cotopaxi", "Mount Huascarán"],  # 43 
    ["Mount Elbrus", "Matterhorn", "Mont Blanc", "Mount Etna"],  # 44 
    ["Jharkhand", "Assam", "West Bengal", "Odisha"],  # 45 
    ["Liver", "Pancreas", "Kidney", "Stomach"],  # 46 
    ["Finland", "Sweden", "Norway", "Denmark"],  # 47 
    ["Volga", "Danube", "Rhine", "Seine"],  # 48 
    ["Iris", "Cornea", "Retina", "Lens"],  # 49 
    ["El Salvador", "Chile", "Indonesia", "Japan"]  # 50 
] 
EasyAnswers = [
    "Purple",                # 1
    "Jonathan Swift",        # 2
    "West Bengal",           # 3
    "Saturn",                # 4 
    "Pancreas",              # 5
    "Athens",                # 6
    "Venus",                 # 7
    "O-",                    # 8
    "Kosi",                  # 9
    "Marie Curie",           # 10
    "China",                 # 11
    "Gregor Mendel",         # 12
    "Kaveri",                # 13
    "Cerebellum",            # 14
    "Uranium",               # 15 
    "Alexander Fleming",     # 16
    "Ahmedabad",             # 17
    "Portuguese",            # 18
    "Soles of feet",         # 19
    "Argon",                 # 20
    "Jupiter",               # 21
    "Amartya Sen",           # 22
    "Kerala",                # 23
    "Uruguay",               # 24
    "Bat",                   # 25
    "Kolkata",               # 26
    "Venus",                 # 27
    "Stapes",                # 28
    "James Chadwick",        # 29
    "Damodar",               # 30
    "Arunachal Pradesh",     # 31
    "Wular Lake",            # 32 
    "Venus",                 # 33 
    "Acetylene",             # 34 
    "Siachen",               # 35 
    "Antoine Lavoisier",     # 36
    "Himalayas",             # 37
    "Neptune",               # 38
    "Henri Becquerel",       # 39
    "Angel Falls",           # 40
    "Huang He",              # 41
    "Mount Vinson",          # 42
    "Aconcagua",             # 43
    "Mount Elbrus",          # 44
    "Jharkhand",             # 45
    "Liver",                 # 46
    "Finland",               # 47
    "Volga",                 # 48
    "Iris",                  # 49
    "El Salvador"            # 50
]

MediumQuestions = [
    "Which Mughal emperor built the city of Fatehpur Sikri?", # 1
    "The novel The God of Small Things, which won the Booker Prize in 1997, was written by whom?", # 2
    "The term \"Golden Quadrilateral\" in India refers to?", # 3
    "What was the name of the world's first artificial satellite launched by the USSR in 1957?", # 4
    "The Bhimbetka caves in Madhya Pradesh are famous for?", # 5
    "In economics, what does the term \"stagflation\" mean?", # 6
    "The nuclear disaster of Chernobyl (1986) took place in which present-day country?", # 7
    "Who composed the famous classical work \"Meghadūta\"?", # 8
    "Which Mughal emperor was known as \"Alamgir\"?", # 9
    "The capital city of Myanmar is?", # 10
    "Which of these gases is used in refrigerators as a coolant?", # 11
    "The Red Fort in Delhi was declared a UNESCO World Heritage Site in which year?", # 12
    "What is the currency of Malaysia?", # 13
    "Who is known as the \"Father of Modern Chemistry\"?", # 14
    "In which year did India adopt the Constitution?", # 15
    "Which scientist formalized the Law of Inertia as his First Law of Motion?", # 16
    "Which Indian Mughal emperor built the \"Buland Darwaza\"?", # 17
    "Which is the lightest metal?", # 18
    "In which year did the Jallianwala Bagh massacre take place?", # 19
    "Who was the first Indian woman to win a gold medal at the Asian Games in athletics?", # 20
    "The Simon Commission (1927) was boycotted in India because?", # 21
    "Which part of the human body secretes Antidiuretic Hormone (ADH)?", # 22
    "\"Satyameva Jayate\" inscribed below the national emblem is taken from which ancient text?", # 23
    "Which gas is commonly known as \"laughing gas\"?", # 24
    "The element with atomic number 82 is?", # 25
    "The largest gland in the human body is?", # 26
    "Who was the Viceroy of India during the Quit India Movement (1942)?", # 27
    "The International Court of Justice is located at?", # 28
    "The famous \"Battle of Talikota\" (1565) led to the fall of which empire?", # 29
    "The \"Grey Revolution\" in India primarily focused on the production of?", # 30
    "In physics, which law states that the pressure applied to a confined fluid is transmitted undiminished in all directions?", # 31
    "Who was the last Governor-General of independent India?", # 32
    "Which vitamin deficiency causes \"Pernicious Anemia\"?", # 33
    "Who among the following was NOT a member of the Drafting Committee of the Indian Constitution?", # 34
    "The chemical formula of bleaching powder is?", # 35
    "The “Anand Math” novel, which inspired the song \"Vande Mataram,\" was written by?", # 36
    "The first successful heart transplant was performed by?", # 37
    "Which Indian mathematician was awarded the Fields Medal in 2014?", # 38
    "Which Indian freedom fighter was popularly known as the \"Lion of Punjab\"?", # 39
    "The \"Battle of Buxar\" was fought in?", # 40
    "In which state is the Brihadeeswara Temple, built by Raja Raja Chola I, located?", # 41
    "Which Indian physicist won the Nobel Prize in Physics in 1930?", # 42
    "Who introduced the \"Permanent Settlement\" system in India?", # 43
    "Who was the first Indian to win a Nobel Prize in Physics?", # 44
    "The chemical element with atomic number 79 is?", # 45
    "Who was the Viceroy of India during the Simon Commission?", # 46
    "In which year was the Indian Space Research Organisation (ISRO) founded?", # 47
    "Which ancient Indian mathematician authored Brahmasphutasiddhanta?", # 48
    "Which vitamin is fat-soluble?", # 49
    "The Harappan Civilization was primarily located along which river?", # 50
    "The \"Red Fort\" in Delhi was built by?", # 51
    "Which Indian state is the largest producer of coffee?", # 52
    "Who was the first Indian to become the President of the United Nations General Assembly?", # 53
    "The \"White Revolution\" in India is associated with?", # 54
    "The famous “Aligarh Movement” in India was started by?", # 55
    "The first Indian woman to participate in the Olympics was?", # 56
    "The famous mathematical constant π (pi) was first rigorously calculated by?", # 57
    "Who wrote \"Gitanjali\"?", # 58
    "The Indian scientist who discovered the \"Raman Effect\" was?", # 59
    "Who was the first woman to become the Chief Minister of an Indian state?", # 60
    "The country known as the \"Land of the Rising Sun\" is?", # 61
    "The first Indian satellite was named?", # 62
    "Who is considered the father of the Indian Space Programme?", # 63
    "The first Indian to win an individual Olympic gold medal was?", # 64
    "The headquarters of the United Nations is located in?", # 65
    "Who was the founder of the Maurya Empire?", # 66
    "Which Indian state has the longest coastline?", # 67
    "Who was the first woman to receive the Padma Vibhushan in India?", # 68
    "Which Indian state is famous for the Sun Temple at Konark?", # 69
    "Who wrote the book \"India Wins Freedom\"?", # 70
    "Who was the first Indian woman to climb Mount Everest?", # 71
    "The world's first vaccine was developed by?", # 72
    "The Indian National Congress was founded in which year?", # 73
    "The famous Ajanta and Ellora caves are located in which state?", # 74
    "The first Indian to win a Nobel Prize in Economic Sciences was?" # 75
]
MediumOptions = [
    ["Akbar", "Shah Jahan", "Humayun", "Babur"], # 1
    ["Arundhati Roy", "Salman Rushdie", "Jhumpa Lahiri", "Kiran Desai"], # 2
    ["A highway network", "A railway network", "A river system", "A port system"], # 3
    ["Sputnik 1", "Explorer 1", "Vostok 1", "Luna 1"], # 4
    ["Buddhist stupas", "Prehistoric cave paintings", "Ancient temples", "Mughal architecture"], # 5
    ["High growth and high inflation", "Low growth and low inflation", "Low growth and high inflation", "High growth and low inflation"], # 6
    ["Ukraine", "Russia", "Belarus", "Poland"], # 7
    ["Kalidasa", "Tyagaraja", "Banabhatta", "Ravi Shankar"], # 8
    ["Aurangzeb", "Bahadur Shah Zafar", "Shah Jahan", "Jahangir"], # 9
    ["Naypyidaw", "Yangon", "Mandalay", "Bagan"], # 10
    ["Helium", "Sulphur Hexafluoride", "Nitrogen", "Freon-12"], # 11
    ["2007", "1998", "2010", "2013"], # 12
    ["Rupiah", "Yuan", "Ringgit", "Kip"], # 13
    ["Antoine Lavoisier", "Dmitri Mendeleev", "Robert Boyle", "John Dalton"], # 14
    ["1951", "1949", "1950", "1947"], # 15
    ["Galileo Galilei", "Isaac Newton", "Gottfried Leibniz", "Johannes Kepler"], # 16
    ["Akbar", "Shah Jahan", "Aurangzeb", "Humayun"], # 17
    ["Lithium", "Aluminum", "Mercury", "Gallium"], # 18
    ["1919", "1920", "1918", "1921"], # 19
    ["P.T. Usha", "Kamaljeet Sandhu", "Anju Bobby George", "K. Malleswari"], # 20
    ["It opposed Home Rule", "It had no Indian members", "It was against Congress leaders", "It wanted partition of India"], # 21
    ["Pituitary Gland", "Endocrine Gland", "Hypothalamus", "Pineal Gland"], # 22
    ["Rigveda", "Mundaka Upanishad", "Bhagavad Gita", "Isavasya Upanishad"], # 23
    ["Nitrous Oxide", "Nitric Oxide", "Nitrogen Dioxide", "Ammonia"], # 24
    ["Lead", "Thallium", "Uranium", "Polonium"], # 25
    ["Liver", "Pancreas", "Kidney", "Adrenal Gland"], # 26
    ["Lord Linlithgow", "Lord Mountbatten", "Lord Curzon", "Lord Wavell"], # 27
    ["The Hague", "New York", "Geneva", "Brussels"], # 28
    ["Vijayanagara Empire", "Sikh Empire", "Maratha Empire", "Chola Empire"], # 29
    ["Milk", "Eggs", "Fertilizer", "Cotton"], # 30
    ["Pascal's Law", "Murphy's Law", "Avogadro's law", "Boyle's Law"], # 31
    ["C. Rajagopalachari", "Lord Mountbatten", "Vallabhbhai Patel", "Rajendra Prasad"], # 32
    ["Vitamin B12", "Vitamin B6", "Vitamin B1", "Vitamin A"], # 33
    ["Allama Iqbal", "Alladi Krishnaswami Ayyar", "K. M. Munshi", "Mohammad Saadulla"], # 34
    ["CaOCl₂", "CaCl₂", "Ca(OH)₂", "CaCO₃"], # 35
    ["Bankim Chandra Chattopadhyay", "Ishwar Chandra Vidyasagar", "Sarat Chandra Chattopadhyay", "Munshi Premchand"], # 36
    ["Christiaan Barnard", "Jonas Salk", "Norman Shumway", "Vladimir Demikhov"], # 37
    ["Manjul Bhargava", "C.R. Rao", "Narendra Karmarkar", "Harish-Chandra"], # 38
    ["Lala Lajpat Rai", "Bhagat Singh", "Udham Singh", "Kartar Singh Sarabha"], # 39
    ["1757", "1764", "1782", "1799"], # 40
    ["Tamil Nadu", "Kerala", "Karnataka", "Andhra Pradesh"], # 41
    ["C.V. Raman", "Meghnad Saha", "Satyendra Nath Bose", "Jagadish Chandra Bose"], # 42
    ["Lord Cornwallis", "Lord Dalhousie", "Lord Wellesley", "Lord Ripon"], # 43
    ["C.V. Raman", "Homi Bhabha", "Satyendra Nath Bose", "Jagadish Chandra Bose"], # 44
    ["Gold", "Mercury", "Iridium", "Tungsten"], # 45
    ["Lord Chelmsford", "Lord Irwin", "Lord Willingdon", "Lord Wavell"], # 46
    ["1969", "1970", "1968", "1971"], # 47
    ["Aryabhata", "Brahmagupta", "Bhaskara I", "Varahamihira"], # 48
    ["Vitamin A", "Vitamin B12", "Vitamin C", "Vitamin K"], # 49
    ["Indus", "Ganges", "Brahmaputra", "Yamuna"], # 50
    ["Shah Jahan", "Akbar", "Aurangzeb", "Humayun"], # 51
    ["Karnataka", "Kerala", "Tamil Nadu", "Assam"], # 52
    ["Vijaya Lakshmi Pandit", "K.P.S. Menon", "Sarojini Naidu", "S. Radhakrishnan"], # 53
    ["Eggs", "Cotton", "Milk", "Oil Seeds"], # 54
    ["Sir Syed Ahmad Khan", "Maulana Azad", "Jawaharlal Nehru", "Sayyid Ahmad Khan"], # 55
    ["Karnam Malleswari", "Nilima Ghose", "P. T. Usha", "Mirabai Chanu"], # 56
    ["Aryabhata", "Archimedes", "Brahmagupta", "Euclid"], # 57
    ["Bankim Chandra Chatterjee", "Rabindranath Tagore", "Sarat Chandra Chattopadhyay", "Munshi Premchand"], # 58
    ["Jagadish Chandra Bose", "Meghnad Saha", "Homi J. Bhabha", "C. V. Raman"], # 59
    ["Jayalalithaa", "Sucheta Kriplani", "Nandini Satpathy", "Shashikala Kakodkar"], # 60
    ["Japan", "South Korea", "Taiwan", "Norway"], # 61
    ["Aryabhata", "Rohini", "INSAT-1A", "Bhaskara I"], # 62
    ["Homi J. Bhabha", "Vikram Sarabhai", "Satish Dhawan", "A. P. J. Abdul Kalam"], # 63
    ["Leander Paes", "Rajyavardhan Singh Rathore", "Abhinav Bindra", "P.V. Sindhu"], # 64
    ["Geneva", "New York", "Brussels", "The Hague"], # 65
    ["Chandragupta Maurya", "Ashoka", "Porus", "Bindusara"], # 66
    ["Gujarat", "Odisha", "Andhra Pradesh", "Kerala"], # 67
    ["M. S. Subbulakshmi", "Sarojini Naidu", "Mother Teresa", "Vijaylaxmi Pandit"], # 68
    ["Maharashtra", "Karnataka", "Gujarat", "Odisha"], # 69
    ["Jawaharlal Nehru", "Raghuram Rajan", "Maulana Azad", "C. Rangarajan"], # 70
    ["Santosh Yadav", "Bachendri Pal", "Arunima Sinha", "Premlata Agarwal"], # 71
    ["Louis Pasteur", "Edward Jenner", "Alexander Fleming", "Robert Koch"], # 72 
    ["1885", "1888", "1891", "1890"], # 73 
    ["Madhya Pradesh", "Maharashtra", "Karnataka", "Gujarat"], # 74
    ["Amartya Sen", "Hargobind Khorana", "V. S. Naipaul", "Kailash Satyarthi"] # 75
]
MediumAnswers = [
    "Akbar", # 1
    "Arundhati Roy", # 2
    "A highway network", # 3
    "Sputnik 1", # 4
    "Prehistoric cave paintings", # 5
    "Low growth and high inflation", # 6
    "Ukraine", # 7
    "Kalidasa", # 8
    "Aurangzeb", # 9
    "Naypyidaw", # 10
    "Freon-12", # 11
    "2007", # 12
    "Ringgit", # 13
    "Antoine Lavoisier", # 14
    "1949", # 15
    "Isaac Newton", # 16
    "Akbar", # 17
    "Lithium", # 18
    "1919", # 19
    "Kamaljeet Sandhu", # 20
    "It had no Indian members", # 21
    "Pituitary Gland", # 22
    "Mundaka Upanishad", # 23
    "Nitrous Oxide", # 24
    "Lead", # 25
    "Liver", # 26
    "Lord Linlithgow", # 27
    "The Hague", # 28
    "Vijayanagara Empire", # 29
    "Fertilizer", # 30
    "Pascal's Law", # 31
    "C. Rajagopalachari", # 32
    "Vitamin B12", # 33
    "Allama Iqbal", # 34
    "CaOCl₂", # 35
    "Bankim Chandra Chattopadhyay", # 36
    "Christiaan Barnard", # 37
    "Manjul Bhargava", # 38
    "Lala Lajpat Rai", # 39
    "1764", # 40
    "Tamil Nadu", # 41
    "C.V. Raman", # 42
    "Lord Cornwallis", # 43
    "C.V. Raman", # 44
    "Gold", # 45
    "Lord Irwin", # 46
    "1969", # 47
    "Brahmagupta", # 48
    "Vitamin A", # 49
    "Indus", # 50
    "Shah Jahan", # 51
    "Karnataka", # 52
    "Vijaya Lakshmi Pandit", # 53
    "Milk", # 54
    "Sir Syed Ahmad Khan", # 55
    "Nilima Ghose", # 56
    "Archimedes", # 57
    "Rabindranath Tagore", # 58
    "C. V. Raman", # 59
    "Sucheta Kriplani", # 60
    "Japan", # 61
    "Aryabhata", # 62
    "Vikram Sarabhai", # 63
    "Abhinav Bindra", # 64
    "New York", # 65
    "Chandragupta Maurya", # 66
    "Gujarat", # 67
    "M. S. Subbulakshmi", # 68
    "Odisha", # 69
    "Maulana Azad", # 70
    "Bachendri Pal", # 71
    "Edward Jenner", # 72
    "1885", # 73
    "Maharashtra", # 74
    "Amartya Sen" # 75
]

HardQuestions = [
"Who was the last ruler of the Satavahana dynasty?", # 1
"In economics, the term \"Phillips Curve\" represents the relationship between?", # 2
"The first Indian satellite to reach geostationary orbit was?", # 3
"Which Indian mathematician gave a proof for the binomial theorem and worked on calculus before Newton?", # 4
"The \"Doctrine of Lapse\" was implemented by?", # 5
"Which ancient Indian text is considered the earliest treatise on statecraft and diplomacy?", # 6
"Which Indian scientist developed the theory of \"Positron Emission\"?", # 7
"Which Indian classical dance form originates from Tamil Nadu and is known for sculpturesque poses?", # 8
"Who wrote the treatise \"Brihat Samhita\", covering astronomy, astrology, and architecture?", # 9
"Who introduced the \"Diwani\" revenue system in Bengal?", # 10
"In quantum mechanics, the Wave Function is denoted by?", # 11
"Who is known as the \"Father of Indian Economics\"?", # 12
"Which Indian ruler is known for the rock edicts at Dhauli and Kalinga?", # 13
"The Indian National Congress split into two groups in 1907; they were?", # 14
"The first woman to win a Booker Prize in literature from India was?", # 15
"The Nobel Prize-winning physicist S. Chandrasekhar was awarded for his work on?", # 16
"The famous Ajanta caves were primarily built during the reign of?", # 17
"In economics, the term \"Giffen Good\" refers to?", # 18
"The Indian mathematician who worked on infinite series before European mathematicians was?", # 19
"Who among the following was the First Native Indian ruler to issue their own coins?", # 20
"The famous \"Diamond Sutra,\" considered the world's first printed book, originated in?", # 21
"Who was the First Indian woman scientist to win the L'Oreal-UNESCO Award for Women in Science in 2002?", # 22
"The Indian historian who wrote \"The Wonder That Was India\" was?", # 23
"The famous Indian mathematician Bhaskara II is known for his work?", # 24
"The first Indian satellite launched for meteorological purposes was?", # 25
"The famous Kailasa temple at Ellora was built during the reign of?", # 26
"Who wrote the book \"India After Gandhi\"?", # 27
"The famous Sun Temple at Konark is designed in the shape of?", # 28
"The Indian mathematician Brahmagupta introduced rules for?", # 29
"The Indian freedom fighter Lala Lajpat Rai died due to injuries sustained in?", # 30
"The Indian Nobel Laureate in Economics, Amartya Sen, is known for his work on?", # 31
"Which Indian state has the highest number of UNESCO World Heritage Sites?", # 32
"Which Indian rules performed Ashwamedha Yagya", # 33
"The famous \"Elephanta Caves\" are dedicated to?", # 34
"The first Indian woman pilot to fly solo was?", # 35
"The English astronomer Sir Fred Hoyle, formulated which of the following Theories?", # 36
"The Indian mathematician who developed continued fraction theory and mock theta functions was?", # 37
"The Indian economist who formulated the \"Drain Theory\" was?", # 38
"The Indian freedom movement leader who formed the \"Servants of India Society\" was?", # 39
"Who is considered the \"Father of Modern India\"?", # 40
"The Indian mathematician Brahmagupta’s work \"Brahmasphutasiddhanta\" dealt with?", # 41
"The Indian freedom fighter who gave the slogan \"Simon Go Back\" was?", # 42
"The Indian mathematician Bhaskara II introduced which important concept in calculus?", # 43
"The famous Buddhist scholar Nagarjuna is credited with founding which school of philosophy?", # 44
"The Indian chemist Asima Chatterjee is best known for her work in?", # 45
"The Indian classical music form \"Dhrupad\" is associated with which musical tradition?", # 46
"The Indian scientist Meghnad Saha is known for?", # 47
"The Sun Temple at Modhera is located in which Indian state?", # 48
"Who wrote the famous book \"Ancient India\"?", # 49
"The famous rock-cut caves at Badami are associated with which dynasty?", # 50
"The Indian mathematician Aryabhata proposed which value for the sidereal rotation of the Earth?", # 51
"The Indian mathematician Bhaskara II solved which type of equations in his work \"Lilavati\"?", # 52
"The Indian leader Gopal Krishna Gokhale was associated with which movement?", # 53
"""Which Indian mathematician gave a systematic treatment of indeterminate equations of the first degree known as “Kuttaka”?""", # 54
"The Brihadeeswarar Temple at Thanjavur, built by Rajaraja Chola I, is constructed primarily from?", # 55
"The Indian scientist Meghnad Saha is best known for the Saha Ionization Equation, which is used in?", # 56
"The famous Buddhist university of Vikramashila was founded by?", # 57
"The Indian classical dance form \"Sattriya\" originated in which state?", # 58
"The Indian emperor Harshavardhana was a patron of which famous Chinese traveler?", # 59
"The Indian astronomer Bhaskara II correctly explained which phenomenon centuries before Europeans?", # 60
]
HardOptions = [
["Yajna Chandra", "Simuka", "Gautamiputra Satakarni", "Pulumavi IV"],                     # 1 
["Inflation and Unemployment", "Demand and Supply", "GDP and Interest Rates", "Price Level and Money Supply"], # 2
["Aryabhata", "Bhaskara I", "INSAT-1A", "Ariane Passenger Payload Experiment (APPLE)"],  # 3
["Brahmagupta", "Bhaskara II", "Madhava of Sangamagrama", "Aryabhata"],               # 4
["Lord Wellesley", "Lord Dalhousie", "Lord Canning", "Lord Cornwallis"],              # 5
["Arthashastra", "Taittiriya Upanishad", "Manusmriti", "Rigveda"],                    # 6
["Meghnad Saha", "Satyendra Nath Bose", "Homi J. Bhabha", "M.G.K. Menon"],            # 7 
["Bharatanatyam", "Bommalattam", "Kavadi Attam", "Oyilattam"],                        # 8
["Varahamihira", "Kalidasa", "Bhatta Bhaskara", "Panini"],                            # 9
["Robert Clive", "Warren Hastings", "Lord Cornwallis", "Lord Wellesley"],             # 10
["Ψ (Psi)", "ε (Epsilon)", "θ (Theta)", "λ (Lambda)"],                                # 11
["Dadabhai Naoroji", "R.C. Dutt", "Adam Smith", "Amartya Sen"],                       # 12
["Ashoka", "Chandragupta Maurya", "Samudragupta", "Harshavardhana"],                  # 13
["Moderates and Radicals", "Liberals and Conservatives", "Radicals and Conservatives", "Loyalists and Rebels"], # 14
["Arundhati Roy", "Kiran Desai", "Jhumpa Lahiri", "Anita Desai"],                     # 15
["Early Works on General Theory of Relativity", "Studies on Photoelectric Effect", "Studies of Physical Processes Important to the Structure and Evolution of Stars", "Studies in the field of Electromagnetism"], # 16
["Vakataka dynasty", "Gupta dynasty", "Maurya dynasty", "Satavahana dynasty"],        # 17
["Inferior goods with upward-sloping demand curve", "Luxury goods", "Substitute goods", "Complementary goods"], # 18
["Madhava of Sangamagrama", "Bhaskara II", "Ramanujan", "Varahamihira"],                              # 19
["Chandragupta Maurya", "Gautamiputra Satakarni", "Harsha", "Samudragupta"],                           # 20
["China", "India", "Japan", "Korea"],                                                 # 21
["Indira Nath", "Asima Chatterjee", "Janaki Ammal", "Archana Sharma"],                # 22 
["R.C. Majumdar", "A.L. Basham", "Romila Thapar", "Bipin Chandra"],                  # 23
["Siddhanta Shiromani", "Surya Siddhanta", "Aryabhatiya", "Brahmasphutasiddhanta"],   # 24
["Bhaskara I", "Rohini", "INSAT-1A", "KALPANA-1"],                                    # 25
["Rashtrakuta Dynasty", "Chola Dynasty", "Gupta Dynasty", "Maurya Dynasty"],          # 26
["Ramachandra Guha", "Bipan Chandra", "R.C. Majumdar", "K.M. Panikkar"],              # 27
["A Chariot with Wheels", "A Lotus", "Sun", "A Lion"],                                # 28
["Zero and Negative numbers", "Trigonometry", "Algebra", "Geometry"],                 # 29
["Jallianwala Bagh Massacre", "Simon Commission Protest", "Quit India Movement", "Non-Cooperation Movement"],    # 30
["Welfare Economics", "International trade", "Monetary Policy", "Game Theory"],       # 31
["Rajasthan", "Maharashtra", "Tamil Nadu", "Karnataka"],                              # 32
["Mirza Raja Sawai Jai Singh II", "Maharaja Suraj Mal", "Mirza Raja Sawai Madho Singh I", "Maharaja Ranjit Singh"],        # 33
["Shiva", "Vishnu", "Krishna", "Indra"],                                              # 34
["Sarla Thakral", "Hansa Mehta", "Avani Chaturvedi", "Harita Kaur Deol"],             # 35 
["Big Bang Theory", "Steady State Theory", "Nebular Hypothesis", "String Theory"],    # 36
["Srinivasa Ramanujan", "C.R. Rao", "Narendra Karmarkar", "Harish Chandra"],          # 37
["Dadabhai Naoroji", "R.C. Dutt", "Jagdish Bhagwati", "Amartya Sen"],                 # 38
["Gopal Krishna Gokhale", "Bal Gangadhar Tilak", "Lala Lajpat Rai", "Bipin Chandra Pal"], # 39
["Raja Ram Mohan Roy", "Mahatma Gandhi", "J.R.D. Tata", "Sardar Vallabhbhai Patel"],  # 40
["Algebra and Arithmetic", "Trigonometry", "Geometry", "Number Theory"],              # 41
["Motilal Nehru", "Mahatma Gandhi", "Bal Gangadhar Tilak", "Lala Lajpat Rai"],        # 42
["Probability", "Solution of Cubic Polynomials", "Imaginary Numbers", "Infinitesimals"], # 43
["Mahayana", "Theravada", "Madhyamaka", "Vajrayana"],                                 # 44
["Organic Chemistry and Medicinal Chemistry", "Physical Chemistry", "Nuclear Chemistry", "Biochemistry"],        # 45
["Sufi Qawwali Tradition", "Folk Music of Bengal", "Hindustani Classical Music", "Carnatic Classical Music"],             # 46
["Ionization Equation in Astrophysics", "Quantum Theory of Photoelectric Effect", "Invention of the Radio", "Contributions in Nuclear Physics"],     # 47
["Gujarat", "Karnataka", "Madhya Pradesh", "Bihar"],                                     # 48
["R.C. Majumdar", "Romila Thapar", "Jadunath Sarkar", "A. L. Basham"],                   # 49
["Rashtrakutas", "Chalukyas", "Pallavas", "Mauryas"], # 50
["24 hours 15 minutes", "23 hours 45 minutes", "24 hours and 3 minutes", "23 hours 56 minutes"], # 51
["Linear Equations", "Trigonometric Equations", "Quadratic Equations", "Differential Equations"],  # 52
["Home Rule Movement", "Non-Cooperation Movement", "Quit India Movement", "Moderate Nationalism"],    # 53
["Aryabhata", "Bhaskaracharya", "Brahmagupta", "Varāhamihira"],                                        # 54
["Sandstone", "Limestone", "Marble", "Granite"],         # 55
["Biochemistry", "Astrophysics", "Organic Chemistry", "Nuclear Physics"], # 56
["Rajaraja I", "Harshavardhana", "Samudragupta", "Dharmapala"],                      # 57
["West Bengal", "Jharkhand", "Odisha", "Assam"],        # 58
["Faxian", "Hiuen Tsang", "Fa Hien", "Yijing"],                               # 59
["Eclipses", "Retrograde motion", "Gravity", "Centripetal Force"],              # 60
]
HardAnswers = [
"Pulumavi IV",                         # 1 
"Inflation and Unemployment",          # 2
"Ariane Passenger Payload Experiment (APPLE)",  # 3
"Madhava of Sangamagrama",             # 4
"Lord Dalhousie",                      # 5
"Arthashastra",                        # 6
"Homi J. Bhabha",                      # 7 
"Bharatanatyam",                       # 8
"Varahamihira",                        # 9
"Robert Clive",                        # 10
"Ψ (Psi)",                             # 11
"Dadabhai Naoroji",                    # 12
"Ashoka",                              # 13
"Moderates and Radicals",              # 14
"Arundhati Roy",                       # 15
"Studies of Physical Processes Important to the Structure and Evolution of Stars", # 16
"Gupta dynasty",                       # 17
"Inferior goods with upward-sloping demand curve", # 18
"Madhava of Sangamagrama",             # 19
"Gautamiputra Satakarni",              # 20
"China",                               # 21
"Indira Nath",                         # 22 
"A.L. Basham",                         # 23
"Siddhanta Shiromani",                 # 24
"KALPANA-1",                           # 25
"Rashtrakuta Dynasty",                 # 26
"Ramachandra Guha",                    # 27
"A Chariot with Wheels",               # 28
"Zero and Negative numbers",           # 29
"Simon Commission Protest",            # 30
"Welfare Economics",                   # 31
"Maharashtra",                         # 32
"Mirza Raja Sawai Jai Singh II",       # 33
"Shiva",                               # 34
"Harita Kaur Deol",                    # 35 
"Steady State Theory",                 # 36
"Srinivasa Ramanujan",                 # 37
"Dadabhai Naoroji",                    # 38
"Gopal Krishna Gokhale",               # 39
"Raja Ram Mohan Roy",                  # 40
"Algebra and Arithmetic",              # 41
"Lala Lajpat Rai",                     # 42
"Infinitesimals",                      # 43
"Madhyamaka",                          # 44
"Organic Chemistry and Medicinal Chemistry",  # 45
"Hindustani Classical Music",          # 46
"Ionization Equation in Astrophysics", # 47
"Gujarat",                             # 48
"R.C. Majumdar",                       # 49
"Chalukyas",                           # 50
"23 hours 56 minutes",                 # 51
"Quadratic Equations",                 # 52
"Moderate Nationalism",                # 53
"Bhaskaracharya",                      # 54
"Granite",                             # 55
"Astrophysics",                        # 56
"Dharmapala",                          # 57
"Assam",                               # 58
"Hiuen Tsang",                         # 59
"Gravity",                             # 60
]

VeryHardQuestions = [
    "The \"Aryabhata approximation\" of π in the 5th century CE was accurate to how many decimal places?", # 1
    "The Indian mathematician Madhava of Sangamagrama developed infinite series for π. Which European mathematician later discovered it independently centuries afterward?", # 2
    "The ancient Indian mathematician Pingala is known for which contribution?", # 3
    "The Indian scientist Homi J. Bhabha was instrumental in establishing which Indian institution in 1945?", # 4
    "Which Indian mathematician introduced the \"Chakravala method\" for solving Pell's equations centuries before it was known in Europe?", # 5
    "The Shatapatha Brahmana contains early references to which astronomical phenomenon?", # 6
    "The Buddhist university of Vallabhi was primarily associated with which sect?", # 7
    "The Gundestrup Cauldron, a richly decorated silver vessel discovered in Denmark, is primarily associated with which ancient culture?", # 8
    "The Kakrapar Atomic Power Station in India is primarily based on which type of reactor?", # 9
    "The Bakhshali Manuscript, rediscovered in the 20th century, contains?", # 10
    "The Sun Temple at Modhera in Gujarat was designed to align with which specific Astronomical event?", # 11
    "The Udayagiri Observatory (built in 5th century CE) during Chandragupta II’s reign was primarily used to?", # 12
    "The Mysore Palace’s Durbar Hall was influenced by which foreign architectural style?", # 13
    "The Kerala School of Mathematics (14th–16th century) derived an infinite series for which trigonometric function first?", # 14
    "The Chola emperor Rajendra I’s naval expedition reached which distant region in the 11th century CE?", # 15
    "The Ajanta murals’ continuous narrative style is an early example of which artistic technique?" # 16
]
VeryHardOptions = [
    ["2 decimal place", "3 decimal places", "4 decimal places", "5 decimal places"],                                 # 1
    ["Isaac Newton", "Gerolamo Cardano", "James Gregory", "Blaise Pascal"],                                          # 2
    ["Binary Numeral System", "Algebraic Solutions", "Trigonometric Tables", "Concept of Zero"],                     # 3
    ["Tata Institute of Fundamental Research (TIFR)", "Indian Institute of Science (IISc)", "Bhabha Atomic Research Centre (BARC)", "IIT Bombay"], # 4
    ["Bhāskara II", "Madhava of Sangamagrama", "Brahmagupta", "Varāhamihira"],                                       # 5
    ["Retrograde Motion of Planets", "Phases of the Moon", "Solar Eclipse Cycles", "Precession of Equinoxes"],       # 6
    ["Pudgalavada (Saṃmitīya)", "Vajrayana", "Mahayana", "Hinayana"],                                                # 7 
    ["Celtic", "Greek", "Mesopotamian", "Egyptian"],                                                                 # 8
    ["Pressurized Heavy Water Reactor (PHWR)", "Boiling Water Reactor (BWR)", "Fast Breeder Reactor (FBR)", "Gas-cooled Reactor"], # 9
    ["The Earliest known use of the Symbol for Zero", "The First Explanation of Calculus", "The Earliest Tables of Sine Values", "The First Proofs of Pythagoras' Theorem"],        # 10
    ["The Autumnal Equinox Moonrise", "The Winter Solstice Sunrise", "The Equinox Sunset", "The Summer Solstice Sunrise"],    # 11
    ["Track the Annual Flooding of Rivers", "Align Ritual Practices with Celestial Events", "Study Medicinal Plants under Varying Sunlight", "Timekeeping for Markets"],       # 12
    ["Baroque", "Gothic", "Indo-Saracenic", "Byzantine"],                                                            # 13
    ["Sine", "Cosine", "Tangent", "Cotangent"],                                                                      # 14
    ["Srivijaya (Sumatra)", "Maldives", "Andaman & Nicobar Islands", "Mauritius"],                                   # 15
    ["Sequential Storytelling", "Fresco with Gold leaf", "Single-point Perspective", "Iconographic Minimalism"],     # 16
]
VeryHardAnswers = [
    "4 decimal places",                     # 1  
    "James Gregory",                        # 2
    "Binary Numeral System",                # 3
    "Tata Institute of Fundamental Research (TIFR)", # 4
    "Bhāskara II",                          # 5  
    "Precession of Equinoxes",              # 6
    "Hinayana",                             # 7  
    "Celtic",                               # 8  
    "Pressurized Heavy Water Reactor (PHWR)", # 9
    "The Earliest known use of the Symbol for Zero",  # 10
    "The Winter Solstice Sunrise",          # 11
    "Align Ritual Practices with Celestial Events",  # 12
    "Indo-Saracenic",                       # 13
    "Sine",                                 # 14  
    "Srivijaya (Sumatra)",                  # 15
    "Sequential Storytelling"               # 16
]

UsedEasyIndices = []
UsedMediumIndices = []
UsedHardIndices = []
UsedVeryHardIndices = []

#                               All FUNCTIONS TO GET ASK QUESTIONS, CHECK ANSWERS, USE LIFELINES, ETC.

def return_date():
    return datetime.date.today().strftime("%d/%m/%Y")
def return_cheque_number():
    return random.randint(100000, 999999)
def return_account_number():
    return random.randint(10000000000, 99999999999)

def print_cheque(full_name, Question_Number):
    cheque_number = return_cheque_number()
    date = return_date()
    account_number = return_account_number()

    line_width = 75 # This section simply handles that pay to the order line does not break the cheque border line.
    name_line = f"PAY TO THE ORDER OF: {full_name}"
    spaces_after_name = line_width - len(name_line)
    spaces_for_name = " " * spaces_after_name

    line_width = 75 # This section simply handles that amount line does not break the cheque border line.
    amount_line = f"Amount: ₹ {PrizeMoneyString[Question_Number-1]}"
    spaces_after_amount = line_width - len(amount_line)
    spaces_for_amount = " " * spaces_after_amount    
    
    cheque = f"""
┌────────────────────────────────────────────────────────────────────────────┐
│                           STATE BANK OF INDIA                              │
│ Cheque No: {cheque_number}                            Date: {date}              │
├────────────────────────────────────────────────────────────────────────────┤
│ {name_line}{spaces_for_name}│                           
│ {amount_line}{spaces_for_amount}│
│                                                                            │
│ Account Number: {account_number}                                                │
│                                                                            │
│                                                     AMITABH BACCHAN        │
│                                                                            │
│                                                       Signature            │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
"""
    print("\nYeh raha Aapki Jeeti hui Dhanrashi ka Cheque. Seedha aapke Bank account mein.")
    print(cheque)

def AskEasyLifeline(AvailableLifelines, UsedLifelines, i, Question_Number, ExactOptions):
    
    while True:
        print("\nAap iss sawaal ke liye ek Lifeline ka upyog karna chahte hain.\nAapke paas abhi tak yeh lifelines bachi hain:\n")
        for Lifeline in AvailableLifelines:
            print(Lifeline)
        ChosenLifeline = str(input("\nKaunsi Lifeline ka upyog karna chahenge?: ")).strip().lower()

        if ChosenLifeline == "50-50" and "50-50" in AvailableLifelines:
            try:
                AvailableLifelines.remove("50-50")
                UsedLifelines.append("50-50")
            except:
                pass
            Easy_Lifeline_50_50(i, Question_Number)
            return

        elif ChosenLifeline == "switch the question" and "Switch the Question" in AvailableLifelines:
            try:
                AvailableLifelines.remove("Switch the Question")
                UsedLifelines.append("Switch the Question")
            except:
                pass
            print("\nAb Aapke Computer Screen Par Ek Naya Sawaal Aayega.\nToh Yeh Raha Aapka Naya Sawaal:\n")
            Ask_EasyQuestion(Question_Number)
            return

        elif ChosenLifeline == "double dip" and "Double Dip" in AvailableLifelines:
            try:
                AvailableLifelines.remove("Double Dip")
                UsedLifelines.append("Double Dip")
            except:
                pass
            Easy_Lifeline_DoubleDip(i, Question_Number, ExactOptions)
            return
        
        elif ChosenLifeline == "power paplu" and "Power Paplu" in AvailableLifelines:
            if len(UsedLifelines) == 0:
                print("\nAapne abhi tak koi lifeline use nahi ki hai.\nIsliye aap Power Paplu Lifeline ka upyog nahi kar sakte.\n")
                AskEasyLifeline(AvailableLifelines, UsedLifelines, i, Question_Number, ExactOptions)
                return
            try:
                AvailableLifelines.remove("Power Paplu")
                UsedLifelines.append("Power Paplu")
            except:
                pass
            
            print("\n Aapne Power Paplu Lifeline ka Upyog kiya hai.\nAb aap apni kisi purani lifeline ko Dobara Jeevit kar sakte hain.\nYeh Rahi Aapki use kari ja chuki Lifelines:\n")
            for Lifeline in UsedLifelines:
                if Lifeline != "Power Paplu":
                    print(Lifeline)
            RevivingLifeline = str(input("\nKaunsi Lifeline ko Jeevit karna chahenge?: ")).strip().lower()
            if RevivingLifeline == "50-50" and "50-50" in UsedLifelines:
                AvailableLifelines.append("50-50")
                continue
            elif RevivingLifeline == "switch the question" and "Switch the Question" in UsedLifelines:
                AvailableLifelines.append("Switch the Question")
                continue
            elif RevivingLifeline == "double dip" and "Double Dip" in UsedLifelines:
                AvailableLifelines.append("Double Dip")
                continue
            elif RevivingLifeline == "power paplu":
                print("\nAap Power Paplu Lifeline ko Jeevit nahi kar sakte.\n")
                try:
                    UsedLifelines.remove("Power Paplu")
                    AvailableLifelines.append("Power Paplu")
                except:
                    pass
                continue
            else:
                print("\nAapne galat Lifeline ka naam likha hai.\n")
                try: 
                    UsedLifelines.remove("Power Paplu")
                    AvailableLifelines.append("Power Paplu")
                except:
                    pass
                continue
        else:
            print("\nAapne galat Lifeline ka naam likha hai.\n")
            continue        
def Easy_Lifeline_50_50(i, Question_Number):
    print("\nToh Aapne Apni 50-50 Lifeline Use Karne ka Faisla Kiya Hai.\n\n",
           "Iska matlab aapke 2 options bachege.\n"
           "Ek Sahi aur ek Galat\n", sep=""
          )
    EasyWrongOptions = []
    for ioption in EasyOptions[i]:
        if ioption != EasyAnswers[i]:
            EasyWrongOptions.append(ioption)
    WrongOption1 = random.choice(EasyWrongOptions)
    OptionsAfterLifeline = [WrongOption1, EasyAnswers[i]]
    random.shuffle(OptionsAfterLifeline)
    print("Yeh Rahe Aapke Saamne 2 Bache hue Options: \n")
    print("A.", OptionsAfterLifeline[0])
    print("B.", OptionsAfterLifeline[1])

    while True:
        PlayerAnswerAfter_50_50 = str(input("\nChoose The Correct Option: ")).strip().lower()
        letter_to_option = { 'a': OptionsAfterLifeline[0].lower(),
                            'b': OptionsAfterLifeline[1].lower(),
                            }
        
        if not PlayerAnswerAfter_50_50:  # Handles empty input
                    print("Invalid Input. Please enter a valid option.")
                    continue
        
        # Quit Option
            
        if PlayerAnswerAfter_50_50.strip().lower() == "quit":
            if Question_Number >= 2:
                print("\nAapne Decide kiya hai ki yahin par Game ko Quit karenge.\nYeh bhi ek samajhdaar faisla hai.\nAap ghar jaa rahe hain le kar apne Jeete huye Paise.\n",sep="")
                print("TOTAL PRIZE MONEY ₹", PrizeMoneyString[Question_Number - 2], sep="")
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()
            else: 
                print("Yeh Pehla sawaal tha, aur aapne Quit karne ka chunav kiya. \nAfsos, is daur mein aap koi dhanrashi le kar nahi jaa rahe.\n")
                print("TOTAL PRIZE MONEY ₹0")
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()

        # Checking Answer

        Medium_50_50_WrongOptions = []
        for ioption in OptionsAfterLifeline:
            if ioption != EasyAnswers[i]:
                Medium_50_50_WrongOptions.append(ioption)
        
        Medium_50_50_WrongOptions = [o.strip().lower() for o in Medium_50_50_WrongOptions]
        
        First_Letter_After_50_50 = PlayerAnswerAfter_50_50[0]
        First_Letter_After_50_50_Plus_Dot = PlayerAnswerAfter_50_50[0] + "."
        First_Letter_After_50_50_Plus_ClosingBracket = PlayerAnswerAfter_50_50[0] + ")"

        if First_Letter_After_50_50 == PlayerAnswerAfter_50_50: # If user entered only option letter.
            attempt_text = letter_to_option.get(First_Letter_After_50_50, PlayerAnswerAfter_50_50)
        elif First_Letter_After_50_50_Plus_Dot == PlayerAnswerAfter_50_50 or First_Letter_After_50_50_Plus_ClosingBracket == PlayerAnswerAfter_50_50: # If user entered only option letter with dot or closing bracket.
            attempt_text = letter_to_option.get(First_Letter_After_50_50, PlayerAnswerAfter_50_50)
        elif MediumAnswers[i].strip().lower() in PlayerAnswerAfter_50_50 and Medium_50_50_WrongOptions[0] not in PlayerAnswerAfter_50_50: # If user entered the full answer text.  
            attempt_text = MediumAnswers[i].strip().lower()
        else:
            attempt_text = PlayerAnswerAfter_50_50
        
        if attempt_text.strip().lower() == MediumAnswers[i].lower().strip():
            print("\nCorrect Answer:", MediumAnswers[i])
            print("\nSahi Jawaab!\n","\nAap Jeet Chuke Hai ₹", PrizeMoneyString[Question_Number-1],sep = "")
            return
        elif attempt_text.lower().strip() in Medium_50_50_WrongOptions:
            print("\nCorrect Answer:", MediumAnswers[i])
            print("\nGalat Jawaab!\n", "Durbhagyavarsh iss KBC ke khel mein aapka Safar yahi khatam hota hai.", "\nAapke saath khel kar hame bahut anand mila.", "\n\nUnfortunately Aap ko iss khel se khali haat hi jaana padega.", "\nUmmed hai ki aapse phir mulakat hogi.", "\n\nTOTAL PRIZE MONEY ₹0", sep = "" )
            print("Press Any Key to Exit ")
            msvcrt.getch()        
            sys.exit()
        else:
            print("Invalid Input\n")
def Easy_Lifeline_DoubleDip(i, Question_Number, ExactOptions):
    print("\nToh Aapne Apni Double Dip Lifeline Use Karne ka Faisla Kiya Hai.\n\n",
           "Iska matlab aapke 2 attempts honge iss sawaal ke liye.\n" , sep=""
          )
    while True: 
        Easy_Attempt1 = str(input("Choose The Correct Option (Attempt 1): ")).strip().lower()
        Easy_Attempt2 = str(input("Choose The Correct Option (Attempt 2): ")).strip().lower()
        letter_to_option = { 'a': ExactOptions[0].lower().strip(),
                            'b': ExactOptions[1].lower().strip(),
                            'c': ExactOptions[2].lower().strip(),
                            'd': ExactOptions[3].lower().strip() }
        
        if not Easy_Attempt1:  # Handles empty input
            print("Invalid Input. Please enter a valid option.")
            continue

        if not Easy_Attempt2:  # Handles empty input
            print("Invalid Input. Please enter a valid option.")
            continue
        
        # Checking Answer

        EasyWrongOptions = []
        for ioption in EasyOptions[i]:
            if ioption != EasyAnswers[i]:
                EasyWrongOptions.append(ioption) # This adds all the wrong options into a list called EasyWrongOptions.
            
        EasyWrongOptions = [o.strip().lower() for o in EasyWrongOptions] # This strips and lowers all the wrong options in the EasyWrongOptions list.

        First_Letter_Attempt1 = Easy_Attempt1[0]
        First_Letter_Attempt1_Plus_Dot = Easy_Attempt1[0] + "."
        First_Letter_Attempt1_Plus_ClosingBracket = Easy_Attempt1[0] + ")"

        First_Letter_Attempt2 = Easy_Attempt2[0]
        First_Letter_Attempt2_Plus_Dot = Easy_Attempt2[0] + "."
        First_Letter_Attempt2_Plus_ClosingBracket = Easy_Attempt2[0] + ")"

        if First_Letter_Attempt1 == Easy_Attempt1: # If user entered only option letter.
            attempt1_text = letter_to_option.get(First_Letter_Attempt1, Easy_Attempt1)
        elif First_Letter_Attempt1_Plus_Dot == Easy_Attempt1 or First_Letter_Attempt1_Plus_ClosingBracket == Easy_Attempt1: # If user entered only option letter with dot or closing bracket.
            attempt1_text = letter_to_option.get(First_Letter_Attempt1, Easy_Attempt1) 
        elif EasyAnswers[i].strip().lower() in Easy_Attempt1 and str(EasyWrongOptions[0]).lower().strip() not in Easy_Attempt1 and str(EasyWrongOptions[1]).lower().strip() not in Easy_Attempt1 and str(EasyWrongOptions[2]).lower().strip() not in Easy_Attempt1: # If user entered only correct full answer and not any wrong option.  
            attempt1_text = EasyAnswers[i].strip().lower()
        else:
            attempt1_text = Easy_Attempt1

        if First_Letter_Attempt2 == Easy_Attempt2: # If user entered only option letter.
            attempt2_text = letter_to_option.get(First_Letter_Attempt2, Easy_Attempt2)
        elif First_Letter_Attempt2_Plus_Dot == Easy_Attempt2 or First_Letter_Attempt2_Plus_ClosingBracket == Easy_Attempt2: # If user entered only option letter with dot or closing bracket.
            attempt2_text = letter_to_option.get(First_Letter_Attempt2, Easy_Attempt2) 
        elif EasyAnswers[i].strip().lower() in Easy_Attempt2 and str(EasyWrongOptions[0]).lower().strip() not in Easy_Attempt2 and str(EasyWrongOptions[1]).lower().strip() not in Easy_Attempt2 and str(EasyWrongOptions[2]).lower().strip() not in Easy_Attempt2: # If user entered only correct full answer and not any wrong option.  
            attempt2_text = EasyAnswers[i].strip().lower()
        else:
            attempt2_text = Easy_Attempt2

        if attempt1_text.strip().lower() == str(EasyAnswers[i]).lower().strip() or attempt2_text.strip().lower() == str(EasyAnswers[i]).lower().strip():
            print("\nCorrect Answer:", EasyAnswers[i])
            print("\nSahi Jawaab!\n","\nAap Jeet Chuke Hai ₹", PrizeMoneyString[Question_Number-1],sep = "")
            return
        elif attempt1_text.lower().strip() in EasyWrongOptions and attempt2_text.lower().strip() in EasyWrongOptions:
            print("\nCorrect Answer:", EasyAnswers[i])
            print("\nGalat Jawaab!\n", "Durbhagyavarsh iss KBC ke khel mein aapka Safar yahi khatam hota hai.", "\nAapke saath khel kar hame bahut anand mila.", "\n\nUnfortunately Aap ko iss khel se khali haat hi jaana padega.", "\nUmmed hai ki aapse phir mulakat hogi.", "\n\nTOTAL PRIZE MONEY ₹0", sep = "" )
            print("Press Any Key to Exit ")
            msvcrt.getch()        
            sys.exit()
        else:
            print("Invalid Input\n")
def Ask_EasyQuestion(Question_Number, i = None): 
        AvailableEasyIndices = [iunique for iunique in range(0,len(EasyQuestions)) if iunique not in UsedEasyIndices]
        if i == None: 
            i = random.choice(AvailableEasyIndices)
        UsedEasyIndices.append(i)

        while True:
            print(x,QuestionNumber[Question_Number-1], "\nFor a Prize of ₹",PrizeMoneyString[Question_Number-1] ,"\n\n", EasyQuestions[i], "\n",sep="")
            ExactOptions = EasyOptions[i].copy()
            
            random.shuffle(ExactOptions) #Now Options are shuffeled. Wherever you write something like ExactOptions[0] after this. This means the shuffled ExactOptions and not the Original. 
            print(Options[0], ExactOptions[0])
            print(Options[1], ExactOptions[1])
            print(Options[2], ExactOptions[2])
            print(Options[3], ExactOptions[3])

            print("\nNote: Type 'Lifeline' to use a Lifeline. \nType 'Quit' to Quit the Game and take Home your Winnings.")
            
            PlayerAnswer = str(input("\nChoose The Correct Option: ")).strip().lower()
            letter_to_option = { 'a': ExactOptions[0].lower(),
                                'b': ExactOptions[1].lower(),
                                'c': ExactOptions[2].lower(),
                                'd': ExactOptions[3].lower() }
            
            if not PlayerAnswer:  # Handles empty input
                print("Invalid Input. Please enter a valid option.")
                continue
            
            # Master Key Option
            
            if PlayerAnswer.strip().lower() == MasterKey.strip().lower():
                print("\nCorrect Answer:", EasyAnswers[i])
                print("\nMASTER KEY ACTIVATED\nSKIPPING THIS QUESTION\n")
                return
            
            # Quit Option
            
            if PlayerAnswer.strip().lower() == "quit":
                if Question_Number >= 2:
                    print("\nAapne Decide kiya hai ki yahin par Game ko Quit karenge.\nYeh bhi ek samajhdaar faisla hai.\nAap ghar jaa rahe hain le kar apne Jeete huye Paise.\n",sep="")
                    print("TOTAL PRIZE MONEY ₹", PrizeMoneyString[Question_Number - 2], sep="")
                    print("Press Any Key to Exit ")
                    msvcrt.getch()
                    sys.exit()
                else: 
                    print("Yeh Pehla sawaal tha, aur aapne Quit karne ka chunav kiya. \nAfsos, is daur mein aap koi dhanrashi le kar nahi jaa rahe.\n")
                    print("TOTAL PRIZE MONEY ₹0")
                    print("Press Any Key to Exit ")
                    msvcrt.getch()
                    sys.exit()

            # Lifelines

            def Easy_Lifeline_Unavailable():
                while True:
                    print("\nAapke Paas koi bhi bachi hui Lifeline nahi hai.\n")
                    PlayerAnswer = str(input("Choose The Correct Option: ")).strip().lower()
                    if PlayerAnswer:
                        return PlayerAnswer
                    print("Invalid Input. Please enter a valid option.")
            
            if "lifeline" in PlayerAnswer and len(AvailableLifelines) > 0:
                AskEasyLifeline(AvailableLifelines, UsedLifelines, i , Question_Number, ExactOptions)
                return
            elif "lifeline" in PlayerAnswer and len(AvailableLifelines) == 0:
                PlayerAnswer = Easy_Lifeline_Unavailable()
            
            # Checking Answer

            EasyWrongOptions = []
            for ioption in EasyOptions[i]:
                if ioption != EasyAnswers[i]:
                    EasyWrongOptions.append(ioption) # This adds all the wrong options into a list called EasyWrongOptions.
            
            EasyWrongOptions = [o.strip().lower() for o in EasyWrongOptions] # This strips and lowers all the wrong options in the EasyWrongOptions list.
            
            First_Letter = PlayerAnswer[0]
            First_Letter_Plus_Dot = First_Letter + "."
            First_Letter_Plus_ClosingBracket = First_Letter + ")"

            if First_Letter == PlayerAnswer: # If user inputs only one letter.
                answer_text = letter_to_option.get(First_Letter, PlayerAnswer)
            elif First_Letter_Plus_Dot == PlayerAnswer or First_Letter_Plus_ClosingBracket == PlayerAnswer: # If user inputs letter with dot or closing bracket.
                answer_text = letter_to_option.get(First_Letter, PlayerAnswer)
            elif EasyAnswers[i].lower().strip() in PlayerAnswer and str(EasyWrongOptions[0]).lower().strip() not in PlayerAnswer and str(EasyWrongOptions[1]).lower().strip() not in PlayerAnswer and str(EasyWrongOptions[2]).lower().strip() not in PlayerAnswer: # If user inputs the correct option text but not the wrong option text.
                answer_text = EasyAnswers[i].lower().strip()
            else:
                answer_text = PlayerAnswer
            
            if answer_text.lower().strip() == EasyAnswers[i].lower().strip():
                print("\nSahi Jawaab!\n","\nAap Jeet Chuke Hai ₹", PrizeMoneyString[Question_Number-1],sep = "")
                return
            elif answer_text.lower().strip() in EasyWrongOptions:
                print("\nCorrect Answer:", EasyAnswers[i])
                print("\nGalat Jawaab!\n", "Durbhagyavarsh iss KBC ke khel mein aapka Safar yahi khatam hota hai.", "\nAapke saath khel kar hame bahut anand mila.", "\n\nUnfortunately Aap ko iss khel se khali haat hi jaana padega.", "\nUmmed hai ki aapse phir mulakat hogi.", "\n\nTOTAL PRIZE MONEY ₹0", sep = "" )
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()
            else:
                print("Invalid Input\n")

def AskMediumLifeline(AvailableLifelines, UsedLifelines, j, Question_Number, ExactOptions):
    
    while True: 
        print("\nAap iss sawaal ke liye ek Lifeline ka upyog karna chahte hain.\nAapke paas abhi tak yeh lifelines bachi hain:\n")
        for Lifeline in AvailableLifelines:
            print(Lifeline)
        ChosenLifeline = str(input("\nKaunsi Lifeline ka upyog karna chahenge?: ")).strip().lower()

        if ChosenLifeline == "50-50" and "50-50" in AvailableLifelines:
            try:
                AvailableLifelines.remove("50-50")
                UsedLifelines.append("50-50")
            except:
                pass
            Medium_Lifeline_50_50(j, Question_Number)
            return

        elif ChosenLifeline == "switch the question" and "Switch the Question" in AvailableLifelines:
            try:
                AvailableLifelines.remove("Switch the Question")
                UsedLifelines.append("Switch the Question")
            except:
                pass
            print("\nAb Aapke Computer Screen Par Ek Naya Sawaal Aayega.\nToh Yeh Raha Aapka Naya Sawaal:\n")
            Ask_MediumQuestion(Question_Number)
            return

        elif ChosenLifeline == "double dip" and "Double Dip" in AvailableLifelines:
            try:
                AvailableLifelines.remove("Double Dip")
                UsedLifelines.append("Double Dip")
            except:
                pass
            Medium_Lifeline_DoubleDip(j, Question_Number, ExactOptions)
            return

        elif ChosenLifeline == "power paplu" and "Power Paplu" in AvailableLifelines:
            if len(UsedLifelines) == 0:
                print("\nAapne abhi tak koi lifeline use nahi ki hai.\nIsliye aap Power Paplu Lifeline ka upyog nahi kar sakte.\n")
                AskMediumLifeline(AvailableLifelines, UsedLifelines, j, Question_Number, ExactOptions)
                return
            try:
                AvailableLifelines.remove("Power Paplu")
                UsedLifelines.append("Power Paplu")
            except:
                pass

            print("\n Aapne Power Paplu Lifeline ka Upyog kiya hai.\nAb aap apni kisi purani lifeline ko Dobara Jeevit kar sakte hain.\nYeh Rahi Aapki use kari ja chuki Lifelines:\n")
            for Lifeline in UsedLifelines:
                if Lifeline != "Power Paplu":
                    print(Lifeline)
            RevivingLifeline = str(input("\nKaunsi Lifeline ko Jeevit karna chahenge?: ")).strip().lower()
            if RevivingLifeline == "50-50" and "50-50" in UsedLifelines:
                AvailableLifelines.append("50-50")
                continue
            elif RevivingLifeline == "switch the question" and "Switch the Question" in UsedLifelines:
                AvailableLifelines.append("Switch the Question")
                continue
            elif RevivingLifeline == "double dip" and "Double Dip" in UsedLifelines:
                AvailableLifelines.append("Double Dip")
                continue
            elif RevivingLifeline == "power paplu":
                print("\nAap Power Paplu Lifeline ko Jeevit nahi kar sakte.\n")
                try:
                    UsedLifelines.remove("Power Paplu")
                    AvailableLifelines.append("Power Paplu")
                except:
                    pass
                continue
            else:
                print("\nAapne galat Lifeline ka naam likha hai.\n")
                try: 
                    UsedLifelines.remove("Power Paplu")
                    AvailableLifelines.append("Power Paplu")
                except:
                    pass
                continue
        else:
            print("\nAapne galat Lifeline ka naam likha hai.\n")
            continue
def Medium_Lifeline_50_50(j, Question_Number):
    print("\nToh Aapne Apni 50-50 Lifeline Use Karne ka Faisla Kiya Hai.\n\n",
           "Iska matlab aapke 2 options bachege.\n"
           "Ek Sahi aur ek Galat\n", sep=""
          )
    MediumWrongOptions = []
    for joption in MediumOptions[j]:
        if joption != MediumAnswers[j]:
            MediumWrongOptions.append(joption)
    WrongOption1 = random.choice(MediumWrongOptions)
    OptionsAfterLifeline = [WrongOption1, MediumAnswers[j]]
    random.shuffle(OptionsAfterLifeline)
    print("Yeh Rahe Aapke Saamne 2 Bache hue Options: \n")
    print("A.", OptionsAfterLifeline[0])
    print("B.", OptionsAfterLifeline[1])

    while True:
        PlayerAnswerAfter_50_50 = str(input("\nChoose The Correct Option: ")).strip().lower()
        letter_to_option = { 'a': OptionsAfterLifeline[0].lower(),
                            'b': OptionsAfterLifeline[1].lower(),
                            }
        
        if not PlayerAnswerAfter_50_50:  # Handles empty input
                    print("Invalid Input. Please enter a valid option.")
                    continue
        
        # Quit Option

        if PlayerAnswerAfter_50_50.strip().lower() == "quit":
            if Question_Number >= 2:
                print("\nAapne Decide kiya hai ki yahin par Game ko Quit karenge.\nYeh bhi ek samajhdaar faisla hai.\nAap ghar jaa rahe hain le kar apne Jeete huye Paise.\n",sep="")
                print("TOTAL PRIZE MONEY ₹", PrizeMoneyString[Question_Number - 2], sep="")
                print_cheque(full_name=full_name, Question_Number=Question_Number)
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()
            else: 
                print("Yeh Pehla sawaal tha, aur aapne Quit karne ka chunav kiya. \nAfsos, is daur mein aap koi dhanrashi le kar nahi jaa rahe.\n")
                print("TOTAL PRIZE MONEY ₹0")
                print_cheque(full_name=full_name, Question_Number=Question_Number)
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()

        Medium_50_50_WrongOptions = []
        for joption in OptionsAfterLifeline:
            if joption != MediumAnswers[j]:
                Medium_50_50_WrongOptions.append(joption)
        
        Medium_50_50_WrongOptions = [o.strip().lower() for o in Medium_50_50_WrongOptions]

        First_Letter_After_50_50 = PlayerAnswerAfter_50_50[0]
        First_Letter_After_50_50_Plus_Dot = PlayerAnswerAfter_50_50[0] + "."
        First_Letter_After_50_50_Plus_ClosingBracket = PlayerAnswerAfter_50_50[0] + ")"

        if First_Letter_After_50_50 == PlayerAnswerAfter_50_50: # If user entered only option letter.
            attempt_text = letter_to_option.get(First_Letter_After_50_50, PlayerAnswerAfter_50_50)
        elif First_Letter_After_50_50_Plus_Dot == PlayerAnswerAfter_50_50 or First_Letter_After_50_50_Plus_ClosingBracket == PlayerAnswerAfter_50_50: # If user entered only option letter with dot or closing bracket.
            attempt_text = letter_to_option.get(First_Letter_After_50_50, PlayerAnswerAfter_50_50)
        elif MediumAnswers[j].strip().lower() in PlayerAnswerAfter_50_50 and Medium_50_50_WrongOptions[0] not in PlayerAnswerAfter_50_50: # If user entered the full answer text.  
            attempt_text = MediumAnswers[j].strip().lower()
        else:
            attempt_text = PlayerAnswerAfter_50_50

        if attempt_text.strip() == MediumAnswers[j].lower().strip():
            print("\nSahi Jawaab!\n","\nAap Jeet Chuke Hai ₹", PrizeMoneyString[Question_Number-1],sep = "")
            return
        elif attempt_text.lower().strip() in Medium_50_50_WrongOptions:
            print("\nCorrect Answer:", MediumAnswers[j])
            print("\nGalat Jawaab!\n", "Durbhagyavarsh iss KBC ke khel mein aapka Safar yahi khatam hota hai.", "\nAapke saath khel kar hame bahut anand mila.", "\n\nUnfortunately ab aapko sirf stage 1 mein jiti gayi prize money ke saath jana padega.", "\nUmmed hai ki aapse phir mulakat hogi.", "\n\nTOTAL PRIZE MONEY ₹10,000", sep = "" )
            print_cheque(full_name=full_name, Question_Number=5)
            print("Press Any Key to Exit ")
            msvcrt.getch()
            sys.exit()
        else:
            print("Invalid Input\n")
def Medium_Lifeline_DoubleDip(j, Question_Number, ExactOptions):
    print("\nToh Aapne Apni Double Dip Lifeline Use Karne ka Faisla Kiya Hai.\n\n",
          "Iska matlab aapke 2 attempts honge iss sawaal ke liye.\n", sep=""
         )
    while True:
        Medium_Attempt1 = str(input("Choose The Correct Option (Attempt 1): ")).strip().lower()
        Medium_Attempt2 = str(input("Choose The Correct Option (Attempt 2): ")).strip().lower()
        
        # Map letters to full options
        letter_to_option = {
            'a': ExactOptions[0].lower().strip(),
            'b': ExactOptions[1].lower().strip(),
            'c': ExactOptions[2].lower().strip(),
            'd': ExactOptions[3].lower().strip()
        }

        # Handle empty input
        if not Medium_Attempt1:
            print("Invalid Input. Please enter a valid option.")
            continue
        if not Medium_Attempt2:
            print("Invalid Input. Please enter a valid option.")
            continue

        # Collect wrong options for comparison
        MediumWrongOptions = []
        for joption in MediumOptions[j]:
            if joption != MediumAnswers[j]:
                MediumWrongOptions.append(joption)
        MediumWrongOptions = [o.strip().lower() for o in MediumWrongOptions]

        # Extract first letters and variants
        First_Letter_Attempt1 = Medium_Attempt1[0]
        First_Letter_Attempt1_Plus_Dot = Medium_Attempt1[0] + "."
        First_Letter_Attempt1_Plus_ClosingBracket = Medium_Attempt1[0] + ")"

        First_Letter_Attempt2 = Medium_Attempt2[0]
        First_Letter_Attempt2_Plus_Dot = Medium_Attempt2[0] + "."
        First_Letter_Attempt2_Plus_ClosingBracket = Medium_Attempt2[0] + ")"

        # Parse Attempt 1
        if First_Letter_Attempt1 == Medium_Attempt1:
            attempt1_text = letter_to_option.get(First_Letter_Attempt1, Medium_Attempt1)
        elif First_Letter_Attempt1_Plus_Dot == Medium_Attempt1 or First_Letter_Attempt1_Plus_ClosingBracket == Medium_Attempt1:
            attempt1_text = letter_to_option.get(First_Letter_Attempt1, Medium_Attempt1)
        elif MediumAnswers[j].strip().lower() in Medium_Attempt1 and all(w not in Medium_Attempt1 for w in MediumWrongOptions):
            attempt1_text = MediumAnswers[j].strip().lower()
        else:
            attempt1_text = Medium_Attempt1

        # Parse Attempt 2
        if First_Letter_Attempt2 == Medium_Attempt2:
            attempt2_text = letter_to_option.get(First_Letter_Attempt2, Medium_Attempt2)
        elif First_Letter_Attempt2_Plus_Dot == Medium_Attempt2 or First_Letter_Attempt2_Plus_ClosingBracket == Medium_Attempt2:
            attempt2_text = letter_to_option.get(First_Letter_Attempt2, Medium_Attempt2)
        elif MediumAnswers[j].strip().lower() in Medium_Attempt2 and all(w not in Medium_Attempt2 for w in MediumWrongOptions):
            attempt2_text = MediumAnswers[j].strip().lower()
        else:
            attempt2_text = Medium_Attempt2

        # Check answers
        if attempt1_text.strip().lower() == MediumAnswers[j].strip().lower() or attempt2_text.strip().lower() == MediumAnswers[j].strip().lower():
            print("\nCorrect Answer:", MediumAnswers[j])
            print("\nSahi Jawaab!\n","\nAap Jeet Chuke Hai ₹", PrizeMoneyString[Question_Number-1], sep="")
            return
        elif attempt1_text.lower().strip() in MediumWrongOptions and attempt2_text.lower().strip() in MediumWrongOptions:
            print("\nCorrect Answer:", MediumAnswers[j])
            print("\nGalat Jawaab!\n", "Durbhagyavarsh iss KBC ke khel mein aapka Safar yahi khatam hota hai.",
                  "\nAapke saath khel kar hame bahut anand mila.",
                  "\n\nUnfortunately ab aapko sirf stage 1 mein jiti gayi prize money ke saath jana padega.",
                  "\nUmmed hai ki aapse phir mulakat hogi.",
                  "\n\nTOTAL PRIZE MONEY ₹10,000", sep="")
            print_cheque(full_name=full_name, Question_Number=5)
            print("Press Any Key to Exit ")
            msvcrt.getch()
            sys.exit()
        else:
            print("Invalid Input\n")
def Ask_MediumQuestion(Question_Number): 
        AvailableMediumIndices = [junique for junique in range(0,len(MediumQuestions)) if junique not in UsedMediumIndices]
        j = random.choice(AvailableMediumIndices)
        UsedMediumIndices.append(j)

        while True:
            print(x,QuestionNumber[Question_Number-1], "\nFor a Prize of ₹",PrizeMoneyString[Question_Number-1] ,"\n\n", MediumQuestions[j], "\n",sep="")
            ExactOptions = MediumOptions[j].copy()
            
            random.shuffle(ExactOptions) #Now Options are shuffeled. Wherever you write something like ExactOptions[0] after this. This means the shuffled ExactOptions and not the Original. 
            print(Options[0], ExactOptions[0])
            print(Options[1], ExactOptions[1])
            print(Options[2], ExactOptions[2])
            print(Options[3], ExactOptions[3])

            print("\nNote: Type 'Lifeline' to use a Lifeline. \nType 'Quit' to Quit the Game and take Home your Winnings.")
            
            PlayerAnswer = str(input("\nChoose The Correct Option: ")).strip().lower()
            letter_to_option = { 'a': ExactOptions[0].lower(),
                                'b': ExactOptions[1].lower(),
                                'c': ExactOptions[2].lower(),
                                'd': ExactOptions[3].lower() }
            
            if not PlayerAnswer:  # Handles empty input
                print("Invalid Input. Please enter a valid option.")
                continue
            
            # Master Key Option
            
            if PlayerAnswer.strip().lower() == MasterKey.strip().lower():
                print("\nCorrect Answer:", MediumAnswers[j])
                print("\nMASTER KEY ACTIVATED\nSKIPPING THIS QUESTION\n")
                return
            
            # Quit Option
            
            if PlayerAnswer.strip().lower() == "quit":
                if Question_Number >= 2:
                    print("\nAapne Decide kiya hai ki yahin par Game ko Quit karenge.\nYeh bhi ek samajhdaar faisla hai.\nAap ghar jaa rahe hain le kar apne Jeete huye Paise.\n",sep="")
                    print("TOTAL PRIZE MONEY ₹", PrizeMoneyString[Question_Number - 2], sep="")
                    print_cheque(full_name=full_name, Question_Number=Question_Number)
                    print("Press Any Key to Exit ")
                    msvcrt.getch()
                    sys.exit()
                else: 
                    print("Yeh Pehla sawaal tha, aur aapne Quit karne ka chunav kiya. \nAfsos, is daur mein aap koi dhanrashi le kar nahi jaa rahe.\n")
                    print("TOTAL PRIZE MONEY ₹0")
                    print_cheque(full_name=full_name, Question_Number=Question_Number)
                    print("Press Any Key to Exit ")
                    msvcrt.getch()
                    sys.exit()

            # Lifelines

            def Medium_Lifeline_Unavailable():
                while True:
                    print("\nAapke Paas koi bhi bachi hui Lifeline nahi hai.\n")
                    PlayerAnswer = str(input("Choose The Correct Option: ")).strip().lower()
                    if PlayerAnswer:
                        return PlayerAnswer
                    print("Invalid Input. Please enter a valid option.")
            
            if "lifeline" in PlayerAnswer and len(AvailableLifelines) > 0:
                AskMediumLifeline(AvailableLifelines, UsedLifelines, j , Question_Number, ExactOptions)
                return
            elif "lifeline" in PlayerAnswer and len(AvailableLifelines) == 0:
                PlayerAnswer = Medium_Lifeline_Unavailable()
            
            # Checking Answer

            MediumWrongOptions = []
            for joption in MediumOptions[j]:
                if joption != MediumAnswers[j]:
                    MediumWrongOptions.append(joption) # This adds all the wrong options into a list called MediumWrongOptions.
            
            MediumWrongOptions = [o.strip().lower() for o in MediumWrongOptions] # This strips and lowers all the wrong options in the MediumWrongOptions list.
            
            First_Letter = PlayerAnswer[0]
            First_Letter_Plus_Dot = First_Letter + "."
            First_Letter_Plus_ClosingBracket = First_Letter + ")"

            if First_Letter == PlayerAnswer: # If user inputs only one letter.
                answer_text = letter_to_option.get(First_Letter, PlayerAnswer)
            elif First_Letter_Plus_Dot == PlayerAnswer or First_Letter_Plus_ClosingBracket == PlayerAnswer: # If user inputs letter with dot or closing bracket.
                answer_text = letter_to_option.get(First_Letter, PlayerAnswer)
            elif MediumAnswers[j].lower().strip() in PlayerAnswer and str(MediumWrongOptions[0]).lower().strip() not in PlayerAnswer and str(MediumWrongOptions[1]).lower().strip() not in PlayerAnswer and str(MediumWrongOptions[2]).lower().strip() not in PlayerAnswer: # If user inputs the correct option text but not the wrong option text.
                answer_text = MediumAnswers[j].lower().strip()
            else:
                answer_text = PlayerAnswer
            
            if answer_text.lower().strip() == MediumAnswers[j].lower().strip():
                print("\nSahi Jawaab!\n","\nAap Jeet Chuke Hai ₹", PrizeMoneyString[Question_Number-1],sep = "")
                return
            elif answer_text.lower().strip() in MediumWrongOptions:
                print("\nCorrect Answer:", MediumAnswers[j])
                print("\nGalat Jawaab!\n", "Durbhagyavarsh iss KBC ke khel mein aapka Safar yahi khatam hota hai.", "\nAapke saath khel kar hame bahut anand mila.", "\n\nUnfortunately ab aapko sirf stage 1 mein jiti gayi prize money ke saath jana padega.", "\nUmmed hai ki aapse phir mulakat hogi.", "\n\nTOTAL PRIZE MONEY ₹10,000", sep = "" )
                print_cheque(full_name=full_name, Question_Number=5)
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()
            else: 
                print("Invalid Input\n")
      
def AskHardLifeline(AvailableLifelines, UsedLifelines, k, Question_Number, ExactOptions):
    
    while True: 
        print("\nAap iss sawaal ke liye ek Lifeline ka upyog karna chahte hain.\nAapke paas abhi tak yeh lifelines bachi hain:\n")
        for Lifeline in AvailableLifelines:
            print(Lifeline)
        ChosenLifeline = str(input("\nKaunsi Lifeline ka upyog karna chahenge?: ")).strip().lower()

        if ChosenLifeline == "50-50" and "50-50" in AvailableLifelines:
            try:
                AvailableLifelines.remove("50-50")
                UsedLifelines.append("50-50")
            except:
                pass
            Hard_Lifeline_50_50(k, Question_Number)
            return

        elif ChosenLifeline == "switch the question" and "Switch the Question" in AvailableLifelines:
            try:
                AvailableLifelines.remove("Switch the Question")
                UsedLifelines.append("Switch the Question")
            except:
                pass
            print("\nAb Aapke Computer Screen Par Ek Naya Sawaal Aayega.\nToh Yeh Raha Aapka Naya Sawaal:\n")
            Ask_HardQuestion(Question_Number)
            return

        elif ChosenLifeline == "double dip" and "Double Dip" in AvailableLifelines:
            try:
                AvailableLifelines.remove("Double Dip")
                UsedLifelines.append("Double Dip")
            except:
                pass
            Hard_Lifeline_DoubleDip(k, Question_Number, ExactOptions)
            return

        elif ChosenLifeline == "power paplu" and "Power Paplu" in AvailableLifelines:
            if len(UsedLifelines) == 0:
                print("\nAapne abhi tak koi lifeline use nahi ki hai.\nIsliye aap Power Paplu Lifeline ka upyog nahi kar sakte.\n")
                AskHardLifeline(AvailableLifelines, UsedLifelines, k, Question_Number, ExactOptions)
                return
            try:
                AvailableLifelines.remove("Power Paplu")
                UsedLifelines.append("Power Paplu")
            except:
                pass

            print("\n Aapne Power Paplu Lifeline ka Upyog kiya hai.\nAb aap apni kisi purani lifeline ko Dobara Jeevit kar sakte hain.\nYeh Rahi Aapki use kari ja chuki Lifelines:\n")
            for Lifeline in UsedLifelines:
                if Lifeline != "Power Paplu":
                    print(Lifeline)
            RevivingLifeline = str(input("\nKaunsi Lifeline ko Jeevit karna chahenge?: ")).strip().lower()
            if RevivingLifeline == "50-50" and "50-50" in UsedLifelines:
                AvailableLifelines.append("50-50")
                continue
            elif RevivingLifeline == "switch the question" and "Switch the Question" in UsedLifelines:
                AvailableLifelines.append("Switch the Question")
                continue
            elif RevivingLifeline == "double dip" and "Double Dip" in UsedLifelines:
                AvailableLifelines.append("Double Dip")
                continue
            elif RevivingLifeline == "power paplu":
                print("\nAap Power Paplu Lifeline ko Jeevit nahi kar sakte.\n")
                try:
                    UsedLifelines.remove("Power Paplu")
                    AvailableLifelines.append("Power Paplu")
                except:
                    pass
                continue
            else:
                print("\nAapne galat Lifeline ka naam likha hai.\n")
                try: 
                    UsedLifelines.remove("Power Paplu")
                    AvailableLifelines.append("Power Paplu")
                except:
                    pass
                continue
        else:
            print("\nAapne galat Lifeline ka naam likha hai.\n")
            continue
def Hard_Lifeline_50_50(k, Question_Number):
    print("\nToh Aapne Apni 50-50 Lifeline Use Karne ka Faisla Kiya Hai.\n\n",
          "Iska matlab aapke 2 options bachege.\n"
          "Ek Sahi aur ek Galat\n", sep=""
         )

    # Collect wrong options
    HardWrongOptions = []
    for koption in HardOptions[k]:
        if koption != HardAnswers[k]:
            HardWrongOptions.append(koption)

    # Randomly remove one wrong option and shuffle remaining
    WrongOption1 = random.choice(HardWrongOptions)
    OptionsAfterLifeline = [WrongOption1, HardAnswers[k]]
    random.shuffle(OptionsAfterLifeline)

    # Display remaining options
    print("Yeh Rahe Aapke Saamne 2 Bache hue Options: \n")
    print("A.", OptionsAfterLifeline[0])
    print("B.", OptionsAfterLifeline[1])

    while True:
        PlayerAnswerAfter_50_50 = str(input("\nChoose The Correct Option: ")).strip().lower()
        letter_to_option = {'a': OptionsAfterLifeline[0].lower(),
                            'b': OptionsAfterLifeline[1].lower()}

        # Handle empty input
        if not PlayerAnswerAfter_50_50:
            print("Invalid Input. Please enter a valid option.")
            continue

        # Quit option
        if PlayerAnswerAfter_50_50.strip().lower() == "quit":
            if Question_Number >= 2:
                print("\nAapne Decide kiya hai ki yahin par Game ko Quit karenge.\nYeh bhi ek samajhdaar faisla hai.\nAap ghar jaa rahe hain le kar apne Jeete huye Paise.\n", sep="")
                print("TOTAL PRIZE MONEY ₹", PrizeMoneyString[Question_Number - 2], sep="")
                print_cheque(full_name=full_name, Question_Number=Question_Number)
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()
            else:
                print("Yeh Pehla sawaal tha, aur aapne Quit karne ka chunav kiya. \nAfsos, is daur mein aap koi dhanrashi le kar nahi jaa rahe.\n")
                print("TOTAL PRIZE MONEY ₹0")
                print_cheque(full_name=full_name, Question_Number=Question_Number)
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()

        # Map input letter to option text or detect full answer
        Hard_50_50_WrongOptions = [o.strip().lower() for o in OptionsAfterLifeline if o != HardAnswers[k]]

        First_Letter_After_50_50 = PlayerAnswerAfter_50_50[0]
        First_Letter_After_50_50_Plus_Dot = PlayerAnswerAfter_50_50[0] + "."
        First_Letter_After_50_50_Plus_ClosingBracket = PlayerAnswerAfter_50_50[0] + ")"

        if First_Letter_After_50_50 == PlayerAnswerAfter_50_50:
            attempt_text = letter_to_option.get(First_Letter_After_50_50, PlayerAnswerAfter_50_50)
        elif First_Letter_After_50_50_Plus_Dot == PlayerAnswerAfter_50_50 or First_Letter_After_50_50_Plus_ClosingBracket == PlayerAnswerAfter_50_50:
            attempt_text = letter_to_option.get(First_Letter_After_50_50, PlayerAnswerAfter_50_50)
        elif HardAnswers[k].strip().lower() in PlayerAnswerAfter_50_50 and Hard_50_50_WrongOptions[0] not in PlayerAnswerAfter_50_50:
            attempt_text = HardAnswers[k].strip().lower()
        else:
            attempt_text = PlayerAnswerAfter_50_50

        # Check correctness
        if attempt_text.strip() == HardAnswers[k].lower().strip():
            print("\nSahi Jawaab!\n","\nAap Jeet Chuke Hai ₹", PrizeMoneyString[Question_Number-1], sep="")
            return
        elif attempt_text.lower().strip() in Hard_50_50_WrongOptions:
            print("\nCorrect Answer:", HardAnswers[k])
            print("\nGalat Jawaab!\n", 
                  "Durbhagyavarsh iss KBC ke khel mein aapka Safar yahi khatam hota hai.", 
                  "\nAapke saath khel kar hame bahut anand mila.", 
                  "\n\nUnfortunately ab aapko sirf stage 2 mein jiti gayi\nprize money ke saath jana padega.", 
                  "\n\nUmmed hai ki aapse phir mulakat hogi.", 
                  "\n\nTOTAL PRIZE MONEY ₹3,20,000", sep="")
            print_cheque(full_name=full_name, Question_Number=10)
            print("Press Any Key to Exit ")
            msvcrt.getch()
            sys.exit()
        else:
            print("Invalid Input\n")
def Hard_Lifeline_DoubleDip(k, Question_Number, ExactOptions):
    print("\nToh Aapne Apni Double Dip Lifeline Use Karne ka Faisla Kiya Hai.\n\n",
          "Iska matlab aapke 2 attempts honge iss sawaal ke liye.\n", sep=""
         )
    while True:
        Hard_Attempt1 = str(input("Choose The Correct Option (Attempt 1): ")).strip().lower()
        Hard_Attempt2 = str(input("Choose The Correct Option (Attempt 2): ")).strip().lower()
        
        # Map letters to full options
        letter_to_option = {
            'a': ExactOptions[0].lower().strip(),
            'b': ExactOptions[1].lower().strip(),
            'c': ExactOptions[2].lower().strip(),
            'd': ExactOptions[3].lower().strip()
        }

        # Handle empty input
        if not Hard_Attempt1:
            print("Invalid Input. Please enter a valid option.")
            continue
        if not Hard_Attempt2:
            print("Invalid Input. Please enter a valid option.")
            continue

        # Collect wrong options for comparison
        HardWrongOptions = []
        for koption in HardOptions[k]:
            if koption != HardAnswers[k]:
                HardWrongOptions.append(koption)
        HardWrongOptions = [o.strip().lower() for o in HardWrongOptions]

        # Extract first letters and variants
        First_Letter_Attempt1 = Hard_Attempt1[0]
        First_Letter_Attempt1_Plus_Dot = Hard_Attempt1[0] + "."
        First_Letter_Attempt1_Plus_ClosingBracket = Hard_Attempt1[0] + ")"

        First_Letter_Attempt2 = Hard_Attempt2[0]
        First_Letter_Attempt2_Plus_Dot = Hard_Attempt2[0] + "."
        First_Letter_Attempt2_Plus_ClosingBracket = Hard_Attempt2[0] + ")"

        # Parse Attempt 1
        if First_Letter_Attempt1 == Hard_Attempt1:
            attempt1_text = letter_to_option.get(First_Letter_Attempt1, Hard_Attempt1)
        elif First_Letter_Attempt1_Plus_Dot == Hard_Attempt1 or First_Letter_Attempt1_Plus_ClosingBracket == Hard_Attempt1:
            attempt1_text = letter_to_option.get(First_Letter_Attempt1, Hard_Attempt1)
        elif HardAnswers[k].strip().lower() in Hard_Attempt1 and all(w not in Hard_Attempt1 for w in HardWrongOptions):
            attempt1_text = HardAnswers[k].strip().lower()
        else:
            attempt1_text = Hard_Attempt1

        # Parse Attempt 2
        if First_Letter_Attempt2 == Hard_Attempt2:
            attempt2_text = letter_to_option.get(First_Letter_Attempt2, Hard_Attempt2)
        elif First_Letter_Attempt2_Plus_Dot == Hard_Attempt2 or First_Letter_Attempt2_Plus_ClosingBracket == Hard_Attempt2:
            attempt2_text = letter_to_option.get(First_Letter_Attempt2, Hard_Attempt2)
        elif HardAnswers[k].strip().lower() in Hard_Attempt2 and all(w not in Hard_Attempt2 for w in HardWrongOptions):
            attempt2_text = HardAnswers[k].strip().lower()
        else:
            attempt2_text = Hard_Attempt2

        # Check answers
        if attempt1_text.strip().lower() == HardAnswers[k].strip().lower() or attempt2_text.strip().lower() == HardAnswers[k].strip().lower():
            print("\nCorrect Answer:", HardAnswers[k])
            print("\nSahi Jawaab!\n","\nAap Jeet Chuke Hai ₹", PrizeMoneyString[Question_Number-1], sep="")
            return
        elif attempt1_text.lower().strip() in HardWrongOptions and attempt2_text.lower().strip() in HardWrongOptions:
            print("\nCorrect Answer:", HardAnswers[k])
            print("\nGalat Jawaab!\n", "Durbhagyavarsh iss KBC ke khel mein aapka Safar yahi khatam hota hai.",
                  "\nAapke saath khel kar hame bahut anand mila.",
                  "\n\nUnfortunately ab aapko sirf stage 2 mein jiti gayi\nprize money ke saath jana padega.",
                  "\n\nUmmed hai ki aapse phir mulakat hogi.",
                  "\n\nTOTAL PRIZE MONEY ₹3,20,000", sep="")
            print_cheque(full_name=full_name, Question_Number=10)
            print("Press Any Key to Exit ")
            msvcrt.getch()
            sys.exit()
        else:
            print("Invalid Input\n")
def Ask_HardQuestion(Question_Number):
    AvailableHardIndices = [kunique for kunique in range(0,len(HardQuestions)) if kunique not in UsedHardIndices]
    k = random.choice(AvailableHardIndices)
    UsedHardIndices.append(k)

    while True: 
        print(x,QuestionNumber[Question_Number-1], "\nFor a Prize of ₹",PrizeMoneyString[Question_Number-1] ,"\n\n", HardQuestions[k], "\n",sep="")
        ExactOptions = HardOptions[k].copy()

        random.shuffle(ExactOptions) #Now Options are shuffeled. Wherever you write something like ExactOptions[0] after this. This means the shuffled ExactOptions and not the Original. 
        print(Options[0], ExactOptions[0])
        print(Options[1], ExactOptions[1])
        print(Options[2], ExactOptions[2])
        print(Options[3], ExactOptions[3])

        print("\nNote: Type 'Lifeline' to use a Lifeline. \nType 'Quit' to Quit the Game and take Home your Winnings.")

        PlayerAnswer = str(input("\nChoose The Correct Option: ")).strip().lower()
        letter_to_option = { 'a': ExactOptions[0].lower(),
                            'b': ExactOptions[1].lower(),
                            'c': ExactOptions[2].lower(),
                            'd': ExactOptions[3].lower() }
        
        if not PlayerAnswer:  # Handles empty input
            print("Invalid Input. Please enter a valid option.")
            continue
        
        # Master Key Option

        if PlayerAnswer.strip().lower() == MasterKey.strip().lower():
            print("\nCorrect Answer:", HardAnswers[k])
            print("\nMASTER KEY ACTIVATED\nSKIPPING THIS QUESTION\n")
            return
        
        # Quit Option

        if PlayerAnswer.strip().lower() == "quit":
            if Question_Number >= 2:
                print("\nAapne Decide kiya hai ki yahin par Game ko Quit karenge.\nYeh bhi ek samajhdaar faisla hai.\nAap ghar jaa rahe hain le kar apne Jeete huye Paise.\n",sep="")
                print("TOTAL PRIZE MONEY ₹", PrizeMoneyString[Question_Number - 2], sep="")
                print_cheque(full_name=full_name, Question_Number=Question_Number)
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()
            else: 
                print("Yeh Pehla sawaal tha, aur aapne Quit karne ka chunav kiya. \nAfsos, is daur mein aap koi dhanrashi le kar nahi jaa rahe.\n")
                print("TOTAL PRIZE MONEY ₹0")
                print_cheque(full_name=full_name, Question_Number=Question_Number)
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()
        
        # Lifelines

        def Hard_Lifeline_Unavailable():
                while True:
                    print("\nAapke Paas koi bhi bachi hui Lifeline nahi hai.\n")
                    PlayerAnswer = str(input("Choose The Correct Option: ")).strip().lower()
                    if PlayerAnswer:
                        return PlayerAnswer
                    print("Invalid Input. Please enter a valid option.")
        
        if "lifeline" in PlayerAnswer and len(AvailableLifelines) > 0:
            AskHardLifeline(AvailableLifelines, UsedLifelines, k , Question_Number, ExactOptions)
            return
        elif "lifeline" in PlayerAnswer and len(AvailableLifelines) == 0:
            PlayerAnswer = Hard_Lifeline_Unavailable()
        
        # Checking Answer

        HardWrongOptions = []
        for koption in HardOptions[k]:
            if koption != HardAnswers[k]:
                HardWrongOptions.append(koption) # This adds all the wrong options into a list called HardWrongOptions.
        
        HardWrongOptions = [o.strip().lower() for o in HardWrongOptions]
        # This strips and lowers all the wrong options in the HardWrongOptions list.
        
        First_Letter = PlayerAnswer[0]
        First_Letter_Plus_Dot = First_Letter + "."  
        First_Letter_Plus_ClosingBracket = First_Letter + ")"

        if First_Letter == PlayerAnswer: # If user inputs only one letter.
            answer_text = letter_to_option.get(First_Letter, PlayerAnswer)
        elif First_Letter_Plus_Dot == PlayerAnswer or First_Letter_Plus_ClosingBracket == PlayerAnswer: # If user inputs letter with dot or closing bracket.
            answer_text = letter_to_option.get(First_Letter, PlayerAnswer)
        elif HardAnswers[k].lower().strip() in PlayerAnswer and str(HardWrongOptions[0]).lower().strip() not in PlayerAnswer and str(HardWrongOptions[1]).lower().strip() not in PlayerAnswer and str(HardWrongOptions[2]).lower().strip() not in PlayerAnswer: # If user inputs the correct option text but not the wrong option text.
            answer_text = HardAnswers[k].lower().strip()
        else:
            answer_text = PlayerAnswer
        
        if answer_text.lower().strip() == HardAnswers[k].lower().strip():
            print("\nSahi Jawaab!\n","\nAap Jeet Chuke Hai ₹", PrizeMoneyString[Question_Number-1],sep = "")
            return
        elif answer_text.lower().strip() in HardWrongOptions:
            print("\nCorrect Answer:", HardAnswers[k])
            print("\nGalat Jawaab!\n", "Durbhagyavarsh iss KBC ke khel mein aapka Safar yahi khatam hota hai.", "\nAapke saath khel kar hame bahut anand mila.", "\n\nUnfortunately ab aapko sirf stage 2 mein jiti gayi\nprize money ke saath jana padega.", "\n\nUmmed hai ki aapse phir mulakat hogi.", "\n\nTOTAL PRIZE MONEY ₹3,20,000", sep = "" )
            print_cheque(full_name=full_name, Question_Number=10)
            print("Press Any Key to Exit ")
            msvcrt.getch()
            sys.exit()
        else:
            print("Invalid Input\n")

def AskVeryHardLifeline(AvailableLifelines, UsedLifelines, l, Question_Number, ExactOptions):

    while True: 
        print("\nAap iss sawaal ke liye ek Lifeline ka upyog karna chahte hain.\nAapke paas abhi tak yeh lifelines bachi hain:\n")
        for Lifeline in AvailableLifelines:
            print(Lifeline)
        ChosenLifeline = str(input("\nKaunsi Lifeline ka upyog karna chahenge?: ")).strip().lower()

        if ChosenLifeline == "50-50" and "50-50" in AvailableLifelines:
            try:
                AvailableLifelines.remove("50-50")
                UsedLifelines.append("50-50")   
            except:
                pass
            VeryHard_Lifeline_50_50(l, Question_Number)
            return

        elif ChosenLifeline == "switch the question" and "Switch the Question" in AvailableLifelines:
            try:
                AvailableLifelines.remove("Switch the Question")
                UsedLifelines.append("Switch the Question")
            except:
                pass
            print("\nAb Aapke Computer Screen Par Ek Naya Sawaal Aayega.\nToh Yeh Raha Aapka Naya Sawaal:\n")
            Ask_VeryHardQuestion(Question_Number)
            return

        elif ChosenLifeline == "double dip" and "Double Dip" in AvailableLifelines:
            try:
                AvailableLifelines.remove("Double Dip")
                UsedLifelines.append("Double Dip")
            except:
                pass
            VeryHard_Lifeline_DoubleDip(l, Question_Number, ExactOptions)
            return

        elif ChosenLifeline == "power paplu" and "Power Paplu" in AvailableLifelines:
            if len(UsedLifelines) == 0:
                print("\nAapne abhi tak koi lifeline use nahi ki hai.\nIsliye aap Power Paplu Lifeline ka upyog nahi kar sakte.\n")
                AskVeryHardLifeline(AvailableLifelines, UsedLifelines, l, Question_Number, ExactOptions)
                return
            try:
                AvailableLifelines.remove("Power Paplu")
                UsedLifelines.append("Power Paplu")
            except:
                pass
            
            print("\n Aapne Power Paplu Lifeline ka Upyog kiya hai.\nAb aap apni kisi purani lifeline ko Dobara Jeevit kar sakte hain.\nYeh Rahi Aapki use kari ja chuki Lifelines:\n")
            for Lifeline in UsedLifelines:
                if Lifeline != "Power Paplu":
                    print(Lifeline)
            RevivingLifeline = str(input("\nKaunsi Lifeline ko Jeevit karna chahenge?: ")).strip().lower()
            if RevivingLifeline == "50-50" and "50-50" in UsedLifelines:
                AvailableLifelines.append("50-50")
                continue
            elif RevivingLifeline == "switch the question" and "Switch the Question" in UsedLifelines:
                AvailableLifelines.append("Switch the Question")
                continue
            elif RevivingLifeline == "double dip" and "Double Dip" in UsedLifelines:
                AvailableLifelines.append("Double Dip")
                continue
            elif RevivingLifeline == "power paplu":
                print("\nAap Power Paplu Lifeline ko Jeevit nahi kar sakte.\n")
                try:
                    UsedLifelines.remove("Power Paplu")
                    AvailableLifelines.append("Power Paplu")
                except:
                    pass
                continue
            else:
                print("\nAapne galat Lifeline ka naam likha hai.\n")
                try: 
                    UsedLifelines.remove("Power Paplu")
                    AvailableLifelines.append("Power Paplu")
                except:
                    pass
                continue
        else:
            print("\nAapne galat Lifeline ka naam likha hai.\n")
            continue
def VeryHard_Lifeline_50_50(l, Question_Number):
    print("\nToh Aapne Apni 50-50 Lifeline Use Karne ka Faisla Kiya Hai.\n\n",
          "Iska matlab aapke 2 options bachege.\n"
          "Ek Sahi aur ek Galat\n", sep=""
         )
    
    VeryHardWrongOptions = []
    for loption in VeryHardOptions[l]:
        if loption != VeryHardAnswers[l]:
            VeryHardWrongOptions.append(loption)
    
    WrongOption1 = random.choice(VeryHardWrongOptions)
    OptionsAfterLifeline = [WrongOption1, VeryHardAnswers[l]]
    random.shuffle(OptionsAfterLifeline)
    
    print("Yeh Rahe Aapke Saamne 2 Bache hue Options: \n")
    print("A.", OptionsAfterLifeline[0])
    print("B.", OptionsAfterLifeline[1])

    while True:
        PlayerAnswerAfter_50_50 = str(input("\nChoose The Correct Option: ")).strip().lower()
        letter_to_option = { 'a': OptionsAfterLifeline[0].lower(),
                             'b': OptionsAfterLifeline[1].lower(),
                           }

        if not PlayerAnswerAfter_50_50:  # Handles empty input
            print("Invalid Input. Please enter a valid option.")
            continue

        # Quit Option
        if PlayerAnswerAfter_50_50.strip().lower() == "quit":
            if Question_Number >= 2:
                print("\nAapne Decide kiya hai ki yahin par Game ko Quit karenge.\nYeh bhi ek samajhdaar faisla hai.\nAap ghar jaa rahe hain le kar apne Jeete huye Paise.\n",sep="")
                print("TOTAL PRIZE MONEY ₹", PrizeMoneyString[Question_Number - 2], sep="")
                print_cheque(full_name=full_name, Question_Number=Question_Number)
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()
            else:
                print("Yeh Pehla sawaal tha, aur aapne Quit karne ka chunav kiya. \nAfsos, is daur mein aap koi dhanrashi le kar nahi jaa rahe.\n")
                print("TOTAL PRIZE MONEY ₹0")
                print_cheque(full_name=full_name, Question_Number=Question_Number)
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()

        VeryHard_50_50_WrongOptions = []
        for loption in OptionsAfterLifeline:
            if loption != VeryHardAnswers[l]:
                VeryHard_50_50_WrongOptions.append(loption)

        VeryHard_50_50_WrongOptions = [o.strip().lower() for o in VeryHard_50_50_WrongOptions]

        First_Letter_After_50_50 = PlayerAnswerAfter_50_50[0]
        First_Letter_After_50_50_Plus_Dot = PlayerAnswerAfter_50_50[0] + "."
        First_Letter_After_50_50_Plus_ClosingBracket = PlayerAnswerAfter_50_50[0] + ")"

        if First_Letter_After_50_50 == PlayerAnswerAfter_50_50:
            attempt_text = letter_to_option.get(First_Letter_After_50_50, PlayerAnswerAfter_50_50)
        elif First_Letter_After_50_50_Plus_Dot == PlayerAnswerAfter_50_50 or First_Letter_After_50_50_Plus_ClosingBracket == PlayerAnswerAfter_50_50:
            attempt_text = letter_to_option.get(First_Letter_After_50_50, PlayerAnswerAfter_50_50)
        elif VeryHardAnswers[l].strip().lower() in PlayerAnswerAfter_50_50 and VeryHard_50_50_WrongOptions[0] not in PlayerAnswerAfter_50_50:
            attempt_text = VeryHardAnswers[l].strip().lower()
        else:
            attempt_text = PlayerAnswerAfter_50_50

        if attempt_text.strip() == VeryHardAnswers[l].lower().strip():
            print("\nSahi Jawaab!\n","\nAap Jeet Chuke Hai ₹", PrizeMoneyString[Question_Number-1], sep = "")
            if Question_Number == len(QuestionNumber):
                print("\nJACKPOT!\n","Hamara Yeh Safar Yahi Khatam Hota Hai.\n", "\nAap hai Kaun Banega Crorepati Season 18 ke WINNER", "\n\nTOTAL PRIZE MONEY ₹7 Crore", sep="")
                print_cheque(full_name=full_name, Question_Number=Question_Number)
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()
            return
        elif attempt_text.lower().strip() in VeryHard_50_50_WrongOptions:
            print("\nCorrect Answer:", VeryHardAnswers[l])
            print("\nGalat Jawaab!\n", "Durbhagyavarsh iss KBC ke khel mein aapka Safar yahi khatam hota hai.", "\nAapke saath khel kar hame bahut anand mila.", "\n\nUnfortunately ab aapko sirf stage 2 mein jiti gayi\nprize money ke saath jana padega.", "\n\nUmmed hai ki aapse phir mulakat hogi.", "\n\nTOTAL PRIZE MONEY ₹3,20,000", sep = "" )
            print_cheque(full_name=full_name, Question_Number=10)
            print("Press Any Key to Exit ")
            msvcrt.getch()
            sys.exit()
        else:
            print("Invalid Input\n")
def VeryHard_Lifeline_DoubleDip(l, Question_Number, ExactOptions):
    print("\nToh Aapne Apni Double Dip Lifeline Use Karne ka Faisla Kiya Hai.\n\n",
          "Iska matlab aapke 2 attempts honge iss sawaal ke liye.\n", sep=""
         )
    while True:
        VeryHard_Attempt1 = str(input("Choose The Correct Option (Attempt 1): ")).strip().lower()
        VeryHard_Attempt2 = str(input("Choose The Correct Option (Attempt 2): ")).strip().lower()

        # Map letters to full options
        letter_to_option = {
            'a': ExactOptions[0].lower().strip(),
            'b': ExactOptions[1].lower().strip(),
            'c': ExactOptions[2].lower().strip(),
            'd': ExactOptions[3].lower().strip()
        }

        # Handle empty input
        if not VeryHard_Attempt1:
            print("Invalid Input. Please enter a valid option.")
            continue
        if not VeryHard_Attempt2:
            print("Invalid Input. Please enter a valid option.")
            continue

        # Collect wrong options for comparison
        VeryHardWrongOptions = []
        for loption in VeryHardOptions[l]:
            if loption != VeryHardAnswers[l]:
                VeryHardWrongOptions.append(loption)
        VeryHardWrongOptions = [o.strip().lower() for o in VeryHardWrongOptions]

        # Extract first letters and variants
        First_Letter_Attempt1 = VeryHard_Attempt1[0]
        First_Letter_Attempt1_Plus_Dot = VeryHard_Attempt1[0] + "."
        First_Letter_Attempt1_Plus_ClosingBracket = VeryHard_Attempt1[0] + ")"

        First_Letter_Attempt2 = VeryHard_Attempt2[0]
        First_Letter_Attempt2_Plus_Dot = VeryHard_Attempt2[0] + "."
        First_Letter_Attempt2_Plus_ClosingBracket = VeryHard_Attempt2[0] + ")"

        # Parse Attempt 1
        if First_Letter_Attempt1 == VeryHard_Attempt1:
            attempt1_text = letter_to_option.get(First_Letter_Attempt1, VeryHard_Attempt1)
        elif First_Letter_Attempt1_Plus_Dot == VeryHard_Attempt1 or First_Letter_Attempt1_Plus_ClosingBracket == VeryHard_Attempt1:
            attempt1_text = letter_to_option.get(First_Letter_Attempt1, VeryHard_Attempt1)
        elif VeryHardAnswers[l].strip().lower() in VeryHard_Attempt1 and all(w not in VeryHard_Attempt1 for w in VeryHardWrongOptions):
            attempt1_text = VeryHardAnswers[l].strip().lower()
        else:
            attempt1_text = VeryHard_Attempt1

        # Parse Attempt 2
        if First_Letter_Attempt2 == VeryHard_Attempt2:
            attempt2_text = letter_to_option.get(First_Letter_Attempt2, VeryHard_Attempt2)
        elif First_Letter_Attempt2_Plus_Dot == VeryHard_Attempt2 or First_Letter_Attempt2_Plus_ClosingBracket == VeryHard_Attempt2:
            attempt2_text = letter_to_option.get(First_Letter_Attempt2, VeryHard_Attempt2)
        elif VeryHardAnswers[l].strip().lower() in VeryHard_Attempt2 and all(w not in VeryHard_Attempt2 for w in VeryHardWrongOptions):
            attempt2_text = VeryHardAnswers[l].strip().lower()
        else:
            attempt2_text = VeryHard_Attempt2

        # Check answers
        if attempt1_text.strip().lower() == VeryHardAnswers[l].strip().lower() or attempt2_text.strip().lower() == VeryHardAnswers[l].strip().lower():
            print("\nCorrect Answer:", VeryHardAnswers[l])
            print("\nSahi Jawaab!\n","\nAap Jeet Chuke Hai ₹", PrizeMoneyString[Question_Number-1], sep="")
            
            if Question_Number == len(QuestionNumber):
                print("\nJACKPOT!\n","Hamara Yeh Safar Yahi Khatam Hota Hai.\n",
                      "\nAap hai Kaun Banega Crorepati Season 18 ke WINNER",
                      "\n\nTOTAL PRIZE MONEY ₹7 Crore", sep="")
                print_cheque(full_name=full_name, Question_Number=Question_Number)
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()
            return
        elif attempt1_text.lower().strip() in VeryHardWrongOptions and attempt2_text.lower().strip() in VeryHardWrongOptions:
            print("\nCorrect Answer:", VeryHardAnswers[l])
            print("\nGalat Jawaab!\n", "Durbhagyavarsh iss KBC ke khel mein aapka Safar yahi khatam hota hai.",
                  "\nAapke saath khel kar hame bahut anand mila.",
                  "\n\nUnfortunately ab aapko sirf stage 2 mein jiti gayi\nprize money ke saath jana padega.",
                  "\n\nUmmed hai ki aapse phir mulakat hogi.",
                  "\n\nTOTAL PRIZE MONEY ₹3,20,000", sep="")
            print_cheque(full_name=full_name, Question_Number=10)
            print("Press Any Key to Exit ")
            msvcrt.getch()
            sys.exit()
        else:
            print("Invalid Input\n")
def Ask_VeryHardQuestion(Question_Number):

    AvailableVeryHardIndices = [lunique for lunique in range(0,len(VeryHardQuestions)) if lunique not in UsedVeryHardIndices]
    l = random.choice(AvailableVeryHardIndices)
    UsedVeryHardIndices.append(l)

    while True:
        print(x,QuestionNumber[Question_Number-1], "\nFor a Prize of ₹",PrizeMoneyString[Question_Number-1] ,"\n\n", VeryHardQuestions[l], "\n",sep="")
        ExactOptions = VeryHardOptions[l].copy()

        random.shuffle(ExactOptions) #Now Options are shuffeled. Wherever you write something like ExactOptions[0] after this. This means the shuffled ExactOptions and not the Original. 
        print(Options[0], ExactOptions[0])
        print(Options[1], ExactOptions[1])
        print(Options[2], ExactOptions[2])
        print(Options[3], ExactOptions[3])

        print("\nNote: Type 'Lifeline' to use a Lifeline. \nType 'Quit' to Quit the Game and take Home your Winnings.")

        PlayerAnswer = str(input("\nChoose The Correct Option: ")).strip().lower()
        letter_to_option = { 'a': ExactOptions[0].lower(),
                            'b': ExactOptions[1].lower(),
                            'c': ExactOptions[2].lower(),
                            'd': ExactOptions[3].lower() }
        
        if not PlayerAnswer:  # Handles empty input
            print("Invalid Input. Please enter a valid option.")
            continue
        
        # Master Key Option

        if PlayerAnswer.strip().lower() == MasterKey.strip().lower():
            print("\nCorrect Answer:", VeryHardAnswers[l])
            print("\nMASTER KEY ACTIVATED\nSKIPPING THIS QUESTION\n")
            return
        
        # Quit Option

        if PlayerAnswer.strip().lower() == "quit":
            if Question_Number >= 2:
                print("\nAapne Decide kiya hai ki yahin par Game ko Quit karenge.\nYeh bhi ek samajhdaar faisla hai.\nAap ghar jaa rahe hain le kar apne Jeete huye Paise.\n",sep="")
                print("TOTAL PRIZE MONEY ₹", PrizeMoneyString[Question_Number - 2], sep="")
                print_cheque(full_name=full_name, Question_Number=Question_Number)
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()
            else: 
                print("Yeh Pehla sawaal tha, aur aapne Quit karne ka chunav kiya. \nAfsos, is daur mein aap koi dhanrashi le kar nahi jaa rahe.\n")
                print("TOTAL PRIZE MONEY ₹0")
                print_cheque(full_name=full_name, Question_Number=Question_Number)
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()
        
        # Lifelines

        def VeryHard_Lifeline_Unavailable():
                while True:
                    print("\nAapke Paas koi bhi bachi hui Lifeline nahi hai.\n")
                    PlayerAnswer = str(input("Choose The Correct Option: ")).strip().lower()
                    if PlayerAnswer:
                        return PlayerAnswer
                    print("Invalid Input. Please enter a valid option.")
        
        if "lifeline" in PlayerAnswer and len(AvailableLifelines) > 0:
            AskVeryHardLifeline(AvailableLifelines, UsedLifelines, l , Question_Number, ExactOptions)
            return
        elif "lifeline" in PlayerAnswer and len(AvailableLifelines) == 0:
            PlayerAnswer = VeryHard_Lifeline_Unavailable()
        
        # Checking Answer

        VeryHardWrongOptions = []
        for loption in VeryHardOptions[l]:
            if loption != VeryHardAnswers[l]:
                VeryHardWrongOptions.append(loption) # This adds all the wrong options into a list called VeryHardWrongOptions.
        
        VeryHardWrongOptions = [o.strip().lower() for o in VeryHardWrongOptions]
        # This strips and lowers all the wrong options in the VeryHardWrongOptions list.
        
        First_Letter = PlayerAnswer[0]
        First_Letter_Plus_Dot = First_Letter + "."  
        First_Letter_Plus_ClosingBracket = First_Letter + ")"

        if First_Letter == PlayerAnswer: # If user inputs only one letter.
            answer_text = letter_to_option.get(First_Letter, PlayerAnswer)
        elif First_Letter_Plus_Dot == PlayerAnswer or First_Letter_Plus_ClosingBracket == PlayerAnswer: # If user inputs letter with dot or closing bracket.
            answer_text = letter_to_option.get(First_Letter, PlayerAnswer)
        elif VeryHardAnswers[l].lower().strip() in PlayerAnswer and str(VeryHardWrongOptions[0]).lower().strip() not in PlayerAnswer and str(VeryHardWrongOptions[1]).lower().strip() not in PlayerAnswer and str(VeryHardWrongOptions[2]).lower().strip() not in PlayerAnswer: # If user inputs the correct option text but not the wrong option text.
            answer_text = VeryHardAnswers[l].lower().strip()
        else:
            answer_text = PlayerAnswer
        
        if answer_text.lower().strip() == VeryHardAnswers[l].lower().strip():
            print("\nSahi Jawaab!\n","\nAap Jeet Chuke Hai ₹", PrizeMoneyString[Question_Number-1],sep = "")
            if Question_Number == len(QuestionNumber):
                print("\nJACKPOT!\n","Hamara Yeh Safar Yahi Khatam Hota Hai.\n", "\nAap hai Kaun Banega Crorepati Season 18 ke WINNER", "\n\nTOTAL PRIZE MONEY ₹7 Crore", sep="")
                print_cheque(full_name=full_name, Question_Number=Question_Number)
                print("Press Any Key to Exit ")
                msvcrt.getch()
                sys.exit()
            return
        elif answer_text.lower().strip() in VeryHardWrongOptions:
            print("\nCorrect Answer:", VeryHardAnswers[l])
            print("\nGalat Jawaab!\n", "Durbhagyavarsh iss KBC ke khel mein aapka Safar yahi khatam hota hai.", "\nAapke saath khel kar hame bahut anand mila.", "\n\nUnfortunately ab aapko sirf stage 2 mein jiti gayi\nprize money ke saath jana padega.", "\n\nUmmed hai ki aapse phir mulakat hogi.", "\n\nTOTAL PRIZE MONEY ₹3,20,000", sep = "" )
            print_cheque(full_name=full_name, Question_Number=10)
            print("Press Any Key to Exit ")
            msvcrt.getch()
            sys.exit()
        else:
            print("Invalid Input\n")

#                                                         MAIN GAME CODE 

Stage1 = "\"STAGE 1\""
Stage2 = "\"STAGE 2\""
Stage3 = "\"STAGE 3\""
print("")
print(Stage1.center(70))
print("")
Ask_EasyQuestion(1)
Ask_EasyQuestion(2)
Ask_EasyQuestion(3)
Ask_EasyQuestion(4)
Ask_EasyQuestion(5)
print("")
print(Stage2.center(70))
print("")
Ask_MediumQuestion(6)
Ask_MediumQuestion(7)
Ask_MediumQuestion(8)
Ask_MediumQuestion(9)
Ask_MediumQuestion(10)
print("")
print(Stage3.center(70))
print("")
Ask_HardQuestion(11)
Ask_HardQuestion(12)
Ask_HardQuestion(13)
Ask_HardQuestion(14)
Ask_HardQuestion(15)
Ask_VeryHardQuestion(16)