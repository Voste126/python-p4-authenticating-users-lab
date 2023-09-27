from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse
from models import db, Article  # Import your Article model here

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json_compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# Define your User model and users list here
users = [{'id': 1, 'username': 'user1'}, {'id': 2, 'username': 'user2'}]

class ClearSession(Resource):
    def delete(self):
        session['page_views'] = 0
        session['user_id'] = None
        return {}, 204

class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):
    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:
            article = Article.query.filter(Article.id == id).first()
            if article:
                article_json = jsonify(article.to_dict())
                return make_response(article_json, 200)
            else:
                return {'message': 'Article not found'}, 404
        else:
            return {'message': 'Maximum pageview limit reached'}, 401

class LoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        data = parser.parse_args()
        username = data['username']

        # Find the user by username (assuming usernames are unique)
        user = next((user for user in users if user['username'] == username), None)

        if user:
            # Set the 'user_id' in the session
            session['user_id'] = user['id']
            return user, 200
        else:
            return {'message': 'User not found'}, 404

class LogoutResource(Resource):
    def delete(self):
        # Remove the 'user_id' from the session
        session.pop('user_id', None)
        return '', 204

class CheckSessionResource(Resource):
    def get(self):
        # Retrieve the 'user_id' from the session
        user_id = session.get('user_id')

        if user_id is not None:
            # Find the user by 'user_id'
            user = next((user for user in users if user['id'] == user_id), None)

            if user:
                return user, 200
            else:
                return {'message': 'User not found'}, 404
        else:
            return '', 401

api.add_resource(LoginResource, '/login')
api.add_resource(LogoutResource, '/logout')
api.add_resource(CheckSessionResource, '/check_session')

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)

