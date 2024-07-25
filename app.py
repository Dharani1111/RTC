from flask import Flask, json, jsonify, request
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)


app.secret_key = "secretkey"

# Configure MongoDB URI
app.config['MONGO_URI'] = "mongodb://localhost:27017/emp"

# Initialize PyMongo
mongo = PyMongo(app)

@app.route('/add', methods=['POST'])
def add_user():
    _json = request.json
    _name = _json.get('name')
    _email = _json.get('email')
    _password = _json.get('pwd')

    # Validate input
    if not _name or not _email or not _password:
        return jsonify({"message": "Name, email, and password are required"}), 400

    try:
        _hashed_password = generate_password_hash(_password)
        mongo.db.employee.insert_one({'name': _name, 'email': _email, 'pwd': _hashed_password})
        return jsonify({"message": "User added successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@app.route('/emp', methods=['GET'])
def users():
    try:
        users_cursor = mongo.db.employee.find()
        users_list = list(users_cursor)  # Convert cursor to list
        return jsonify(json.loads(dumps(users_list))), 200  # Convert list to JSON
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@app.route('/emp/<id>', methods=['GET'])
def user(id):
    try:
        user = mongo.db.employee.find_one({'_id': ObjectId(id)})
        if user:
            return dumps(user), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@app.route('/update/<id>', methods=['PUT'])
def update_user(id):
    _json = request.json
    _name = _json.get('name')
    _email = _json.get('email')
    _password = _json.get('pwd')

    # Validate input
    if not _name or not _email or not _password:
        return jsonify({"message": "Name, email, and password are required"}), 400

    try:
        _hashed_password = generate_password_hash(_password)
        update_result = mongo.db.employee.update_one(
            {'_id': ObjectId(id)},
            {'$set': {'name': _name, 'email': _email, 'pwd': _hashed_password}}
        )

        if update_result.matched_count == 0:
            return jsonify({"message": "User not found"}), 404

        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@app.route('/delete/<id>', methods=['DELETE'])
def delete_user(id):
    try:
        delete_result = mongo.db.employee.delete_one({'_id': ObjectId(id)})
        
        if delete_result.deleted_count == 0:
            return jsonify({"message": "User not found"}), 404

        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

if __name__ == "__main__":
    app.run(debug=True, port=5001)
