import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from datetime import datetime

# TMDb API key (updated with your key)
TMDB_API_KEY = "bb913df908fe6ec917afca94c992a8d22"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_MOVIE_URL = f"{TMDB_BASE_URL}/discover/movie"
TMDB_CREDITS_URL = f"{TMDB_BASE_URL}/movie/{{movie_id}}/credits"
TMDB_DETAILS_URL = f"{TMDB_BASE_URL}/movie/{{movie_id}}"

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def get_tmdb_movies(page):
    """Fetch movies from TMDb API with pagination."""
    params = {
        "api_key": TMDB_API_KEY,
        "sort_by": "revenue.desc",  # Sort by revenue to get popular movies
        "page": page,
        "primary_release_date.gte": "1970-01-01",  # Movies from 1970 onwards
        "include_adult": False
    }
    response = requests.get(TMDB_MOVIE_URL, params=params, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"Error fetching page {page}: {response.status_code}")
        return []

def get_movie_details(movie_id):
    """Fetch detailed movie data including budget, revenue, and cast."""
    details_url = TMDB_DETAILS_URL.format(movie_id=movie_id)
    credits_url = TMDB_CREDITS_URL.format(movie_id=movie_id)
    
    # Get movie details
    details_response = requests.get(details_url, params={"api_key": TMDB_API_KEY}, headers=HEADERS)
    credits_response = requests.get(credits_url, params={"api_key": TMDB_API_KEY}, headers=HEADERS)
    
    movie_data = {}
    if details_response.status_code == 200:
        details = details_response.json()
        movie_data.update({
            "MovieID": details.get("id"),
            "Title": details.get("title"),
            "Overview": details.get("overview"),
            "ReleaseYear": details.get("release_date", "")[:4] if details.get("release_date") else None,
            "Genres": ", ".join([g["name"] for g in details.get("genres", [])]),
            "Rating": details.get("vote_average"),
            "Budget": details.get("budget"),
            "Revenue": details.get("revenue"),
            "Language": details.get("original_language"),
            "Country": ", ".join([c["name"] for c in details.get("production_countries", [])]) if details.get("production_countries") else None
        })
        # Calculate profit
        budget = details.get("budget", 0)
        revenue = details.get("revenue", 0)
        movie_data["Profit"] = revenue - budget if budget and revenue else None
    
    if credits_response.status_code == 200:
        credits = credits_response.json()
        movie_data["Cast"] = ", ".join([c["name"] for c in credits.get("cast", [])[:5]])  # Top 5 cast members
    
    return movie_data

def scrape_movies(max_pages=5):
    """Scrape movies from TMDb and save to CSV."""
    movies_list = []
    
    for page in range(1, max_pages + 1):
        print(f"Scraping page {page}...")
        movies = get_tmdb_movies(page)
        for movie in movies:
            movie_id = movie.get("id")
            movie_data = get_movie_details(movie_id)
            if movie_data:
                movies_list.append(movie_data)
            time.sleep(random.uniform(0.2, 0.5))  # Respectful delay to avoid overwhelming the server
        time.sleep(1)  # Additional delay between pages
    
    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(movies_list)
    df = df[["MovieID", "Title", "Genres", "Rating", "ReleaseYear", "Overview", "Country", 
             "Language", "Cast", "Budget", "Revenue", "Profit"]]  # Reorder columns
    df.to_csv("movies_data.csv", index=False, encoding="utf-8")
    print(f"Saved {len(df)} movies to movies_data.csv")
    return df

def main():
    try:
        # Scrape 5 pages (approx. 100 movies, adjust as needed)
        scrape_movies(max_pages=5)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()