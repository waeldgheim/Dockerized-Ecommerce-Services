#!/usr/bin/python 
import requests
from flask import Flask,request,jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

class InsufficientAmount(Exception):
    pass

class UserAlreadyTaken(Exception):
    pass

def register(user):
    """Registers the user in the database, checks if the username is already in use, and creates a wallet for the user 
    initialized to 0$
    :param user: contains all information about the customer
    :type user: dictionary
    :raises UserAlreadyTaken: if the user's username is already in the database, it doesn't allow him to register
    :return: A message confirming registration status and the infromation of the registered user
    :rtype: Both are dictionaries
    """
    registered_user = {}
    message ={}
    try:
        if get_user_by_username(user['username']) != {}:
            raise UserAlreadyTaken("Username already taken")
        query = {"1":"INSERT INTO users (fullname, username, password, age, address, gender, marital_status, wallet) VALUES (?, ?, ?, ?, ?, ?, ?, 0)"
                , "2":(user['fullname'], user['username'], user['password'], user['age'], user['address'], user['gender'], user['marital_status']) }
        requests.post('http://172.17.0.2:5000/api/post', json=query)
        message["status"] = "Successful Registration"
        registered_user = user
    except UserAlreadyTaken as e:
        message["status"] = "Username already taken"
    finally:
        return message,registered_user

def delete(username):
    """Deletes the user, if found, from the database
    :param username: the username of the user to be deleted
    :type user: string
    :return: A message confirming deletion status
    :rtype: Dictionary
    """
    message = {}
    user = get_user_by_username(username)
    if user == {}:
        message["status"] = "User not found"
        return message
    try: 
        query={"1":"DELETE from users WHERE username = ?", 
               "2":(username,)}
        requests.delete('http://172.17.0.2:5000/api/delete', json=query)
        message["status"] = "User deleted successfully" 
    except: 
        message["status"] = "Cannot delete user" 
    finally: 
        return message

def update_user(user):
    """Updates the user in the database having the same username as the user passed as a parameter. It check if the 
    user is found in the database. The wallet can't be updated using this function.
    :param user: contains all information about the updated customer
    :type user: dictionary
    :return: The information of the updated user if update is complete, a message if update fails
    :rtype: Both are dictionaries
    """
    username = user["username"]
    message = {}
    updated_user = {} 
    l = get_user_by_username(username)
    if l == {}:
        message["status"] = 'User not found'
        return message,updated_user
    try:
        query = {"1":"UPDATE users SET fullname = ?, username = ?, password= ?, age= ?, address= ?, gender= ?, marital_status= ? WHERE username =?", 
                 "2": (user["fullname"], user["username"], user["password"], user["age"], user["address"],user["gender"],user["marital_status"], user["username"],)}
        requests.put('http://172.17.0.2:5000/api/put', json=query)
        message["status"] = "Succefully updated customer"
        updated_user = get_user_by_username(user["username"])
    except:
         message["status"] = "Unsuccessful update"
         updated_user = {} 
    finally: 
        return message,updated_user

def get_users():
    """Get all users from the database
    :return: list containing information of all users
    :rtype: List of dictionaries
    """
    users = []
    try:
        query = {"1":"SELECT * FROM users"}
        users = requests.get('http://172.17.0.2:5000/api/get', json=query).json()
    except:
        users = []
    return users

def get_user_by_username(username): 
    """Gets information of a specific user through his username
    :param username: The username of the wanted customer
    :type user: string
    :return: The information of the the wanted user
    :rtype: Dictionary
    """
    user = {}
    try:
        query = {"1":"SELECT * FROM users WHERE username = ?",
                "2":(username,)}
        user = requests.get('http://172.17.0.2:5000/api/get', json=query).json()
    except:
        user = {}
    return user

def charge(username,amount):
    """Increasing the wallet of the user by a number (amount)
    :param username: the username of the user whose wallet is to be modified
    :type username: string
    :param amount: amount we want to add to the wallet
    :type amount: float
    :raises TypeError: if the amount given is not in integers nor float, it raises the error
    :return: A message confirming the status of charging and the updated user
    :rtype: Both are dictionaries
    """
    message = {}
    user = get_user_by_username(username)
    message["status"] = "Successfully charged!"
    updated_user = {} 
    try:
        if type(amount)!= float and type(amount)!= int:
            raise TypeError
        query= {"1":"UPDATE users SET  wallet= ? WHERE username =?", 
                "2": (user["wallet"]+amount, user["username"],) }
        requests.put('http://172.17.0.2:5000/api/put', json=query)
        updated_user = get_user_by_username(user["username"]) 
    except:
         message["status"] = "Amount should be a number" 
         updated_user = {} 
    finally: 
        return message,updated_user

    
def deduce_wallet(username,amount):
    """Decreasing the wallet of the user by a number (amount)
    :param username: the username of the user whose wallet is to be modified
    :type username: string
    :param amount: amount we want to reduce from the wallet
    :type amount: float
    :raises TypeError: if the amount given is not in integers nor float, it raises the error
    :raises InsufficientAmount: if the user's wallet has less then the amount to be reduced, the error is raised
    :return: A message confirming the status of reducing and the updated user
    :rtype: Both are dictionaries
    """
    message = {}
    message["status"] = "Successfully reduced!"
    user = get_user_by_username(username)
    updated_user = {} 
    try:
        if type(amount)!= float and type(amount)!= int:
            raise TypeError
        if user["wallet"] < amount:
            raise InsufficientAmount('Not enough available to spend {}'.format(amount))
        query = {"1":"UPDATE users SET  wallet= ? WHERE username =?", 
                 "2":(user["wallet"]-amount, user["username"],)}
        requests.put('http://172.17.0.2:5000/api/put', json=query)
        updated_user = get_user_by_username(user["username"]) 
    except InsufficientAmount:
         message["status"] = 'Not enough available to spend {}'.format(amount)
         updated_user = {} 
    except:
         message["status"] = "Amount should be a number" 
         updated_user = {} 
    finally: 
        return message,updated_user


@app.route('/api/users', methods=['GET'])
def api_get_users():
    """API implementation of get_users()
    :return: the information of all users in the database
    :rtype: json object
    """
    return jsonify(get_users())

@app.route('/api/users/<username>', methods=['GET'])
def api_get_user(username):
    """API implementation of get_user_by_username()
    :param username: the username of the user whose information we are getting
    :type username: string
    :return: the information of the user
    :rtype: json object
    """
    return jsonify(get_user_by_username(username))

@app.route('/api/users/add', methods = ['POST'])
def api_add_user():
    """API implementation of register()
    :return: A message confirming registration status and the infromation of the registered user
    :rtype: json object
    """
    user = request.get_json()
    return jsonify(register(user))

@app.route('/api/users/update', methods = ['PUT'])
def api_update_user():
    """API implementation of update_user()
    :return: The information of the updated user if update is complete, a message if update fails
    :rtype: json object
    """
    user = request.get_json()
    return jsonify(update_user(user))

@app.route('/api/users/delete/<username>', methods = ['DELETE'])
def api_delete_user(username):
    """API implementation of delete()
    :param username: the username of the user whom we're deleting
    :type username: string
    :return: A message confirming deletion status
    :rtype: json object
    """
    return jsonify(delete(username))


@app.route('/api/users/charge/<username>', methods = ['PUT'])
def api_charge(username):
    """API implementation of charge()
    :param username: the username of the user whose wallet we're charging
    :type username: string
    :return: A message confirming the status of charging and the updated user
    :rtype: json object
    """
    amount = request.get_json()
    return jsonify(charge(username,amount))

@app.route('/api/users/deduce/<username>', methods = ['PUT'])
def api_reduce(username):
    """API implementation of deduce_wallet()
    :param username: the username of the user whose wallet we're decreasing
    :type username: string
    :return: A message confirming the status of deducing and the updated user
    :rtype: json object
    """
    amount = request.get_json()
    return jsonify(deduce_wallet(username,amount))

if __name__ == "__main__":
    """Runs the flask app
    """
    app.run(host="0.0.0.0",port=3000) #run app   