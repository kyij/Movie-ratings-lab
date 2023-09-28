"""Server for movie ratings app."""

from flask import (Flask, render_template, request, flash, session, redirect)

from model import connect_to_db, db

import crud

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def homepage():
    """View homepage."""
    return render_template('homepage.html')

@app.route('/movies')
def all_movies():
    """View all movies."""

    movies = crud.get_movies()

    return render_template("all_movies.html", movies=movies)

@app.route("/movies/<movie_id>")
def show_movie(movie_id):
    """Show details on a particular movie."""

    movie= crud.get_movie_by_id(movie_id)

    return render_template("movie_details.html", movie=movie)

@app.route('/users')
def display_users():
    """Show all users"""
    users = crud.get_users()

    return render_template("all_users.html", users=users)

@app.route('/users', methods=["POST"])
def register_user():
    """Create a new user"""
    email = request.form.get("email")
    password = request.form.get("password")

    user = crud.get_user_by_email(email)
    if user:
        flash("Cannot create an account with that email. Try again.")
    else:
        user = crud.create_user(email, password)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.")

    return redirect("/")

@app.route('/login', methods=["POST"])
def login_user():
    """Log user in"""
    email = request.form.get("email")
    password = request.form.get("password")

    user = crud.get_user_by_email(email)
    if not user or user.password != password:
        flash("This email or password you entered is incorrect.")
    else:
        session["user_email"] = user.email
        flash(f"Welcome back {user.email}!")
    
    return redirect('/')

@app.route("/movies/<movie_id>/ratings", methods= ["POST"])
def create_rating(movie_id):
    """Create a rating for the movie"""
    logged_email = session.get("user_email")
    # if request.form.get('rating') is ""
    rating_score = request.form.get("rating")

    if logged_email is None:
        flash("Must be a logged in user to access this service")
    elif not rating_score:
        flash("Please select a score.")
    else:
        user = crud.get_user_by_email(logged_email)
        movie = crud.get_movie_by_id(movie_id)

        rating = crud.create_rating(user, movie, int(rating_score))
        db.session.add(rating)
        db.session.commit()

        flash(f"You rated this movie {rating_score} out of 5")

    return redirect(f"/movies/{movie_id}")


@app.route('/users/<user_id>')
def show_user(user_id):

    users = crud.get_users_profile(user_id)

    return render_template("users_profile.html", user=users)


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)