#!/usr/bin/python 
import sqlite3
from flask import Flask,request,jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

class InsufficientAmount(Exception):
    pass

class UserAlreadyTaken(Exception):
    pass

def connect_to_db(): 
    conn = sqlite3.connect('database.db')
    return conn

def create_db_table(): 
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
    finally: 
        conn.close()

def register(user):
    registered_user = {}
    message ={}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (fullname, username, password, age, address, gender, marital_status, wallet) VALUES (?, ?, ?, ?, ?, ?, ?, 0)"
                    , (user['fullname'], user['username'], user['password'], user['age'], user['address'], user['gender'], user['marital_status']) ) 
        if get_user_by_username(user['username']) != {}:
            raise UserAlreadyTaken("Username already taken")
        conn.commit() 
        message["status"] = "Successful Registration"
        registered_user = get_user_by_username(user["username"])
    except UserAlreadyTaken as e:
        conn.rollback() 
        message["status"] = "Username already taken"
    except:
        conn.rollback()
    finally:
         conn.close() 
    return message,registered_user

def delete(username):
    message = {} 
    user = get_user_by_username(username)
    if user == {}:
        message["status"] = "User not found"
        return message
    try: 
        conn = connect_to_db()
        conn.execute("DELETE from users WHERE username = ?", (username,)) 
        conn.commit()
        message["status"] = "User deleted successfully" 
    except: 
        conn.rollback()
        message["status"] = "Cannot delete user" 
    finally: 
        conn.close() 
    return message

def update(user):
    username = user["username"]
    message = {}
    updated_user = {} 
    l = get_user_by_username(username)
    if l == {}:
        message["status"] = 'User not found'
        return message,updated_user
    try:
        conn = connect_to_db() 
        cur = conn.cursor()
        cur.execute("UPDATE users SET fullname = ?, username = ?, password= ?, age= ?, address= ?, gender= ?, marital_status= ? WHERE username =?", 
                    (user["fullname"], user["username"], user["password"], user["age"], user["address"],user["gender"],user["marital_status"], user["username"],)) 
        conn.commit()
        updated_user = get_user_by_username(user["username"])
    except:
         conn.rollback() 
         updated_user = {} 
    finally: 
         conn.close() 
    return updated_user

def get_users(): 
    users = []
    try:
        conn = connect_to_db() 
        conn.row_factory = sqlite3.Row
        cur = conn.cursor() 
        cur.execute("SELECT * FROM users") 
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
            users.append(user)
    except:
        users = []
    return users

def get_user_by_username(username): 
    user = {}
    try:
        conn = connect_to_db() 
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?",(username,))
        row = cur.fetchone()
        user["user_id"] = row["user_id"] 
        user["fullname"] = row["fullname"] 
        user["username"] = row["username"] 
        user["password"] = row["password"] 
        user["age"] = row["age"] 
        user["address"] = row["address"] 
        user["gender"] = row["gender"] 
        user["marital_status"] = row["marital_status"]  
        user["wallet"] = row["wallet"]
    except:
        user = {}
    return user

def charge(username,amount):
    message = {}
    user = get_user_by_username(username)
    message["status"] = "Successfully charged!"
    updated_user = {} 
    try:
        conn = connect_to_db() 
        cur = conn.cursor()
        if type(amount)!= float and type(amount)!= int:
            raise TypeError
        cur.execute("UPDATE users SET  wallet= ? WHERE username =?", 
                        (amount, user["username"],)) 
        conn.commit()
        updated_user = get_user_by_username(user["username"]) 
    except:
         message["status"] = "Amount should be a number"
         conn.rollback() 
         updated_user = {} 
    finally: 
         conn.close() 
    return message,updated_user

    

def deduce(username,amount):
    message = {}
    message["status"] = "Successfully reduced!"
    user = get_user_by_username(username)
    updated_user = {} 
    try:
        conn = connect_to_db() 
        cur = conn.cursor()
        if type(amount)!= float and type(amount)!= int:
            raise TypeError
        if user["wallet"] < amount:
            raise InsufficientAmount('Not enough available to spend {}'.format(amount))
        cur.execute("UPDATE users SET  wallet= ? WHERE username =?", 
                        (user["wallet"]-amount, user["username"],)) 
        conn.commit()
        updated_user = get_user_by_username(user["username"]) 
    except InsufficientAmount:
         message["status"] = 'Not enough available to spend {}'.format(amount)
         conn.rollback() 
         updated_user = {} 
    except:
         message["status"] = "Amount should be a number"
         conn.rollback() 
         updated_user = {} 
    finally: 
         conn.close() 
    return message,updated_user


@app.route('/api/users', methods=['GET'])
def api_get_users():
    return jsonify(get_users())

@app.route('/api/users/<username>', methods=['GET'])
def api_get_user(username):
    return jsonify(get_user_by_username(username))

@app.route('/api/users/add', methods = ['POST'])
def api_add_user():
    user = request.get_json()
    return jsonify(register(user))

@app.route('/api/users/update', methods = ['PUT'])
def api_update_user():
    user = request.get_json()
    return jsonify(update(user))

@app.route('/api/users/delete/<username>', methods = ['DELETE'])
def api_delete_user(username):
    return jsonify(delete(username))


@app.route('/api/users/charge/<username>', methods = ['PUT'])
def api_charge(username):
    amount = request.get_json()
    return jsonify(charge(username,amount))

@app.route('/api/users/deduce/<username>', methods = ['PUT'])
def api_reduce(username):
    amount = request.get_json()
    return jsonify(deduce(username,amount))

if __name__ == "__main__":
    #app.debug = True
    #app.run(debug=True)
    app.run() #run app    


user1 = {
    "fullname" : "John Doe",
    "username" : "jdsd", 
    "password" : "1234", 
    "age" : "54", 
    "address" : "Beirut",
    "gender" : "male" ,
    "marital_status" : "married"
}