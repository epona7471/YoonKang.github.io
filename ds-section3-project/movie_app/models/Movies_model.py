from movie_app import db
#user_model
class Movies(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    imdb_id = db.Column(db.String(64))
    title = db.Column(db.String(64), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String)

    def __repr__(self):
        return f"User {self.id}"
