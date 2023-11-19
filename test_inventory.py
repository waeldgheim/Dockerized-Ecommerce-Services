import pytest
from inventory import *
from flask import json

@pytest.fixture
def item1():
    item = {
        "name": "tuna",
        "category": "food",
        "price": 3,
        "description": "Tuna Fish",
        "count": 55
    }
    return item

@pytest.fixture
def item2():
    item = {
        "name": "kinder",
        "category": "food",
        "price": 1.5,
        "description": "Chocolate",
        "count": 1
    }
    return item

@pytest.fixture
def item_wrong_category():
    item = {
        "name": "Persil",
        "category": "detergent",
        "price":7 ,
        "description": "To wash clothes",
        "count": 16
    }
    return item

@pytest.fixture
def item1_updated():
    item = {
        "name": "tuna",
        "category": "food",
        "price": 5,
        "description": "Imported Tuna Fish",
        "count": 0
    }
    return item

def test_add(item1):
    x,y = add_goods(item1)
    assert x["status"] == "Successful Registration"
    assert y["name"] == item1["name"]
    assert y["description"] == item1["description"]

def test_add_wrong_category(item_wrong_category):
    x= add_goods(item_wrong_category)
    assert x["status"] == "Category is invalid"

def test_deduce_good(item1):
    x,y= deduce_good(item1["name"])
    assert x["status"] == "Succefully deduced item"
    assert y["count"] == item1["count"] - 1

def test_deduce_good_not_found(item_wrong_category):
    x,y= deduce_good(item_wrong_category["name"])
    assert x["status"] == 'Good not found'
    assert y == {}

def test_update_good(item1_updated):
    x,y = update_good(item1_updated)
    assert x["status"] == "Succefully updated good"
    assert y["name"] == item1_updated["name"]
    assert y["price"] == item1_updated["price"]
    assert y["count"] == item1_updated["count"]

def test_update_good_not_found(item_wrong_category):
    x,y = update_good(item_wrong_category)
    assert x["status"] == 'Good not found'
    assert y == {}

def test_deduce_good_out_of_stock(item1_updated):
    x,y = deduce_good(item1_updated["name"])
    assert x["status"] == "Good is out of stock"
    assert y == {}


def test_api_add(item2):
    response = app.test_client().post( 
        '/api/goods/add', 
        data=json.dumps(item2), 
        content_type='application/json', ) 
    x,y = json.loads(response.get_data(as_text=True)) 
    assert response.status_code == 200 
    assert x["status"] == "Successful Registration"
    assert y["name"] == item2["name"]
    assert y["count"] == item2["count"]

def test_api_update(item1):
    response = app.test_client().put( 
        '/api/goods/update', 
        data=json.dumps(item1), 
        content_type='application/json', ) 
    x,y = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200 
    assert x["status"] == "Succefully updated good"
    assert y["name"] == item1["name"]
    assert y["price"] == item1["price"]
    assert y["count"] == item1["count"]

def test_api_deduce(item1):
    response = app.test_client().put(f'/api/goods/deduce/{item1["name"]}')
    x,y = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200 
    assert x["status"] == "Succefully deduced item"
    assert y["count"] == item1["count"] - 1