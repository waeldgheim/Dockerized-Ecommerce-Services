#!/usr/bin/python 
import requests
import json
from flask import Flask,request,jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

class CategoryNotFound(Exception):
    pass

class OutOfStock(Exception):
    pass

class InsuffcientAmount(Exception):
    pass

class AlreadyRegistered(Exception):
    pass


def add_goods(good):
    """Adds the good to the database
    :param good: Contains information about the good
    :type user: dictionary
    :raises CategoryNotFound: if the category is invalid, the error will be raised
    :return: A message confirming registration status and the information of the registered good
    :rtype: Both are dictionaries
    """
    message ={}
    try:
        if good["category"].lower() !="food" and  good["category"].lower() !="clothes" and good["category"].lower() !="accessories" and good["category"].lower() !="electronics":
            raise CategoryNotFound ("Category is invalid")
        query = {"1":"INSERT INTO goods (name,category,price,description,count) VALUES (?, ?, ?, ?, ?)"
                , "2": [good['name'], good['category'], good['price'], good['description'], good['count']]}
        requests.post('http://172.17.0.2:5000/api/post', json=query)
        message["status"] = "Successful Registration"
    except:
        message["status"] = "Category is invalid"
        good = {}
    finally:
        return message,good

def deduce_good(name,amount):
    """Reduces the count of the good by a certain number
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
        if good["count"]  == 0:
            raise OutOfStock ("Good is out of stock")
        elif good["count"] - amount < 0:
            raise InsuffcientAmount("Not enough ")
        query = {"1":"UPDATE goods SET count= ? WHERE name =?", 
                "2":(good["count"] - amount, good["name"],)}
        requests.put('http://172.17.0.2:5000/api/put', json=query)
        updated_good = get_good_by_name(good["name"])
        message["status"] = "Succefully deduced item"
    except OutOfStock:
        message['status'] = "Good is out of stock"
    except InsuffcientAmount:
        message['status']='Not enough {} in stock'.format(good["name"])
    except:
         updated_good = {} 
    finally: 
        return message,updated_good

def update_good(good):
    """Updates the information of a specified good
    :param good: contains the information of the specified good
    :type name: dictionary
    :return: A message confirming update status and the information of the updated good
    :rtype: Both are dictionaries
    """
    message = {}
    updated_good = {} 
    l = get_good_by_name(good["name"])
    if l == {}:
       message["status"] = 'Good not found'
       return message,updated_good
    try:
        if good["category"].lower() !="food" and  good["category"].lower() !="clothes" and good["category"].lower() !="accessories" and good["category"].lower() !="electronics":
            raise CategoryNotFound ("Category is invalid")
        query = {"1": "UPDATE goods SET name = ?, category = ?, price= ?, description= ?, count= ? WHERE name =?", 
                 "2": (good["name"], good["category"], good["price"], good["description"], good["count"], good["name"],)}
        requests.put('http://172.17.0.2:5000/api/put', json=query)
        message["status"] = "Succefully updated good"
        updated_good = good
    except:
         updated_good = {}
         message["status"] = "Category is invalid"
    finally:
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
        query = {"1":"SELECT * FROM goods WHERE name = ?",
                 "2":(name,)}
        good = requests.get('http://172.17.0.2:5000/api/get', json=query).json()
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
    amount = request.get_json()
    return jsonify(deduce_good(name,amount))

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
    app.run(host ='0.0.0.0',port=7000) #run app