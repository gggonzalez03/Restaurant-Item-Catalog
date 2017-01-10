import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# required instance of a class declarative base
# to let sqlalchemy know that this is a special
# class that corresponds to a table in the database
Base = declarative_base()

class User(Base):
    __tablename__= "user"

    # Create the columns in table user
    user_id =Column(Integer,
                    primary_key=True)
    user_name = Column(String(80),
                  nullable=False)
    email = Column(String,
                   nullable=False)
    picture = Column(String,
                     nullable=True)
    refresh_token = Column(String,
                           nullable=True)


class Restaurant(Base):
    __tablename__ = 'restaurant'

    # create the columns in table restaurant
    id = Column(Integer,
                primary_key=True)
    name = Column(String(80),
                  nullable=False)
    user_id = Column(String(80),
                       ForeignKey('user.user_id'))
    user = relationship(User)

class MenuItem(Base):
    __tablename__ = 'menu_item'

    # create the columns in table menu_item
    id = Column(Integer,
                primary_key=True)
    name =Column(String(80),
                 nullable = False)
    description = Column(String(250))
    price = Column(String(8))
    course = Column(String(250))
    restaurant_id = Column(Integer,
                           ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)


    @property
    def serialize(self):
        # Returns a serializable data
        return {
            "name": self.name,
            "description": self.description,
            "id": self.id,
            "price": self.price,
            "course": self.course,
        }


# create a create_engine instance that
# points to the database engine that will be used
# in the module
engine = create_engine(
    'sqlite:///restaurantmenu.db')

# goes to the database and adds
# the classes that correspond to
# tables in the database
Base.metadata.create_all(engine)
