from flask import Flask, send_from_directory, request
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import recsys
import sqlite3
import time
import imp
import shutil
import os
import time

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/kwontaekhyun/Library/CloudStorage/OneDrive-postech.ac.kr/2022-가을학기/과제연구2/W&D_ML_RecSys/admin.db'
app.config['SECRET_KEY'] = 'qwer1234'

db = SQLAlchemy(app)

admin = Admin(app)


class Links(db.Model):
    movieId = db.Column(db.Integer)
    imdbId = db.Column(db.Integer)
    tmdbId = db.Column(db.Integer, primary_key=True)


class Movies(db.Model):
    movieId = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    genres = db.Column(db.Text)


class Ratings(db.Model):
    userId = db.Column(db.Integer)
    movieId = db.Column(db.Integer)
    rating = db.Column(db.Float)
    timestamp = db.Column(db.Text, primary_key=True)


class Tags(db.Model):
    userId = db.Column(db.Integer)
    movieId = db.Column(db.Integer)
    tag = db.Column(db.Text)
    timestamp = db.Column(db.Text, primary_key=True)


admin.add_view(ModelView(Links, db.session))
admin.add_view(ModelView(Movies, db.session))
admin.add_view(ModelView(Ratings, db.session))
admin.add_view(ModelView(Tags, db.session))


@app.route("/")
def base():
    return send_from_directory('client/public', 'index.html')


@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)


@app.route("/test")
def test():
    return "<p>Hello, this is Test page!</p>"


@app.route('/message')
def generate_random():
    args = request.args
    return "Hello " + args['name']


@app.route('/movie')
def recommend_movies():
    args = request.args
    userID = int(args['userid'])

    if userID:
        time.sleep(12)

        predictions = list(recsys.model.predict(
            input_fn=recsys.tf_utils.pandas_input_fn(
                df=recsys.ranking_pool[recsys.ranking_pool['userID'] == userID]))
        )
        prediction_df = recsys.ranking_pool[recsys.ranking_pool['userID'] == userID].copy(
        )
        prediction_df['prediction'] = [p['predictions'][0]for p in predictions]

        predict_movies = prediction_df.sort_values(
            by=['prediction'], ascending=False).iloc[0:10]['itemID'].apply(
                lambda x: recsys.movie_dict[x]['imdbID']
        ).to_json(orient='records')
        print(predict_movies)
        return predict_movies
    else:
        return ''


@app.route('/movies_by_genre')
def get_movies_by_genre():
    return recsys.new_rating_movies_by_genre


@app.route('/geres')
def get_genres():
    return recsys.new_rating_genres


@app.route('/new_user_id')
def get_new_user_id():
    print(recsys.new_rating_userId)
    return str(recsys.new_rating_userId)


@app.route('/ratings', methods=['POST'])
def add_ratings():
    new_rating_list = request.form.getlist('newRatings')
    newRatings = []

    for new_rating in new_rating_list:
        newRatings.append(eval(new_rating))

    con = sqlite3.connect("admin.db")
    cursor = con.cursor()

    for idx, newRating in enumerate(newRatings):
        print(recsys.new_rating_userId)
        print(int(newRating['movieId']))
        print(float(newRating['rating']))
        print(str(int(time.time())))

        cursor.execute("INSERT INTO Ratings VALUES (?, ?, ?, ?)",
                       (int(recsys.new_rating_userId), int(newRating['movieId']), float(newRating['rating']), str(int(time.time()) + idx)))

    con.commit()
    con.close()

    shutil.rmtree('./models')
    imp.reload(recsys)

    time.sleep(120)

    return 'sucess'


if __name__ == "__main__":
    app.run(port=4000, debug=False)
