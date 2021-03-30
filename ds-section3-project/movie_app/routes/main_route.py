from flask import Blueprint, render_template, request #db추가하고 user query 가져오기?
from movie_app.utils import main_funcs
from movie_app import db
from movie_app.models.Preference_model import Preference
from movie_app.models.Movies_model import Movies

#from twit_app.services import tweepy_api, embedding_api
#실행전에 db migration 명령어 실행, no search table error
#python -m flask run
"""
1. 디비랑 매칭
- tweet_model, user_model
2. 데이터 베이스와 관련된 코드 작성
- main_route
3. db 연결 (flask DB CLI )
4. user_route 수정
5. tweepy_api

export FLASK_APP=twit_app
flask run
"""

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/compare', methods=["GET", "POST"])
def compare_index():
    """
    users 에 유저들을 담아 넘겨주세요. 각 유저 항목은 다음과 같은 딕셔너리
    형태로 넘겨주셔야 합니다.
     -  {
            "id" : "유저의 아이디 값이 담긴 숫자",
            "username" : "유저의 유저이름 (username) 이 담긴 문자열"
        }

    prediction 은 다음과 같은 딕셔너리 형태로 넘겨주셔야 합니다:
     -   {
             "result" : "예측 결과를 담은 문자열입니다",
             "compare_text" : "사용자가 넘겨준 비교 문장을 담은 문자열입니다"
         }
    """
    #request.args.get()
    preferences = Preference.query.all() 
    movie = None
    if request.method == "POST":
        request_data = request.form.get('preference')
        if request_data:
            preference_id = request_data
            preference_selected = Preference.query.filter_by(id=preference_id).first()
            genre1_temp = preference_selected.genre1
            genre2_temp = preference_selected.genre2
            year_temp = preference_selected.year_range
            movie_list = Movies.query.all()
            for movie in movie_list:
                year_lower = int(year_temp[:4])
                year_upper = int(year_temp[-4:])
                if (genre1_temp in movie.genre) and (genre2_temp in movie.genre) and (movie.year >= year_lower and movie.year <= year_upper):
                    return render_template('compare_user.html', preferences=preferences, movie=movie), 200
            movie = None
            return render_template('compare_user.html', preferences=preferences, movie=movie), 200
    return render_template('compare_user.html',preferences=preferences, movie=movie), 200

        
#    preferences = Preference.query.all()
    

    return render_template('compare_user.html', preferences=preferences, prediction=prediction), 200

@bp.route('/user')
def user_index():
    """
    user_list 에 유저들을 담아 템플렛 파일에 넘겨주세요
    """

    msg_code = request.args.get('msg_code', None)
    
    alert_msg = main_funcs.msg_processor(msg_code) if msg_code is not None else None

    preference_list = Preference.query.all()
#    for preference in Preferences:
#        temp = {'id' : preference.id,
#                'Genre1' : preference.genre1,
#                'Genre2' : preference.genre2,
#                'year_range' : preference.year_range}
#        preference_list.append(temp)

    genre_list = ['Comedy', 'Fantasy', 'Romance', 'Action', 'Crime', 'Drama', 'Thriller', 'Family', 'Biography', 'History', 'Horror',
                  'Sci-Fi', 'Mystery', 'Adventure', 'War', 'Music', 'Western', 'Animation','Sport', 'Musical', 'Reality-TV', 'News']
    year_list = ['1990~2000','2000~2010','2010~2020']
 
    return render_template('user.html', alert_msg=alert_msg, preference_list=preference_list, genre_list=genre_list, year_list=year_list)
