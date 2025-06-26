primarchs = [ "Horus", "Leman Russ", "Ferrus Manus", "Fulgrim", "Vulkan", "Rogal Dorn", "Roboute Guilliman", "Sanguinius", "Lion El'Jonson", "Perturabo", "Magnus the Red","Mortarion", "Jaghatai Khan", "Corvus Corax", "Lorgar", "Konrad Curze","Alpharius", "Angron"]
loyal_primarch = [primarchs[1],primarchs[2],primarchs[4],primarchs[5],primarchs[6],primarchs[7],primarchs[8],primarchs[12],primarchs[13]]
traitor_primarch = [p for p in primarchs if p not in loyal_primarch]
daddy = input('Who is your daddy?')

for p in primarchs:
    if p == daddy:
        Astartes = True
        break
    else:
        Astartes = False

if Astartes == True:
    for p in loyal_primarch:
        if p == daddy:
            loyal = True
            break
        else: loyal = False
else: loyal = 'Unknown'

if loyal == True:
    print(f'{daddy}? Death to the false Emperor!')
if loyal == False:
    print(f'{daddy}? For Horus Lupercal!')
if loyal == 'Unknown':
    print(f'{daddy}? Piss off zeno scum!')



