#!/usr/bin/python 
import sqlite3
from customer import *
from inventory import *
from flask import Flask,request,jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


def connect_to_db(): 
    conn = sqlite3.connect('database.db')
    return conn

def get_prices():
    goods = []

    conn = connect_to_db() 
    conn.row_factory = sqlite3.Row
    cur = conn.cursor() 
    cur.execute("SELECT * FROM goods") 
    rows = cur.fetchall()
    for i in rows:
        good = {}
        good["name"] = i["name"] 
        good["price"] = i["price"] 
        goods.append(good)
    
    return goods

def sale(username,name):
    good = get_good_by_name(name)
    user = get_user_by_username(username)
    message = {}
    try:
        if user["wallet"] >= good["price"] and good["count"] > 0:
            deduce_wallet(username,good["price"])
            deduce_good(name)
        elif user["wallet"] < good["price"]:
            raise InsufficientAmount('Not enough available to spend {}'.format(good["price"]))
        elif good["count"] == 0:
            raise OutOfStock('{} is out of stock'.format(good["name"]))
        message["status"] = "Purchase successful"
        save_purchase(username,name)
    except InsufficientAmount:
        message["status"] = 'Not enough available to spend {}'.format(good["price"])
    except OutOfStock:
        message["status"] = '{} is out of stock'.format(good["name"])
    except:
        message["status"] = 'Purchase Failed'
    return message

def save_purchase(username,name):
    l = {"username" : username,"name" : name}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO history (name, item) VALUES (?, ?)"
                    , (l['username'], l['name']) ) 
        conn.commit() 
    except:
        conn.rollback()
    finally:
         conn.close() 

def get_history(username):
    history = {}

    conn = connect_to_db() 
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM history WHERE name = ?",(username,))
    rows = cur.fetchall()
    for row in rows:
        if row["item"] in history:
            history[row["item"]] += 1
        else:
            history[row["item"]] = 1

    return history

@app.route('/api/prices', methods=['GET'])
def api_get_prices():
    return jsonify(get_prices())

@app.route('/api/goods/<name>', methods=['GET'])
def api_get_user(name):
    return jsonify(get_good_by_name(name))

@app.route('/api/sale/<username>,<name>', methods = ['POST'])
def api_sale(username,name):
    return jsonify(sale(username,name))

@app.route('/api/history/<username>', methods=['GET'])
def api_history(username):
    return jsonify(get_history(username))

if __name__ == "__main__":
    #app.debug = True
    #app.run(debug=True)
    app.run() #run app    