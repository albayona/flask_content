import copy

from flask_cors import cross_origin
from flask_restful import Resource, reqparse

from models.course_model import CourseModel


class CourseRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="Must have a name.")
    parser.add_argument('course_code', type=str, required=True, help="Must have a course code.")
    parser.add_argument('description', type=str, required=True, help="Must have a description.")

    @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
    def post(self):
        data = CourseRegister.parser.parse_args()

        if CourseModel.find_by_code(data['course_code']):
            return {"message": f"Course with course code: {data['course_code']} already "
                               f"exists."}, 400

        course = CourseModel(**data)  # unpacking the dictionary
        course.save_to_db()

        return {"message": f"Course was created successfully."}, 201


class CourseCode(Resource):

    @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
    def get(self, course_code: str):
        # only search courses
        course = CourseModel.find_by_code(course_code)
        if course:
            return course.json(), 200
        return {'message': 'Course not found.'}, 404

    @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
    def put(self, course_code: str):

        # This parser will be used to update fields that can me modifiable
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=False)
        parser.add_argument('description', type=str, required=False)
        parser.add_argument('course_code', type=str, required=False)

        data = parser.parse_args()
        course = CourseModel.find_by_code(course_code)

        if course is None:
            # If the course isn't found, create a new coruse using the Course parser

            # Creates a copy of the Course parser and removes the 'code' argument so that
            #   it is no longer necessary in the request body
            put_parser = copy.copy(parser)
            put_parser.remove_argument('course_code')

            data1 = put_parser.parse_args()
            data1['course_code'] = course_code

            admin = CourseModel(**data1)
            admin.save_to_db()
            return admin.json(), 201

        course.name = data['name']
        course.description = data['description']

        course.save_to_db()
        return course.json(), 200

    @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
    def delete(self, course_code: str):
        course_to_delete = CourseModel.find_by_code(course_code)
        if course_to_delete:
            course_to_delete.delete_from_db()
            return {'message': 'Course deleted.'}, 200
        return {}, 204


class CourseName(Resource):

    @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
    def get(self, name: str):
        # only search courses
        course = CourseModel.find_by_name(name)
        if course:
            return course.json()
        return {'message': 'Course not found.'}, 404


class CoursesList(Resource):

    @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
    def get(self):
        return {'courses': [course.json() for course in CourseModel.query.all()]}
