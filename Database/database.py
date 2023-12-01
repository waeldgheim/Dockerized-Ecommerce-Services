import sqlite3
import requests
from flask import Flask,request, jsonify

app = Flask(__name__)


def create_db_table(): 
    #Creates the 3 tables user, inventory, and history
    try: 
        conn = sqlite3.connect('database.db')
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
                    item TEXT NOT NULL,
                    amount INTEGER NOT NULL DEFAULT 0
                    ); 
                ''')   
        conn.commit() 
        print("History table created successfully") 
    except: 
        print("History table creation failed - Maybe table") 

    finally: 
        conn.close()

sqlite3.connect('database.db')
create_db_table()

@app.route('/api/get',methods=['GET'])
def api_get():
    '''Receives API Get requests from other containers and process them
    '''
    res = {}
    res1 = []
    query = request.get_json()
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        if query["1"] == "SELECT * FROM users":
            cur.execute(query["1"])
            rows = cur.fetchall()
            for i in rows:
                user = {}
                user["user_id"] = i["user_id"] 
                user["fullname"] = i["fullname"] 
                user["username"] = i["username"] 
                user["password"] = i["password"] 
                user["age"] = i["age"] 
                user["address"] = i["address"] 
                user["gender"] = i["gender"] 
                user["marital_status"] = i["marital_status"] 
                user["wallet"] = i["wallet"]
                res1.append(user)
            conn.close()
            return res1
        
        elif query["1"] == "SELECT * FROM goods":
            cur.execute(query["1"])
            rows = cur.fetchall()
            for i in rows:
                good = {}
                good["name"] = i["name"] 
                good["price"] = i["price"] 
                res1.append(good)
            conn.close()
            return res1
        
        else:
            cur.execute(query["1"],tuple(query["2"]))
            
            if query["1"] == "SELECT * FROM users WHERE username = ?":
                row = cur.fetchone()
                res["user_id"] = row["user_id"] 
                res["fullname"] = row["fullname"] 
                res["username"] = row["username"] 
                res["password"] = row["password"] 
                res["age"] = row["age"] 
                res["address"] = row["address"] 
                res["gender"] = row["gender"] 
                res["marital_status"] = row["marital_status"]  
                res["wallet"] = row["wallet"]
                conn.close()
                return res

            elif query["1"] == "SELECT * FROM goods WHERE name = ?":
                row = cur.fetchone()
                res["user_id"] = row["user_id"] 
                res["name"] = row["name"] 
                res["category"] = row["category"] 
                res["price"] = row["price"] 
                res["description"] = row["description"] 
                res["count"] = row["count"] 
                conn.close()
                return res

            elif query["1"] == "SELECT * FROM history WHERE name = ?":
                rows = cur.fetchall()
                for row in rows:
                    if row["item"] in res:
                        res[row["item"]] += row["amount"]
                    else:
                        res[row["item"]] = row["amount"]
                conn.close()
                return res
    except:
       conn.rollback()
    finally:
       conn.close()
    return {}

@app.route('/api/post',methods=['POST'])
def api_post():
    '''Receives API POST requests from other containers and process them
    '''
    try:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        query = request.get_json()
        cur.execute(query["1"],tuple(query["2"]))
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()
    return {}
    
@app.route('/api/put',methods=['PUT'])
def api_put():
    '''Receives API PUT requests from other containers and process them
    '''
    try:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        query = request.get_json()
        cur.execute(query["1"],tuple(query["2"]))
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()
        return {}
    
@app.route('/api/delete',methods=['DELETE'])
def api_delete():
    '''Receives API DELETE requests from other containers and process them
    '''
    try:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        query = request.get_json()
        cur.execute(query["1"],tuple(query["2"]))
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()
        return {}
    
if __name__ == "__main__":
    """Runs the flask app
    """
    app.run(host="0.0.0.0",port=5000) #run app  