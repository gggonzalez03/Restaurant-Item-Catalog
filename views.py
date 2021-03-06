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
from restaurantmenu_database_setup import Base, User, Restaurant, MenuItem, engine

# clien id
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
# create connectionw ith the database engine "sqlite"
# engine = create_engine("sqlite:///restaurantmenu.db")

# make connection between classes and
# corresponding tables in the database
Base.metadata.bind = engine
# create a session
DBSession = sessionmaker(bind=engine)
session = DBSession()


def add_user(login_session):
    new_user = User(name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(new_user)
    session.commit()


def get_user_by_email(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user
    except:
        return None


def get_user_by_id(user_id):
    user = session.query(User).filter_by(user_id=user_id).one()
    return user


def get_menu_by_restaurant(restaurant_id):
    menu = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    items = []
    for item in menu:
        items.append(item.serialize)

    return jsonify(results=items)


def is_item_owned(menu_item_id):
    item = session.query(MenuItem).filter_by(id=menu_item_id).one()
    if login_session['email'] == item.restaurant.user.email:
        return jsonify(results=[{"answer": True}])

    return jsonify(results=[{"answer": False}])

def is_rest_owned(restaurant_id):
    item = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if login_session['email'] == item.user.email:
        return jsonify(results=[{"answer": True}])

    return jsonify(results=[{"answer": False}])


def get_all_restaurants():
    all_restaurants = session.query(Restaurant).all()
    items = []
    for item in all_restaurants:
        items.append(item.serialize)

    return jsonify(results=items)


# ALL VIEWS
def login():
    if request.method == "POST":
        # This will not be implemented for now since
        # currently, I am working on the OAuth
        pass
    else:
        if 'username' in login_session:
            return redirect(url_for('all_restaurants_view'))

        state = "".join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
        login_session['state'] = state
        return render_template('login.html', STATE=state)


def google_login():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Get auth code from the javascript ajax request
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
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

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
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

    if not get_user_by_email(login_session['email']):
        add_user(login_session)

    response = make_response(json.dumps('User is being logged in'),
                             200)
    response.headers['Content-Type'] = 'application/json'
    return response


def google_logout():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps("Current user not connected."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    print credentials

    # Revoke the token using google API
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        return redirect(url_for('login'))

    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def all_restaurants_view():
    """
    Renders a template that shows all the restaurants
    :return: A rendered template that shows all the restaurants
    """
    all_restaurants = session.query(Restaurant).all()
    return render_template("restaurants.html",
                           all_restaurants=all_restaurants,
                           logged_in_user=get_user_by_email(login_session['email']))


def add_restaurant():
    if 'username' not in login_session:
        return redirect(url_for('login'))

    if request.method == "POST":
        user_id = get_user_by_email(login_session['email']).user_id
        restaurant_name = request.form['restaurantname']
        new_restaurant = Restaurant(user_id=user_id,
                                    name=restaurant_name)
        session.add(new_restaurant)
        session.commit()
        return redirect(url_for("all_restaurants_view"))
    else:
        return render_template("addrestaurant.html")


def edit_restaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect(url_for('login'))
    restaurant_to_edit = session.query(Restaurant).filter_by(id=restaurant_id).one()
    user_id = get_user_by_email(login_session['email']).user_id

    # return an error if the user is trying to edit a restaurant
    # that is not his own
    if user_id != restaurant_to_edit.user.user_id:
        response = make_response(json.dumps('Oops. You\'re trying to touch something that is not yours!', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
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
    if 'username' not in login_session:
        return redirect(url_for('login'))
    restaurant_to_be_deleted = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_to_be_deleted = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    user_id = get_user_by_email(login_session['email']).user_id

    # return an error if the user is trying to edit a restaurant
    # that is not his own
    if user_id != restaurant_to_be_deleted.user.user_id:
        response = make_response(json.dumps('Oops. You\'re trying to touch something that is not yours!', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

    if request.method == "POST":
        if request.form["todeleterestaurant"] == "Yes":
            session.delete(restaurant_to_be_deleted)

            for item in menu_to_be_deleted:
                session.delete(item)

            session.commit()
            return redirect(url_for("all_restaurants_view"))
        else:
            return redirect(url_for("all_restaurants_view"))
    else:
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
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
    menu_by_restaurant = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return render_template("menu.html",
                           restaurant=restaurant,
                           items=menu_by_restaurant,
                           logged_in_user=get_user_by_email(login_session['email']))


def add_menu_item(restaurant_id):
    """
    Creates a new menu entry in the database
    :param: Id of the restaurant that will be having a new item in the menu
    :return: Returns a rendered template or redirectioin
    """
    if 'username' not in login_session:
        return redirect(url_for('login'))

    restaurant_owner_id = session.query(Restaurant).filter_by(id=restaurant_id).one().user.user_id
    user_id = get_user_by_email(login_session['email']).user_id

    if user_id != restaurant_owner_id:
        response = make_response(json.dumps('Oops. You\'re trying to touch something that is not yours!', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

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
    if 'username' not in login_session:
        return redirect(url_for('login'))
    edited_item = session.query(MenuItem).filter_by(id=int(menu_id)).one()
    user_id = get_user_by_email(login_session['email']).user_id

    if user_id != edited_item.restaurant.user.user_id:
        response = make_response(json.dumps('Oops. You\'re trying to touch something that is not yours!', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
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
    if 'username' not in login_session:
        return redirect(url_for('login'))

    item_to_delete = session.query(MenuItem).filter_by(id=menu_id).one()
    user_id = get_user_by_email(login_session['email']).user_id

    if user_id != item_to_delete.restaurant.user.user_id:
        response = make_response(json.dumps('Oops. You\'re trying to touch something that is not yours!', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

    if request.method == 'POST':
        if request.form['todeletemenuitem'] == "Yes":
            session.delete(item_to_delete)
            session.commit()
        else:
            # TODO:
            # Add flash messages
            pass
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html', item_to_delete=item_to_delete,
                               restaurant_id=restaurant_id)


def restaurant_menu_json(restaurant_id):
    if 'username' not in login_session:
        return redirect(url_for('login'))
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id).all()

    return jsonify(MenuItems=[i.serialize for i in items])


def restaurant_menu_item_json(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect(url_for('login'))
    item = session.query(MenuItem).filter_by(id=menu_id).first()
    return jsonify(item.serialize)
