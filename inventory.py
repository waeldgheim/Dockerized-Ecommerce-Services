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
    """Connects to the database
    """
    conn = sqlite3.connect('database.db')
    return conn

def add_goods(good):
    """Adds the good to the database
    :param good: Contains information about the good
    :type user: dictionary
    :raises CategoryNotFound: if the category is invalid, the error will be raised
    :return: A message confirming registration status and the information of the registered good
    :rtype: Both are dictionaries
    """
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

def deduce_good(name):
    """Reduces the count of the good by one
    :param name: Name of the good whose count we want to reduce
    :type name: string
    :raises OutOfStock: when the count of the good = 0 before deduction, the error will be raised
    :return: A message confirming deduction status and the information of the updated good
    :rtype: Both are dictionaries
    """
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
         conn.rollback() 
         updated_good = {} 
    finally: 
         conn.close() 
    return message,updated_good

def update_good(good):
    """Updates the information of a specified good
    :param good: contains the information of the specified good
    :type name: dictionary
    :return: A message confirming update status and the information of the updated good
    :rtype: Both are dictionaries
    """
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
         conn.rollback() 
         updated_good = {} 
    finally: 
         conn.close() 
    return message,updated_good


def get_good_by_name(name): 
    """Get the information of the good from the database using its name
    :param name: Name of the good we want to extract
    :type name: string
    :return: the information of the specified good
    :rtype: dictionary
    """
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
    """API implementation of add_goods()
    :return: A message confirming registration status and the infromation of the registered good
    :rtype: json object
    """  
    good = request.get_json()
    return jsonify(add_goods(good))

@app.route('/api/goods/deduce/<name>', methods = ['PUT'])
def api_reduce(name):
    """API implementation of deduce_good()
    :param name: the name of the good whose count we're reducing
    :type name: string
    :return: A message confirming deduction status and the information of the updated good
    :rtype: json object
    """
    return jsonify(deduce_good(name))

@app.route('/api/goods/update', methods = ['PUT'])
def api_update_user():
    """API implementation of update_good()
    :return: A message confirming update status and the information of the updated good
    :rtype: json object
    """
    good = request.get_json()
    return jsonify(update_good(good))

if __name__ == "__main__":
    """Runs the flask app
    """
    #app.debug = True
    #app.run(debug=True)
    app.run() #run app