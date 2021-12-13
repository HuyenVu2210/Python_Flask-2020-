import requests

def call_api_rating(isbn):
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "NA7gLUDqQEzbPyRkWgzn1Q", "isbns": isbn})
	data = res.json()
	books = data["books"]
	rate = res = [ sub['average_rating'] for sub in books ]
	rating = rate[0]
	return rating

def call_api_number_of_rating(isbn):
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "NA7gLUDqQEzbPyRkWgzn1Q", "isbns": isbn})
	data = res.json()
	books = data["books"]
	ratings_count = res = [ sub['ratings_count'] for sub in books ]
	number_of_rating = ratings_count[0]
	return number_of_rating

if __name__ == "__main__":
    main()
