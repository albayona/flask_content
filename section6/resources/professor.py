import copy
from flask_restful import Resource, reqparse

from models.course_model import CourseModel
from models.booklist_model import BooklistModel

from models.user_model import ProfessorModel, UserModel
from resources.user_parser import UserParser



class ProfessorRegister(Resource):

    def post(self):
        data = UserParser.parser.parse_args()

        # ensure username is proper
        if not data['username'][0].isalpha():
            return {"message": f"Invalid username."}, 400

        if UserModel.find_by_username(data['username']):
            return {"message": f"User with username: {data['username']} already exists."}, 400

        if UserModel.find_by_code(data['code']):
            return {"message": f"User with code: {data['code']} already exists."}, 400

        if UserModel.find_by_email(data['email']):
            return {"message": f"User with email: {data['email']} already exists."}, 400

        user = ProfessorModel(**data)  # unpacking the dictionary
        user.save_to_db()

        return {"message": f"Professor was created successfully."}, 201


class ProfessorCode(Resource):

    def get(self, code: int):
        # only search professors
        professor = ProfessorModel.find_by_code(code)
        if professor:
            return professor.json(), 200
        return {'message': 'Professor not found.'}, 404

    def put(self, code: int):

        # This parser will be used to update fields that can me modifiable
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=False)
        parser.add_argument('first_name', type=str, required=False)
        parser.add_argument('last_name', type=str, required=False)
        parser.add_argument('description', type=str, required=False)
        parser.add_argument('picture', type=str, required=False)

        data = parser.parse_args()
        professor = ProfessorModel.find_by_code(code)

        if not data['username'][0].isalpha():
            return {'message': 'Invalid username.'}, 400

        if professor is None:
            # If the professor isn't found, create a new professor using the User parser

            # Creates a copy of the User parser and removes the 'code' argument so that
            #   it is no longer necessary in the request body
            put_parser = copy.copy(UserParser.parser)
            put_parser.remove_argument('code')

            data1 = put_parser.parse_args()
            data1['code'] = code

            admin = ProfessorModel(**data1)
            admin.save_to_db()
            return admin.json(), 201

        professor.username = data['username']
        professor.first_name = data['first_name']
        professor.last_name = data['last_name']
        professor.description = data['description']
        professor.picture = data['picture']

        professor.save_to_db()
        return professor.json(), 200

    def delete(self, code):
        professor_to_delete = ProfessorModel.find_by_code(code)
        if professor_to_delete:
            professor_to_delete.delete_from_db()
            return {'message': 'Professor deleted.'}, 200
        return {}, 204

class ProfessorRegCourse(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('course_code', type=str, required=True)

    def post(self, code):

        course_code = ProfessorRegCourse.parser.parse_args()['course_code']

        course = CourseModel.find_by_code(course_code)
        if course:
            professor = ProfessorModel.find_by_code(code)
            if professor:
                # make sure the course isn't already added
                if course in professor.courses:
                    return {"message": f"Course {course.course_code} already added."}, 200

                professor.courses.append(course)

                professor.save_to_db()
                return {"message": "Course added successfully."}, 201

            return {"message": f"Professor {code} does not exist."}, 404
        return {"message": f"Course {course_code} does not exist."}, 404


class ProfessorDeleteCourse(Resource):

    def delete(self, code: str, course_code: str):
        # if course and professor exist, add the cours
        course = CourseModel.find_by_code(course_code)

        if course:
            professor = ProfessorModel.find_by_code(code)
            if professor:
                # make sure the course isn't already removed
                if course in professor.courses:
                    professor.courses.remove(course)
                    professor.save_to_db()
                    return {"message": f"Course {course.course_code} removed."}, 200
                return {"message": f"Professor {code} not in {course_code}"}, 404
            return {"message": f"Professor {code} does not exist."}, 404
        return {"message": f"Course {course_code} does not exist."}, 404

class ProfessorRegBooklist(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True)

    def post(self, code):

        name = ProfessorRegBooklist.parser.parse_args()['name']

        booklist = BooklistModel.find_by_name(name)
        if booklist:
            Professor = ProfessorModel.find_by_code(code)
            if Professor:

                # make sure the booklist isn't already added
                if booklist in Professor.booklists:
                    return {"message": f"Booklist {booklist.name} already added."}, 200

                Professor.booklists.append(booklist)
                Professor.save_to_db()
                return {"message": "Booklist added successfully."}, 201

            return {"message": f"Professor {code} does not exist."}, 404
        return {"message": f"booklist {name} does not exist."}, 404


class ProfessorBooklist(Resource):

    def delete(self, code: str, name: str):
        # if booklist and Professor exist, delete the booklist
        booklist = BooklistModel.find_by_name(name)

        if booklist:
            professor = ProfessorModel.find_by_code(code)
            if professor:
                # make sure the booklist isn't already removed
                if booklist in professor.booklists:
                    professor.booklists.remove(booklist)
                    professor.save_to_db()
                    return {"message": f"Booklist {booklist.name} removed."}, 200
                return {"message": f"Professor {code} not in {booklist}"}, 404
            return {"message": f"Professor {code} does not exist."}, 404
        return {"message": f"Booklist {booklist} does not exist."}, 404

    def get(self, code: str, name: str):
        # if booklist and professor exist, delete the booklist
        booklist = BooklistModel.find_by_name(name)
        if booklist:
            professor = ProfessorModel.find_by_code(code)
            if professor:
                # make sure the booklist isn't already removed
                if booklist in professor.booklists:
                    print(f"#######{booklist.json()}")
                    return {"booklist": booklist.json()}, 200
                return {"message": f"Booklist {booklist.name} not found."}, 404
            return {"message": f"Professor {code} does not exist."}, 404
        return {"message": f"Booklist {booklist} does not exist."}, 404

class ProfessorUsername(Resource):

    def get(self, username: str):
        # only search students
        professor = ProfessorModel.find_by_username(username)
        if professor:
            return professor.json()
        return {'message': 'Professor not found.'}, 404


class ProfessorsList(Resource):
    def get(self):
        return {'professors': [professor.json() for professor in ProfessorModel.query.all()]}


class ProfessorCoursesList(Resource):
    def get(self, code):
        professor = ProfessorModel.find_by_code(code)

        if professor:
            return {"message": [course.json() for course in professor.courses]}
        return {"message": f"Professor {code} does not exist."}, 404

class ProfessorBooklistsList(Resource):
    def get(self, code):
        professor = ProfessorModel.find_by_code(code)

        if professor:
            return {"message": [booklist.json() for booklist in professor.booklists]}
        return {"message": f"Professor {code} does not exist."}, 404

