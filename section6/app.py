from flask import Flask, request, jsonify
from flask_restful import Api
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims, jwt_refresh_token_required, verify_fresh_jwt_in_request, current_user
)

from resources.content import ContentByInterests, Content, ContentList, ContentFile
from security import authenticate, identity, Login, role_required
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
    return user.type



@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username


@app.route('/protected', methods=['GET'])
@jwt_required
@role_required("f")
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
api.add_resource(Login, '/auth')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=8080, debug=True)

