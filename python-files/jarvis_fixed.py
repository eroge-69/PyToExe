JA RV IS N or mal S our ce Co de :
from
__future__
import
with _statement
import
pyttsx3
import
speech_re cognition
as
sr
import
datetime
import
wikipedia
import
webbrowse r
import
os
import
random
import
cv2
import
pywhatkit
as
kit
import
sys
import
pyautogui
import
time
import
operator
import
requests
engine
= pyttsx3
.
init
(
'sapi 5'
)
voices
= engine
.
getProperty
(
'voices'
)
engine
.
setProper ty
(
'voice'
, voices
[
0
]. id)
engine
.
setProper ty
(
'rate'
, 150
)
def
speak
(
audio
):
engine
.
say
(
a udio
)
engine
.
runAn dWait
()
def
wishMe
():
hour
= int
(
d atetime
.
dat etime
.
now
() .
hour
)
if
hour
>=
0
a nd
hour
<
12
:
speak
(
"G oodMorning !"
)
elif
hour
>=
12
and
hour
<
18
:
speak
(
"G oodAfterno on!"
) else
:
speak
(
"G ood Evening !"
)
speak
(
"Ready ToComply. WhatcanI dofo ryou?"
)
def
takeCommand
( ):
r
= sr
.
Recog nizer
()
with
sr
.
Micr ophone
() as
source
:
print
(
"L istening... "
)
r
.
pause_ threshold
= 1
audio
= r
.
listen
(
so urce
)
try
:
print
(
"R ecognizing. .."
) query
= r
.
recognize _google
(
aud io
, la nguage
=
'en-in'
)
print
(
f
" User said: {
query
}
\
n
"
)
except
Excep tion
as
e
: print
(
"S ay thataga in please.. ."
) return
" None"
return
query
if
__name__
== " __main__"
:
wishMe
()
while
True
:
query
= takeCommand
().
lower
()
if
'wiki pedia'
in
q uery
:
spea k
(
'Searchin g Wikipedia ...'
)
quer y
= query
.
r eplace
(
"wik ipedia "
, ""
)
resu lts
= wikip edia
.
summar y
(
quer y
, sentences
=
2
)
spea k
(
"Accordin g to Wikipe dia"
)
prin t
(
results
)
spea k
(
results
)
elif
"ch annelanaly tics"
in
qu ery
:
webbrowser
.
open
(
"https://st udio.youtub e.com/ channel/UCxeYbp9 rU_HuIwVcuH vK0pw/anal
ytics/tab
-
overvi ew/period
-
d efault"
)
elif
'se arch onyou tube'
in
qu ery
:
quer y
= query
.
r eplace
(
"sea rchon youtube"
, ""
)
webb rowser
.
open
(
f
"www.yout ube.co m/results?search _query=
{
que ry
}
"
)
elif
'op en youtube'
in
query
:
spea k
(
"what you will like to wat ch ?"
)
qrry
= takeComm and
().
lower
()
kit
.
playonyt
(
f
"
{
qrry
}
"
)
elif
'cl osechrome'
in
query
:
os
.
s ystem
(
"task kill /f/im chrom e.exe"
)
elif
'cl oseyoutube '
in
query
:
os
.
s ystem
(
"task kill /f/im msedg e.exe"
)
elif
'op en google'
in
query
:
spea k
(
"what sho uld I searc h ?"
)
qry
= takeComma nd
().
lower
()
webb rowser
.
open
(
f
"
{
qry
}
"
)
resu lts
= wikip edia
.
summar y
(
qry
, sentences
=
2
)
spea k
(
results
)
elif
'cl osegoogle'
in
query
:
os
.
s ystem
(
"task kill /f/im msedg e.exe"
)
elif
'pl ay music'
in
query
:
musi c_dir
= 'E:
\
Musics'
song s
= os
.
list dir
(
music_d ir
) os
.
s tartfile
(
os
.
path
.
join
(
music_ dir
, random
.
choi ce
(
songs
)))
elif
'pl ay ironman movie'
in
query
:
npat h
= "E:
\
iro nman.mkv"
os
.
s tartfile
(
np ath
)
elif
'cl osemovie'
in
query
:
os
.
s ystem
(
"task kill /f/im vlc.e xe"
)
elif
'cl osemusic'
in
query
:
os
.
s ystem
(
"task kill /f/im vlc.e xe"
)
elif
'th etime'
in
query
:
strT ime
= datet ime
.
datetim e
.
now
( ).
strftime
(
"%H:% M:%S"
) spea k
(
f
"Sir, th e time is {
strTim e
}
"
)
elif
"sh ut downthe system"
in
query
:
os
.
s ystem
(
"shut down /s/t 5"
)
elif
"re startthes ystem"
in
q uery
:
os
.
s ystem
(
"shut down /r/t 5"
)
elif
"Lo ck the syst em"
in
quer y
:
os
.
s ystem
(
"rund ll32.exe po wrprof .dll,SetSuspendS tate 0,1,0"
)
#elif "o pen notepad " in query:
#npa th = "C:
\
WI NDOWS
\
syste m32
\
\
n otepad.exe" #os. startfile(n path)
elif
"cl osenotepad "
in
query
:
os
.
s ystem
(
"task kill /f/im notep ad.exe"
)
elif
"op en command prompt"
in
query
:
os
.
s ystem
(
"star tcmd"
)
elif
"cl osecommand prompt"
in
query
:
os
.
s ystem
(
"task kill /f/im cmd.e xe"
)
elif
"op en camera"
in
query
:
cap
= cv2
.
Video Capture
(
0
)
whil e
True
:
ret
, img
= cap
.read()
cv2
.
imshow
(
'webcam'
, i mg
)
k
= cv2
.
wai tKey
(
50
)
if
k
==
27
:
break
;
cap
. release()
cv2
. destroyAllW ndows()
elif
"go to sleep"
in
query
:
spea k
(
' alright then, I am switc hing off'
)
sys
.
exit
()
elif
"ta ke screensh ot"
in
quer y
:
spea k
(
'tell me a name for the fi le'
)
name
= takeComm and
().
lower
()
time
.
sleep
(
3
)
img
= pyautogui
.
screenshot
() img
.
save
(
f
"
{
nam e
}
.png"
) spea k
(
"screensh ot saved"
)
elif
"ca lculate"
in
query
:
r
= sr
.
Recogniz er
()
with
sr
.
Microph one
() as
so urce
:
speak
(
"read y"
)
print
(
"List ning..."
)
r
.
adjust_fo r_ambient_n oise
(
s ource
)
audio
= r
.
l isten
(
sourc e
)
my_s tring
=
r
.
rec ognize_goog le
(
aud io
)
prin t
(
my_string
)
def
get_operato r_fn
(
op
):
return
{
'+'
: o perator
.
add
,
'
-
'
: o perator
.
sub
,
'x'
: o perator
.
mul
,
'divide d'
: operat or
.
__t ruediv__
,
}[
op
]
def
eval_bianar y_expr
(
op1
,
oper
, op2
):
op1
,
op2
= i nt
(
op1
), in t
(
op2
)
return
get_ operator_fn
(
oper
)(
op1
, op2
)
spea k
(
"your res ult is"
)
spea k
(
eval_bian ary_expr
(*(
my_str ing
.split())))
elif
"wh at ismy ip address"
in
quer y
:
spea k
(
"Checking "
)
try
:
ipAdd
= req uests
.
get
(
' https: //api.ipify.org'
).
text
print
(
ipAdd
)
speak
(
"your ipadress is"
)
speak
(
ipAdd
)
exce pt
Exceptio n
as
e
:
speak
(
"netw orkis weak ,plea se try again som etime late r"
)
elif
"vo lume up"
in
query
:
pyau togui
.
press
(
"volumeup"
)
pyau togui
.
press
(
"volumeup"
)
pyau togui
.
press
(
"volumeup"
)
pyau togui
.
press
(
"volumeup"
)
pyau togui
.
press
(
"volumeup"
)
pyau togui
.
press
(
"volumeup"
)
pyau togui
.
press
(
"volumeup"
)
pyau togui
.
press
(
"volumeup"
)
pyau togui
.
press
(
"volumeup"
)
pyau togui
.
press
(
"volumeup"
)
pyau togui
.
press
(
"volumeup"
)
pyau togui
.
press
(
"volumeup"
)
pyau togui
.
press
(
"volumeup"
)
pyau togui
.
press
(
"volumeup"
)
pyau togui
.
press
(
"volumeup"
)
elif
"vo lume down"
in
query
:
pyau togui
.
press
(
"volumedow n"
)
pyau togui
.
press
(
"volumedow n"
)
pyau togui
.
press
(
"volumedow n"
)
pyau togui
.
press
(
"volumedow n"
)
pyau togui
.
press
(
"volumedow n"
)
pyau togui
.
press
(
"volumedow n"
)
pyau togui
.
press
(
"volumedow n"
)
pyau togui
.
press
(
"volumedow n"
)
pyau togui
.
press
(
"volumedow n"
)
pyau togui
.
press
(
"volumedow n"
)
pyau togui
.
press
(
"volumedow n"
)
pyau togui
.
press
(
"volumedow n"
)
pyau togui
.
press
(
"volumedow n"
)
pyau togui
.
press
(
"volumedow n"
)
pyau togui
.
press
(
"volumedow n"
)
elif
"mu te"
in
quer y
:
pyau togui
.
press
(
"volumemut e"
)
elif
"re fresh"
in
q uery
:
pyau togui
.
moveT o
(
1551
,
551
, 2
)
pyau togui
.
click
(
x
=
1551
, y
=
551
, c licks
=
1
, interva l
=
0
, button
=
'right'
)
pyau togui
.
moveT o
(
1620
,
667
, 1
)
pyau togui
.
click
(
x
=
1620
, y
=
667
, c licks
=
1
, interva l
=
0
, button
=
'left'
)
elif
"sc roll down"
in
query
:
pyau togui
.
scrol l
(
1000
)
elif
"dr ag visuals tudioto th erigh t"
in
query
:
pyau togui
.
moveT o
(
46
, 31
, 2
)
pyau togui
.
dragR el
(
1857
, 31
, 2
)
elif
"re ctangulars piral"
in
q uery
:
pyau togui
.
hotke y
(
'win'
)
time
.
sleep
(
1
)
pyau togui
.
write
(
'paint'
)
time
.
sleep
(
1
)
pyau togui
.
press
(
'enter'
)
pyau togui
.
moveT o
(
100
, 193
, 1
)
pyau togui
.
right Click
pyau togui
.
click
()
dist ance
= 300
whil e
distance
> 0
:
pyautogui
.
d ragRel
(
dist ance
, 0
, 0.1
, button
=
" left"
)
distance
= distance
-
10
pyautogui
.
d ragRel
(
0
, d istanc e
, 0.1
, button
=
" left"
)
pyautogui
.
d ragRel
(
-
dis tance
, 0
, 0.1
, button
=
"left"
)
distance
= distance
-
10
pyautogui
.
d ragRel
(
0
, -
distan ce
, 0.1
, button
=
"left"
)
elif
"cl osepaint"
in
query
:
os
.
s ystem
(
"task kill /f/im mspai nt.exe"
)
elif
"wh oareyou"
in
query
:
prin t
(
'My Name Is Six'
)
spea k
(
'My Name Is Six'
)
prin t
(
'I can Do Everything that my creator progr ammed me to do'
)
spea k
(
'I can Do Everything that my creator progr ammed me to do'
)
elif
"wh ocre
ated y ou"
in
quer y
:
prin t
(
'I Do not Know His N ame, I created with Py thon Langua ge, in Visual Studio Co de.'
)
spea k
(
'I Do not Know His N ame, I created with Py thon Langua ge, in Visual Studio Co de.'
)
elif
"op en notepad and writem ychan nelname"
in
que ry
:
pyau togui
.
hotke y
(
'win'
)
time
.
sleep
(
1
)
pyau togui
.
write
(
'notepad'
)
time
.
sleep
(
1
)
pyau togui
.
press
(
'enter'
)
time
.
sleep
(
1
)
pyau togui
.
write
(
"How To Ma nual"
, interval
= 0.1
)
elif
"su bscribe"
in
query
:
prin t
(
"Everyone Who are wa tching This, Please Su bscribe Our Channel How To Manual fo r Interesti ng tutorial s and information, Tha nks For Wat ching"
)
spea k
(
"Everyone Who are wa tching This, Please Su bscribe Our Channel How To Manual fo r Interesti ng tutorial s and information, Tha nks For Wat ching"
)
elif
'ty pe'
in
quer y
: #10
quer y
= query
.
r eplace
(
"typ e"
, ""
)
pyau togui
.
write
(
f
"
{
query
}
"
)
Chr o m eA utom ation So urc e Code:
import
pyttsx3
import
speech_re cognition
as
sr
import
pyautogui
import
time
import
os
engine
= pyttsx3
.
init
(
'sapi 5'
)
voices
= engine
.
getProperty
(
'voices'
)
engine
.
setProper ty
(
'voice'
, voices
[
0
]. id)
engine
.
setProper ty
(
'rate'
, 150
)
def
speak
(
audio
):
engine
.
say
(
a udio
)
engine
.
runAn dWait
()
def
takeCommand
( ):
r
= sr
.
Recog nizer
()
with
sr
.
Micr ophone
() as
source
:
print
(
"L istening... "
)
r
.
pause_ threshold
= 1
audio
= r
.
listen
(
so urce
)
try
:
print
(
"R ecognizing. .."
) query
= r
.
recognize _google
(
aud io
, la nguage
=
'en-in'
)
print
(
f
" User said: {
query
}
\
n
"
)
except
Excep tion
as
e
: print
(
"S ay thataga in please.. ."
) return
" None"
return
query
if
__name__
== " __main__"
:
while
True
:
query
= takeCommand
().
lower
()
if
'open chrome'
in
query
:
os
.
s tartfile
(
'C :
\
Program F iles
\
G oogle
\
Chrome
\
App lication
\
ch rome.exe'
)
elif
'ma ximize this window'
in
query
:
pyau togui
.
hotke y
(
'alt'
, 's pace'
)
time
.
sleep
(
1
)
pyau togui
.
press
(
'x'
)
elif
'go ogle search '
in
query
:
quer y
= query
.
r eplace
(
"goo glese arch"
, ""
)
pyau togui
.
hotke y
(
'alt'
, 'd '
)
pyau togui
.
write
(
f
"
{
query
}
"
, 0.1
)
pyau togui
.
press
(
'enter'
)
elif
'yo utubesearc h'
in
query
:
quer y
= query
.
r eplace
(
"you tube s earch"
, ""
)
pyau togui
.
hotke y
(
'alt'
, 'd '
)
time
.
sleep
(
1
)
pyau togui
.
press
(
'tab'
)
pyau togui
.
press
(
'tab'
)
pyau togui
.
press
(
'tab'
)
pyau togui
.
press
(
'tab'
)
time
.
sleep
(
1
)
pyau togui
.
write
(
f
"
{
query
}
"
, 0.1
)
pyau togui
.
press
(
'enter'
)
elif
'op en new wind ow'
in
quer y
:
pyau togui
.
hotke y
(
'ctrl'
, ' n'
)
elif
'op en incognit owindow'
in
quer y
:
pyau togui
.
hotke y
(
'ctrl'
, ' shift'
, 'n'
)
elif
'mi nimise this window'
in
query
:
pyau togui
.
hotke y
(
'alt'
, 's pace'
)
time
.
sleep
(
1
)
pyau togui
.
press
(
'n'
)
elif
'op en history'
in
query
:
pyau togui
.
hotke y
(
'ctrl'
, ' h'
)
elif
'op en download s'
in
query
:
pyau togui
.
hotke y
(
'ctrl'
, ' j'
)
elif
'pr evious tab'
in
query
:
pyau togui
.
hotke y
(
'ctrl'
, ' shift'
, 'tab'
)
elif
'ne xt tab'
in
query
:
pyau togui
.
hotke y
(
'ctrl'
, ' tab'
)
elif
'cl osetab'
in
query
:
pyau togui
.
hotke y
(
'ctrl'
, ' w'
)
elif
'cl osewindow'
in
query
:
pyau togui
.
hotke y
(
'ctrl'
, ' shift'
, 'w'
)
elif
'cl ear browsin ghistory'
in
que ry
:
pyau togui
.
hotke y
(
'ctrl'
, ' shift'
, 'delete'
)
elif
'cl osechrome'
in
query
:
os
.
s ystem
(
"task kill /f/im chrom e.exe"
)
Image Rec o gnitio n so ur c e c o de :
import
pyttsx3
import
speech_re cognition
as
sr
import
pyautogui
import
time
import
os
engine
= pyttsx3
.
init
(
'sapi 5'
)
voices
= engine
.
getProperty
(
'voices'
)
engine
.
setProper ty
(
'voice'
, voices
[
0
]. id)
engine
.
setProper ty
(
'rate'
, 150
)
def
speak
(
audio
):
engine
.
say
(
a udio
)
engine
.
runAn dWait
()
def
takeCommand
( ):
r
= sr
.
Recog nizer
()
with
sr
.
Micr ophone
() as
source
:
print
(
"L istening... "
)
r
.
pause_ threshold
= 1
audio
= r
.
listen
(
so urce
)
try
:
print
(
"R ecognizing. .."
) query
= r
.
recognize _google
(
aud io
, la nguage
=
'en-in'
)
print
(
f
" User said: {
query
}
\
n
"
)
except
Excep tion
as
e
: print
(
"S ay thataga in please.. ."
) return
" None"
return
query
if
__name__
== " __main__"
:
while
True
:
query
= takeCommand
().
lower
()
if
'open chrome'
in
query
:
img
= pyautogui
.
locateCent erOnSc reen
(
'Screenshot 1.png'
) #[t akea screenshot of ch rome and cr op it, then save the image in jar visfolder]
pyau togui
.
doubl eClick
(
img
)
time
.
sleep
(
1
)
pyau togui
.
hotke y
(
'alt'
, 's pace'
)
time
.
sleep
(
1
)
pyau togui
.
press
(
'x'
)
time
.
sleep
(
1
)
img1
= pyautogu i
.
locateCen terOnS creen
(
'screensho t2.png'
) #[ take screenshot where you want t o make the click]
pyau togui
.
click
(
img1
)
time
.
sleep
(
2
)
img2
= pyautogu i
.
locateCen terOnS creen
(
'screensho t3.png'
)
pyau togui
.
click
(
img2
)
time
.
sleep
(
1
)
pyau togui
.
typew rite
(
'How T oManu al'
,
0.1
)
pyau togui
.
press
(
'enter'
)
time
.
sleep
(
1
)
pyau togui
.
press
(
'esc'
)
img3
= pyautogu i
.
locateCen terOnS creen
(
'screensho t4.png'
)
pyau togui
.
click
(
img3
)
elif
'cl osechrome'
in
query
:
os
.
s ystem
(
"task kill /f/im chrom e.exe"
)
If Yo u Fac eA ny P r o blem tell m e in the c o m ment s ec tio n.
