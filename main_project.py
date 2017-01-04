from flask import Flask
import views

app = Flask(__name__)

methods = ["GET","POST"]
app.add_url_rule('/restaurants',
                 view_func=views.all_restaurants_view,
                 methods=methods)
app.add_url_rule('/restaurants/<int:restaurant_id>/',
                 view_func=views.restaurant_menu,
                 methods=methods)
app.add_url_rule('/restaurants/<int:restaurant_id>/new',
                 view_func=views.new_menu_item,
                 methods=methods)
app.add_url_rule('/restaurants/<int:restaurant_id>/<int:menu_id>/edit',
                 view_func=views.edit_menu_item,
                 methods=methods)
app.add_url_rule('/restaurants/<int:restaurant_id>/<int:menu_id>/delete',
                 view_func=views.delete_menu_item,
                 methods=methods)
#JSON URLS
app.add_url_rule('/restaurants/<int:restaurant_id>/menu/JSON',
                 view_func=views.restaurant_menu_JSON,
                 methods=methods)
app.add_url_rule('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON',
                 view_func=views.restaurant_menu_item_JSON,
                 methods=methods)

if __name__ == '__main__':
    app.secret_key = "secret key"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
