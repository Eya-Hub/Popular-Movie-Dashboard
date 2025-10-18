import requests
from bs4 import BeautifulSoup
import csv

# IMDb Top 250 URL
url = "https://www.imdb.com/chart/top/"
headers = {
    "User-Agent": "Mozilla/5.0"
}

# Send GET request
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Locate the movie entries
movies = soup.select("li.ipc-metadata-list-summary-item")

# Prepare CSV file
with open("top_10_movies.csv", mode="w", newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Rank", "Title", "Rating"])  # Header

    # Extract and write top 10 movies
    for i, movie in enumerate(movies[:10], start=1):
        title = movie.select_one("h3.ipc-title__text").text.strip()
        rating_tag = movie.select_one("span.ipc-rating-star")
        rating = rating_tag.text.strip() if rating_tag else "N/A"
        writer.writerow([i, title, rating])

print("✅ Top 10 movies saved to 'top_10_movies.csv'")
