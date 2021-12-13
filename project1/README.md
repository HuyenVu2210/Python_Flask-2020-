# Project 1

DATABASE_URL = postgres://osyiubtjehypzp:f595845261c6c7b86a910f5752fda7e8e270ee8c7a1513288992e49690b9b2bf@ec2-23-20-129-146.compute-1.amazonaws.com:5432/danpnp8u4phiri

Database consists of 3 table:
- users: id, username, email, password
- books: id, isbn, title, author, year, average_score
- review: id, review_content, book_id, user_id, score

1. Register: user have to provide an username, email (unique), password and confirm that password. The password is hashed before saved into database.

2. Login: user login using email and password.

3. Home: user can search for book by isbn, title, author or publication date (can just type in part of these)

4. Search results: a table of search results, each row consist of book's isbn, title, author, publication date and a detail button which on click direct to the book detail page.

5. Book detail: Details of book: isbn, title, author, publication date, number of ratings and average rating on Goodbook. And also a rating scale with average score and a text box for user to send review about this book. User have to check the rating scale and input some review to submit review.

6. My reviews: User can view their reviews consist of the book title, review content and score.

7. /api/isbn: return a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score


