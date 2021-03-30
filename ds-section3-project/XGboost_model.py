import pandas as pd
import numpy as np
from collections import Counter
import joblib
from movie_app.models.Movies_model import Movies, db
from movie_app.models.Movies_Recommended_model import Movies_Recommended, db
from movie_app.models.Preference_model import Preference, db


def data_preprocess():
    #raw data file 불러오기
    df_movies = pd.read_csv('IMDb movies.csv')
    df_ratings = pd.read_csv('IMDb ratings.csv')
    #필요한 demographic data만 취하고 나머지는 제외Mov
    df_ratings = df_ratings[['imdb_title_id','males_18age_avg_vote','males_30age_avg_vote','females_18age_avg_vote','females_30age_avg_vote']]

    df_movies = df_movies.merge(df_ratings,on='imdb_title_id')


    #제거할 feature들을 제거
    df_movies = df_movies.drop(columns = ['imdb_title_id','budget','usa_gross_income','worlwide_gross_income','metascore',
                                          'reviews_from_critics','title','original_title','date_published','language','description'])

    #특이 data 변경
    df_movies['year'] = df_movies['year'].replace('TV Movie 2019',2019)

    # 'year' column을 object 에서 numeric으로 변경
    df_movies['year'] = pd.to_numeric(df_movies['year'])

    #year 1990 이상만 다시 저장
    df_movies = df_movies[(df_movies.year >= 1990)]

    #NaN값 제거
    df_movies = df_movies.dropna(subset=['director','writer','actors','country','production_company','reviews_from_users'])

    #india 영화 제거
    df_movies = df_movies[~df_movies.country.str.contains("India")]
    #df_movies = df_movies[~df_movies.country.str.contains("China")]

    #Duration(상영시간의 경우), 영화가 너무 길면, 거부감을 발생시킬 수 있으므로, 99.8 percentile로 극단치를 제거하도록 한다.
    temp1 = np.percentile(df_movies.duration,99.8)
    temp2 = np.percentile(df_movies.duration,0.02)
    df_movies = df_movies[(df_movies.duration <= temp1) & (df_movies.duration >= temp2)]

    #Genres의 cardinality 집합
    genres = []
    for i in df_movies.genre:
        temp = i.split(', ')
        for j in temp:
            if j in genres:
                continue
            else:
                genres.append(j)

    #country의 cardinality 집합
    countries = []
    for i in df_movies.country:
        temp = i.split(', ')
        for j in temp:
            if j in countries:
                continue
            else:
                countries.append(j)

    #Binary value로 encoding 진행
    for i in genres:
        df_movies[i] = np.where(df_movies['genre'].str.contains(i),1,0)
    for i in countries:
        df_movies[i] = np.where(df_movies['country'].str.contains(i),1,0)


    #director, writer, actor 이름들을 가지고 있는 raw list를 생성
    directors = []
    writers = []
    actors = []
    production_companies = []

    for i in df_movies.director:
        temp = i.split(', ')
        for j in temp:
            directors.append(j)
        
    for i in df_movies.writer:
        temp = i.split(', ')
        for j in temp:
            writers.append(j)

    for i in df_movies.actors:
        temp = i.split(', ')
        for j in temp:
            actors.append(j)

    for i in df_movies.production_company:
        temp = i.split(', ')
        for j in temp:
            production_companies.append(j)

    director_score_list = Counter(directors) 
    writer_score_list = Counter(writers)
    actor_score_list = Counter(actors)
    production_companies_list = Counter(production_companies)

    #해당 dataset의 이름을 score로 교체
    df_movies['director_score'] = [max(director_score_list[j] for j in i.split(', ')) for i in df_movies.director]
    df_movies['writer_score'] = [max(writer_score_list[j] for j in i.split(', ')) for i in df_movies.writer]
    df_movies['actor_score'] = [ sum(actor_score_list[j] for j in i.split(', ')) / len(i.split(', ')) for i in df_movies.actors]
    df_movies['production_company_score'] = [production_companies_list[i] for i in df_movies.production_company]

    #encoding이 완료된 feature들을 제거
    df_movies = df_movies.drop(columns=['director','writer','production_company','actors','genre','country'])

    #추천하는 대상의 성향에 따라 target 점수가 달라질 수 있다.
    target_list = ['avg_vote','males_18age_avg_vote','males_30age_avg_vote','females_18age_avg_vote','females_30age_avg_vote']

    #이번 모델은 모든 사용자의 점수를 기준으로 만든다.
    target = 'avg_vote'
    target_list.remove(target)

    df_movies = df_movies.drop(columns =target_list)
    df_movies = df_movies.drop(columns ='votes')
    df_movies = df_movies.dropna(subset=[target])

    #rating 6.5 이상은 true, 그 이하는 false로 avg_vote값을 변경 
    df_movies[target] = (df_movies[target] >= 6.5)

    return df_movies, genres



##이제 머신러닝 API에 적용해보자. 먼저 train/validation/test set 분리에 있어서는, dimension 대비 dataset의 수가 충분하다고 판단되므로, 3-way holdout method를 적용한다

def XGboost_MovieClassifier(df_movies):
    from sklearn.model_selection import train_test_split
    target = 'avg_vote'
    train, test = train_test_split(df_movies, test_size=4000, 
                                stratify=df_movies[target], random_state=2)

    train, val = train_test_split(train, test_size=4000, 
                                stratify=train[target], random_state=2)

    features = train.drop(columns=[target]).columns

    X_train = train[features]
    y_train = train[target]
    X_val = val[features]
    y_val = val[target]
    X_test = test[features]
    y_test = test[target]

    #XGBclassifier(Gradient Boost Classifier) 알고리즘 적용

    # from xgboost import XGBClassifier
    # from category_encoders import OrdinalEncoder
    # from sklearn.impute import SimpleImputer
    # from sklearn.ensemble import RandomForestClassifier
    # from sklearn.pipeline import make_pipeline

    # #0.697436 / 0.302564
    # ratio = 0.35
    # pipe = XGBClassifier(n_estimators=3                                #이거 나중에 300으로
    #                 , random_state=2
    #                 , n_jobs=-1
    #                 , max_depth=7
    #                 , learning_rate=0.2
    #                 ,scale_pos_weight=ratio
    #                 )

    # eval_set = [(X_train, y_train), 
    #             (X_val, y_val)]

    # pipe.fit(X_train, y_train, 
    #         eval_set=eval_set,
    #         eval_metric='error', # #(wrong cases)/#(all cases)
    #         early_stopping_rounds=5                                         #이거 나중에 50으로 수정
    #         ) # 50 rounds 동안 스코어의 개선이 없으면 멈춤


    # #검증 정확도 확인
    # from sklearn.metrics import accuracy_score
    # #pkl로 모델 저장

    # joblib.dump(pipe, 'XGboost_movie.pkl')
    # # load model
    # pipe = joblib.load('XGboost_movie.pkl')
    # X_test.to_csv("X_test.csv", mode='w')

    return X_test


def recommendation_update(X_test):
#시나리오 분석
    pipe = joblib.load('XGboost_movie.pkl')
    #X_test = pd.read_csv('X_test.csv')
    #X_test = X_test.set_index("Unnamed: 0", inplace = True)
    
    y_pred_proba = pipe.predict_proba(X_test)

    df_movies = pd.read_csv('IMDb movies.csv')
    movie_names = df_movies[['imdb_title_id','original_title']].loc[X_test.index]

    temp = pd.Series(y_pred_proba[:,1],list(movie_names['imdb_title_id']))
    temp_sorted = temp.sort_values(ascending=False)

    for i in range(5):
        new_Movies_Recommended = Movies_Recommended(imdb_id = temp_sorted.index[i], Prob_score = temp_sorted[i])
        new_Movies = Movies(imdb_id = temp_sorted.index[i],
                            title = df_movies[(df_movies['imdb_title_id'] == temp_sorted.index[i])]['title'].iloc[0],
                            year = df_movies[(df_movies['imdb_title_id'] == temp_sorted.index[i])]['year'].iloc[0],
                            genre = df_movies[(df_movies['imdb_title_id'] == temp_sorted.index[i])]['genre'].iloc[0])
        db.session.add(new_Movies_Recommended)
        db.session.add(new_Movies)
        db.session.commit()
