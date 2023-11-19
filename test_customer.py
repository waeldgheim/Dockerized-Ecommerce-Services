import pytest
from customer import *
from flask import json

@pytest.fixture
def customer1():
    customer = {
        "fullname" : "John Doe",
        "username" : "john", 
        "password" : "1234", 
        "age" : "54", 
        "address" : "Beirut",
        "gender" : "male" ,
        "marital_status" : "married"
    }
    return customer

@pytest.fixture
def customer1_same_username():
    customer = {
        "fullname" : "John Wick",
        "username" : "john", 
        "password" : "5678", 
        "age" : "44", 
        "address" : "US",
        "gender" : "male" ,
        "marital_status" : "divorced"
    }
    return customer

@pytest.fixture
def customer_not_found():
    customer = {
        "fullname" : "Afif Itani",
        "username" : "afif", 
        "password" : "4568", 
        "age" : "67", 
        "address" : "Beirut",
        "gender" : "male" ,
        "marital_status" : "single"
    }
    return customer



def test_register(customer1):
    x,y = register(customer1)
    assert x["status"] == "Successful Registration"
    assert y["wallet"] == 0
    assert y["username"] == customer1["username"]

def test_register_taken_username(customer1_same_username):
    x,y = register(customer1_same_username)
    assert x["status"] == "Username already taken"
    assert y == {}

def test_update_user(customer1_same_username):
    x = update_user(customer1_same_username)
    assert x["username"] == customer1_same_username["username"]
    assert x["password"] == customer1_same_username["password"]
    assert x["address"] == customer1_same_username["address"]
    assert x["marital_status"] == customer1_same_username["marital_status"]

def test_update_not_found(customer_not_found):
    x,y = update_user(customer_not_found)
    assert x["status"] == 'User not found'
    assert y == {}

def test_get_users(customer1_same_username,customer_not_found):
    register(customer_not_found)
    x = get_users()
    assert len(x) == 2
    assert x[0]["username"] == customer1_same_username["username"]
    assert x[1]["username"] == customer_not_found["username"]
    

def test_get_users_by_username(customer1_same_username):
    x = get_user_by_username(customer1_same_username["username"])
    assert x["fullname"] == customer1_same_username["fullname"]
    assert x["password"] == customer1_same_username["password"]
    assert x["age"] == customer1_same_username["age"]
    assert x["address"] == customer1_same_username["address"]

def test_get_users_by_username_not_found():
    x = get_user_by_username('toufic')
    assert x == {}

def test_charge(customer1_same_username):
    x,y = charge(customer1_same_username["username"],5)
    assert x["status"] == "Successfully charged!"
    assert y["wallet"] == 5

def test_charge_not_number(customer_not_found):
    x,y = charge(customer_not_found["username"],"ab")
    assert x["status"] == "Amount should be a number"
    assert y == {}

def test_deduce_amount(customer1_same_username):
    x,y = deduce_wallet(customer1_same_username["username"],2)
    assert x["status"] == "Successfully reduced!"
    assert y["wallet"] == 3

def test_deduce_insufficient_amount(customer1_same_username):
    x,y = deduce_wallet(customer1_same_username["username"],10)
    assert x["status"] == 'Not enough available to spend {}'.format(10)
    assert y == {}  

def test_delete(customer1_same_username,customer_not_found):
    y = delete(customer_not_found["username"])
    x = delete(customer1_same_username["username"])
    assert x["status"] == "User deleted successfully"
    assert y["status"] == "User deleted successfully"

def test_delete_not_found():
    x = delete("hady")
    assert x["status"] == "User not found"


def test_api_register(customer1):
    response = app.test_client().post( 
        '/api/users/add', 
        data=json.dumps(customer1), 
        content_type='application/json', ) 
    x,y = json.loads(response.get_data(as_text=True)) 
    assert response.status_code == 200 
    assert x["status"] == "Successful Registration"
    assert y["wallet"] == 0
    assert y["username"] == customer1["username"]

def test_api_register_taken_username(customer1_same_username):
    response = app.test_client().post( 
        '/api/users/add', 
        data=json.dumps(customer1_same_username), 
        content_type='application/json', )
    x,y = json.loads(response.get_data(as_text=True)) 
    assert response.status_code == 200 
    assert x["status"] == "Username already taken"
    assert y == {}

def test_api_update_user(customer1_same_username):
    response = app.test_client().put( 
        '/api/users/update', 
        data=json.dumps(customer1_same_username), 
        content_type='application/json', )
    x = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200 
    assert x["username"] == customer1_same_username["username"]
    assert x["password"] == customer1_same_username["password"]
    assert x["address"] == customer1_same_username["address"]
    assert x["marital_status"] == customer1_same_username["marital_status"]

def test_api_update_not_found(customer_not_found):
    response = app.test_client().put( 
        '/api/users/update', 
        data=json.dumps(customer_not_found), 
        content_type='application/json', )
    x,y = json.loads(response.get_data(as_text=True)) 
    assert response.status_code == 200 
    assert x["status"] == 'User not found'
    assert y == {}

def test_api_get_users(customer1_same_username,customer_not_found):
    register(customer_not_found)
    response = app.test_client().get('/api/users')
    x = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200 
    assert len(x) == 2
    assert x[0]["username"] == customer1_same_username["username"]
    assert x[1]["username"] == customer_not_found["username"]

def test_api_get_users_by_username(customer1_same_username):
    response = app.test_client().get(f'/api/users/{customer1_same_username["username"]}')
    x = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200 
    assert x["fullname"] == customer1_same_username["fullname"]
    assert x["password"] == customer1_same_username["password"]
    assert x["age"] == customer1_same_username["age"]
    assert x["address"] == customer1_same_username["address"]

def test_api_charge(customer1_same_username):
    response = app.test_client().put( 
        f'/api/users/charge/{customer1_same_username["username"]}', 
        data=json.dumps(5), 
        content_type='application/json', )
    x,y = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200 
    assert x["status"] == "Successfully charged!"
    assert y["wallet"] == 5

def test_api_deduce_amount(customer1_same_username):
    response = app.test_client().put( 
        f'/api/users/deduce/{customer1_same_username["username"]}', 
        data=json.dumps(2), 
        content_type='application/json', )
    x,y = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert x["status"] == "Successfully reduced!"
    assert y["wallet"] == 3

def test_api_deduce_insufficient_amount(customer1_same_username):
    response = app.test_client().put( 
        f'/api/users/deduce/{customer1_same_username["username"]}', 
        data=json.dumps(10), 
        content_type='application/json', )
    x,y = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert x["status"] == 'Not enough available to spend {}'.format(10)
    assert y == {} 

def test_api_delete(customer1_same_username):
    response = app.test_client().delete(f'/api/users/delete/{customer1_same_username["username"]}')
    x = json.loads(response.get_data(as_text=True))
    assert x["status"] == "User deleted successfully"