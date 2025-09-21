import fdb  
 
f = open('dbversion.txt', 'r') 
 
ver = f.read() 
 
print (ver) 
 
 def Del_User_RBD(): 
     con = fdb.connect(dsn=f'10.64.4.11:/cluster/db/ncore-fssp-rbd-{ver}.fdb', user='sysdba', password='�#j') 
     cur = con.cursor() 
     cur.execute("delete from mon$attachments where mon$user containing '@r64' or mon$remote_process containing 'IBExpert' or mon$remote_process containing 'RedExpert'") 
     con.commit() 
    con.close() 
def Del_User_ED(): 
    con = fdb.connect(dsn=f'10.64.4.10:/cluster/db/ncore-fssp-{ver}.fdb', user='sysdba', password='�#j') 
    cur = con.cursor() 
    cur.execute("select * from mon$attachments where mon$user containing '@r64' or mon$remote_process containing 'IBExpert' or mon$remote_process containing 'RedExpert'") 
    cur.execute("delete from mon$attachments where mon$user containing '@r64' or mon$remote_process containing 'IBExpert' or mon$remote_process containing 'RedExpert'") 
    print(cur.fetchall()) 
    con.commit() 
    con.close() 
 
Del_User_RBD() 
Del_User_ED()
