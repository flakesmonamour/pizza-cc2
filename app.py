#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request,jsonify, make_response,abort
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify(
[
            {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address
        } for restaurant in restaurants
    ]), 200

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas]), 200
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')
    price = data.get('price')
    
    pizza = db.session.get(Pizza, pizza_id)
    restaurant = db.session.get(Restaurant, restaurant_id)
    if not pizza or not restaurant:
            return jsonify({"errors": ["Pizza or Restaurant not found"]}), 404

    if not isinstance(price, (int, float)) or price < 1 or price > 30:
        return jsonify({"errors": ["validation errors"]}), 400
    try:
        restaurant_pizza = RestaurantPizza(pizza_id=pizza_id, restaurant_id=restaurant_id, price=price)
        db.session.add(restaurant_pizza)
        db.session.commit()
        return jsonify({
            'id': restaurant_pizza.id,
            'price': restaurant_pizza.price,
            'pizza_id': restaurant_pizza.pizza_id,
            'restaurant_id': restaurant_pizza.restaurant_id,
            'pizza': pizza.to_dict(),
            'restaurant': restaurant.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = db.session.get(Restaurant, id)  
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    return jsonify(restaurant.to_dict()), 200
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)  
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    db.session.delete(restaurant)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(port=5555, debug=True)
