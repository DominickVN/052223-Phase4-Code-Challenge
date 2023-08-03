from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from models import db, Restaurant, RestaurantPizza, Pizza
import os
from flask_migrate import Migrate

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([{
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
        } for restaurant in restaurants])

class RestaurantResource(Resource):
    def get(self, restaurant_id):
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            return {'error': 'Restaurant not found'}, 404
        return {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'restaurant_pizzas': [rp.serialize() for rp in restaurant.restaurant_pizzas],
        }

    def delete(self, restaurant_id):
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            return {'error': 'Restaurant not found'}, 404

        db.session.delete(restaurant)
        db.session.commit()

        return '', 204

class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        if price is None or pizza_id is None or restaurant_id is None:
            return jsonify({'errors': ['Validation errors']}), 400

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not pizza or not restaurant:
            return jsonify({'errors': ['Pizza or Restaurant not found']}), 400

        try:
            price = int(price)
        except ValueError:
            return jsonify({'errors': ['Invalid price value']}), 400

        if not (1 <= price <= 30):
            return jsonify({'errors': ['Price must be between 1 and 30']}), 400

        restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )
        db.session.add(restaurant_pizza)
        db.session.commit()

        restaurant_pizza = RestaurantPizza.query.get(restaurant_pizza.id)

        return jsonify(restaurant_pizza.serialize()), 201

class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([{
            'id': pizza.id,
            'name': pizza.name,
            'ingredients': pizza.ingredients,
        } for pizza in pizzas])

api.add_resource(RestaurantsResource, '/restaurants')
api.add_resource(RestaurantResource, '/restaurants/<int:restaurant_id>')
api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')
api.add_resource(PizzasResource, '/pizzas')

if __name__ == '__main__':
    app.run(port=5555, debug=True)