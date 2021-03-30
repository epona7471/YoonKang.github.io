from movie_app import db

class Preference(db.Model):
    __tablename__ = 'preference'
    id = db.Column(db.Integer, primary_key=True)
    genre1 = db.Column(db.String(64))
    genre2 = db.Column(db.String(64))
    year_range = db.Column(db.Integer)

    def __repr__(self):
        return f"{self.id}, {self.genre1}, {self.genre2}, {self.year_range}"
