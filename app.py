import os
from flask import (
    Flask, flash, render_template, 
    redirect, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_books")
def get_books():
    books = mongo.db.books.find()
    return render_template("books.html", books=books)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username exists in the database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if existing_user:
            flash("Oops! Looks like that username already exists")
            return redirect(url_for("register"))

        register = {
            "firstname": request.form.get("firstname"),
            "lastname": request.form.get("lastname"),
            "university": request.form.get("university"),
            "course": request.form.get("course"),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # new user goes into the session cookie
        session["user"] = request.form.get("username").lower()
        flash("Awesome! Registration complete!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username is in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure password is the same
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # incorrect password
                flash("Oops! Thats the wrong Username or Password!")
                return redirect(url_for("login"))

        else:
            # no username found
            flash("Oops! Thats the wrong Username or Password!")
            return redirect(url_for("login"))
    
    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    if session["user"].lower() == username.lower():
        user = mongo.db.users.find_one({"username": username})
        details = list(mongo.db.users.find({"username": username}))
        return render_template("profile.html", user=user, details=details)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    flash("See you soon!")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        is_pdf = "on" if request.form.get("is_pdf") else "off"
        book = {
            "topic_name": request.form.get("topic_name"),
            "sub_topic": request.form.get("sub_topic"),
            "book_name": request.form.get("book_name"),
            "book_author": request.form.get("book_author"),
            "book_description": request.form.get("book_description"),
            "book_rating": request.form.get("book_rating"),
            "is_pdf": is_pdf,
            "book_link": request.form.get("book_link"),
            "book_image": request.form.get("book_image"),
            "created_by": session["user"]
        }
        mongo.db.tasks.insert_one(book)
        flash("Book uploaded to UniBook!")
        return redirect(url_for("get_books"))

    topics = mongo.db.topics.find().sort("topic", 1)
    return render_template("add_book.html", topics=topics)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True) 
