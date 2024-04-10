from flask import Flask, request , render_template
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from functools import wraps

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
api = Api(app)
bcrypt = Bcrypt(app)


ADMIN_PASSWORD_HASH = bcrypt.generate_password_hash("admin123").decode("utf-8")


# DATABASES
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def serialize(self):
        return {"id": self.id, "username": self.username, "role": self.role}

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    url = db.Column(db.String(100), nullable=False)

    def serialize(self):
        return {"id": self.id, "title": self.title, "url": self.url}


# MIDDLEWARE
def user_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = request.json.get("username")
        password = request.json.get("password")

        user = Users.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return {"error": "unautorized access"}, 401
        return f(*args, **kwargs)

    return decorated_function


def is_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = request.json.get("username")
        password = request.json.get("password")

        user = Users.query.filter_by(username=username).first()

        if not user or not user.check_password(password) or user.role != "admin":
            return {"error": "only admins can register users"}, 401

        return f(*args, **kwargs)

    return decorated_function


# CONTROLLERS
class MovieList(Resource):

    def get(self):
        movies = Movies.query.all()
        movies_data = [movie.serialize() for movie in movies]
        return {"movies": movies_data}

    @user_auth
    def post(self):
        data = request.json
        title = data.get("title")
        url = data.get("url")

        movie = Movies.query.filter_by(title=title).first()
        if movie:
            return {"error": "movie already added!"}, 400

        if not title or not url:
            return {"error": "title and url are required"}, 400

        new_movie = Movies(title=title, url=url)
        db.session.add(new_movie)
        db.session.commit()

        return {"msg": f"Movie {title} added!"}, 201


class Movie(Resource):

    def get(self, movie_id):
        movie = Movies.query.get(movie_id)
        if movie:
            return movie.serialize(), 200
        return {"error": "movie not found"}, 404

    @user_auth
    def put(self, movie_id):
        data = request.json
        title = data.get("title")
        url = data.get("url")

        movie = Movies.query.get(movie_id)

        if movie:
            movie.title = title
            movie.url = url
            db.session.commit()
            return movie.serialize(), 200
        return {"error": "movie not found"}, 404

    @user_auth
    def delete(self, movie_id):
        movie = Movies.query.get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
            return {"msg": f"movie deleted!"}, 200

        return {"error": "movie not found"}, 404


class User_list(Resource):
    @is_admin
    def get(self):
        data = request.json
        username = data.get("username")
        user = Users.query.filter_by(username=username).first()

        if user.role == "admin":
            users = [user.serialize() for user in Users.query.all()]
            return {"users": users}, 200

        return user.serialize(), 200

    @is_admin
    def post(self):
        data = request.json
        new_user = data.get("user")
        new_username = new_user.get("username")
        new_password = new_user.get("password")
        role = new_user.get("role", "user")

        if Users.query.filter_by(username=new_username).first():
            return {"error": "Username already exists"}, 400

        new_user = Users(username=new_username, role=role)
        new_user.set_password(new_password)
        db.session.add(new_user)
        db.session.commit()

        return {"msg": f"User {new_username} added!"}, 201


class User(Resource):
    @user_auth
    def get(self, user_id):
        user = Users.query.get(user_id)
        if user:
            return user.serialize(), 200
        return {"error": "user not found"}, 404
    
    @is_admin
    def delete(self, user_id):
        user = Users.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return {"msg": f"user deleted!"}, 200

        return {"error": "user not found"}, 404

    @is_admin
    def put(self, user_id):
        data = request.json.get("user")
        username = data.get("username")
        password = data.get("password")

        user = Users.query.get(user_id)

        if user:
            user.username = username
            user.set_password(password)
            db.session.commit()
            return user.serialize(), 200

        return {"error": "user not found"}, 404

class Auth(Resource):
    @user_auth
    def post(self):
        username = request.json.get("username")
        password = request.json.get("password")
        
        user = Users.query.filter_by(username=username).first().serialize()
        user["password"] = password
        
        return user, 200
    
    
# configs

api.add_resource(MovieList, "/movies")
api.add_resource(Movie, "/movies/<int:movie_id>")

api.add_resource(User_list, "/user")
api.add_resource(User, "/user/<int:user_id>")

api.add_resource(Auth, "/auth")

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/movie/<int:movie_id>")
def inner(movie_id):
    return render_template("inner.html")


with app.app_context():
    db.create_all()

app.run(debug=True)
