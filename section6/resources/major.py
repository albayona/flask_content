import copy

from flask_restful import Resource, reqparse

from models.major_model import MajorModel


class MajorRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="Must have a name.")

    def post(self):
        data = MajorRegister.parser.parse_args()

        if MajorModel.find_by_name(data['name']):
            return {"message": f"Major {data['name']} already exists."}, 200

        major = MajorModel(**data)  # unpacking the dictionary
        major.save_to_db()

        return {"message": f"Major was created successfully."}, 201


class MajorName(Resource):

    def get(self, name: str):
        # only search majors
        major = MajorModel.find_by_name(name)
        if major:
            return major.json()
        return {'message': 'Major not found.'}, 404

    def put(self, name: str):

        # This parser will be used to update fields that can me modifiable
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=False)

        data = parser.parse_args()
        major = MajorModel.find_by_name(name)

        if major is None:
            data1 = parser.parse_args()

            major = MajorModel(**data1)
            major.save_to_db()
            return major.json(), 201

        major.name = data['name']
        major.save_to_db()
        return major.json(), 200

    def delete(self, name: str):
        major_to_delete = MajorModel.find_by_name(name)
        if major_to_delete:
            major_to_delete.delete_from_db()
            return {'message': 'Major deleted.'}, 200
        return {}, 204


class MajorsList(Resource):
    def get(self):
        return {'majors': [major.json() for major in MajorModel.query.all()]}
