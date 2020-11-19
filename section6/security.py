from flask import request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_claims



from models.user import UserModel
from functools import update_wrapper
from flask_restful import abort, Resource, reqparse
from werkzeug.security import safe_str_cmp

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
    parser.add_argument('type', type=str, required=True, help="This field cannot be blank")

    def post(self):
        data = Login.parser.parse_args()

        user = authenticate(data["username"], data["password"])

        if not user:
            return jsonify({"msg": "Bad username or password"}), 401

        # We can now pass this complex object directly to the
        # create_access_token method. This will allow us to access
        # the properties of this object in the user_claims_loader
        # function, and get the identity of this object from the
        # user_identity_loader function.
        access_token = create_access_token(identity=user)
        ret = {'access_token': access_token}
        return ret, 200

