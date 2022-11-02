from flask import Flask, send_from_directory, request, jsonify
from flask_admin import Admin
from flask_cors import CORS
import rec_model

app = Flask(__name__)
CORS(app)

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

admin = Admin(app, name='microblog', template_mode='bootstrap3')


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


@app.route('/movie', methods=['GET'])
def recommend_movies():
    res = rec_model.results(request.args.get('title'))
    return jsonify(res)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
