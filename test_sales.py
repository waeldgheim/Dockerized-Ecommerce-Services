import pytest
from inventory import *
from customer import *
from sales import *
from flask import json

@pytest.fixture
def kinder():
    item = {
        "name": "kinder",
        "category": "food",
        "price": 1.5,
        "description": "Chocolate",
        "count": 1
    }
    return item

@pytest.fixture
def tuna():
    item = {
        "name": "tuna",
        "category": "food",
        "price": 3.0,
        "description": "Tuna Fish",
        "count": 54
    }
    return item

@pytest.fixture
def afif():
    item = {
        "fullname" : "Afif Itani",
        "username" : "afif", 
        "password" : "4568", 
        "age" : "67", 
        "address" : "Beirut",
        "gender" : "male" ,
        "marital_status" : "single"
    }
    return item

@pytest.fixture
def john():
    item = {
        "fullname" : "John Wick",
        "username" : "john", 
        "password" : "5678", 
        "age" : "44", 
        "address" : "US",
        "gender" : "male" ,
        "marital_status" : "divorced"
    }
    return item


def test_get_prices():
    x = get_prices()
    assert len(x) == 2
    assert x[0] == {'name': 'tuna', 'price': 3.0}
    assert x[1] == {'name': 'kinder', 'price': 1.5}

def test_get_good_by_name(kinder):
    x = get_good_by_name(kinder["name"])
    assert x["name"] == kinder["name"]
    assert x["category"] == kinder["category"]
    assert x["price"] == kinder["price"]
    assert x["description"] == kinder["description"]
    assert x["count"] == kinder["count"]

def test_get_good_not_found():
    x = get_good_by_name("persil")
    assert x == {}

def test_sale(john,kinder,tuna):
    prev = get_user_by_username(john["username"])
    x = sale(john["username"],kinder["name"])
    y = sale(john["username"],tuna["name"])
    cust = get_user_by_username(john["username"])
    t = get_good_by_name(tuna["name"])
    k = get_good_by_name(kinder["name"])
    assert x["status"] == "Purchase successful"
    assert y["status"] == "Purchase successful"
    assert cust["wallet"] == prev["wallet"] - 4.5
    assert t["count"] == tuna["count"] - 1
    assert k["count"] == kinder["count"] - 1

def test_sale_out_of_stock(john,kinder):
    charge(john["username"],5)
    x = sale(john["username"],kinder["name"])
    cust = get_user_by_username(john["username"])
    k = get_good_by_name(kinder["name"])
    assert x["status"] == '{} is out of stock'.format(kinder["name"])
    assert cust["wallet"] == 5.5
    assert k["count"] == 0

def test_sale_not_enough_money(afif,tuna):
    x = sale(afif["username"],tuna["name"])
    cust = get_user_by_username(afif["username"])
    t = get_good_by_name(tuna["name"])
    assert x["status"] == 'Not enough available to spend {}'.format(tuna["price"])
    assert cust["wallet"] == 0
    assert t["count"] == tuna["count"] - 1

def test_sale_good_not_found(john):
    x = sale(john["username"],"persil")
    assert x["status"] == 'Purchase Failed'

def test_history(john):
    x = get_history(john["username"])
    assert len(x) == 2
    assert x == {"kinder":1,"tuna":1}

def test_api_get_prices():
    response = app.test_client().get('/api/prices')
    x = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert len(x) == 2
    assert x[0] == {'name': 'tuna', 'price': 3.0}
    assert x[1] == {'name': 'kinder', 'price': 1.5}

def test_api_get_good_by_name(tuna):
    update_good(tuna)
    response = app.test_client().get(f'/api/goods/{tuna["name"]}')
    x = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert x["name"] == tuna["name"]
    assert x["category"] == tuna["category"]
    assert x["price"] == tuna["price"]
    assert x["description"] == tuna["description"]
    assert x["count"] == tuna["count"]

def test_api_sale(john,tuna):
    prev = get_user_by_username(john["username"])
    response = app.test_client().post(f'/api/sale/{john["username"]},{tuna["name"]}')
    x = json.loads(response.get_data(as_text=True))
    cust = get_user_by_username(john["username"])
    t = get_good_by_name(tuna["name"])
    assert response.status_code == 200
    assert x["status"] == "Purchase successful"
    assert cust["wallet"] == prev["wallet"] - 3.0
    assert t["count"] == tuna["count"] - 1

def test_api_sale_out_of_stock(john,kinder):
    response = app.test_client().post(f'/api/sale/{john["username"]},{kinder["name"]}')
    x = json.loads(response.get_data(as_text=True))
    cust = get_user_by_username(john["username"])
    k = get_good_by_name(kinder["name"])
    assert response.status_code == 200
    assert x["status"] == '{} is out of stock'.format(kinder["name"])
    assert cust["wallet"] == 2.5
    assert k["count"] == 0

def test_api_sale_not_enough_money(afif,tuna):
    response = app.test_client().post(f'/api/sale/{afif["username"]},{tuna["name"]}') 
    x = json.loads(response.get_data(as_text=True))
    cust = get_user_by_username(afif["username"])
    t = get_good_by_name(tuna["name"])
    assert response.status_code == 200
    assert x["status"] == 'Not enough available to spend {}'.format(tuna["price"])
    assert cust["wallet"] == 0
    assert t["count"] == tuna["count"] - 1

def test_api_history(john):
    response = app.test_client().get( f'/api/history/{john["username"]}') 
    x = json.loads(response.get_data(as_text=True))
    assert len(x) == 2
    assert x == {"kinder":1,"tuna":2}