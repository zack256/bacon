from flask import Flask, render_template, redirect, request, send_from_directory, jsonify
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
import start_db
import manual_site as manual

app = start_db.app; db = start_db.db

class AutoActor (db.Model):
    __tablename__ = "a_actors"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120))
    born = db.Column(db.Integer)
    died = db.Column(db.Integer)
    note = db.Column(db.String(1024))
    is_manual = db.Column(db.Boolean)
    movies = db.relationship("AutoRole")

    def format_name(self):
        if self.born:
            if self.died:
                return self.name + " (" + str(self.born) + "-" + str(self.died) + ")"
            return self.name + " (b." + str(self.born) + ")"
        if self.died:
            return self.name + " (d." + str(self.died) + ")"
        return self.name

class AutoMovie (db.Model):
    __tablename__ = "a_movies"
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    year = db.Column(db.Integer)
    note = db.Column(db.String(1024))
    is_manual = db.Column(db.Boolean)
    actors = db.relationship("AutoRole")

    def format_title(self):
        if self.year:
            return self.title + " (" + str(self.year) + ")"
        return self.title

class AutoRole (db.Model):
    __tablename__ = "a_roles"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    actor_id = db.Column(db.Integer(), db.ForeignKey('a_actors.id'), primary_key = True, autoincrement = False)
    movie_id = db.Column(db.Integer(), db.ForeignKey('a_movies.id'), primary_key = True, autoincrement = False)
    actor = db.relationship(AutoActor, backref = "a_movies_backref")
    movie = db.relationship(AutoMovie, backref = "a_actors_backref")

@app.route("/")
def home_page_handler():
    #return render_template("index.html")
    return redirect("/db/")

@app.route("/assets/<path:file_path>")
def get_asset_file(file_path):
    path = config.paths.WORKING_DIR + "assets/"
    return send_from_directory(path, file_path, as_attachment = True)

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

@app.route("/db/forms/add-actor/", methods = ["POST"])
def db_add_actor_form_handle():
    name = request.form["name"]
    born = request.form["born"]
    died = request.form["died"]
    note = request.form["note"]
    actor = AutoActor()
    if name == "":
        return "Name can't be blank!"
    actor.name = name
    if born:
        actor.born = int(born)
    if died:
        actor.died = int(died)
    actor.note = note
    actor.is_manual = True
    db.session.add(actor)
    db.session.commit()
    return redirect("/db/actors/{}/".format(actor.id))

@app.route("/db/forms/add-movie/", methods = ["POST"])
def db_add_movie_form_handle():
    title = request.form["title"]
    year = request.form["year"]
    note = request.form["note"]
    movie = AutoMovie()
    if title == "":
        return "Title can't be blank!"
    movie.title = title
    if year:
        movie.year = int(year)
    movie.note = note
    movie.is_manual = True
    db.session.add(movie)
    db.session.commit()
    return redirect("/db/movies/{}/".format(movie.id))

def bridge_helper(l, home_dict, away_dict):
    c = l.pop(0)
    if c > 0:   # Actor
        focus = AutoActor.query.get(c)
        for role in focus.movies:
            idx = -role.movie_id
            if idx in home_dict:
                continue
            l.append(idx)
            home_dict[idx] = [home_dict[c][0] + 1, c]
            if idx in away_dict:
                return idx
    else:   # Movie
        focus = AutoMovie.query.get(-c)
        for role in focus.actors:
            idx = role.actor_id
            if idx in home_dict:
                continue
            l.append(idx)
            home_dict[idx] = [home_dict[c][0] + 1, c]
            if idx in away_dict:
                return idx
    return None

def bridge_bfs(a1, a2):
    if a1 == a2:
        return [a1]
    d1 = {a1 : [0, None]}; d2 = {a2 : [0, None]}; l1 = [a1]; l2 = [a2]
    while True:
        if len(l1) == 0 or len(l2) == 0:
            return False
        match = bridge_helper(l1, d1, d2)
        if match:
            break
        match = bridge_helper(l2, d2, d1)
        if match:
            break
    path = []; cu = match
    while cu != None:
        if cu > 0:
            path.append(cu)
        else:
            path.append(cu)
        cu = d1[cu][1]
    path2 = []; cu = d2[match][1]
    while cu != None:
        if cu > 0:
            path2.append(cu)
        else:
            path2.append(cu)
        cu = d2[cu][1]
    return path[::-1] + path2

@app.route("/db/bacon")
@app.route("/db/bacon/")
def db_bacon_page():
    a1_id_str = request.args.get("a1", "", str)
    a2_id_str = request.args.get("a2", "", str)
    case = 0    # case 0: no actors specified.
    path_dict = {}; path_list = []
    if a1_id_str == a2_id_str == "":    # both empties, probably a page reload.
        pass
    else:
        try:
            a_id_1 = int(a1_id_str); a_id_2 = int(a2_id_str)
        except:
            case = 1    # case 1 : invalid actor(s).
        if case == 1:
            pass
        else:
            a1 = AutoActor.query.get(a_id_1)
            a2 = AutoActor.query.get(a_id_2)
            if a1 == None or a2 == None:
                case = 1
            elif a1 == a2:
                case = 2    # case 2 : same actors.
                path_list = [AutoActor.query.get(a_id_1)]   # the actor is sent for jinja to display.
            else:
                path_list = bridge_bfs(a_id_1, a_id_2)
                if path_list:
                    case = 3    # case 3 : successful path found.
                    for path_node in path_list:
                        if path_node > 0:   # actor
                            node = AutoActor.query.get(path_node)
                            path_dict[path_node] = node
                        else:   # movie
                            node = AutoMovie.query.get(-path_node)
                            path_dict[path_node] = node
                else:
                    case = 4    # case 4 : no connection found- there are seperate groups of actors in the database.
                    path_list = [a1, a2]
    return render_template("db/bacon.html", case = case, path_dict = path_dict, path_list = path_list)

@app.route("/db/ajax/get-actor/")
def ajax_get_actor():
    a_id = request.args.get("a_id", 0, int)
    fail = False
    if a_id == 0:
        fail = True
    else:
        actor = AutoActor.query.get(a_id)
        if actor:
            res = actor.name
        else:
            fail = True
    if fail:
        res = "No actor was found with that ID!"
    return jsonify(actor = res, a_id = a_id, success = not fail)









