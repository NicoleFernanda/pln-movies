from bs4 import BeautifulSoup
import pandas as pd
import requests


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def get_movies_info():
    df = pd.DataFrame(columns=[
        "title", "year", "streamings", "synopsis_introduction", "synopsis_content",
        "just_watch_rating", "rotten_tomatoes_rating", 
        "imdb_ratings", "genres", "movie_duration", "age_classification"
    ])

    with open('movies_links.csv', 'r') as file:
        for link in file:  # Pula o cabeçalho

            link = link.strip()

            response = requests.get(link, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # pega os nomes dos streamings
            streamings_tags = soup.find_all("img", class_="provider-icon wide icon")
            streamings_names = [img.get("alt") for img in streamings_tags]

            # pega a sinopse
            div_synopsis = soup.find("div", id="synopsis")
            synopsis_content = div_synopsis.find("p").get_text(strip=True)

            # pega as avaliações
            ratings_rotten_jw = soup.find_all("div", class_="jw-scoring-listing__rating--group jw-scoring-listing__rating--no-link")
            rating_just_watch = "NAOAVALIADO"
            rating_rotten_tomatoes = "NAOAVALIADO"
            rating_imdb = "NAOAVALIADO"

            if len(ratings_rotten_jw) > 1:
                rating_just_watch = ratings_rotten_jw[0].get_text(strip=True)
                rating_rotten_tomatoes = ratings_rotten_jw[1].get_text(strip=True)
            
            rating_imdb = soup.find("div", class_="jw-scoring-listing__rating--group jw-scoring-listing__rating--link")
            if rating_imdb:
                rating_imdb = rating_imdb.text.strip()
            
            # pega o titulo
            title = soup.find_all("h1")
            if title:
                title = title[0].get_text(strip=True)
            else:
                title = "VAZIO"

            # pega o ano
            year = soup.find("span", class_="release-year").get_text(strip=True)
    
            infos = soup.find_all("div", class_="poster-detail-infos__value")
            genres = infos[4].get_text(strip=True).split(',')
            genres = [genre.strip() for genre in genres]
            movie_duration = infos[6].get_text(strip=True)

            age_classification = 'L'
            
            if len(infos) >= 9:
                age_classification = infos[8].get_text(strip=True)            
            
            df = pd.concat([df, pd.DataFrame([{
                "title": title,
                "year": year,
                "streamings": streamings_names,
                "synopsis_content": synopsis_content,
                "just_watch_rating": rating_just_watch,
                "rotten_tomatoes_rating": rating_rotten_tomatoes,
                "imdb_ratings": rating_imdb,
                "genres": genres,
                "movie_duration": movie_duration,
                "age_classification": age_classification
            }])], ignore_index=True)

    df.to_csv("movies_info.csv", index=False, encoding="utf-8")

get_movies_info()