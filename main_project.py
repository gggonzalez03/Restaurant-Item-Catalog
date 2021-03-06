from flask import Flask
import views

app = Flask(__name__)

methods = ["GET","POST"]
# Show login page
app.add_url_rule('/login',
                 view_func=views.login,
                 methods=methods)

app.add_url_rule('/',
                 view_func=views.login,
                 methods=methods)
# Google Plus login
app.add_url_rule('/googlelogin',
                 view_func=views.google_login,
                 methods=methods)

# Google Plus logout
app.add_url_rule('/googlelogout',
                 view_func=views.google_logout,
                 methods=methods)

# Show all restaurants
app.add_url_rule('/restaurants',
                 view_func=views.all_restaurants_view,
                 methods=methods)

# Show all restaurants
app.add_url_rule('/restaurant/menu/<int:restaurant_id>',
                 view_func=views.get_menu_by_restaurant,
                 methods=methods)


# Show form to add a new restaurant
app.add_url_rule("/restaurants/add",
                 view_func=views.add_restaurant,
                 methods=methods)

# Show form to edit a restaurant
app.add_url_rule('/restaurants/<int:restaurant_id>/edit',
                 view_func=views.edit_restaurant,
                 methods=methods)

# Show form to delete a restaurant from the database
app.add_url_rule("/restaurants/<int:restaurant_id>/delete",
                 view_func=views.delete_restaurant,
                 methods=methods)

# Show the menu of a restaurant
app.add_url_rule('/restaurants/<int:restaurant_id>/',
                 view_func=views.restaurant_menu,
                 methods=methods)

# Show form to add new item on get
# and add new menu item on post
app.add_url_rule('/restaurants/<int:restaurant_id>/new',
                 view_func=views.add_menu_item,
                 methods=methods)

# Show form to edit an item on get
# and edit an item on post
app.add_url_rule('/restaurants/<int:restaurant_id>/<int:menu_id>/edit',
                 view_func=views.edit_menu_item,
                 methods=methods)

# Show form to delete an item on get
# and delete an item on post
app.add_url_rule('/restaurants/<int:restaurant_id>/<int:menu_id>/delete',
                 view_func=views.delete_menu_item,
                 methods=methods)
#JSON URLS
# Get JSON formatted menu of a restaurant
app.add_url_rule('/restaurants/<int:restaurant_id>/menu/JSON',
                 view_func=views.restaurant_menu_json,
                 methods=methods)

# Get JSON formatted details of an item in a menu of a restaurant
app.add_url_rule('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON',
                 view_func=views.restaurant_menu_item_json,
                 methods=methods)

# Get JSON formatted response asking question "Is the logged in user the owner of
# a particular menu_item in a restaurant"
app.add_url_rule('/restaurant/menu/<int:menu_item_id>/isowned',
                 view_func=views.is_item_owned,
                 methods=methods)

app.add_url_rule('/restaurant/<int:restaurant_id>/isowned',
                 view_func=views.is_rest_owned,
                 methods=methods)

app.add_url_rule('/restaurants/JSON',
                 view_func=views.get_all_restaurants,
                 methods=methods)

if __name__ == '__main__':
    app.secret_key = "secret key"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
