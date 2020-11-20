import copy

from flask_restful import Resource, reqparse

from models.booklist_model import BooklistModel
from models.user_model import AdminModel, UserModel
from resources.user_parser import UserParser


class AdminRegister(Resource):

    def post(self):
        data = UserParser.parser.parse_args()

        if not data['username'][0].isalpha():
            return {'message': 'Invalid username.'}, 400

        if UserModel.find_by_username(data['username']):
            return {"message": f"User with username: {data['username']} already exists."}, 400

        if UserModel.find_by_code(data['code']):
            return {"message": f"User with code: {data['code']} already exists."}, 400

        if UserModel.find_by_email(data['email']):
            return {"message": f"User with email: {data['email']} already exists."}, 400

        user = AdminModel(**data)  # unpacking the dictionary
        user.save_to_db()

        return {"message": f"Admin was created successfully."}, 201


class AdminCode(Resource):

    def get(self, code: int):
        # only search admins
        admin = AdminModel.find_by_code(code)
        if admin:
            return admin.json(), 200
        return {'message': 'Admin not found.'}, 404

    def put(self, code: int):

        # This parser will be used to update fields that can me modifiable
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=False)
        parser.add_argument('first_name', type=str, required=False)
        parser.add_argument('last_name', type=str, required=False)
        parser.add_argument('description', type=str, required=False)
        parser.add_argument('picture', type=str, required=False)

        data = parser.parse_args()
        admin = AdminModel.find_by_code(code)

        if not data['username'][0].isalpha():
            return {'message': 'Invalid username.'}, 400

        if admin is None:
            # If the admin isn't found, create a new admin using the user parser

            # Creates a copy of the User parser and removes the 'code' argument so that
            #   it is no longer necessary in the request body
            put_parser = copy.copy(UserParser.parser)
            put_parser.remove_argument('code')

            data1 = put_parser.parse_args()
            data1['code'] = code

            admin = AdminModel(**data1)
            admin.save_to_db()
            return admin.json(), 201

        admin.username = data['username']
        admin.first_name = data['first_name']
        admin.last_name = data['last_name']
        admin.description = data['description']
        admin.picture = data['picture']

        admin.save_to_db()
        return admin.json(), 200

    def delete(self, code: int):
        admin_to_delete = AdminModel.find_by_code(code)
        if admin_to_delete:
            admin_to_delete.delete_from_db()
            return {'message': 'Admin deleted.'}, 200
        return {}, 204


class AdminBooklistsList(Resource):
    def get(self, code):
        admin = AdminModel.find_by_code(code)

        if admin:
            return {"message": [booklist.json() for booklist in admin.booklists]}
        return {"message": f"Admin {code} does not exist."}, 404


class AdminRegBooklist(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True)

    def post(self, code):

        name = AdminRegBooklist.parser.parse_args()['name']

        booklist = BooklistModel.find_by_name(name)
        if booklist:
            Admin = AdminModel.find_by_code(code)
            if Admin:

                # make sure the booklist isn't already added
                if booklist in Admin.booklists:
                    return {"message": f"Booklist {booklist.name} already added."}, 200

                Admin.booklists.append(booklist)
                Admin.save_to_db()
                return {"message": "Booklist added successfully."}, 201

            return {"message": f"Admin {code} does not exist."}, 404
        return {"message": f"booklist {name} does not exist."}, 404


class AdminBooklist(Resource):

    def delete(self, code: str, name: str):
        # if booklist and Admin exist, delete the booklist
        booklist = BooklistModel.find_by_name(name)

        if booklist:
            admin = AdminModel.find_by_code(code)
            if admin:
                # make sure the booklist isn't already removed
                if booklist in admin.booklists:
                    admin.booklists.remove(booklist)
                    admin.save_to_db()
                    return {"message": f"Booklist {booklist.name} removed."}, 200
                return {"message": f"Admin {code} not in {booklist}"}, 404
            return {"message": f"Admin {code} does not exist."}, 404
        return {"message": f"Booklist {booklist} does not exist."}, 404

    def get(self, code: str, name: str):
        # if booklist and admin exist, delete the booklist
        booklist = BooklistModel.find_by_name(name)
        if booklist:
            admin = AdminModel.find_by_code(code)
            if admin:
                # make sure the booklist isn't already removed
                if booklist in admin.booklists:
                    print(f"#######{booklist.json()}")
                    return {"booklist": booklist.json()}, 200
                return {"message": f"Booklist {booklist.name} not found."}, 404
            return {"message": f"Admin {code} does not exist."}, 404
        return {"message": f"Booklist {booklist} does not exist."}, 404


class AdminUsername(Resource):

    def get(self, username: str):
        # only search admins
        admin = AdminModel.find_by_username(username)
        if admin:
            return admin.json()
        return {'message': 'Admin not found.'}, 404


class AdminsList(Resource):
    def get(self):
        return {'admins': [admin.json() for admin in AdminModel.query.all()]}
