from db import db


class MajorModel(db.Model):
    __tablename__ = 'major'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name: str):
        self.name = name

    def json(self):
        return {'name': self.name}

    @classmethod
    def find_by_name(cls, name: str):
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
