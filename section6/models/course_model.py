from db import db


class CourseModel(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    course_code = db.Column(db.String(100))
    description = db.Column(db.String(500))

    def __init__(self, name: str, course_code: str, description: str):
        self.name = name
        self.course_code = course_code
        self.description = description

    def json(self):
        return {'name': self.name, 'course_code': self.course_code, 'description': self.description}

    @classmethod
    def find_by_name(cls, name: str):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_code(cls, course_code: str):
        return cls.query.filter_by(course_code=course_code).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
