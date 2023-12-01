import pytest
from customer import *
from flask import json

@pytest.fixture
def customer1():
    '''Information for one customer
    :return: Information about the customer
    :rtype: Dictionary
    '''
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
    '''Information for customer of the same username
    :return: Information about the customer
    :rtype: Dictionary
    '''
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
    '''Information about a customer to test if found in the database
    :return: Information about the customer
    :rtype: Dictionary
    '''
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
    '''This tests the register function. It is expected to have a successful registration
    :param customer1: contains information about the customer
    :type customer1: dictionary
    '''
    x,y = register(customer1)
    assert x["status"] == "Successful Registration"
    assert y["wallet"] == 0
    assert y["username"] == customer1["username"]

def test_register_taken_username(customer1_same_username):
    '''This tests the register function. It should detect that the username is already used in the database
    :param customer1_same_username: contains information about the customer
    :type customer1_same_username: dictionary
    '''
    x,y = register(customer1_same_username)
    assert x["status"] == "Username already taken"
    assert y == {}

def test_update_user(customer1_same_username):
    '''This tests the update function. It should successfully update the user with the matching username 
    :param customer1_same_username: contains information about the updated customer
    :type customer1_same_username: dictionary
    '''
    x = update_user(customer1_same_username)
    assert x["username"] == customer1_same_username["username"]
    assert x["password"] == customer1_same_username["password"]
    assert x["address"] == customer1_same_username["address"]
    assert x["marital_status"] == customer1_same_username["marital_status"]

def test_update_not_found(customer_not_found):
    '''This tests the update function. It should not find the username in the database 
    :param customer_not_found: contains information about the customer
    :type customer_not_found: dictionary
    '''
    x,y = update_user(customer_not_found)
    assert x["status"] == 'User not found'
    assert y == {}

def test_get_users(customer1_same_username,customer_not_found):
    '''This tests the get function. It should return all information about all users in the database
    :param customer1_same_username: contains information about the first customer
    :type customer1_same_username: dictionary
    :param customer_not_found: contains information about the second customer
    :type customer_not_found: dictionary
    '''
    register(customer_not_found)
    x = get_users()
    assert len(x) == 2
    assert x[0]["username"] == customer1_same_username["username"]
    assert x[1]["username"] == customer_not_found["username"]
    

def test_get_users_by_username(customer1_same_username):
    '''This tests the get by name function. It should return all information about a specific user
    :param customer1_same_username: contains information about the customer
    :type customer1_same_username: dictionary
    '''
    x = get_user_by_username(customer1_same_username["username"])
    assert x["fullname"] == customer1_same_username["fullname"]
    assert x["password"] == customer1_same_username["password"]
    assert x["age"] == customer1_same_username["age"]
    assert x["address"] == customer1_same_username["address"]

def test_get_users_by_username_not_found():
    '''This tests the get by name function. It should not return any user since the username doesn't exist
    '''
    x = get_user_by_username('toufic')
    assert x == {}

def test_charge(customer1_same_username):
    '''This tests the charge function. It should increment the user's wallet by 5
    :param customer1_same_username: contains information about the customer
    :type customer1_same_username: dictionary
    '''
    x,y = charge(customer1_same_username["username"],5)
    assert x["status"] == "Successfully charged!"
    assert y["wallet"] == 5

def test_charge_not_number(customer_not_found):
    '''This tests the charge function. It shouldn't change anything since the customer is not in the database
    :param customer_not_found: contains information about the customer
    :type customer_not_found: dictionary
    '''
    x,y = charge(customer_not_found["username"],"ab")
    assert x["status"] == "Amount should be a number"
    assert y == {}

def test_deduce_amount(customer1_same_username):
    '''This tests the deduce function. It should decrease the user's wallet by 2
    :param customer1_same_username: contains information about the customer
    :type customer1_same_username: dictionary
    '''
    x,y = deduce_wallet(customer1_same_username["username"],2)
    assert x["status"] == "Successfully reduced!"
    assert y["wallet"] == 3

def test_deduce_insufficient_amount(customer1_same_username):
    '''This tests the deduce function. It shouldn't change anything since the customer's wallet doesn't contain 10$
    :param customer1_same_username: contains information about the customer
    :type customer1_same_username: dictionary
    '''
    x,y = deduce_wallet(customer1_same_username["username"],10)
    assert x["status"] == 'Not enough available to spend {}'.format(10)
    assert y == {}  

def test_delete(customer1_same_username,customer_not_found):
    '''This tests the delete function. It should delete both customers from the database
    :param customer1_same_username: contains information about the first customer
    :type customer1_same_username: dictionary
    :param customer_not_found: contains information about the second customer
    :type customer_not_found: dictionary
    '''
    y = delete(customer_not_found["username"])
    x = delete(customer1_same_username["username"])
    assert x["status"] == "User deleted successfully"
    assert y["status"] == "User deleted successfully"

def test_delete_not_found():
    '''This tests the delete function. It shouldn't delete the customer since it is not found in the databse
    '''
    x = delete("hady")
    assert x["status"] == "User not found"


def test_api_register(customer1):
    '''This tests the register function using api. It should register the customer successfully
    :param customer1: contains information about the customer
    :type customer1: dictionary
    '''
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
    '''This tests the register function using api. It shouldn't register the customer since the username is already
    taken
    :param customer1_same_username: contains information about the customer
    :type customer1_same_username: dictionary
    '''
    response = app.test_client().post( 
        '/api/users/add', 
        data=json.dumps(customer1_same_username), 
        content_type='application/json', )
    x,y = json.loads(response.get_data(as_text=True)) 
    assert response.status_code == 200 
    assert x["status"] == "Username already taken"
    assert y == {}

def test_api_update_user(customer1_same_username):
    '''This tests the update function using api. It should successfully update the user
    taken
    :param customer1_same_username: contains information about the customer
    :type customer1_same_username: dictionary
    '''
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
    '''This tests the update function using api. It shouldn't update the customer since the customer is not in the
    database
    :param customer_not_found: contains information about the customer
    :type customer_not_found: dictionary
    '''
    response = app.test_client().put( 
        '/api/users/update', 
        data=json.dumps(customer_not_found), 
        content_type='application/json', )
    x,y = json.loads(response.get_data(as_text=True)) 
    assert response.status_code == 200 
    assert x["status"] == 'User not found'
    assert y == {}

def test_api_get_users(customer1_same_username,customer_not_found):
    '''This tests the get function using api. It should return the details of all customers in the database
    :param customer1_same_username: contains information about the first customer
    :type customer1_same_username: dictionary
    :param customer_not_found: contains information about the second customer
    :type customer_not_found: dictionary
    '''
    register(customer_not_found)
    response = app.test_client().get('/api/users')
    x = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200 
    assert len(x) == 2
    assert x[0]["username"] == customer1_same_username["username"]
    assert x[1]["username"] == customer_not_found["username"]

def test_api_get_users_by_username(customer1_same_username):
    '''This tests the get by username function using api. It should return the details of the specific customer
    :param customer1_same_username: contains information about the customer
    :type customer1_same_username: dictionary
    '''
    response = app.test_client().get(f'/api/users/{customer1_same_username["username"]}')
    x = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200 
    assert x["fullname"] == customer1_same_username["fullname"]
    assert x["password"] == customer1_same_username["password"]
    assert x["age"] == customer1_same_username["age"]
    assert x["address"] == customer1_same_username["address"]

def test_api_charge(customer1_same_username):
    '''This tests the charge function using api. It should increment the user's wallet by 5
    :param customer1_same_username: contains information about the customer
    :type customer1_same_username: dictionary
    '''
    response = app.test_client().put( 
        f'/api/users/charge/{customer1_same_username["username"]}', 
        data=json.dumps(5), 
        content_type='application/json', )
    x,y = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200 
    assert x["status"] == "Successfully charged!"
    assert y["wallet"] == 5

def test_api_deduce_amount(customer1_same_username):
    '''This tests the deduce function using api. It should decrease the user's wallet by 2
    :param customer1_same_username: contains information about the customer
    :type customer1_same_username: dictionary
    '''
    response = app.test_client().put( 
        f'/api/users/deduce/{customer1_same_username["username"]}', 
        data=json.dumps(2), 
        content_type='application/json', )
    x,y = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert x["status"] == "Successfully reduced!"
    assert y["wallet"] == 3

def test_api_deduce_insufficient_amount(customer1_same_username):
    '''This tests the deduce function using api. It shouldn't update the wallet since there is less than 10$ in the 
    user's wallet
    :param customer1_same_username: contains information about the customer
    :type customer1_same_username: dictionary
    '''
    response = app.test_client().put( 
        f'/api/users/deduce/{customer1_same_username["username"]}', 
        data=json.dumps(10), 
        content_type='application/json', )
    x,y = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert x["status"] == 'Not enough available to spend {}'.format(10)
    assert y == {} 

def test_api_delete(customer1_same_username):
    '''This tests the delete function using api. It should deleted the specified customer
    :param customer1_same_username: contains information about the customer
    :type customer1_same_username: dictionary
    '''
    response = app.test_client().delete(f'/api/users/delete/{customer1_same_username["username"]}')
    x = json.loads(response.get_data(as_text=True))
    register(customer1_same_username)
    charge(customer1_same_username["username"],5)
    assert x["status"] == "User deleted successfully"