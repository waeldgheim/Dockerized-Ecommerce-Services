#!/usr/bin/python
import requests
import json
from flask import Flask,request,jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

class InsufficientAmount(Exception):
    pass

class OutOfStock(Exception):
    pass

def get_prices():
    """Gets the name and the price of each element in the database
    :return: A list of dictionaries each containing the name and the price of the goods
    :rtype: list
    """
    goods = []
    try:
        query = {"1":"SELECT * FROM goods"}
        goods = requests.get('http://172.17.0.2:5000/api/get', json=query).json()
    except:
        goods=[]
    return goods

def sale(username,name,amount):
    """This is called when a purchase occured. The count of the item will be reduced by a certain amount and the users wallet will
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
    user = requests.get('http://172.17.0.3:3000/api/users/{}'.format(username)).json()
    message = {}
    try:
        if user["wallet"] >= (good["price"]*amount) and good["count"] > amount:
            requests.put('http://172.17.0.3:3000/api/users/deduce/{}'.format(username),json =(good["price"]*amount))
            requests.put('http://172.17.0.4:7000/api/goods/deduce/{}'.format(name),json= amount)
        elif user["wallet"] < (good["price"]*amount):
            raise InsufficientAmount('Not enough available to spend {}'.format(good["price"]*amount))
        elif good["count"] == 0:
            raise OutOfStock('{} is out of stock'.format(good["name"]))
        elif good["count"] - amount<0:
            raise ('Not enough {} in stock'.format(good["name"]))
        message["status"] = "Purchase successful"
        save_purchase(username,name,amount)
    except InsufficientAmount:
       message["status"] = 'Not enough available to spend {}'.format(good["price"]*amount)
    except OutOfStock:
       message["status"] = '{} is out of stock'.format(good["name"])
    except:
       message["status"] ='Not enough {} in stock'.format(good["name"])
    return message

def save_purchase(username,name,amount):
    """Saves the purchase made by a customer in the databse by saving his username and the name of the item
    :param username: username of the user who made the purchase
    :type username: string
    :param name: name of the item that got purchased
    :type name: string
    """
    l = {"username" : username,"name" : name, "amount":amount}
    query = {"1":"INSERT INTO history (name, item,amount) VALUES (?, ?, ?)",
                "2": (l['username'], l['name'],l['amount']) }
    requests.post('http://172.17.0.2:5000/api/post', json=query)

def get_history(username):
    """Given the username of the customer, this function returns the purchase history of this customer by
    adding the item to a dictionary. If it was already found, increase it value by one. If not, initialize it to 1.
    :param username: username of the customer whose history we want
    :type username: string
    :return: Purchase history of the customer
    :rtype: dictionary
    """
    history = {}
    try:
        query = {"1":"SELECT * FROM history WHERE name = ?",
                    "2":(username,)}
        history = requests.get('http://172.17.0.2:5000/api/get', json=query).json()
    except:
        history = {}
    return history

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
    amount = request.get_json()
    return jsonify(sale(username,name,amount))

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
    app.run(host ='0.0.0.0',port=8000) #run app