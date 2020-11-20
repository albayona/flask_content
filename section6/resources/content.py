from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse

from flask import current_app as app, request
from werkzeug.utils import secure_filename

import s3config
from models.content_model import ContentModel, InterestModel
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from s3helpers import upload_file_to_s3
from security import role_required

with app.app_context():
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )




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





class ContentByInterests(Resource):
    decorators = [limiter.limit("2/10seconds")]
    @jwt_required
    def get(self, key):
        return {'contents': InterestModel.find_by_keyword(key).json_contents()}


class ContentFile(Resource):

    @jwt_required
    @role_required("admin")
    def post(self):

        file = request.files["file"]

        if file:
            file.filename = secure_filename(file.filename)
            output = upload_file_to_s3(file, s3config.S3_BUCKET)
        else:
            return {"message": "File is not valid"}, 400

        return {"url": output}, 200


class ContentList(Resource):



    # @inject
    # def getLimiter(service: LimiterService):
    #     print(f"MyService instance is {service}")  # We want to see the object that gets created
    #     return service.get_data()
    #
    # decorators = [getLimiter.limit("2 per minute")]

    decorators = [limiter.limit("2/10seconds")]

    @jwt_required
    @role_required("admin")
    def get(self):
        return {'contents': list(map(lambda x: x.json(), ContentModel.query.all()))}
