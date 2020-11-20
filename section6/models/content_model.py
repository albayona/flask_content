from db import db


class CommentModel(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DATETIME())
    text = db.Column(db.String(130))

    content_id = db.Column(db.Integer, db.ForeignKey('contents.id'))
    content = db.relationship('ContentModel')

    def json(self):
        return {

            'id': self.id,
            'date': self.date,
            'text': self.text

        }


association_table = db.Table('contents_interests', db.Model.metadata,
                             db.Column('contents_id', db.Integer, db.ForeignKey('contents.id')),
                             db.Column('interests_id', db.Integer, db.ForeignKey('interests.id'))
                             )


class InterestModel(db.Model):
    __tablename__ = 'interests'
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(80), unique=True)
    contents = db.relationship(
        "ContentModel", secondary=association_table, back_populates="interests")

    def __init__(self, keyword):
         self.keyword = keyword
         self.contents = []


    def json(self):
        return {
            'id': self.id,
            'keyword': self.keyword,
        }

    def json_contents(self):
        return {
            'contents': [content.json() for content in self.contents]
        }


    @classmethod
    def find_by_keyword(cls, key):
        return cls.query.filter_by(keyword=key).first()



class ContentModel(db.Model):
    __tablename__ = 'contents'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pages = db.Column(db.Integer)
    likes = db.Column(db.Integer)
    title = db.Column(db.String(80))
    creator = db.Column(db.String(80))
    description = db.Column(db.String(80))
    language = db.Column(db.String(80))
    year = db.Column(db.String(20))
    imageURL = db.Column(db.String(80))
    documentURL = db.Column(db.String(80))
    interests = db.relationship("InterestModel", secondary=association_table, back_populates="contents")
    comments = db.relationship('CommentModel', lazy='dynamic')

    def __init__(self,  likes, pages, title, creator, description, language, year, imageURL, documentURL):
        self.likes = likes
        self.pages = pages
        self.title = title
        self.creator = creator
        self.description = description
        self.language = language
        self.year = year
        self.imageURL = imageURL
        self.documentURL = documentURL


    def json(self):
        return {
            'id': self.id,
            'pages': self.pages,
            'likes': self.likes,
            'title': self.title,
            'creator': self.creator,
            'description': self.description,
            'language': self.language,
            'year': self.year,
            'imageURL': self.imageURL,
            'documentURL': self.documentURL,
            'interests':  [interest.json() for interest in self.interests],
            'comments':  [comment.json() for comment in self.comments.all()]
        }

    @classmethod
    def find_by_title(cls, title):
        return cls.query.filter_by(title=title).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


