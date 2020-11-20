from flask import Flask, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity, get_jwt_claims
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Api

from blacklist import BLACKLIST
from resources.booklist import BookListRegContent, BooklistRegister, BooklistContentList

from resources.student import StudentRegister, StudentCode, StudentsList, StudentBooklistsList, \
    StudentBooklist, StudentRegBooklist
from security import Login, role_required, Logout, TokenRefresh

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'jose'
api = Api(app)
app.app_context().push()

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

app.config[
    'JWT_SECRET_KEY'] = 'jose'  # we can also use app.secret like before, Flask-JWT-Extended can recognize both
app.config['JWT_BLACKLIST_ENABLED'] = True  # enable blacklist feature
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access',
                                            'refresh']  # allow blacklisting for access and refresh tokens
jwt = JWTManager(app)  # /auth


@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return user.type


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST


# The following callbacks are used for customizing jwt response/error messages.
# The original ones may not be in a very pretty format (opinionated)
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'message': 'The token has expired.',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(
        error):  # we have to keep the argument here, since it's passed in by the caller internally
    return jsonify({
        'message': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        'error': 'authorization_required'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        "description": "The token is not fresh.",
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        "description": "The token has been revoked.",
        'error': 'token_revoked'
    }), 401


# JWT configuration ends


@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/protected', methods=['GET'])
@jwt_required
@role_required("f")
def protected():
    ret = {
        'current_identity': get_jwt_identity(),
        'current_roles': get_jwt_claims()
    }
    return jsonify(ret), 200


from resources.content import ContentList, Content, ContentByInterests, ContentFile

api.add_resource(Content, '/content/<string:id>', '/content/')
api.add_resource(ContentList, '/contents/')
api.add_resource(ContentByInterests, '/interests/<string:key>')
api.add_resource(ContentFile, '/upload/')
api.add_resource(Login, '/login/')
api.add_resource(Logout, '/logout/')
api.add_resource(TokenRefresh, '/refresh/')
api.add_resource(BookListRegContent, '/booklists/<string:name>/')
api.add_resource(BooklistRegister, '/booklists/')
api.add_resource(BooklistContentList, '/booklists/<string:name>/contents/')


api.add_resource(StudentRegister, '/students/')
api.add_resource(StudentCode, '/students/<int:code>')
api.add_resource(StudentsList, '/studentslist/')
api.add_resource(StudentBooklistsList, '/students/<int:code>/booklists/')
api.add_resource(StudentBooklist, '/students/<int:code>/booklists/<string:name>')
api.add_resource(StudentRegBooklist, '/students/<int:code>/booklists/')


if __name__ == '__main__':
    from db import db

    db.init_app(app)
    app.run(port=5000, debug=True)
