from movie_app import db

class Movies_Recommended(db.Model):
    __tablename__ = "movies_recommended"
    id = db.Column(db.Integer, primary_key=True)
    imdb_id = db.Column(db.String(64))
    Prob_score = db.Column(db.Float)
    def __repr__(self):
        return f"Movies_Recommended {self.id}"
