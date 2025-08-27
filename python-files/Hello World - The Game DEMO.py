import random
game = 1
taskdone = 1
score = 0
tasksorder = ["train","feed","vet"]
tasks = ["rest","pet","wash","play","love","danger"]
good = []
bad = []
evo = 0
rating = ""
rank = ""

def train(score,good,bad,tasksorder):
    input()
    print("You have a gym in your garage that could work")
    input()
    print("You could also train it for simple things like sitting, to stay and to come.")
    input()
    print("OR, you could also teach it how to bite for protection")
    find = input("What will you do? [gym, train, bite]")

    if find == "train":
        print("You teach",pet,"how to stay, come and sit on your command")
        input()
        print(pet,"is now very well behaved.")
        score = score + 2
        good.append("train")
        tasksorder.remove("train")
        
    if find == "gym":
        print("You took",pet,"to the gym and told it to exercise.")
        input()
        print(pet,"can't do anything since he doesn't have arms or legs. Just rolling on a treadmill..")
        input()
        print(pet,"hasn't learnt anything.")
        #nothing changes
        tasksorder.remove("train")
        
    if find != "train" and find != "gym" and find != "bite":
        print("That is not an option")
        train(score,good,bad,tasksorder)
    
    if find == "bite":
        print("You teach",pet,"to bite bad people.")
        input()
        if score < 0:
            print(pet,"bites you instead! He remembers what you did previously.")
            if "feed" in bad:
                print("When you fed him soggy pizza..")
            if "feed2" in bad:
                print("When you told him to eat air particles..")
            if "vet" in bad:
                print("That boring vet music..")
            if "vet2" in bad:
                print("That horrible joke..")
            input()
            print(pet,"is very badly behaved!")
            score = score - 1
            bad.append("train")
        if score >= 0:
            print(pet,"listens to you and does it perfectly on the dummy.")
            input()
            print(pet,"is now behaved!")
            score = score + 1
            good.append("train")
            
        tasksorder.remove("train")
    return score

def feed(score,good,bad,tasksorder):
    input()
    print("There is a shop around the corner but you have only 1 pound you need for your mum")
    input()
    print("You also have a quarter of a soggy pizza in your pocket")
    input()
    find = input("What will you do? [shop, pizza, nothing]")

    if find == "shop":
        print("You went to the shop and got the pet a fresh bowl of salad for",pet)
        input()
        print(pet,"loved it!")
        input()
        print("It's like the plants on Earth!")
        score = score + 1
        good.append("feed")
        tasksorder.remove("feed")
        
    if find == "pizza":
        print("You gave the soggy pizza in your pocket to",pet)
        input()
        print(pet,"spat it out! He stares at you, menacingly.")
        input()
        print(pet,"didn't like that.")
        score = score - 1
        bad.append("feed")
        #nothing changes
        tasksorder.remove("feed")
        
    if find != "shop" and find != "pizza" and find != "nothing":
        print("That is not an option")
        feed(score,good,bad,tasksorder)
    
    if find == "nothing":
        print("You told",pet,"to eat the air particles.")
        input()
        print(pet,"is disgusted!")
        score = score - 2
        bad.append("feed2")
        tasksorder.remove("feed")
    return score
        
def vet(score,good,bad,tasksorder):
    #THIS IS JUST THE FEED ONE COPY AND PASTED! EDIT IT!
    input()
    print("You and",pet,"are on your way to the vet.")
    input()
    print(pet,"seems a little bored.")
    input()
    print("You can play some music on the radio")
    input()
    print("You can also tell him a joke from your joke book.")
    input()
    find = input("What will you do? [music, joke, nothing]")

    if find == "music":
        print("You played some music on your favourite radio channel, hoping",pet,"liked it too..")
        input()
        print("The music was horrible")
        input()
        print(pet,"hated it!")
        score = score - 2
        bad.append("vet")
        tasksorder.remove("vet")
        
    if find == "joke":
        print("You told him a joke from your joke book",pet)
        input()
        print(pet,"sat there in boredem, not finding any of them amusing")
        #nothing changes
        bad.append("vet2")
        tasksorder.remove("vet")
        
    if find != "music" and find != "joke" and find != "nothing":
        print("That is not an option")
        vet(score,good,bad,tasksorder)
    
    if find == "nothing":
        print("You sat there with",pet,"in silence.")
        input()
        print("Turns out",pet,"actually pefers silence over noise")
        input()
        print("What the world really wants is peace and quiet..")
        input()
        print(pet,"loved it, suprisingly..")
        score = score + 2
        good.append("vet")
        tasksorder.remove("vet")
    return score

task = random.choice(tasks)

print("Welcome to 'Hello World'. Press enter to continue.")
input()
print("Note: Every dialogue you see, you have to press enter to continue.")
input()
print("Note: Because I can't be bothered to do genders and stuff, all orbs are boys. Tough, girls!")
input()
name = input("What is your name?").title()
print("Welcome,",name)
input()
pet = input("What is the name of your world?").title()
print("The objective of this game is to take care of",pet,"and give it all its nececcaties.")
input()
print("This game will take ~ 10 mins to beat, if you can..")
input()
print("Everything you do affects what happens in the future.")
input()
print("Everything should be in YOUR PET'S INTEREST!")
input()
print("These first 3 tasks, you can choose your options.")
input()
while game == 1:
    taskdone = 1
    if taskdone == 1:
        print("Oh no. You found a mysterious orb lying on the floor.")
        input()
        print("It has a face and it looks sad and lonely.")
        input()
        find = input("What do you want to do with it? [train, feed, vet, leave]").lower()
        if find == "train" or find == "feed" or find == "vet" and find != "leave":
            print("You name your new pet",pet,"and go home with it to",find,"it.")
            input()
        if find == "train":
            found = "trained"
            print("You decide you want to train it first.")
            score = train(score,good,bad,tasksorder)
            taskdone= taskdone + 1
            
        if find == "feed":
            found = "fed"
            print("You decide you want to feed it first.")
            score = feed(score,good,bad,tasksorder)
            taskdone= taskdone + 1
            
        if find == "vet":
            found = "vetted"
            print("You decide you want to take it to the vet first.")
            score = vet(score,good,bad,tasksorder)
            taskdone= taskdone + 1
            
        if find == "leave":
            print("You leave the orb there but an urge tells you to come back.")
            print("The orb will rememeber that..")
            score = score - 1
            input()
            print("30 mins later..")
            input()
            
        if find != "train" and find != "feed" and find != "vet" and find != "leave":
            print("That is not an option")
            input()
            print("Try again.")
            input()
            
    if taskdone == 2:
        print("You have taken",pet,"home and",found,"it")
        input()
        if score > 0:
            print(pet,"is very happy!")
            print("He evolved into",pet,"II")
            pet = pet + " " + "II"
            print(pet,"is now much bigger and stronger!")
            evo = 2
            
        if score < 0:
            print(pet,"is sad")
            print("He doesn't want to even look at you.")
            evo = 0
            
        if score == 0:
            print(pet,"feels OK")
            print("He doesn't look happy nor sad")
            print("He evolved into",pet,"I")
            pet = pet + " " + "I"
            print(pet,"is bigger and slightly stronger!")
            evo = 1
            
        input()
        section = 1
        while section == 1:
            print("What do you want to do with it next?")
            find = input(tasksorder).lower()
            if find not in tasksorder:   
                print("That is not an option")
                input()
                print("Try again.")
                input()

            if find in tasksorder:
                if find == "train":
                    print("You decide you want to train it next.")
                    train(score,good,bad,tasksorder)
                    taskdone= taskdone + 1
                    section = 0
                    
                if find == "feed":
                    print("You decide you want to feed it next.")
                    feed(score,good,bad,tasksorder)
                    taskdone= taskdone + 1
                    section = 0
                    
                if find == "vet":
                    print("You decide you want to take it to the vet next.")
                    vet(score,good,bad,tasksorder)
                    taskdone= taskdone + 1
                    section = 0
                    
    if taskdone == 3:
        print("You have now",found,pet,".")
        input()
        if score > 0:
            print(pet,"likes you alot!")
            
        if score < 0:
            print(pet,"hates you a lot.")
            
        if score == 0:
            print(pet,"thinks you are alright.")
            
        input()
        section = 1
        while section == 1:
            print("What do you want to do with it next?")
            find = input(tasksorder).lower()
            if find not in tasksorder:   
                print("That is not an option")
                input()
                print("Try again.")
                input()

            if find in tasksorder:
                if find == "train":
                    print("You decide you want to train it now.")
                    train(score,good,bad,tasksorder)
                    taskdone= taskdone + 1
                    section = 0
                    
                if find == "feed":
                    print("You decide you want to feed it now.")
                    feed(score,good,bad,tasksorder)
                    taskdone= taskdone + 1
                    section = 0
                    
                if find == "vet":
                    print("You decide you want to take it to the vet now.")
                    vet(score,good,bad,tasksorder)
                    taskdone= taskdone + 1
                    section = 0

    if taskdone == 4:
        print("You have now",found,pet,".")
        input()
        print("This is the end of the demo of 'Hello World'")
        input()
        if score > 3:
            rating = "Good"
            print(pet,"has loved his time with you.")
            if "train" in good:
                print("He enjoyed the training.")
            if "feed" in good:
                print("He enjoyed the salad.")
            if "vet" in good:
                print("He found the vet trip fun.")
            
        if score < 3:
            rating = "Bad"
            print(pet,"has hated his time with you")
            if "train" in bad:
                print("He hated the training.")
            if "feed" in bad:
                print("He hated the soggy pizza.")
            if "feed2" in bad:
                print("He hated it when you told him to eat air.")
            if "vet" in bad:
                print("He hated the music.")
            if "vet2" in bad:
                print("He hated the jokes.")
            
        if score == 3:
            rating = "OK"
            print(pet,"has found his time alright.")
            print(pet,"has had his ups and downs with you..")
            if "train" in good:
                print("He enjoyed the training.")
            if "feed" in good:
                print("He enjoyed the salad.")
            if "vet" in good:
                print("He found the vet trip nice.")
            print("BUT")
            if "train" in bad:
                print("He hated the training.")
            if "feed" in bad:
                print("He hated the soggy pizza.")
            if "vet" in bad:
                print("He hated the vet trip.")
            
        input()
        print("You completed..")
        input()
        print("Hello World!")
        input()
        print("Your score:",score)
        input()
        print("Bonus Evolution Points:",evo)
        input()
        newscore = score+evo
        print("New score:",newscore)
        input()
        if "vet2" in bad:
            bad.remove("vet2")
            bad.append("vet")
        if "feed2" in bad:
            bad.remove("feed2")
            bad.append("feed")
        print("Good activities:",good)
        input()
        print("Bad activities:",bad)
        input()
        print("Overall rating:",rating)
        if score == 5:
            rank = "A*! Perfect!"
        if score == 4:
            rank = "A! Great!"
        if score == 3:
            rank = "B! Good!"
        if score == 2:
            rank = "C! OK!"
        if score == 1:
            rank = "D! Not bad.."
        if score == 0:
            rank = "E! Quite bad.."
        if score < 0:
            rank = "F! Awful!"
        print("Rank:",rank)
        #taskdone = 5 #for full game..
        #Full game - tasks will be selected randomly to do in scanerios
        #e.g. if protect, a bad creature will appear and that's when evolutions will come in play.
        #or, 
        tryagain = input("Try again? (y/n)").lower()
        if tryagain == "y":
            if score != 5:
                print("Let's see if you can do better than",score)
            if score == 5:
                print("Let's see if you can find out all endings of the game..")
        else:
            print("Thank you for playing, 'Hello World'.")
            game = 0