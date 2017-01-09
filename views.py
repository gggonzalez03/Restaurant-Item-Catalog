import os, sys
import random, string
import httplib2
import json
import requests
from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from restaurantmenu_database_setup import Base, Restaurant, MenuItem, serialize

# clien id
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
# create connectionw ith the database engine "sqlite"
engine = create_engine("sqlite:///restaurantmenu.db")

# make connection between classes and
# corresponding tables in the database
Base.metadata.bind = engine
# create a session
DBSession = sessionmaker(bind=engine)
session = DBSession()
# functions to interact with restaurant table
# create functions
def add_restaurant(restaurant_name):
    """This will add a new restaurant in the database
    :param restaurant_name: Name of the restaurant being added in String
    :return: None
    """
    if isinstance(restaurant_name, str):
        new_restaurant = Restaurant(name=restaurant_name)
        session.add(new_restaurant)
        session.commit()
    else:
        raise TypeError("Restaurant name must be of type String")


# read functions
def get_all_restaurants():
    """This will return all the rows in the
    restaurant table
    :return: A list of tuples of restaurants
    """
    return session.query(Restaurant).all()


def get_a_restaurant_by_id(restaurant_id):
    """
    Gets a single row from Restaurant table by id
    :param restaurant_id: Id of the restaurant that is being retrieved
    :return: A dictionary contains information about a restaurant
    """
    return session.query(Restaurant).filter_by(id=restaurant_id).first()


# update functions
def rename_a_restaurant(restaurant_id, restaurant_new_name):
    """This will update the name of the given
    restaurant
    :param restaurant_new_name: New name to be set for the restaurant
    :param restaurant_id: Id of the restaurant being renamed
    :return: None
    """
    to_rename_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
    to_rename_restaurant.name = restaurant_new_name
    session.add(to_rename_restaurant)
    session.commit()


# delete functions
def delete_a_restaurant(restaurant_id):
    """This will delete a specific row in the
        database where the id is the given restaurant_id
    :param restaurant_id: Id of the restaurant being deleted in Integer
    :return: none
    """
    if isinstance(restaurant_id, int):
        to_delete_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
        session.delete(to_delete_restaurant)
        session.commit()
    else:
        raise TypeError("Restaurant Id must be of type Integer")


# FUNCTIONS FOR INTERACTING WITH MENUITEM TABLE
# create functions
# read functions
def get_all_menu():
    return session.query(MenuItem).all()


def get_menu_by_restaurant(restaurant_id):
    """This will return the menu of a specific
    restaurant

    Args:
        restaurant_id: Id of the restaurant
    """
    if isinstance(restaurant_id, int):
        return session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    else:
        raise TypeError("Restaurant id must be an integer")


# DELETE FUNCTIONS

# ALL VIEWS
def login():
    if request.method == "POST":
        # Validate state token
        if request.args.get('state') != login_session['state']:
            response = make_response(json.dumps('Invalid state parameter.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        # Obtain authorization code
        code = request.data
        try:
            print "Trying"
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
            print "Still trying"
            oauth_flow.redirect_uri = 'postmessage'
            print "Still trying"
            credentials = oauth_flow.step2_exchange(code)
            print "Still trying"
        except FlowExchangeError:
            print "It tried"
            response = make_response(
                json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Check that the access token is valid.
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
               % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'
            print "Error 500"
            return response

        # Verify that the access token is used for the intended user.
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            response = make_response(
                json.dumps("Token's user ID doesn't match given user ID."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Verify that the access token is valid for this app.
        if result['issued_to'] != CLIENT_ID:
            response = make_response(
                json.dumps("Token's client ID does not match app's."), 401)
            print "Token's client ID does not match app's."
            response.headers['Content-Type'] = 'application/json'
            return response

        # Store the access token in the session for later use.
        login_session['credentials'] = credentials.access_token
        login_session['gplus_id'] = gplus_id

        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        login_session['username'] = data['name']
        login_session['picture'] = data['picture']
        login_session['email'] = data['email']

        stored_credentials = login_session.get('credentials')
        stored_gplus_id = login_session.get('gplus_id')
        if stored_credentials is not None and gplus_id == stored_gplus_id:
            response = make_response(json.dumps('Current user is already connected.'),
                                     200)
            response.headers['Content-Type'] = 'application/json'
            return response

    else:
        state = "".join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
        login_session['state'] = state
        return render_template('login.html', STATE=state)


def all_restaurants_view():
    """
    Renders a template that shows all the restaurants
    :return: A rendered template that shows all the restaurants
    """
    all_restaurants = get_all_restaurants()
    return render_template("restaurants.html", all_restaurants=all_restaurants, user=login_session['username'])


def add_restaurant():
    if request.method == "POST":
        restaurant_name = request.form['restaurantname']
        new_restaurant = Restaurant(name=restaurant_name)
        session.add(new_restaurant)
        session.commit()
        return redirect(url_for("all_restaurants_view"))
    else:
        return render_template("addrestaurant.html")


def edit_restaurant(restaurant_id):
    restaurant_to_edit = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == "POST":
        restaurant_to_edit.name = request.form['restaurantnewname']
        session.add(restaurant_to_edit)
        session.commit()
        return redirect(url_for("all_restaurants_view"))
    else:
        return render_template("editrestaurant.html",
                               restaurant_id=restaurant_id,
                               restaurant_to_edit_name=restaurant_to_edit.name)


def delete_restaurant(restaurant_id):
    restaurant_to_be_deleted = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == "POST":
        if request.form["todeleterestaurant"] == "Yes":
            session.delete(restaurant_to_be_deleted)
            session.commit()
            return redirect(url_for("all_restaurants_view"))
        else:
            return redirect(url_for("all_restaurants_view"))
    else:
        print "success"
        return render_template("deleterestaurant.html",
                               restaurant_id=restaurant_id,
                               restaurant_name=restaurant_to_be_deleted.name)


def restaurant_menu(restaurant_id):
    """
    Create a template for viewing a restaurant's
    menu
    :param restaurant_id: The id of the restaurant that we need the menu from
    :return: A template for viewing a restaurant's menu
    """
    restaurant = get_a_restaurant_by_id(restaurant_id)
    menu_by_restaurant = get_menu_by_restaurant(restaurant.id)
    return render_template("menu.html",
                           restaurant=restaurant,
                           items=menu_by_restaurant)


def add_menu_item(restaurant_id):
    """
    Creates a new menu entry in the database
    :param: Id of the restaurant that will be having a new item in the menu
    :return: Returns a rendered template or redirectioin
    """
    if request.method == 'POST':
        # TODO:
        # description and others should accept values
        # add input tags into the HTML file
        newItem = MenuItem(name=request.form['additemname'],
                           description=request.form['additemdescription'],
                           price=request.form['additemprice'],
                           course=request.form['additemcourse'],
                           restaurant_id=int(restaurant_id))
        session.add(newItem)
        session.commit()
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template('addmenuitem.html', restaurant_id=restaurant_id)


def edit_menu_item(restaurant_id, menu_id):
    """
    Updates a menu in the MenuItem table
    :return: A rendered template or a redirection
    """
    edited_item = session.query(MenuItem).filter_by(id=int(menu_id)).one()
    if request.method == 'POST':
        if request.form['submitedititem'] == "Edit":
            edited_item.name = request.form['edititemname']
            edited_item.price = request.form['edititemprice']
            edited_item.description = request.form['edititemdescription']
            edited_item.course = request.form['edititemcourse']
            session.add(edited_item)
            session.commit()
            return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
        else:
            return redirect(
                url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template(
            'editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item_to_edit=edited_item)


def delete_menu_item(restaurant_id, menu_id):
    """
    Deletes a menu item
    :param restaurant_id: Restaurant id in integer, used
            for redirection in this function
    :param menu_id: Id of the item being deleted
    :return: A rendered template or a redirection
    """
    if request.method == 'POST':
        if request.form['todeletemenuitem'] == "Yes":
            item_to_delete = session.query(MenuItem).filter_by(id=menu_id).one()
            session.delete(item_to_delete)
            session.commit()
        else:
            # TODO:
            # Add flash messages
            pass
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        item_to_delete = session.query(MenuItem).filter_by(id=menu_id).one()
        return render_template('deletemenuitem.html', item_to_delete=item_to_delete,
                               restaurant_id=restaurant_id)


        # JSON VIEWS
        # TODO:
        # serialize does not work
        # make it work


def restaurant_menu_JSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id).all()

    return jsonify(MenuItems=[i.serialize for i in items])


def restaurant_menu_item_JSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).first()
    return jsonify(item.serialize)
