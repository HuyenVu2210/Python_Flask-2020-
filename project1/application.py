import os
import requests

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bcrypt import Bcrypt

from function import call_api_rating, call_api_number_of_rating

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"): 
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config['SECRET_KEY'] = '123' 
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

##########################################################

@app.route("/", methods=["GET", "POST"])
def register():
	if request.method == "POST":
		username = request.form.get("username")
		email = request.form.get("email")
		password = request.form.get("password")
		confirm_password = request.form.get("confirm_password")
		
		count = db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).rowcount

		if username == '' or email == '' or password == '' or confirm_password == '':
			return render_template("register_final.html", message="Please enter all the required fields")
		if password != '':
			pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
		if count == 1:
			return render_template("register_final.html", message="Email is already registered")
		if password != confirm_password:
			return render_template("register_final.html", message="Couldn't confirm password")

		db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)",
			            {"username": username, "email": email, "password": pw_hash})
		db.commit()
		session["email"] = email
		return redirect(url_for('home'))

	if "email" in session:
		email = session.get("email")
		return redirect(url_for('home'))

	return render_template("register_final.html")

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		email = request.form.get("email")
		password = request.form.get("password")
		user = db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).fetchone()

		if email == '' or password == '':
			return render_template("login_final.html", message="Please enter all the fields")
		if user == None:
			return render_template("login_final.html", message="Email does not exist")
		if bcrypt.check_password_hash(user.password, password) == False:
			return render_template("login_final.html", message="Password is incorrect")

		session["email"] = email
		return redirect(url_for('home'))

	if "email" in session:
		email = session.get("email")
		return redirect(url_for('home'))

	return render_template("login_final.html")

@app.route("/logout")
def logout():
	session.pop("email", None)
	return redirect(url_for('register'))

@app.route("/home", methods=["GET", "POST"])
def home():
	if "email" in session:
		email = session.get("email")
		user = db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).fetchone()
		return render_template("home_final.html", user=user)
	return redirect(url_for('register'))


@app.route("/searchresults", methods=["POST"])
def search_results():
	if "email" in session:
		if request.method == "POST":
			isbn = request.form.get("isbn")
			title = request.form.get("title")
			author = request.form.get("author")
			year = request.form.get("year")
			book1 = []
			book2 = []
			book3 = []
			book4 = []

#			if book1 == [] and book2 == [] and book3 == [] and book4 == []:
#				return render_template("home_final.html", message='Please enter at least one field')

			if isbn != '':
				book1 = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn", {"isbn": '%' + str(isbn) + '%'}).fetchall()
			
			if title != '':
				book2 = db.execute("SELECT * FROM books WHERE title LIKE :title", {"title": '%' + str(title) + '%'}).fetchall()
			
			if author != '':
				book3 = db.execute("SELECT * FROM books WHERE author LIKE :author", {"author": '%' + str(author) + '%'}).fetchall()
			
			if year != '':
				book4 = db.execute("SELECT * FROM books WHERE year LIKE :year", {"year": '%' + str(year) + '%'}).fetchall()

			return render_template("search_results_final.html", book1=book1, book2=book2, book3=book3, book4=book4)
		return render_template("home_final.html")
	return redirect(url_for('register'))

@app.route("/detail", methods=["GET", "POST"])
def detail():
	if "email" in session:
		if request.method == "POST":
			book_id = request.form.get("book_id")
			book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
#			reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall()
			review_count = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).rowcount
			users = db.execute("SELECT * FROM reviews, users WHERE reviews.user_id = users.id AND reviews.book_id = :book_id", {"book_id": book_id}).fetchall()

			rating = call_api_rating(book.isbn)
			number_of_rating = call_api_number_of_rating(book.isbn)

			session["book_id"] = book_id

			if review_count == 0:
				return render_template("book_detail_final.html", book=book, rating=rating, number_of_rating=number_of_rating, message1="There is no review for this book")

			return render_template("book_detail_final.html", book=book, rating=rating, number_of_rating=number_of_rating, users=users)

		return redirect(url_for('home'))
	return redirect(url_for('register'))

@app.route("/PostReview", methods=["GET","POST"])
def review():
	if "email" in session:
		if request.method == "POST":
			if "book_id" in session:
				book_id = session.get("book_id")
				email = session.get("email")

				user = db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).fetchone()
				book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
				reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall()
				user_id = user.id
				count = db.execute("SELECT * FROM reviews WHERE book_id = :book_id AND user_id = :user_id", {"book_id": book_id, "user_id": user_id}).rowcount
				users = db.execute("SELECT * FROM reviews, users WHERE reviews.user_id = users.id AND reviews.book_id = :book_id", {"book_id": book_id}).fetchall()

				rating = call_api_rating(book.isbn)
				number_of_rating = call_api_number_of_rating(book.isbn)
				new_review = request.form.get("new_review")
				score = request.form.get("score")

				if count == 1:
					return render_template("book_detail_final.html", book=book, rating=rating, number_of_rating=number_of_rating, reviews=reviews, users=users, message="You have already posted review for this book")

				if new_review == '':
					return render_template("book_detail_final.html", book=book, rating=rating, number_of_rating=number_of_rating, reviews=reviews, users=users, message="Please write some review")

				if score == None:
					return render_template("book_detail_final.html", book=book, rating=rating, number_of_rating=number_of_rating, reviews=reviews, users=users, message="Please rate this book")
				else:
					score = int(request.form.get("score"))
					average_score = int(book.average_score)

					if average_score == 0:
						new_average_score = book.average_score + score
						n_a_s = round(new_average_score, 2)
					else:
						new_average_score = (book.average_score + score)/2
						n_a_s = round(new_average_score, 2)

				db.execute("INSERT INTO reviews (review_content, user_id, book_id, score) VALUES (:review_content, :user_id, :book_id, :score)",
				        {"review_content": new_review, "user_id": user_id, "book_id": book_id, "score": score})
				db.execute("UPDATE books SET average_score = :average_score WHERE id = :book_id",
				        {"average_score": n_a_s, "book_id": book_id})
				db.commit()
				session["book_id"] = book_id
     
				return render_template("book_detail_final.html", book=book, rating=rating, number_of_rating=number_of_rating, new_review=new_review, reviews=reviews, users=users, n_a_s=n_a_s)

		return redirect(url_for('home'))
	return redirect(url_for('register'))	

@app.route("/myreviews")
def my_reviews():
	if "email" in session:
		email = session.get("email")
		user = db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).fetchone()
		user_id = user.id
#		reviews = db.execute("SELECT * FROM reviews WHERE user_id = :user_id", {"user_id": user_id}).fetchall()
		books = db.execute("SELECT * FROM reviews, books WHERE reviews.book_id = books.id AND reviews.user_id = :user_id", {"user_id": user_id}).fetchall()
		return render_template("my_reviews.html", books=books)
	redirect(url_for('register'))

@app.route("/api/<string:isbn>")
def book_api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    book_id = book.id
    average_score = str(book.average_score)
    review_count = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).rowcount

    if book is None:
        return jsonify({"error": "Invalid isbn"}), 422

    return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": review_count,
           	"average_score": average_score,
        })

