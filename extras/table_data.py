from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# create connection with the database engine "sqlite"
engine = create_engine('sqlite:///restaurantmenu.db')

# make connection between classes and
# their corresponding tables in the database
Base.metadata.bind = engine

# create a session for python and
# database engine
DBSession = sessionmaker(bind=engine)

session = DBSession()

new_restaurant = Restaurant(name="Pizza Palace")
session.add(new_restaurant)
session.commit()

print(session.query(Restaurant).all())

new_menu_item = MenuItem(name="Cheese Pizza",
                         description="Made with all natural ingredients and fresh mozzarella",
                         price="8.99",
                         course="Entree",
                         restaurant=new_restaurant)
session.add(new_menu_item)
session.commit()
session.query()
print(session.query(MenuItem).all())
