from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from restaurantmenu_database_setup import Base, Restaurant, MenuItem, serialize

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
def all_restaurants_view():
    """
    Renders a template that shows all the restaurants
    :return: A rendered template that shows all the restaurants
    """
    all_restaurants = get_all_restaurants()
    return render_template('restaurants.html', all_restaurants=all_restaurants)


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


def new_menu_item(restaurant_id):
    """
    Creates a new menu entry in the database
    :param: Id of the restaurant that will be having a new item in the menu
    :return: Returns a rendered template or redirectioin
    """
    if request.method == 'POST':
        # TODO:
        # description and others should accept values
        # add input tags into the HTML file
        newItem = MenuItem(name=request.form['name'],
                           description=None,
                           price=None,
                           course=None,
                           restaurant_id=int(restaurant_id))
        session.add(newItem)
        session.commit()
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)


def edit_menu_item(restaurant_id, menu_id):
    """
    Updates a menu in the MenuItem table
    :return: A rendered template or a redirection
    """
    edited_item = session.query(MenuItem).filter_by(id=int(menu_id)).one()
    if request.method == 'POST':
        if request.form['name'] and request.form['editornot'] == "Edit":
            edited_item.name = request.form['name']
            session.add(edited_item)
            session.commit()
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template(
            'editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=edited_item)


def delete_menu_item(restaurant_id, menu_id):
    """
    Deletes a menu item
    :param restaurant_id: Restaurant id in integer, used
            for redirection in this function
    :param menu_id: Id of the item being deleted
    :return: A rendered template or a redirection
    """
    item_to_delete = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(item_to_delete)
        session.commit()
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html', item=item_to_delete, restaurant_id=restaurant_id)


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
