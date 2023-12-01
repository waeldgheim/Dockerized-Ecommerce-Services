import sqlite3

def connect_to_db(): 
    #Connect to database
    conn = sqlite3.connect('database.db')
    return conn

def create_db_table(): 
    #Creates the 3 tables user, inventory, and history
    try: 
        conn = connect_to_db()
        conn.execute(''' 
                     CREATE TABLE users ( 
                      user_id INTEGER PRIMARY KEY NOT NULL,
                      fullname TEXT NOT NULL,
                      username TEXT NOT NULL,
                      password TEXT NOT NULL,
                      age TEXT NOT NULL,
                      address TEXT NOT NULL,
                      gender TEXT NOT NULL,
                      marital_status TEXT NOT NULL,
                      wallet INTEGER NOT NULL DEFAULT 0
                      ); 
                    ''')
        conn.commit() 
        print("User table created successfully") 
    except: 
        print("User table creation failed - Maybe table") 

    try:
        conn.execute(''' 
                     CREATE TABLE goods ( 
                      user_id INTEGER PRIMARY KEY NOT NULL,
                      name TEXT NOT NULL,
                      category TEXT NOT NULL,
                      price FLOAT NOT NULL,
                      description TEXT NOT NULL,
                      count INTEGER NOT NULL
                      ); 
                    ''')   
        conn.commit() 
        print("Goods table created successfully") 
    except: 
        print("Goods table creation failed - Maybe table")
    try:
        conn.execute(''' 
                    CREATE TABLE history ( 
                    user_id INTEGER PRIMARY KEY NOT NULL,
                    name TEXT NOT NULL,
                    item TEXT NOT NULL
                    ); 
                ''')   
        conn.commit() 
        print("History table created successfully") 
    except: 
        print("History table creation failed - Maybe table") 

    finally: 
        conn.close()

connect_to_db()
create_db_table()