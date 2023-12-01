import pytest
from inventory import *
from flask import json

@pytest.fixture
def item1():
    '''Information for the first item
    :return: Information about the item
    :rtype: Dictionary
    '''
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
    '''Information for the second item
    :return: Information about the item
    :rtype: Dictionary
    '''
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
    '''Information for an item with an invalid category
    :return: Information about the item
    :rtype: Dictionary
    '''
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
    '''Updated information for the first item
    :return: Information about the item
    :rtype: Dictionary
    '''
    item = {
        "name": "tuna",
        "category": "food",
        "price": 5,
        "description": "Imported Tuna Fish",
        "count": 0
    }
    return item

def test_add(item1):
    '''This tests the add function. It is expected to have a successful registration
    :param item1: contains information about the item
    :type item1: dictionary
    '''
    x,y = add_goods(item1)
    assert x["status"] == "Successful Registration"
    assert y["name"] == item1["name"]
    assert y["description"] == item1["description"]

def test_add_wrong_category(item_wrong_category):
    '''This tests the add function. It shouldn't register the item since the category is invalid
    :param item_wrong_category: contains information about the item
    :type item_wrong_category: dictionary
    '''
    x= add_goods(item_wrong_category)
    assert x["status"] == "Category is invalid"

def test_deduce_good(item1):
    '''This tests the deduce function. It should deduce the amount of the item by one
    :param item1: contains information about the item
    :type item1: dictionary
    '''
    x,y= deduce_good(item1["name"])
    assert x["status"] == "Succefully deduced item"
    assert y["count"] == item1["count"] - 1

def test_deduce_good_not_found(item_wrong_category):
    '''This tests the deduce function. It shouldn't update the database since the good is not found
    :param item_wrong_category: contains information about the item
    :type item_wrong_category: dictionary
    '''
    x,y= deduce_good(item_wrong_category["name"])
    assert x["status"] == 'Good not found'
    assert y == {}

def test_update_good(item1_updated):
    '''This tests the update function. It should successfully update the database
    :param item1_updated: contains information about the updated item
    :type item1_updated: dictionary
    '''
    x,y = update_good(item1_updated)
    assert x["status"] == "Succefully updated good"
    assert y["name"] == item1_updated["name"]
    assert y["price"] == item1_updated["price"]
    assert y["count"] == item1_updated["count"]

def test_update_good_not_found(item_wrong_category):
    '''This tests the update function. It shouldn't update the database since the item is not found
    :param item_wrong_category: contains information about the item
    :type item_wrong_category: dictionary
    '''
    x,y = update_good(item_wrong_category)
    assert x["status"] == 'Good not found'
    assert y == {}

def test_deduce_good_out_of_stock(item1_updated):
    '''This tests the deduce function. It should be unsuccessful since the item's count is 0
    :param item1_updated: contains information about the item
    :type item1_updated: dictionary
    '''
    x,y = deduce_good(item1_updated["name"])
    assert x["status"] == "Good is out of stock"
    assert y == {}


def test_api_add(item2):
    '''This tests the add function using api. It is expected to have a successful registration
    :param item2: contains information about the item
    :type item2: dictionary
    '''
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
    '''This tests the update function using api. It should successfully update the database
    :param item1: contains information about the updated item
    :type item1: dictionary
    '''
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
    '''This tests the deduce function using api. It should deduce the amount of the item by one
    :param item1: contains information about the item
    :type item1: dictionary
    '''
    response = app.test_client().put(f'/api/goods/deduce/{item1["name"]}')
    x,y = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200 
    assert x["status"] == "Succefully deduced item"
    assert y["count"] == item1["count"] - 1