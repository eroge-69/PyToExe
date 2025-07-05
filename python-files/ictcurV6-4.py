# Programme currency converter
#uprogramme name ictcurv6-3.py
import datetime
import decimal
print()
#def variables
curc=" "
amr1=0
amr2=0
ams1=0
ams2=0

# below vales as on 01.07.25
# no 1
usd1=294.8076
usd2=303.2500
# no 2
gbp1=403.4146
gbp2=417.8330
# no 3
eur1=345.7522
eur2=358.7599
# no 4
aud1=190.4664
aud2=202.7074
# no 5
jpy1=2.0519
jpy2=2.1178
# no 6
sgd1=229.0552
sgd2=242.1544
# no 7
cad1=215.2949
cad2=223.5615
# no 8
sek1=19.6940
sek2=32.3111
# no 9 
hkd1=37.5833
hkd2=38.7787
# no  10
nzd1=176.7022
nzd2=185.9377
# no 11
chf1=364.3433
chf2=387.3666
# no 12
bhd1=685.5188
bhd2=803.7370
# no 13
kwd1=883.0744
kwd2=991.7098
# no 14
omr1=746.3668
omr2=787.6009
# no 15
qar1=66.5816
qar2=85.0643
# no 16
sar1=76.2721
sar2=82.6181
# no 17 hi
aed1=78.0612
aed2=84.4096
# no 18
cny1=39.1544
cny2=43.2497
# no 19
ind1=3.51
ind2=3.60
# no 21
taka1=2.44
taka2=2.64
# no 20
icta1=round(((usd1+gbp1+eur1+aud1+jpy1+sgd1+cad1+sek1+hkd1+nzd1+chf1+bhd1+kwd1+omr1+qar1+sar1+aed1+cny1+ind1+taka1)/20),4)
icta2=round(((usd2+gbp2+eur2+aud2+jpy2+sgd2+cad2+sek2+hkd2+nzd2+chf2+bhd2+kwd2+omr2+qar2+sar2+aed2+cny2+ind2+taka2)/20),4)

ictc1=icta1
ictc2=icta2

print(" Institute of Computer Technology")
print()
print (" 🌻 -ICT-CURRENCY CONVERTER ")
print("    Nce_Ict. - by L.Siva - " ) 
print("    Updated date 1st July 2025 ")
print()
print("     ",datetime.datetime.now())
print(" Permenant changes only by ICT, Nice_ICT    Authorization  ")
print()
print(" Any Temporary changes to be done for       currencies ")
print()
opt1=input(" Enter........ Y/N   ")
print()
print("No   Currency          Buy.     Sel.")
print(" 1. US Doller       ",usd1," ",usd2)
print(" 2. Sterling Pounds ",gbp1," ",gbp2)
print(" 3. Euro            ",eur1," ",eur2)
print(" 4. Australian Dol. ",aud1," ",aud2)
print(" 5. Japanese  Yen.    ",jpy1,"   ",jpy2)
print(" 6. Singapore Dol.  ",sgd1," ",sgd2) 
print(" 7. Canadian Dol.   ",cad1," ",cad2)
print(" 8. Swedish Kroners  ",sek1,"   ",sek2)
print(" 9. Hongkong Dollars ",hkd1,"  ",hkd2)
print("10. Newzealand Dol. ",nzd1," ",nzd2)
print("11. Swiss Francs    ",chf1," ",chf2)
print("12. Bahrain Dinars  ",bhd1," ",bhd2) 
print("13. Kuwait Dinars   ",kwd1," ",kwd2)
print("14. Omani Riyals    ",omr1," ",omr2) 
print("15. Qatar Riyals     ",qar1,"  ",qar2) 
print("16. Saudi Arabian Rl ",sar1,"  ",sar2)
print("17. UAE Dirhams      ",aed1,"  ",aed2)  
print("18. Chinese Yuan     ",cny1,"  ",cny2)
print("19. Indian Ruppies    ",ind1,"     ",ind2)
print("20. Ict currency    ",ictc1," ",ictc2)
print("21. Bangladesh Taka.  ",taka1,"     ",taka2)

while opt1== "Y" or opt1== "y":
   print()
   opt2=int(input(" Enter option No :  "))
 
   if opt2==1:
    print(' .Buy  ',usd1,'.Sel  ',usd2)
    usd3=float(input(" Enter Buying Value  USD  "))
    usd4=float(input(" Enter Selling Value     "))
    usd1=usd3
    usd2=usd4
    
   if opt2==2:
    print(' .Buy  ',gbp1,'.Sel  ',gbp2)
    gbp3=float(input(" Enter Buying Value  GBP  "))
    gbp4=float(input(" Enter Selling Value     "))
    gbp1=gbp3
    gbp2=gbp4
    
   if opt2==3:
    print(' .Buy  ',eur1,'.Sel  ',eur2)  
    eur3=float(input(" Enter Buying Value  EUR "))
    eur4=float(input(" Enter Selling Value  "))
    eur1=eur3
    eur2=eur4
    
   if opt2==4:
     print(' .Buy  ', aud1,'.Sel  ', aud2)   
     aud3=float(input(" Enter Buying Value  AUD "))
     aud4=float(input(" Enter Selling Value  "))
     aud1=aud3
     aud2=aud4
     
   if opt2==5:
    print(' .Buy  ',jpy1,'.Sel  ',jpy2)  
    jpy3=float(input(" Enter Buying Value  JPY "))
    jpy4=float(input(" Enter Selling Value  "))
    jpy1=jpy3
    jpy2=jpy4
    
   if opt2==6:
    print(' .Buy  ',sgd1,'.Sel  ',sgd2)  
    sgd3=float(input(" Enter Buying Value  SGD "))
    sgd4=float(input(" Enter Selling Value  "))
    sgd1=sgd3
    sgd2=sgd4
    
   if opt2==7:
    print(' .Buy  ',cad1,'.Sel  ',cad2)   
    cad3=float(input(" Enter Buying Value  CAD "))
    cad4=float(input(" Enter Selling Value  "))
    cad1=cad3
    cad2=cad4
    
   if opt2==8:
    print(' .Buy  ',sek1,'.Sel  ',sek2)     
    sek3=float(input(" Enter Buying Value  SEK  "))
    sek4=float(input(" Enter Selling Value  "))
    sek1=sek3
    sek2=sek4
    
   if opt2==9:
    print(' .Buy  ',hkd1,'.Sel  ',hkd2)   
    hkd1=float(input(" Enter Buying Value  HKD "))
    hkd2=float(input(" Enter Selling Value  "))
    hkd3=hkd1
    hkd4=hkd2
    
   if opt2==10:
     print(' .Buy  ',nzd1,'.Sel  ',nzd2)   
     nzd3=float(input(" Enter Buying Value  NZD "))
     nzd4=float(input(" Enter Selling Value  "))
     nzd1=nzd3
     nzd2=nzd4
     
   if opt2==11:
     print(' .Buy  ',chf1,'.Sel  ',chf2)   
     chf3=float(input(" Enter Buying Value  CHF "))
     chf4=float(input(" Enter Selling Value  "))
     chf1=chf3
     chf2=chf4
     
   if opt2==12:
      print(' .Buy  ',bhd1,'.Sel  ',bhd2)   
      bhd3=float(input(" Enter Buying Value  BHD"))
      bhd4=float(input(" Enter Selling Value  "))
      bhd1=bhd3
      bhd2=bhd4
      
   if opt2==13:
      print(' .Buy  ', kwd1,'.Sel  ', kwd2)   
      kwd3=float(input(" Enter Buying Value  KWD "))
      kwd4=float(input(" Enter Selling Value  "))
      kwd1=kwd3
      kwd2=kwd4
      
   if opt2==14:
      print(' .Buy  ', omr1,'.Sel  ', omr2)   
      omr3=float(input(" Enter Buying Value  OMR "))
      omr4=float(input(" Enter Selling Value  "))
      omr1=omr3
      omr2=omr4
      
   if opt2==15:
      print(' .Buy  ', qar1,'.Sel  ', qar2) 
      qar3=float(input(" Enter Buying Value  QAR "))
      qar4=float(input(" Enter Selling Value  "))
      qar1=qar3
      qar2=qar4
      
   if opt2==16:
      print(' .Buy  ', sar1,'.Sel  ', sar2) 
      sar3=float(input(" Enter Buying Value  SAR "))
      sar4=float(input(" Enter Selling Value  "))
      sar1=sar3
      sar2=sar4
      
   if opt2==17:
      print(' .Buy  ', aed1,'.Sel  ', aed2) 
      aed3=float(input(" Enter Buying Value AED  "))
      aed4=float(input(" Enter Selling Value  "))
      aed1=aed3
      aed2=aed4
      
   if opt2==18:
      print(' .Buy  ', cny1,'.Sel  ', cny2) 
      cny3=float(input(" Enter Buying Value CNY  "))
      cny4=float(input(" Enter Selling Value  "))
      cny1=cny3
      cny2=cny4
      
   if opt2==19:
      print(' .Buy  ', ind1,'.Sel  ', ind2) 
      ind3=float(input(" Enter Buying Value IND  "))
      ind4=float(input(" Enter Selling Value  "))
      ind1=ind3
      ind2=ind4
      
   if opt2==20:
      print(' .Buy  ', ictc1,'.Sel  ', ictc2) 
      ictc3=float(input(" Enter Buying Value  "))
      ictc4=float(input(" Enter Selling Value  "))
      ictc1=ictc3
      ictc2=ictc4
      
   if opt2==21:
      print(' .Buy  ', Taka1,'.Sel  ', Taka2) 
      taka3=float(input(" Enter Buying Value  "))
      taka4=float(input(" Enter Selling Value  "))
      taka1=taka3
      taka3=taka4
      
   print()
   opt1=input(" More changes ........ Y/N   ")
    
   print()
print()
cur1=input(" Enter Currency No. Required ")
#print()
amt=int(input("Enter Amt in SLR to be converted : " ))
amtt=int(input("Enter how many currency Required  : "))
# convertion calculations
amt1=round((amt/usd1),2)
amt11=round((amt/usd2),2)
amtt1=round((amtt*usd1),2)
amtt11=round((amtt*usd2),2)

amt2=round((amt/gbp1),2)
amt21=round((amt/gbp2),2)
amtt2=round((amtt*gbp1),2)
amtt21=round((amtt*gbp2),2)

amt3=round((amt/eur1),2)
amt31=round((amt/eur2),2)  
amtt3=round((amtt*eur1),2)
amtt31=round((amtt*eur2),2)
       
amt4=round((amt/aud1),2)
amt41=round((amt/aud2),2)
amtt4=round((amtt*aud1),2)
amtt41=round((amtt*aud2),2)

amt5=round((amt/jpy1),2)
amt51=round((amt/jpy2),2)
amtt5=round((amtt*jpy1),2)
amtt51=round((amtt*jpy2),2)

amt6=round((amt/sgd1),2)
amt61=round((amt/sgd2),2)  
amtt6=round((amtt*sgd1),2)
amtt61=round((amtt*sgd2),2)

amt7=round((amt/cad1),2)
amt71=round((amt/cad2),2)
amtt7=round((amtt*cad1),2)
amtt71=round((amtt*cad2),2)

amt8=round((amt/sek1),2)
amt81=round((amt/sek2),2)
amtt8=round((amtt*sek1),2)
amtt81=round((amtt*sek2),2)

amt9=round((amt/hkd1),2)
amt91=round((amt/hkd2),2)
amtt9=round((amtt*hkd1),2)
amtt91=round((amtt*hkd2),2)

amt10=round((amt/nzd1),2)
amt101=round((amt/nzd2),2)
amtt10=round((amtt*nzd1),2)
amtt101=round((amtt*nzd2),2)

amt11=round((amt/chf1),2)
amt111=round((amt/chf2),2)
amtt11=round((amtt*chf1),2)
amtt111=round((amtt*chf2),2)

amt12=round((amt/bhd1),2)
amt121=round((amt/bhd2),2)
amtt12=round((amtt*bhd1),2)
amtt121=round((amtt*bhd2),2)

amt13=round((amt/kwd1),2)
amt131=round((amt/kwd2),2)
amtt13=round((amtt*kwd1),2)
amtt131=round((amtt*kwd2),2)

amt14=round((amt/omr1),2)
amt141=round((amt/omr2),2)
amtt14=round((amtt*omr1),2)
amtt141=round((amtt*omr2),2)

amt15=round((amt/qar1),2)
amt151=round((amt/qar2),2)
amtt15=round((amtt*qar1),2)
amtt151=round((amtt*qar2),2)

amt16=round((amt/sar1),2)
amt161=round((amt/sar2),2)
amtt16=round((amtt*sar1),2)
amtt161=round((amtt*sar2),2)

amt17=round((amt/aed1),2)
amt171=round((amt/aed2),2)
amtt17=round((amtt*aed1),2)
amtt171=round((amtt*aed2),2)

amt18=round((amt/cny1),2)
amt181=round((amt/cny2),2)
amtt18=round((amtt*cny1),2)
amtt181=round((amtt*cny2),2)

amt19=round((amt/ind1),2)
amt191=round((amt/ind2),2)
amtt19=round((amtt*ind1),2)
amtt191=round((amtt*ind2),2)

amt20=round((amt/ictc1),2)
amt201=round((amt/ictc2),2)
amtt20=round((amtt*ictc1),2)
amtt201=round((amtt*ictc2),2)

amt30=round((amt/taka1),2)
amt301=round((amt/taka2),2)
amtt30=round((amtt*taka1),2)
amtt301=round((amtt*taka2),2)

if int(cur1)==1:
 curc="US Dollar   "
 amr1=usd1
 amr2=usd2
 amr3=usd1
 amr4=usd2
 ams1=amt1
 ams2=amt11
 ams3=amtt1
 ams4=amtt11
 
if int(cur1)==2:
 curc="Ster.Pound "
 amr1=gbp1
 amr2=gbp2
 amr3=gbp1
 amr4=gbp2
 ams1=amt2
 ams2=amt21
 ams3=amtt2
 ams4=amtt21
 
if int(cur1)==3:
 curc="Euro        "
 amr1=eur1
 amr2=eur2
 amr3=eur1
 amr4=eur2
 ams1=amt3
 ams2=amt31
 ams3=amtt3
 ams4=amtt31
 
if int(cur1)==4:
 curc="Aus.Doller  "
 amr1=aud1
 amr2=aud2
 amr3=aud1
 amr4=aud2
 ams1=amt4
 ams2=amt41
 ams3=amtt4
 ams4=amtt41
 
if int(cur1)==5:
 curc="Japanese Yen"
 amr1=jpy1
 amr2=jpy2
 amr3=jpy1
 amr4=jpy2
 ams1=amt5
 ams2=amt51  
 ams3=amtt5
 ams4=amtt51
 
if int(cur1)==6:
 curc="Sing doller "
 amr1=sgd1
 amr2=sgd2
 amr3=sgd1
 amr4=sgd2
 ams1=amt6
 ams2=amt61
 ams3=amtt6
 ams4=amtt61
 
if int(cur1)==7:
 curc="Canadian $ "
 amr1=cad1
 amr2=cad2
 amr3=cad1
 amr4=cad2
 ams1=amt7
 ams2=amt71
 ams3=amtt7
 ams4=amtt71
 
if int(cur1)==8:
 curc="Swedish Kro"
 amr1=sek1
 amr2=sek2
 amr3=sek1
 amr4=sek2
 ams1=amt8
 ams2=amt81
 ams3=amtt8
 ams4=amtt81
 
if int(cur1)==9:
 curc="Hong Kong $b"
 amr1=hkd1
 amr2=hkd2
 amr3=hkd1
 amr4=hkd2
 ams1=amt9
 ams2=amt91
 ams3=amtt9
 ams4=amtt91
 
if int(cur1)==10:
 curc="NewZealand $"
 amr1=nzd1
 amr2=nzd2
 amr3=nzd1
 amr4=nzd2
 ams1=amt10
 ams2=amt101
 ams3=amtt10
 ams4=amtt101
 
if int(cur1)==11:
 curc="Swiss Franc "
 amr1=chf1
 amr2=chf2
 amr3=chf1
 amr4=chf2
 ams1=amt11
 ams2=amt111
 ams3=amtt11
 ams4=amtt111
 
if int(cur1)==12:
 curc="Baharain Din"
 amr1=bhd1
 amr2=bhd2
 amr3=bhd1
 amr4=bhd2
 ams1=amt12
 ams2=amt121
 ams3=amtt12
 ams4=amtt121
 
if int(cur1)==13:
 curc="Kuwait Din  "
 amr1=kwd1
 amr2=kwd2
 amr3=kwd1
 amr4=kwd2
 ams1=amt13
 ams2=amt131
 ams3=amtt13
 ams4=amtt131
 
if int(cur1)==14:
 curc="Omaan Riyals"
 amr1=omr1
 amr2=omr2
 amr3=omr1
 amr4=omr2
 ams1=amt14
 ams2=amt141
 ams3=amtt14
 ams4=amtt141
 
if int(cur1)==15:
 curc="Qutar Riyals"
 amr1=qar1
 amr2=qar2
 amr3=qar1
 amr4=qar2
 ams1=amt15
 ams2=amt151
 ams3=amtt15
 ams4=amtt151
 
if int(cur1)==16:
 curc="Saudi.Riyals"
 amr1=sar1
 amr2=sar2
 amr3=sar1
 amr4=sar2
 ams1=amt16
 ams2=amt161
 ams3=amtt16
 ams4=amtt161
 
if int(cur1)==17:
 curc="UAE Dhirams "
 amr1=aed1
 amr2=aed2
 amr3=aed1
 amr4=aed2
 ams1=amt17
 ams2=amt171
 ams3=amtt17
 ams4=amtt171
 
if int(cur1)==18:
 curc="Chinese Yuan"
 amr1=cny1
 amr2=cny2
 amr3=cny1
 amr4=cny2
 ams1=amt18
 ams2=amt181
 ams3=amtt18
 ams4=amtt181
 
if int(cur1)==19:
 curc="Indian Rs.  "
 amr1=ind1
 amr2=ind2
 amr3=ind1
 amr4=ind2
 ams1=amt19
 ams2=amt191
 ams3=amtt19
 ams4=amtt191
 
if int(cur1)==20:
 curc="ICT Cur Rs.  "
 amr1=ictc1
 amr2=ictc2
 amr3=ictc1
 amr4=ictc2
 ams1=amt20
 ams2=amt201
 ams3=amtt20
 ams4=amtt201
 
if int(cur1)==21:
 curc="Taka Rs.    "
 amr1=taka1
 amr2=taka2
 amr3=taka1
 amr4=taka2
 ams1=amt30
 ams2=amt301
 ams3=amtt30
 ams4=amtt301
 
# output 
print()
print("_________________________________________")
print("🌻 Institute of Computer Technology(ICT )")
print("_________________________________________")
print(datetime.datetime.now())
# number format
amt="{:,.2f}".format(amt)
amtt="{:,.2f}".format(amtt)
amr1="{:,.2f}".format(amr1)
ams1="{:,.2f}".format(ams1)
amr2="{:,.2f}".format(amr2)
ams2="{:,.2f}".format(ams2)
ams3="{:,.2f}".format(ams3)
ams4="{:,.2f}".format(ams4)
print()

print("Amount  SLR :-",amt)
print("__________________________________________")
print("Currency ..... Buy/Sel ..... Required....")
print("",curc," ",amr1,"    ",ams1)
print("               ",amr2,"    ",ams2)
print("__________________________________________")
print(" CurReq      Rs.           ",ams3)
print(" ",amtt,"  Rs.           ",ams4)
print("__________________________________________")
print("Subscribe to siva8293@gmail.com ")
cont=input("Enter Any Key to quit  " )


    
    