#!/usr/bin/python 
import sqlite3
from customer import *
from inventory import *
from flask import Flask,request,jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


def connect_to_db(): 
    """Connects to the database
    """
    conn = sqlite3.connect('database.db')
    return conn

def get_prices():
    """Gets the name and the price of each element in the database
    :return: A list of dictionaries each containing the name and the price of the goods
    :rtype: list
    """
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
    """This is called when a purchase occured. The count of the item will be reduced by one and the users wallet will
    be reduced by the price by the item. It also calls the function to save the purchase in the database.
    :param username: username of the user who made the purchase
    :type username: string
    :param name: name of the item that got purchased
    :type name: string
    :raises InsufficientAmount: if the user doesn't have the item's price in his wallet, the error will be raised
    :raises OutOfStock: if the item's count is equal to 0, the error will be raised
    :return: A message confirming purchase status
    :rtype: Dictionary
    """
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
    """Saves the purchase made by a customer in the databse by saving his username and the name of the item
    :param username: username of the user who made the purchase
    :type username: string
    :param name: name of the item that got purchased
    :type name: string
    """
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
    """Given the username of the customer, this function returns the purchase history of this customer by
    adding the item to a dictionary. If it was already found, increase it value by one. If not, initialize it to 1.
    :param username: username of the customer whose history we want
    :type username: string
    :return: Purchase history of the customer
    :rtype: dictionary
    """
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
    """API implementation of get_prices()
    :return: the prices of all items in the database
    :rtype: json object
    """
    return jsonify(get_prices())

@app.route('/api/goods/<name>', methods=['GET'])
def api_get_good(name):
    """API implementation of get_good_by_name()
    :param name: name of the good whose details we want
    :type name: string 
    :return: the information of the item
    :rtype: json object
    """
    return jsonify(get_good_by_name(name))

@app.route('/api/sale/<username>,<name>', methods = ['POST'])
def api_sale(username,name):
    """API implementation of sale()
    :param username: username of the customer who did the purchase
    :type username: string 
    :param name: name of the good that got purchased
    :type name: string 
    :return: A message confirming purchase status
    :rtype: json object
    """
    return jsonify(sale(username,name))

@app.route('/api/history/<username>', methods=['GET'])
def api_history(username):
    """API implementation of get_history()
    :param username: username of the customer whose history we're seeking
    :type username: string 
    :return: Purchase history of the customer
    :rtype: json object
    """
    return jsonify(get_history(username))

if __name__ == "__main__":
    #app.debug = True
    #app.run(debug=True)
    app.run() #run app