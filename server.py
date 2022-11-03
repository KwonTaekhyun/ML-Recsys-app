from flask import Flask, send_from_directory, request, jsonify
from flask_admin import Admin
from flask_cors import CORS
import recsys

app = Flask(__name__)
CORS(app)

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

admin = Admin(app, name='microblog', template_mode='bootstrap3')

predictions = list(recsys.model.predict(
    input_fn=recsys.tf_utils.pandas_input_fn(df=recsys.test)))
prediction_df = recsys.test.drop(recsys.RATING_COL, axis=1)
prediction_df[recsys.PREDICT_COL] = [p['predictions'][0]
                                     for p in predictions]


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

    if args['userid']:
        predict_movies = prediction_df[prediction_df['userID'] == int(args['userid'])].sort_values(
            by=['prediction'], ascending=False).iloc[0:10]['itemID'].apply(lambda x: recsys.movie_dict[x]['imdbID']).to_json(orient='records')
        return predict_movies
    else:
        return ''


if __name__ == "__main__":
    app.run(port=5000, debug=True)
