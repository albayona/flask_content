from flask import request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_claims, create_refresh_token, \
    jwt_required, get_raw_jwt, \
    jwt_refresh_token_required, get_jwt_identity

from blacklist import BLACKLIST
from functools import update_wrapper
from flask_restful import abort, Resource, reqparse
from werkzeug.security import safe_str_cmp

from models.user_model import UserModel


def authenticate(username, password):
    user = UserModel.find_by_username(username)
    if user and safe_str_cmp(user.password, password):
        return user


def identity(payload):
    user_id = payload['identity']
    return UserModel.find_by_id(user_id)


def role_required(role):
    def decorator(fn):
        def wrapped_function(*args, **kwargs):
            # For authorization er return status code 403
            if not safe_str_cmp(get_jwt_claims(), role):
                return {"msg": "You do not meet the roles required for this operation"}, 403
            return fn(*args, **kwargs)

        return update_wrapper(wrapped_function, fn)

    return decorator


class Login(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('username', type=str, required=True, help="This field cannot be blank")
    parser.add_argument('password', type=str, required=True, help="This field cannot be blank")

    def post(self):
        data = Login.parser.parse_args()

        user = UserModel.find_by_username(data['username'])

        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity=user, fresh=True)
            refresh_token = create_refresh_token(user)
            return {
                       'access_token': access_token,
                       'refresh_token': refresh_token
                   }, 200

        return {"message": "Invalid Credentials!"}, 401


class Logout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        BLACKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200
