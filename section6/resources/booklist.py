import copy

from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse

from models.booklist_model import BooklistModel
from models.content_model import ContentModel


class BooklistRegister(Resource): #TODO: change to create under user
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="Must have a name.")
    parser.add_argument('description', type=str, required=True, help="Must have a description.")
    parser.add_argument('imageURL', type=str, required=True, help="Must have an image.")

    @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
    @jwt_required
    def post(self):
        data = BooklistRegister.parser.parse_args()

        if BooklistModel.find_by_name(data['name']):
            return {"message": f"booklist {data['name']} already exists."}, 200

        booklist = BooklistModel(**data)  # unpacking the dictionary
        booklist.save_to_db()

        return {"message": f"Booklist was created successfully."}, 201


class BooklistName(Resource):
    @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
    @jwt_required
    def get(self, name: str):
        # only search booklists
        booklist = BooklistModel.find_by_name(name)
        if booklist:
            return booklist.json()
        return {'message': 'Booklist not found.'}, 404

    @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
    @jwt_required
    def put(self, name: str):

        data = BooklistRegister.parser.parse_args()
        booklist = BooklistModel.find_by_name(name)

        if booklist is None:
            created_booklist = BooklistModel(**data)
            created_booklist.save_to_db()
            return created_booklist.json(), 201

        booklist.name = data['name']
        booklist.save_to_db()
        return booklist.json(), 200

    def delete(self, name: str):
        booklist_to_delete = BooklistModel.find_by_name(name)
        if booklist_to_delete:
            booklist_to_delete.delete_from_db()
            return {'message': 'Booklist deleted.'}, 200
        return {}, 204


class BookListRegContent(Resource):

    @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, help="Must have an id.")
        data = parser.parse_args()
        booklist = BooklistModel.find_by_name(name)

        if booklist:
            content = ContentModel.find_by_id(data['id'])

            if content:
                booklist.contents.append(content)
                booklist.save_to_db()
                return {"message": "Content added successfully."}, 201
            return {"message": "Content does not exist."}, 404
        return {"message": "Booklist does not exist."}, 404


class BooklistList(Resource):
    @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
    def get(self):
        return {'booklists': [booklist.json() for booklist in BooklistModel.query.all()]}


class BooklistContentList(Resource):
    @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
    def get(self, name):
        booklist = BooklistModel.find_by_name(name)

        if booklist:
            return {'contents': [content.json() for content in booklist.contents]}
