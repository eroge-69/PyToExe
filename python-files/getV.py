import pymysql.cursors
import openpyxl
from datetime import datetime

ho='koji.mysql.tools'
pw='Xb4f6H79mV' #Qqaa11qq
nam='koji_eco'
p='pha.xlsx'


x=[['CO','b'],
      ['SO2','c'],
      ['NO2','d'],
      ['NO','e'],
      ['H2S','f'],
      ['O3','g'],
      ['NH3','h'],
      ['PM2_5','i'],
      ['PM10','j'],
      ['PSum','k'],
      ['R','l']]
av=['avg(%s) as %s' % (i[0],i[0]) for i in x[:-2]]+['avg(PM2_5)+avg(PM10) as PSum']

id={
      'Bila_Tserkva':['"Біла Церква"', '"x" as R'],
      'Bohuslav':  ['"Богуслав"', 'avg(R) as R'],
      'Boryspil':  ['"Бориспіль"', 'avg(R) as R'],
      'Boyarka':   ['"Боярка"', 'avg(R) as R'],
      'Brovary':   ['"Бровари"', '"x" as R'],
      'Dymerka':   ['"Велика Димерка"', 'avg(R) as R'],
      'Ivankiv':   ['"Іванків"', 'avg(R) as R'],
      'Kaharlyk':  ['"Кагарлик"','avg(R) as R'],
      'Uzyn':      ['"Узин"','avg(R) as R'],
      'Obukhiv':   ['"Обухів"','"x" as R'],
      'Pereiaslav':['"Перяслав"','avg(R) as R'],
      'Irpin':    ['"Ірпінь"','"x" as R'],
      'Pidhirtsi':['"Підгірці"','"x" as R'],
      'Vasylkiv': ['"Васильків"','avg(R) as R'],
      'Vyshhorod':['"Вишгород"','avg(R) as R'],
      'Vyshneve': ['"Вишневе"','avg(R) as R']
}

da=datetime.now()

h=input('Время (текущий час - %d, Ентер) '%da.hour) or str(da.hour)
d=input('Дата (текущая дата %s, Ентер) '%datetime.strftime(da,'%Y-%m-%d')) or datetime.strftime(da,'%Y-%m-%d')
cdi=' group by date(timestamp), hour(timestamp) having date(timestamp)="%s" and hour(timestamp)=%s;' %(d,h)
sub={j:','.join(['select timestamp',id[j][0]+' as na']+av+[id[j][1]])+' from koji_modbus.%s'+ cdi for j in id}


b=openpyxl.load_workbook(p)
s=b.active
s['l2'].value=datetime.strptime(d, '%Y-%m-%d').date()
s['k2'].value='%s год.'%h
konekt=pymysql.connect(host=ho,user=nam,password=pw,cursorclass=pymysql.cursors.DictCursor)
ku=konekt.cursor()
n=5
for i in sub:
      print (i)
      ku.execute(sub[i]%i)
      aa=ku.fetchall()
      if len(aa)==0:
            for j in x:
                  s[j[1]+str(n)].value='ab'
                  s['a'+str(n)].value=id[i][0]
      else:
            a=aa[0]
            for j in x:
                  s[j[1]+str(n)].value=a[j[0]]
                  s['a'+str(n)].value=id[i][0]

      n=n+1
b.save(p)
ku.close()
konekt.close()
##del b,n,ku,konekt,s,sub,cdi,d,h,ho,pw,id,p,nam,x


