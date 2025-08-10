import os
W,H=20,10
SNAKE="🐍";FOOD="🍎";EMPTY="  "
GREEN="\033[42m";RESET="\033[0m"
TITLE="\033[1;31mT\033[1;33mh\033[1;32me \033[1;34mg\033[1;35ma\033[1;36mm\033[1;37me \033[1;31mi\033[1;33ms \033[1;32mb\033[1;34mu\033[1;35mi\033[1;36ml\033[1;37mt \033[1;31mb\033[1;33my \033[1;32mP\033[1;34my\033[1;35mt\033[1;36mh\033[1;37mo\033[1;31mn"+RESET
def draw(s,f,c):
    os.system('cls'if os.name=='nt'else'clear')
    print(TITLE+"\n")
    print(f"Score:{c}")
    for y in range(H):
        row=""
        for x in range(W):
            if (y,x) in s: row+=GREEN+SNAKE+RESET
            elif (y,x)==f: row+=GREEN+FOOD+RESET
            else: row+=GREEN+EMPTY+RESET
        print(row)
def main():
    s=[(H//2,W//2)];d=(0,1);f=(0,0);c=0
    while True:
        draw(s,f,c)
        m=input("Move (WASD,Q):").lower()
        if m=="q": break
        dirs={"w":(-1,0),"s":(1,0),"a":(0,-1),"d":(0,1)}
        if m in dirs:
            nd=dirs[m]
            if len(s)>1 and nd==(-d[0],-d[1]): nd=d
            else: d=nd
            h=(s[0][0]+d[0], s[0][1]+d[1])
            if h[0]<0 or h[0]>=H or h[1]<0 or h[1]>=W or h in s:
                print("Game Over!"); break
            s.insert(0,h)
            if h==f: c+=1
            else: s.pop()
if __name__=="__main__":
    main()
