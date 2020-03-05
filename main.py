from flask import Flask, render_template, redirect, request, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func as sql_func
import config.config
import config.paths
import config.constants
import datetime
import csv
import random
import math
import start_db

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
    is_manual = db.Column(db.Boolean)
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
    if not actor.is_manual: # delete_mode is used to tell the user if the actor/movie can be deleted.
        delete_mode = 0     # 0 : can't be deleted as it came from the original import, and its better if those aren't deleted.
    elif movies != []:
        delete_mode = 1     # 1 : has movies attached, better to have the user confirm he wants to delete the actor by manually deleting each role.
    else:
        delete_mode = 2     # 2 : can delete.
    return render_template("actor.html", actor = actor, movies = movies, delete_mode = delete_mode)

@app.route("/db/movies/<int:mid>")
@app.route("/db/movies/<int:mid>/")
def db_movie_pg_handle(mid):
    movie = AutoMovie.query.get(mid)
    if movie == None:
        return "Movie not found!"
    actors = sorted([role.actor for role in movie.actors], key = lambda x : [x.name])
    if not movie.is_manual:
        delete_mode = 0
    elif actors != []:
        delete_mode = 1
    else:
        delete_mode = 2
    return render_template("movie.html", movie = movie, actors = actors, delete_mode = delete_mode)

@app.route("/db")
@app.route("/db/")
def db_home_pg_handle():
    rand_actors = AutoActor.query.order_by(sql_func.random()).limit(config.constants.DB_HOME_ACTORS_SHOWN).all()
    rand_movies = AutoMovie.query.order_by(sql_func.random()).limit(config.constants.DB_HOME_MOVIES_SHOWN).all()
    return render_template("main.html", actors = rand_actors, movies = rand_movies)

@app.route("/db/actors")
@app.route("/db/actors/")
def db_actors_pg_handle():
    query = request.args.get("query", "", str)
    page = request.args.get("page", 1, int)
    actor_query = AutoActor.query.filter(AutoActor.name.like(query + "%"))
    total_matches = actor_query.count()
    if total_matches == 0:
        return render_template("actors.html", total_matches = total_matches, query = query, actors = [])
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
    return render_template("actors.html", actors = actors, total_matches = total_matches, page = page, total_pages = total_pages, query = query)

@app.route("/db/movies")
@app.route("/db/movies/")
def db_movies_pg_handle():
    query = request.args.get("query", "", str)
    page = request.args.get("page", 1, int)
    movie_query = AutoMovie.query.filter(AutoMovie.title.like(query + "%"))
    total_matches = movie_query.count()
    if total_matches == 0:
        return render_template("movies.html", total_matches = total_matches, query = query, movies = [])
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
    return render_template("movies.html", movies = movies, total_matches = total_matches, page = page, total_pages = total_pages, query = query)

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

def edit_a_year(given, former):
    try:
        given = int(given)
        return given    # year is valid.
    except:
        if given == "":
            return None     # blanking the year.
        else:
            return former   # invalid year, reverting to what is already there.

@app.route("/db/forms/edit-actor/", methods = ["POST"])
def db_edit_actor_form_handle():
    a_id = request.form["a_id"]
    actor = AutoActor.query.get(int(a_id))
    if actor == None:
        return "Actor doesn't exist!"
    if actor.is_manual:
        name = request.form["name"]
        if name == "":
            return "Name can't be blank!"
        actor.name = name
    actor.born = edit_a_year(request.form["born"], actor.born)
    actor.died = edit_a_year(request.form["died"], actor.died)
    note = request.form["note"]
    actor.note = note
    db.session.commit()
    return redirect("/db/actors/{}/".format(actor.id))

@app.route("/db/forms/edit-movie/", methods = ["POST"])
def db_edit_movie_form_handle():
    m_id = request.form["m_id"]
    movie = AutoMovie.query.get(int(m_id))
    if movie == None:
        return "Movie doesn't exist!"
    if movie.is_manual:
        title = request.form["title"]
        if title == "":
            return "Title can't be blank!"
        movie.title = title
    movie.year = edit_a_year(request.form["year"], movie.year)
    note = request.form["note"]
    movie.note = note
    db.session.commit()
    return redirect("/db/movies/{}/".format(movie.id))

@app.route("/db/forms/delete-actor/", methods = ["POST"])
def db_delete_actor_form_handle():
    a_id = request.form["a_id"]
    actor = AutoActor.query.get(int(a_id))
    if actor == None:
        return "Actor doesn't exist!"
    if not actor.is_manual:
        return "Can't delete an Actor that was added to the database initially."
    if actor.movies != []:
        return "Can't delete an Actor that has movies!"
    db.session.delete(actor)
    db.session.commit()
    return redirect("/db/actors/")

@app.route("/db/forms/delete-movie/", methods = ["POST"])
def db_delete_movie_form_handle():
    m_id = request.form["m_id"]
    movie = AutoMovie.query.get(int(m_id))
    if movie == None:
        return "Movie doesn't exist!"
    if not movie.is_manual:
        return "Can't delete a Movie that was added to the database initially."
    if movie.actors != []:
        return "Can't delete a Movie that has actors!"
    db.session.delete(movie)
    db.session.commit()
    return redirect("/db/movies/")

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
    return render_template("bacon.html", case = case, path_dict = path_dict, path_list = path_list)

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

@app.route("/db/ajax/get-movie/")
def ajax_get_movie():
    m_id = request.args.get("m_id", 0, int)
    fail = False
    if m_id == 0:
        fail = True
    else:
        movie = AutoMovie.query.get(m_id)
        if movie:
            res = movie.title
        else:
            fail = True
    if fail:
        res = "No movie was found with that ID!"
    return jsonify(movie = res, m_id = m_id, success = not fail)

@app.route("/db/forms/add-role/", methods = ["POST"])
def db_add_role_form_handle():
    fail = False
    try:
        a_id = int(request.form["a_id"])
        m_id = int(request.form["m_id"])
    except:
        fail = True
    actor = AutoMovie.query.get(int(m_id))
    movie = AutoMovie.query.get(int(m_id))
    if actor == None or movie == None:
        fail = True
    if fail:
        return "Invalid ID(s)."
    if AutoRole.query.filter((AutoRole.actor_id == a_id) & (AutoRole.movie_id == m_id)).first():
        return "Role already exists!"
    coming_from = request.form["from"]
    role = AutoRole()
    role.actor_id = a_id
    role.movie_id = m_id
    role.is_manual = True
    db.session.add(role)
    db.session.commit()
    if coming_from == "actor":
        return redirect("/db/actors/{}/".format(a_id))
    return redirect("/db/movies/{}/".format(m_id))









