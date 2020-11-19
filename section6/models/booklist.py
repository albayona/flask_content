from db import db


association_table = db.Table('booklist_contents', db.Model.metadata,
                             db.Column('booklists_id', db.Integer, db.ForeignKey('booklists.id')),
                             db.Column('contents_id', db.Integer, db.ForeignKey('contents.id')),
                             )

class BooklistModel(db.Model):
    __tablename__ = 'booklists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.String(80))
    imageURL = db.Column(db.String(80))
    contents = db.relationship(
        "ContentModel", secondary=association_table)

    def __init__(self, name, description, imageURL):
        self.name = name
        self.description = description
        self.imageURL = imageURL

    def json(self):
        return {

        'name' : self.name,
        'description' : self.description,
        'imageURL' : self.imageURL,
        'contents': [content.json() for content in self.contents],
        }

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()


    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
