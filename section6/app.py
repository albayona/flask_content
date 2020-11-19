from flask import Flask, request, jsonify
from flask_restful import Api
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims, jwt_refresh_token_required, verify_fresh_jwt_in_request
)

from resources.content import ContentByInterests, Content, ContentList, ContentFile
from security import authenticate, identity
from resources.user import UserRegister
from resources.item import Item, ItemList
from resources.store import Store, StoreList

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'jose'
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)  # /auth

@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return user.role

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    user = authenticate(username, password)

    if not user:
        return jsonify({"msg": "Bad username or password"}), 401

    # We can now pass this complex object directly to the
    # create_access_token method. This will allow us to access
    # the properties of this object in the user_claims_loader
    # function, and get the identity of this object from the
    # user_identity_loader function.
    access_token = create_access_token(identity=user)
    ret = {'access_token': access_token}
    return jsonify(ret), 200


@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    ret = {
        'current_identity': get_jwt_identity(),
        'current_roles': get_jwt_claims()
    }
    return jsonify(ret), 200

api.add_resource(Content, '/content/<string:id>', '/content')
api.add_resource(ContentList, '/contents')
api.add_resource(ContentByInterests, '/interests/<string:key>')
api.add_resource(ContentFile, '/upload')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=8080, debug=True)

