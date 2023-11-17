#!/usr/bin/python 
import sqlite3
from flask import Flask,request,jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

class CategoryNotFound(Exception):
    pass

class OutOfStock(Exception):
    pass

class AlreadyRegistered(Exception):
    pass

def connect_to_db(): 
    conn = sqlite3.connect('database.db')
    return conn

def create_db_table(): 
    try: 
        conn = connect_to_db()
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
        print("User table created successfully") 
    except: 
        print("User table creation failed - Maybe table") 
    finally: 
        conn.close()

def add_goods(good):
    message ={}
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO goods (name,category,price,description,count) VALUES (?, ?, ?, ?, ?)"
                , (good['name'], good['category'], good['price'], good['description'], good['count']) ) 
    try:
        if good["category"].lower() !="food" and  good["category"].lower() !="clothes" and good["category"].lower() !="accessories" and good["category"].lower() !="electronics":
            message["status"] = "Category is invalid"
            raise CategoryNotFound ("Category is invalid")
        conn.commit() 
        message["status"] = "Successful Registration"
    except CategoryNotFound:
        conn.rollback()
        return message
    except:
        conn.rollback()
    finally:
         conn.close() 
    return message,good

def deduce(name):
    good = get_good_by_name(name)
    updated_good = {}
    message = {}
    if good == {}:
        message["status"] = 'Good not found'
        return message,updated_good
    try:
        conn = connect_to_db() 
        cur = conn.cursor()
        if good["count"] - 1 <0:
            raise OutOfStock ("Good is out of stock")
        cur.execute("UPDATE goods SET count= ? WHERE name =?", 
                    (good["count"] - 1, good["name"],))
        conn.commit()
        updated_good = get_good_by_name(good["name"])
        message["status"] = "Succefully deduced item"
    except OutOfStock:
        conn.rollback() 
        message['status'] = "Good is out of stock"
    except:
         print("ka")
         conn.rollback() 
         updated_good = {} 
    finally: 
         conn.close() 
    return message,updated_good

def update(good):
    name = good["name"]
    message = {}
    updated_good = {} 
    l = get_good_by_name(name)
    if l == {}:
        message["status"] = 'Good not found'
        return message,updated_good
    try:
        conn = connect_to_db() 
        cur = conn.cursor()
        cur.execute("UPDATE goods SET name = ?, category = ?, price= ?, description= ?, count= ? WHERE name =?", 
                    (good["name"], good["category"], good["price"], good["description"], good["count"], good["name"],)) 
        conn.commit()
        updated_good = get_good_by_name(good["name"])
        message["status"] = "Succefully updated good"
    except:
         print("hon")
         conn.rollback() 
         updated_good = {} 
    finally: 
         conn.close() 
    return message,updated_good


def get_good_by_name(name): 
    good = {}
    try:
        conn = connect_to_db() 
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM goods WHERE name = ?",(name,))
        row = cur.fetchone()
        good["user_id"] = row["user_id"] 
        good["name"] = row["name"] 
        good["category"] = row["category"] 
        good["price"] = row["price"] 
        good["description"] = row["description"] 
        good["count"] = row["count"] 
    except:
        good = {}
    return good

@app.route('/api/goods/add', methods = ['POST'])
def api_add_user():
    good = request.get_json()
    return jsonify(add_goods(good))

@app.route('/api/goods/deduce/<name>', methods = ['PUT'])
def api_reduce(name):
    return jsonify(deduce(name))

@app.route('/api/goods/update', methods = ['PUT'])
def api_update_user():
    good = request.get_json()
    return jsonify(update(good))

if __name__ == "__main__":
    #app.debug = True
    #app.run(debug=True)
    app.run() #run app