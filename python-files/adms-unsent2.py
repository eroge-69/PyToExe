import mysql.connector
import datetime
import sys
import time

now = datetime.datetime.now()
tgljam = now.strftime("%Y-%m-%d %H:%M")
tgl = now.strftime("%Y-%m-%d")
date = now.strftime("%m%d%Y")
jam = now.strftime("%H%M")
datefilename = now.strftime("%m%d%Y%H%M")
v_dataon_date= now.strftime("%Y-%m-%d %H:%M")

# connect to mysql database
mydb = mysql.connector.connect(
  host="10.10.252.36",
  port="17770",
  user="adms",
  passwd="adms135",
  database="adms_db",
  charset="utf8"
)

#date = input("input date (mmddyyyy)?")
sql="""
	SELECT
		id,
		RIGHT(CONCAT('0000000000',userinfo.`badgenumber`),10) as userid,
		DATE_FORMAT(checktime,'%Y%m%d') as tanggal,
		DATE_FORMAT(checktime,'%H%i') as jam,
		checktime,
		dataon
	FROM checkinout
	LEFT OUTER JOIN userinfo on (checkinout.userid = userinfo.userid) 
	WHERE DATE_FORMAT(checktime,'%Y%m') >= DATE_FORMAT(NOW() - INTERVAL 60 DAY,'%Y%m') AND dataon<1
	"""
#print (sql) #test sql

#print(mydb) #test connection

mycursor = mydb.cursor()
myupdate = mydb.cursor()



mycursor.execute(sql)
tot_row =0
myresult = mycursor.fetchall()
tot_row = mycursor.rowcount

f = open("BMSS"+datefilename+".txt", "w")
i = 0
j = 0

for x in myresult:
	#print(x)
	tex=x[1] + "," + x[2] + "," + x[3] +"\r"
	f.write(tex)
	i=i+1
	print (i," of ",tot_row," rows")
	myupdate.execute("UPDATE checkinout SET dataon=1, dataon_date=%s WHERE id=%s AND checktime=%s and dataon<1",(datefilename,x[0],x[4]))
	j=j+myupdate.rowcount

print ("100% Complete")

f.close()
mydb.commit()
print(i," row(s) write to file, ",j, " record(s) updated")
time.sleep( 5 )
