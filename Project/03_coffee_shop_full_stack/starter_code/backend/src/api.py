import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
# Set to true to output Autherror exceptions
app.config['PROPAGATE_EXCEPTIONS'] = True
setup_db(app)
CORS(app)

''' 
Readme...
Ctrl + shft + P  format pep8
Frontend
In order to run the frontend npm install ,npm uninstall node-sass 
 npm install sass , then ionic serve while in the frontend folder
 Ionic take a bit of time to run
 
 Backend
 In order to run the backend upgrade and install requirements.txt file
 Then while in the src in the backend $env:FLASK_APP="api.py", flask run

'''

# db_drop_and_create_all()

# ROUTES
# This endpoint doesnt need a token since its for public

@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]

    return jsonify({
        "success": True,
        "drinks": formatted_drinks
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_detailed_drinks(token):
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]

    return jsonify({
        "success": True,
        "drinks": formatted_drinks
    })
# Able to post using manager profile,
# however the test on the post creating a dictionary as
# a final result for recipe instead of list
# hence, getting error when using the get_drinks() fun,
# when using the correct body, it works well
# [{"name": "water", "color": "blue", "parts": 1}]
#  when the braces(list) added it works well
# check the input in database.db (vscode sqlite viewer)

# Utilizing json.dumps to fetch the data for recipe
@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def create_drinks(token):
    body = request.get_json()
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    try:
        drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        drink.insert()

        return jsonify({
            "success": True,
            "drinks": drink.long()
        })
    except:
        abort(422)

# getting error for recipe, stating expecting array error


@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drinks(token, drink_id):
    body = request.get_json()
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
        if "title" in body:
            drink.title = body.get("title")
        if "recipe" in body:
            drink.recipe = json.dumps(body['recipe'])
        drink.update()

        return jsonify({
            "success": True,
            "drinks": drink.long()
        })
    except:
        abort(422)


@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drinks(token, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            "success": True,
            "delete": drink_id
        })
    except:
        abort(422)

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
    }), 404


# To handle Auth Errors
# Imported Autherror,
# Still not getting the correct errors, getting 500 server error only
# @app.errorhandler(AuthError)
# def handle_auth_error(ex):
#     response = jsonify(ex.error)
#     response.status_code = ex.status_code
#     return response
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error_code": error.status_code,
        "error_message": error.error
    }), error.status_code


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal server error"
    }), 500


# In order to run our app as python api.py
if __name__ == '__main__':
    app.debug = True
    app.run(host="127.0.0.1")
