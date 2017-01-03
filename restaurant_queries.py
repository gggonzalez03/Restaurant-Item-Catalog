from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from restaurantmenu_database_setup import Base, Restaurant, MenuItem

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

# delete functions

# functions to interact with menu table
# read functions
def get_all_menu():
    return session.query(MenuItem).all()

def get_menu_by_restaurant(restaurant_id):
    """This will return the manu of a specific
    restaurant

    Args:
        restaurant_id: Id of the restaurant
    """
    if isinstance(restaurant_id, int):
        return session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    else:
        raise TypeError("Restaurant id must be an integer")

# update functions

# delete functions
