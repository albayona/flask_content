from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
from werkzeug.utils import secure_filename

import s3config
from s3helpers import upload_file_to_s3
from models.content import ContentModel, InterestModel
from security import role_required


class Content(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('pages', type=int, required=True, help="This field cannot be blank")
    parser.add_argument('title', type=str, required=True, help="This field cannot be blank")
    parser.add_argument('creator', type=str, required=True, help="This field cannot be blank")
    parser.add_argument('description', type=str, required=True, help="This field cannot be blank")
    parser.add_argument('language', type=str, required=True, help="This field cannot be blank")
    parser.add_argument('year', type=str, required=True, help="This field cannot be blank")
    parser.add_argument('imageURL', type=str, required=True, help="This field cannot be blank")
    parser.add_argument('documentURL', type=str, required=True, help="This field cannot be blank")
    parser.add_argument('interests', type=list, location='json', required=True, help="This field cannot be blank")

    @jwt_required
    def get(self, id):
        content = ContentModel.find_by_id(id)
        if content:
            return content.json()
        return {'message': 'Content not found'}, 404

    @jwt_required
    def post(self):


        data = Content.parser.parse_args()
        content = ContentModel(
            0,
            data['pages'],
            data['title'],
            data['creator'],
            data['description'],
            data['language'],
            data['year'],
            data['imageURL'],
            data['documentURL']
        )


        interests = data['interests']

        for interestData in interests:
            keyword = interestData["keyword"]

            interest = InterestModel.find_by_keyword(keyword)

            if not interest:
                interest = InterestModel(keyword)

            interest.contents.append(content)
            content.interests.append(interest)

        print(content)

        try:
            content.save_to_db()
        except:
            return {"message": "An error occurred creating the content."}, 500

        return {"message": "Content created successfully."}, 201

    @jwt_required
    @role_required("admin")
    def delete(self, id):
        store = ContentModel.find_by_id(id)
        if store:
            store.delete_from_db()

        return {'message': 'Content deleted'}


@jwt_required
@role_required("admin")
class ContentList(Resource):
    def get(self):
        return {'contents': list(map(lambda x: x.json(), ContentModel.query.all()))}

@jwt_required
class ContentByInterests(Resource):
    def get(self, key):
        return {'contents': InterestModel.find_by_keyword(key).json_contents()}

@jwt_required
class ContentFile(Resource):
    def post(self):

        file = request.files["file"]

        if file:
            file.filename = secure_filename(file.filename)
            output = upload_file_to_s3(file, s3config.S3_BUCKET)
        else:
            return {"message": "File is not valid"}, 400

        return {"url": output}, 200
