import sqlite3 as sql

print("1 - добавление\n2 - получение\n3 - удаление")
choice = int(input("> "))
con = sql.connect('test.db')
with con:
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS `test` (`name` STRING, `surname` STRING)")

    if choice == 1:
        name = input("Name\n> ")
        surname = input("Surname\n> ")
        cur.execute(f"INSERT INTO `test` VALUES ('{name}', '{surname}')")
    elif choice == 2:
        cur.execute("SELECT * FROM `test`")
        rows = cur.fetchall()
        for row in rows:
            print(row[0], row[1])
    elif choice == 3:
        uuu = input("Имя: ")
        cur.execute('DELETE FROM test WHERE name = ?', (uuu,))
    else:
        print("Вы ошиблись")

    con.commit()
    cur.close()