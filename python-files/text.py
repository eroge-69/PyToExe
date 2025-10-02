import mysql.connector
#ساخت_سرور
db_host = "localhost"
db_user = "root"
db_pass = "1234"  
db_name = "car"

schema = """
create table if not exists cars (
    id int auto_increment primary key,
    company            varchar(50) not null,
    model              varchar(50) not null,
    product_year       int not null check(product_year between 1995 and 2025),
    color              varchar(50) not null,
    passenger_capacity int not null check(passenger_capacity between 2 and 8),
    price              int not null check(price > 1000),
    petrol             tinyint not null,
    gas                tinyint not null,
    electric           tinyint not null,
    trunk              tinyint not null,
    transmission       varchar(30) not null,
    distance           float not null,
    fuel_tank          int not null,
    created_at         timestamp default current_timestamp
);
"""

def init_db():
    con = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass
    )
    cur = con.cursor()
    cur.execute(f"create database if not exists {db_name}")
    cur.execute(f"use {db_name}")
    cur.execute(schema)
    con.commit()
    cur.close()
    con.close()

if __name__ == "__main__":
    init_db()
    print("MySQL db ready:", db_name)
