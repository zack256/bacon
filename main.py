from flask import Flask, render_template, redirect, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func as sql_func
import config.config
import config.paths
import config.constants
import datetime
import work.shortest_path
import csv
import random
import math

app = Flask(__name__)

app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = config.config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

#---Testing DB (below)---
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
#---Testing DB (above)---

class AutoActor (db.Model):
    __tablename__ = "a_actors"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120))
    csv_id = db.Column(db.Integer, unique = True)
    movies = db.relationship("AutoRole")

class AutoMovie (db.Model):
    __tablename__ = "a_movies"
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    csv_id = db.Column(db.Integer, unique = True)
    actors = db.relationship("AutoRole")

class AutoRole (db.Model):
    __tablename__ = "a_roles"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    #actor_id = db.Column(db.Integer(), db.ForeignKey('a_actors.id'), primary_key = True, autoincrement = False)
    #movie_id = db.Column(db.Integer(), db.ForeignKey('a_movies.id'), primary_key = True, autoincrement = False)
    actor_id = db.Column(db.Integer(), db.ForeignKey('a_actors.csv_id'), primary_key = True, autoincrement = False)
    movie_id = db.Column(db.Integer(), db.ForeignKey('a_movies.csv_id'), primary_key = True, autoincrement = False)
    actor = db.relationship(AutoActor, backref = "a_movies_backref")
    movie = db.relationship(AutoMovie, backref = "a_actors_backref")

@app.route("/")
def home_page_handler():
    return render_template("index.html")

@app.route("/manual")
@app.route("/manual/")
def manual_page_handler():
    all_actors = Actor.query.all()
    all_movies = Movie.query.all()
    #actors = sorted(actors, key = lambda x : x.name)
    #movies = sorted(movies, key = lambda x : (x.name, x.year))
    actors = random.sample(all_actors, config.constants.MANUAL_HOME_ACTORS_SHOWN)
    movies = random.sample(all_movies, config.constants.MANUAL_HOME_MOVIES_SHOWN)
    return render_template("manual.html", actors = actors, movies = movies, all_actors = all_actors, all_movies = all_movies)

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

@app.route("/manual/actors")
@app.route("/manual/actors/")
def actors_page_handle():
    actors = sorted(Actor.query.all(), key = lambda x : x.name)
    return render_template("actors.html", actors = actors)

@app.route("/manual/movies")
@app.route("/manual/movies/")
def movies_page_handle():
    movies = sorted(Movie.query.all(), key = lambda x : x.name)
    return render_template("movies.html", movies = movies)

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

@app.route("/manual/bacon")
@app.route("/manual/bacon/")
def bacon_pg_handler():
    # only actors to start.
    id1 = request.args.get("a1", "", int)
    id2 = request.args.get("a2", "", int)
    if id1 == id2:
        return "Can't do the same actor!"
    edges = []
    roles = Role.query.all()
    actors = Actor.query.all()
    movies = Movie.query.all()
    for role in roles:
        edge_list = [role.actor_id, -role.movie_id, 1]
        edges.append(edge_list)
    shortest_path_results = work.shortest_path.shortest_path(edges = edges, source = id1, dest = id2)
    if type(shortest_path_results) == dict: # only the visited dict returned, thus there are 2+ seperate groups and there is no connection between the requested pair of actors.
        actor1 = Actor.query.get(id1)
        actor2 = Actor.query.get(id2)
        return render_template("bacon.html", success = False, actor1 = actor1, actor2 = actor2)
    else:   # connection found.
        dest_list, visited = shortest_path_results
        dist, prev = dest_list
        path_dict = {id2 : None}
        path_list = [id2]
        while True:
            path_dict[prev] = None
            path_list.append(prev)
            if prev == id1:
                break
            prev = visited[prev][1]
        for ac in actors:
            if ac.id in path_dict:
                path_dict[ac.id] = ac
        for mo in movies:
            if -mo.id in path_dict:
                path_dict[-mo.id] = mo
        path_list.reverse()
        return render_template("bacon.html", success = True, path_dict = path_dict, path_list = path_list)

@app.route("/db/actors/<int:aid>")
@app.route("/db/actors/<int:aid>/")
def db_actor_pg_handle(aid):
    actor = AutoActor.query.get(aid)
    if actor == None:
        return "Actor not found!"
    movies = sorted([role.movie for role in actor.movies], key = lambda x : [x.title])
    return render_template("db/actor.html", actor = actor, movies = movies)

@app.route("/db/movies/<int:mid>")
@app.route("/db/movies/<int:mid>/")
def db_movie_pg_handle(mid):
    movie = AutoMovie.query.get(mid)
    if movie == None:
        return "Movie not found!"
    app.logger.error([movie, movie.title, movie.id, movie.csv_id])
    actors = sorted([role.actor for role in movie.actors], key = lambda x : [x.name])
    return render_template("db/movie.html", movie = movie, actors = actors)

@app.route("/db")
@app.route("/db/")
def db_home_pg_handle():
    rand_actors = AutoActor.query.order_by(sql_func.random()).limit(config.constants.DB_HOME_ACTORS_SHOWN).all()
    rand_movies = AutoMovie.query.order_by(sql_func.random()).limit(config.constants.DB_HOME_MOVIES_SHOWN).all()
    return render_template("db/main.html", actors = rand_actors, movies = rand_movies)

@app.route("/db/actors")
@app.route("/db/actors/")
def db_actors_pg_handle():
    query = request.args.get("query", "", str)
    page = request.args.get("page", 1, int)
    actor_query = AutoActor.query.filter(AutoActor.name.like(query + "%"))
    total_matches = actor_query.count()
    if total_matches == 0:
        return render_template("db/actors.html", total_matches = total_matches, query = query, actors = [])
    shown = config.constants.DB_ACTORS_PG_SHOWN_PER_PAGE
    total_pages = math.ceil(total_matches / shown)
    if page < 1 or page % 1 != 0:
        page = 1
    elif page > total_pages:
        page = total_pages
    offset = (page - 1) * shown
    if query == "":
        actors = actor_query.order_by(AutoActor.id).offset(offset).limit(shown).all()  # if no query is specified, sorts by ID. if this isn't happening then the actors shown will be ones with weird names with quotes at the front, not ideal.
    else:
        actors = actor_query.order_by(AutoActor.name).offset(offset).limit(shown).all()
    return render_template("db/actors.html", actors = actors, total_matches = total_matches, page = page, total_pages = total_pages, query = query)

@app.route("/db/movies")
@app.route("/db/movies/")
def db_movies_pg_handle():
    query = request.args.get("query", "", str)
    page = request.args.get("page", 1, int)
    movie_query = AutoMovie.query.filter(AutoMovie.title.like(query + "%"))
    total_matches = movie_query.count()
    if total_matches == 0:
        return render_template("db/movies.html", total_matches = total_matches, query = query, movies = [])
    shown = config.constants.DB_MOVIES_PG_SHOWN_PER_PAGE
    total_pages = math.ceil(total_matches / shown)
    if page < 1 or page % 1 != 0:
        page = 1
    elif page > total_pages:
        page = total_pages
    offset = (page - 1) * shown
    if query == "":
        movies = movie_query.order_by(AutoMovie.id).offset(offset).limit(shown).all()
    else:
        movies = movie_query.order_by(AutoMovie.title).offset(offset).limit(shown).all()
    return render_template("db/movies.html", movies = movies, total_matches = total_matches, page = page, total_pages = total_pages, query = query)

def remove_leading_spaces_from_all_entries():
    # single use, hopefully.
    for actor in AutoActor.query.all():
        actor.name = actor.name.strip()
    db.session.commit()





