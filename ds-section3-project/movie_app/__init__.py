from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import config
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app(config=None):
    app = Flask(__name__)
    
    if app.config["ENV"] == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')
    if config is not None:
        app.config.update(config)

    # app.config.from_object(os.environ['APP_SETTINGS'])
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from movie_app.routes import (main_route, user_route)
    app.register_blueprint(main_route.bp)
    app.register_blueprint(user_route.bp, url_prefix='/api')
    
    from XGboost_model import data_preprocess, XGboost_MovieClassifier, recommendation_update
    
    df_movies, genres = data_preprocess()
    X_test = XGboost_MovieClassifier(df_movies)
    with app.app_context():
        db.create_all()
        recommendation_update(X_test)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
