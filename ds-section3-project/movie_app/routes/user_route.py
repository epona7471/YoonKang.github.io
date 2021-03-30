from flask import Blueprint, request, redirect, url_for, Response
from movie_app.models.Preference_model import Preference, db
from movie_app.models.Movies_model import Movies, db
#from movie_app.services.tweepy_api import get_user, get_tweets
#from movie_app.services.embedding_api import get_embeddings

bp = Blueprint('user', __name__)


@bp.route('/user', methods=['POST'])
def add_user():
    """
    add_user 함수는 JSON 형식으로 전달되는 폼 데이터로 유저를 트위터에서 조회한 뒤에
    해당 유저와 해당 유저의 트윗들을 벡터화한 값을 데이터베이스에 저장합니다.

    요구사항:
      - HTTP Method: `POST`
      - Endpoint: `api/user`
      - 받는 JSON 데이터 형식 예시:
            ```json
            {
                "username":"업데이트할 유저의 username",
            }
            ```
    """
    
    genre_1 = request.form['genre_1']
    genre_2 = request.form['genre_2']
    year_range = request.form['year']
    if (genre_1 and genre_2 and year_range) is not None:                                     #이거 좀 애매해서 확인해봐야함
      new_preference = Preference(genre1 = genre_1, genre2=genre_2, year_range=year_range)
      db.session.add(new_preference)
      db.session.commit()
      return redirect(url_for('main.user_index', msg_code=0), code=200)
    else:
      return "Needs preference data", 400

@bp.route('/user/')
@bp.route('/user/<int:preference_id>')
def delete_user(preference_id=None):
    """
    delete_user 함수는 `user_id` 를 엔드포인트 값으로 넘겨주면 해당 아이디 값을 가진 유저를 데이터베이스에서 제거해야 합니다.

    요구사항:
      - HTTP Method: `GET`
      - Endpoint: `api/user/<user_id>`

    상황별 요구사항:
      -  `user_id` 값이 주어지지 않은 경우:
        - 리턴값: 없음
        - HTTP 상태코드: `400`
      - `user_id` 가 주어졌지만 해당되는 유저가 데이터베이스에 없는 경우:
        - 리턴값: 없음
        - HTTP 상태코드: `404`
      - 주어진 `username` 값을 가진 유저를 정상적으로 데이터베이스에서 삭제한 경우:
        - 리턴값: main_route.py 에 있는 user_index 함수로 리다이렉트 합니다.
        - HTTP 상태코드: `200`
    """
    #user_id = request.args.get('user_id')
    
    if preference_id is None:
      #breakpoint()
      return "",400
    else:
      temp = Preference.query.filter_by(id = preference_id).first()
      if temp is None:
        return "",404
      else:
        db.session.delete(temp)
        db.session.commit()
        return redirect(url_for('main.user_index', msg_code=3), code=200)
 
