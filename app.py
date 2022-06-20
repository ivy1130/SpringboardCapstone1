import os
import requests

from auth import API_KEY
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from random import randrange

from forms import UserAddForm, LoginForm, EditUserForm
from models import db, connect_db, User, Favorite

CURR_USER_KEY = "curr_user"
BASE_URL = "https://api.thecatapi.com/v1"


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get(('DATABASE_URL').replace("postgres://", "postgresql://", 1), 'postgresql:///cat_finder'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

##############################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup."""

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)


@app.route('/logout', methods=["POST"])
def logout():
    """Handle logout of user."""

    do_logout()
    flash("You have successfully been logged out!", 'success')
    return redirect('/login')


##############################################################################
# Homepage and error page

@app.route('/')
def index():
    """Show home page of all cat breeds, allow user to search specific breed, allow user to filter by breed characteristics."""
    res = requests.get(f'{BASE_URL}/breeds', headers=API_KEY)
    data = res.json()
    return render_template('index.html', breeds=data)


@app.route('/oops')
def oops():
    """Display sorry page."""

    return render_template('sorry.html')


##############################################################################
# Cat breed routes

@app.route('/cats/<breed_id>')
def breed_info(breed_id):
    """Show information of a specific breed.
    
    Redirect to an error page if it is not a valid breed.
    """
    res = requests.get(f'{BASE_URL}/breeds', headers=API_KEY)
    data = res.json()
    # The API has a get request for finding a breed by its name, but often times, it returns empty JSON, so I had to do this roundabout way of requesting all the breeds > finding the index of the dict matching the cat breed's id > pulling that dict out of the full list

    if not any(d['id'] == breed_id for d in data):
        return redirect('/oops')

    breed_idx = [i for i, d in enumerate(data) if breed_id in d.values()][0]
    breed = data[breed_idx]

    img_res = requests.get(f'{BASE_URL}/images/search', params={"breed_ids":breed_id, "limit":5}, headers=API_KEY)
    img_data = img_res.json()

    if g.user:
        favs = (fav.breed_name for fav in g.user.favorites)
    else:
        favs = ()

    return render_template('cat_info.html', breed=breed, imgs=img_data, favs=favs, user=g.user)


@app.route('/api/togglefav', methods=["POST"])
def toggle_fav():
    """Add breed to favorites. If the breed is already in favorites, remove it."""

    breed_name = request.json["breed_name"]

    if g.user:
        favs = (fav.breed_name for fav in g.user.favorites)
        if breed_name in favs:
            fav = Favorite.query.get_or_404((g.user.id, f'{breed_name}'))
            db.session.delete(fav)
            db.session.commit()

            return jsonify(message=f"deleted ({g.user.id}, {breed_name}) from favorites")
        else:
            new_fav = Favorite(user_id=g.user.id, breed_name=breed_name)
            db.session.add(new_fav)
            db.session.commit()
            response_json = jsonify(fav=new_fav.serialize())

            return (response_json, 201)



##############################################################################
# Random Cat routes

@app.route('/random')
def show_random_cat():
    """Redirect to a random cat."""

    res = requests.get(f'{BASE_URL}/breeds', headers=API_KEY)
    data = res.json()

    breed_idx = randrange(len(data))
    breed_id = data[breed_idx]['id']

    return redirect(f'/cats/{breed_id}')


##############################################################################
# User routes

@app.route('/users/<int:user_id>')
def show_user_profile(user_id):
    """Show profile of a specific user and their favorited breeds."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    fav_breed_names = [fav.breed_name for fav in user.favorites]
    fav_breeds_info = []

    res = requests.get(f'{BASE_URL}/breeds', headers=API_KEY)
    data = res.json()
    for breed_name in fav_breed_names:
        breed_idx = [i for i, d in enumerate(data) if breed_name in d.values()][0]
        breed_info = data[breed_idx]
        fav_breeds_info.append(breed_info)

    return render_template('user_profile.html', user=user, fav_breeds=fav_breeds_info)


@app.route('/users/<int:user_id>/edit', methods=["GET", "POST"])
def edit_user_profile(user_id):
    """Handle update of user details and update database."""

    if not g.user or user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = EditUserForm(obj=g.user)

    if form.validate_on_submit():
        password = form.password.data

        if g.user.authenticate(g.user.username, password):
            g.user.username = form.username.data
            g.user.email = form.email.data
            g.user.image_url = form.image_url.data or User.image_url.default.arg,

            db.session.commit()

            return redirect(f"/users/{g.user.id}")
        
        flash("Password incorrect! Your details have not been changed.", "danger")
        return redirect("/")
    
    return render_template('edit_user.html', form=form, user_id=g.user.id)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req