from flask import Flask, render_template, redirect, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import config.config
import config.paths
import datetime

app = Flask(__name__)

app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = config.config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Actor (db.Model):
    __tablename__ = "actors"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), unique = True)
    born = db.Column(db.Integer)    # yr
    dead = db.Column(db.Integer)    # yr
    created = db.Column(db.DateTime())
    movies = db.relationship("Role")

class Movie (db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), unique = True)
    year = db.Column(db.Integer)
    created = db.Column(db.DateTime())
    actors = db.relationship("Role")

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    actor_id = db.Column(db.Integer(), db.ForeignKey('actors.id'), primary_key = True, autoincrement = False)
    movie_id = db.Column(db.Integer(), db.ForeignKey('movies.id'), primary_key = True, autoincrement = False)
    notes = db.Column(db.String(80))    # optional.
    actor = db.relationship(Actor, backref = "movies_backref")
    movie = db.relationship(Movie, backref = "actors_backref")

@app.route("/")
def home_page_handler():
    return render_template("index.html")

@app.route("/manual")
@app.route("/manual/")
def manual_page_handler():
    actors = Actor.query.all()
    movies = Movie.query.all()
    actors = sorted(actors, key = lambda x : x.name)    # hmm maybe needa do fname/lname...
    movies = sorted(movies, key = lambda x : (x.name, x.year))
    return render_template("manual.html", actors = actors, movies = movies)

@app.route("/assets/<path:file_path>")
def get_asset_file(file_path):
    path = config.paths.WORKING_DIR + "assets/"
    return send_from_directory(path, file_path, as_attachment = True)

@app.route("/manual/forms/add-actor/", methods = ["POST"])
def add_actor_form_handle():
    name = request.form["name"]
    born = request.form["born"]
    dead = request.form["dead"]
    actor = Actor()
    actor.name = name
    if born:
        actor.born = int(born)
    if dead:
        actor.dead = int(dead)
    actor.created = datetime.datetime.now()
    db.session.add(actor)
    db.session.commit()
    return redirect("/manual/actors/{}/".format(actor.id))

@app.route("/manual/forms/add-movie/", methods = ["POST"])
def add_movie_form_handle():
    name = request.form["name"]
    year = request.form["year"]
    movie = Movie()
    movie.name = name
    if year:
        movie.year = int(year)
    movie.created = datetime.datetime.now()
    db.session.add(movie)
    db.session.commit()
    return redirect("/manual/movies/{}/".format(movie.id))

@app.route("/manual/forms/add-role/", methods = ["POST"])
def add_role_form_handle():
    ac = request.form["actor"]
    mo = request.form["movie"]
    no = request.form["notes"]
    actor = Actor.query.filter(Actor.name == ac).first()
    movie = Movie.query.filter(Movie.name == mo).first()
    if not actor:
        return "Invalid actor."
    if not movie:
        return "Invalid movie."
    already = Role.query.filter((Role.actor_id == actor.id) & (Role.movie_id == movie.id)).first()
    if already:
        return "Role already exists."
    role = Role(notes = no)
    role.actor_id = actor.id
    role.movie_id = movie.id
    db.session.add(role)
    db.session.commit()
    return redirect("/manual/")

@app.route("/manual/actors/<int:aid>")
@app.route("/manual/actors/<int:aid>/")
def manual_actor_pg_handle(aid):
    actor = Actor.query.get(aid)
    if actor == None:
        return "Actor not found!"
    movies = Movie.query.all()
    movie_dict = {}
    for movie in movies:
        movie_dict[movie.id] = movie
    roles = Role.query.filter(Role.actor_id == actor.id).all()
    role_list = []
    for role in roles:
        role_list.append([movie_dict[role.movie_id], role.notes])
    role_list = sorted(role_list, key = lambda x : (x[0].name, x[0].year))
    return render_template("actor.html", actor = actor, movies = role_list)

@app.route("/manual/movies/<int:mid>")
@app.route("/manual/movies/<int:mid>/")
def manual_movie_pg_handle(mid):
    movie = Movie.query.get(mid)
    if movie == None:
        return "Movie not found!"
    actors = Actor.query.all()
    actor_dict = {}
    for actor in actors:
        actor_dict[actor.id] = actor
    roles = Role.query.filter(Role.movie_id == movie.id).all()
    role_list = []
    for role in roles:
        role_list.append([actor_dict[role.actor_id], role.notes])
    role_list = sorted(role_list, key = lambda x : (x[0].name))
    return render_template("movie.html", movie = movie, actors = role_list)

@app.route("/manual/web")
@app.route("/manual/web/")
def web_graph_pg_handle():
    actors = Actor.query.all()
    movies = Movie.query.all()
    roles = Role.query.all()
    actors = sorted(actors, key = lambda x : x.name)
    actor_dict = {}
    for actor in actors:
        actor_dict[actor.id] = actor
    movie_dict = {}
    for movie in movies:
        movie_dict[movie.id] = movie
    connections = {}
    movie_clusters = {}
    for role in roles:
        if role.movie_id not in movie_clusters:
            movie_clusters[role.movie_id] = [role.actor_id]
        else:
            movie_clusters[role.movie_id].append(role.actor_id)
    for m_id in movie_clusters:
        cluster = movie_clusters[m_id]
        for i in range(len(cluster) - 1):
            for j in range(i + 1, len(cluster)):
                #tup = (cluster[i], cluster[j])
                ke = str(cluster[i]) + "," + str(cluster[j])
                if ke not in connections:
                    connections[ke] = [m_id]
                else:
                    connections[ke].append(m_id)
    return render_template("web.html", actors = actors, connections = connections, movie_dict = movie_dict)



