from flask_restful import Resource, reqparse
from flask import jsonify

from models.booklist_model import BooklistModel
from models.course_model import CourseModel
from models.major_model import MajorModel
from models.user_model import UserModel, StudentModel
import copy

from resources.user_parser import UserParser


class StudentRegister(Resource):
    student_parser = reqparse.RequestParser()
    student_parser.add_argument('semester', type=int, required=True,
                                help="Must have a semester.")

    def post(self):

        data = UserParser.parser.parse_args()
        data['semester'] = StudentRegister.student_parser.parse_args()['semester']

        # ensure username is proper
        if not data['username'][0].isalpha():
            return {"message": f"Invalid username."}, 400

        if UserModel.find_by_username(data['username']):
            return {"message": f"User with username: {data['username']} already exists."}, 400

        if UserModel.find_by_code(data['code']):
            return {"message": f"User with code: {data['code']} already exists."}, 400

        if UserModel.find_by_email(data['email']):
            return {"message": f"User with email: {data['email']} already exists."}, 400

        user = StudentModel(**data)  # unpacking the dictionary
        user.save_to_db()

        return {"message": f"Student was created successfully."}, 201


class StudentCode(Resource):

    def get(self, code: int):
        # only search students
        student = StudentModel.find_by_code(code)
        if student:
            return student.json(), 200
        return {'message': 'Student not found.'}, 404

    def put(self, code):

        # This parser will be used to update fields that can me modifiable
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=False)
        parser.add_argument('first_name', type=str, required=False)
        parser.add_argument('last_name', type=str, required=False)
        parser.add_argument('description', type=str, required=False)
        parser.add_argument('picture', type=str, required=False)

        student = StudentModel.find_by_code(code)
        data = parser.parse_args()

        if not data['username'][0].isalpha():
            return {'message': 'Invalid username.'}, 400

        if student is None:
            # If the student isn't found, create a new student using the User parser

            # Creates a copy of the User parser and removes the 'code' argument so that
            #   it is no longer necessary in the request body
            put_parser = copy.copy(UserParser.parser)
            put_parser.remove_argument('code')

            data1 = put_parser.parse_args()

            # add 'code' and 'semester' to the data1 dictionary so that it can unpacked properly
            data1['code'] = code
            data1['semester'] = StudentRegister.student_parser.parse_args()['semester']

            admin = StudentModel(**data1)
            admin.save_to_db()
            return admin.json(), 201

        student.username = data['username']
        student.first_name = data['first_name']
        student.last_name = data['last_name']
        student.description = data['description']
        student.picture = data['picture']

        student.save_to_db()
        return student.json(), 200

    def delete(self, code):
        student_to_delete = StudentModel.find_by_code(code)
        if student_to_delete:
            student_to_delete.delete_from_db()
            return {'message': 'Student deleted.'}, 200
        return {}, 204


class StudentRegCourse(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('course_code', type=str, required=True)

    def post(self, code):

        course_code = StudentRegCourse.parser.parse_args()['course_code']

        course = CourseModel.find_by_code(course_code)
        if course:
            student = StudentModel.find_by_code(code)
            if student:

                # make sure the course isn't already added
                if course in student.courses:
                    return {"message": f"Course {course.course_code} already added."}, 200

                student.courses.append(course)

                student.save_to_db()
                return {"message": "Course added successfully."}, 201

            return {"message": f"Student {code} does not exist."}, 404
        return {"message": f"Course {course_code} does not exist."}, 404


class StudentDeleteCourse(Resource):

    def delete(self, code: str, course_code: str):
        # if course and student exist, add the cours
        course = CourseModel.find_by_code(course_code)

        if course:
            student = StudentModel.find_by_code(code)
            if student:
                # make sure the course isn't already removed
                if course in student.courses:
                    student.courses.remove(course)
                    student.save_to_db()
                    return {"message": f"Course {course.course_code} removed."}, 200
                return {"message": f"Student {code} not in {course_code}"}, 404
            return {"message": f"Student {code} does not exist."}, 404
        return {"message": f"Course {course_code} does not exist."}, 404


class StudentRegMajor(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True)

    def post(self, code):

        name = StudentRegMajor.parser.parse_args()['name']

        major = MajorModel.find_by_name(name)
        if major:
            student = StudentModel.find_by_code(code)
            if student:

                # make sure the course isn't already added
                if major in student.majors:
                    return {"message": f"Major {major.name} already added."}, 200

                student.majors.append(major)

                student.save_to_db()
                return {"message": "Major added successfully."}, 201

            return {"message": f"Student {code} does not exist."}, 404
        return {"message": f"Major {name} does not exist."}, 404


class StudentDeleteMajor(Resource):

    def delete(self, code: str, name: str):
        # if major and student exist, add the major
        major = MajorModel.find_by_name(name)
        if major:
            student = StudentModel.find_by_code(code)
            if student:
                # make sure the major isn't already removed
                if major in student.majors:
                    major.students.remove(student)
                    student.save_to_db()
                    return {"message": f"Course {major.name} removed."}, 200
                return {"message": f"Student {code} not in {major}"}, 404
            return {"message": f"Student {code} does not exist."}, 404
        return {"message": f"Course {major} does not exist."}, 404


class StudentRegBooklist(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True)

    def post(self, code):

        name = StudentRegBooklist.parser.parse_args()['name']

        booklist = BooklistModel.find_by_name(name)
        if booklist:
            student = StudentModel.find_by_code(code)
            if student:

                # make sure the booklist isn't already added
                if booklist in student.booklists:
                    return {"message": f"Booklist {booklist.name} already added."}, 200

                student.booklists.append(booklist)
                student.save_to_db()
                return {"message": "Booklist added successfully."}, 201

            return {"message": f"Student {code} does not exist."}, 404
        return {"message": f"booklist {name} does not exist."}, 404


class StudentBooklist(Resource):

    def delete(self, code: str, name: str):
        # if booklist and student exist, delete the booklist
        booklist = BooklistModel.find_by_name(name)

        if booklist:
            student = StudentModel.find_by_code(code)
            if student:
                # make sure the booklist isn't already removed
                if booklist in student.booklists:
                    student.booklists.remove(booklist)
                    student.save_to_db()
                    return {"message": f"Booklist {booklist.name} removed."}, 200
                return {"message": f"Student {code} not in {booklist}"}, 404
            return {"message": f"Student {code} does not exist."}, 404
        return {"message": f"Booklist {booklist} does not exist."}, 404

    def get(self, code: str, name: str):
        # if booklist and student exist, delete the booklist
        booklist = BooklistModel.find_by_name(name)
        if booklist:
            student = StudentModel.find_by_code(code)
            if student:
                # make sure the booklist isn't already removed
                if booklist in student.booklists:
                    print(f"#######{booklist.json()}")
                    return {"booklist": booklist.json()}, 200
                return {"message": f"Booklist {booklist.name} not found."}, 404
            return {"message": f"Student {code} does not exist."}, 404
        return {"message": f"Booklist {booklist} does not exist."}, 404


class StudentUsername(Resource):

    def get(self, username: str):
        # only search students
        student = StudentModel.find_by_username(username)
        if student:
            return student.json(), 200
        return {'message': 'Student not found.'}, 404


class StudentsList(Resource):
    def get(self):
        return {'students': [student.json() for student in StudentModel.query.all()]}


class StudentCoursesList(Resource):
    def get(self, code):
        student = StudentModel.find_by_code(code)

        if student:
            return {"message": [course.json() for course in student.courses]}
        return {"message": f"Student {code} does not exist."}, 404


class StudentMajorsList(Resource):
    def get(self, code):
        student = StudentModel.find_by_code(code)

        if student:
            return {"message": [major.json() for major in student.majors]}
        return {"message": f"Student {code} does not exist."}, 404


class StudentBooklistsList(Resource):
    def get(self, code):
        student = StudentModel.find_by_code(code)

        if student:
            return {"message": [booklist.json() for booklist in student.booklists]}
        return {"message": f"Student {code} does not exist."}, 404
