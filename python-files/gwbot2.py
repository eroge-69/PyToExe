import requests as r,time as t,re,pyperclip as pc
from plyer import notification as n
from colorama import init as i,Fore as F,Style as S
import threading as th,keyboard as k,os,sys
i(autoreset=True)
A="config.txt"
B="1399918238388981843"
C="1399918238434856998"
def D():return open(A).read().strip()if os.path.exists(A)else""
def E(x):open(A,"w").write(x.strip())
def F0(T):
 u=f"https://discord.com/api/v9/users/@me/guilds/{B}/member"
 h={"Authorization":T,"User-Agent":"Mozilla/5.0"}
 try:
  res=r.get(u,headers=h)
  if res.status_code==200:
   return C in res.json().get("roles",[])
  else:
   return False
 except:
  return False
G=D();G=input("Please input your token:\n>> ").strip()or G if not G or G.lower()=="your_token_here"else G;E(G)
if not F0(G):print(F.RED+S.BRIGHT+"\n[ACCESS DENIED] Invalid role.\n");sys.exit(1)
H={"1":("10 Million+","1394958063341015081"),"2":("1–10 Million","1394958060828627064")}
I=re.compile(r"- (?:🆔 )?Job ID \(PC\): ```([^\s`]+)```",re.M);J=None;K=None;L=False;M=True;N=None
def O():os.system('cls'if os.name=='nt'else'clear')
def P():print(F.MAGENTA+"="*50);print(F.CYAN+S.BRIGHT+"         TRRST  A U T O  J O I N E R");print(F.MAGENTA+"="*50+"\n")
def Q(x):print(F.CYAN+"[INFO]"+S.RESET_ALL+" "+x)
def R(x):print(F.GREEN+"[SUCCESS]"+S.RESET_ALL+" "+x)
def S0(x):print(F.YELLOW+"[WARNING]"+S.RESET_ALL+" "+x)
def T0(x):print(F.RED+"[ERROR]"+S.RESET_ALL+" "+x)
def U(x):
 for l in x.strip().splitlines():
  if any(l.startswith(p)for p in["- 🌐 Join Link:","- Job ID (Mobile):"]):continue
  print({True:F.MAGENTA,False:F.YELLOW}[l.startswith("- 🏷️ Name:")]+l if l.startswith("- 🏷️ Name:")or l.startswith("- 💰 Money per sec:")else F.CYAN+l if l.startswith("- 👥 Players:")else F.GREEN+S.BRIGHT+l if"Brainrot Notify"in l or"Chilli Hub"in l else l)
def V():
 global N,L,M
 while M:
  if L:t.sleep(0.1);continue
  try:
   a=r.get(K,headers={"Authorization":G,"User-Agent":"Mozilla/5.0","Accept":"*/*","Referer":f"https://discord.com/channels/@me/{J}"})
   if a.status_code!=200:T0(f"HTTP {a.status_code}: {a.text}");t.sleep(0.5);continue
   d=a.json();b=d[0];c=b["id"]
   if c==N:t.sleep(0.1);continue
   N=c;u=b["author"]["username"];v=b.get("content","")
   for e in b.get("embeds",[]):v+=f"\n{e.get('title','')}\n{e.get('description','')}"+''.join([f"\n- {f1['name']}: {f1['value']}"for f1 in e.get("fields",[])])
   O();P();R(f"New message from {u}:");U(v)
   l=v.splitlines()
   x,y,z,w=[next((l1 for l1 in l if s in l1),"")for s in["Brainrot Notify","- 🏷️ Name:","- 💰 Money per sec:","- 👥 Players:"]]
   f="\n".join(filter(None,[x,y,z,w]))
   m=I.search(v)
   if m and not L:
    g=m.group(1).strip();pc.copy(g);n.notify(title="Discord Job-ID Notification",message=f,timeout=8);R(f"Copied Job-ID code: {g}")
   else:Q("No Job-ID code found.")
  except Exception as e:T0(f"Exception occurred: {e}")
  t.sleep(0.1)
def W():
 global L,M,J,K,N
 while M:
  if k.is_pressed('['):L=not L;Q("Paused"if L else"Resumed");t.sleep(0.5)
  if k.is_pressed(']'):L=True;Q("Returning to menu...");t.sleep(0.5);X();N=None;L=False
  t.sleep(0.1)
def X():
 global J,K
 O();P();print(F.BLUE+"=== Channel Selection Menu ===")
 for k1,(n1,_)in H.items():print(f"{k1}. {n1}")
 print(F.BLUE+"===============================\n")
 while True:
  ch=input(F.CYAN+"Select a channel (1 or 2): ").strip()
  if ch in H:
   n2,J=H[ch];K=f"https://discord.com/api/v9/channels/{J}/messages?limit=1";R(f"Monitoring channel: {n2}");break
  else:T0("Invalid selection. Please enter 1 or 2.")
if __name__=="__main__":X();th.Thread(target=W,daemon=True).start();V()
