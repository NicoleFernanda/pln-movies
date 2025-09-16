from bs4 import BeautifulSoup
import pandas as pd
import requests
import string
#from nltk.stem import RSLPStemmer 
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def get_movies_info():
    df = pd.DataFrame(columns=[
        "Link","title", "year", "streamings", "synopsis_introduction", "synopsis_content",
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
            synopsis_content = tokens(synopsis_content)

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
                "Link": link,
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

    df.to_csv("movies_info.csv", index=False, encoding="utf-8", sep=";")

def tokens(sinopse): 
    # Verificar se a sinopse não é None ou vazia
    if not sinopse or pd.isna(sinopse):
        return ""
    
    #stemmer = RSLPStemmer()
    lemmatizer = WordNetLemmatizer()
    
    # Converter para minúsculas
    sinopse = sinopse.lower()
    
    # Remover pontuações
    sinopse = sinopse.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenizar (dividir em palavras)
    palavras = word_tokenize(sinopse, language='portuguese')
    
    # Carregar stopwords em português
    stop_words = set(stopwords.words('portuguese'))
    
    # Remover stopwords
    palavras_filtradas = [palavra for palavra in palavras if palavra not in stop_words]

    #palavras_stemmed = [stemmer.stem(palavra) for palavra in palavras_filtradas]

    # Lemmatizar
    lemmas = [lemmatizer.lemmatize(palavra) for palavra in palavras_filtradas]
    
    palavras_finais = [
        palavra for palavra in lemmas 
        if len(palavra) > 2 and palavra.isalpha()  # Só letras
    ]
    
    return palavras_finais 

get_movies_info()