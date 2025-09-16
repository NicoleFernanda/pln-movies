from bs4 import BeautifulSoup
import pandas as pd
import requests
import string
import nltk
from nltk.stem import RSLPStemmer 
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


# precisa rodar apenas uma vez, para baixar as dependências
# depois da primeira vez, pode comentar.
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('rslp')


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def get_movies_info():
    """
    Pega informações dos filmes listados no arquivo movies_links, dentro da pasta data.

    """
    df = pd.DataFrame(columns=[
        "link","title", "year", "streamings", "synopsis_content", "synopsis_lemming",
        "synopsis_stemming", "just_watch_rating", "rotten_tomatoes_rating", 
        "imdb_ratings", "genres", "movie_duration", "age_classification"
    ])

    with open('data/movies_links.csv', 'r') as file:
        # percorre os links dentro do arquivo
        for link in file:

            link = link.strip()

            # acessa os links
            response = requests.get(link, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # pega os nomes dos streamings
            streamings_tags = soup.find_all("img", class_="provider-icon wide icon")
            streamings_names = [img.get("alt") for img in streamings_tags]

            # pega a sinopse
            div_synopsis = soup.find("div", id="synopsis")
            synopsis_content = div_synopsis.find("p").get_text(strip=True)

            # filtra as palavras e, a partir dela, faz o stemming e lemming
            clean_words = clean_synopis(synopsis_content)
            synopsis_lemming = lemma(clean_words)
            synopsis_stemming = stemming(clean_words)

            # pega as avaliações
            # caso não existam avaliações, deixa como não avaliado
            ratings_rotten_jw = soup.find_all("div", class_="jw-scoring-listing__rating--group jw-scoring-listing__rating--no-link")
            rating_just_watch = "NAOAVALIADO"
            rating_rotten_tomatoes = "NAOAVALIADO"
            rating_imdb = "NAOAVALIADO"

            # caso existam valores, dai salva na variavel
            if len(ratings_rotten_jw) > 1:
                rating_just_watch = ratings_rotten_jw[0].get_text(strip=True)
                rating_rotten_tomatoes = ratings_rotten_jw[1].get_text(strip=True)
            
            # mesma coisa para o rating do imdb, caso exista, é salvo na variável
            rating_imdb = soup.find("div", class_="jw-scoring-listing__rating--group jw-scoring-listing__rating--link")
            if rating_imdb:
                rating_imdb = rating_imdb.text.strip()
            
            # pega o titulo, caso não encontre, fica como vazio
            title = soup.find_all("h1")
            if title:
                title = title[0].get_text(strip=True)
            else:
                title = "VAZIO"

            # pega o ano
            year = soup.find("span", class_="release-year").get_text(strip=True)
    
            # pega informa~]oes diversas
            infos = soup.find_all("div", class_="poster-detail-infos__value")

            # pega os generos do titulo
            genres = infos[4].get_text(strip=True).split(',')
            genres = [genre.strip() for genre in genres]

            # pega a duração do filme
            movie_duration = infos[6].get_text(strip=True)

            # classificação de idade livre por padrão 
            age_classification = 'L'
            
            # caso exista essa classificação, é salva
            if len(infos) >= 9:
                age_classification = infos[8].get_text(strip=True)            
            
            # adiciona no dataframe
            df = pd.concat([df, pd.DataFrame([{
                "link": link,
                "title": title,
                "year": year,
                "streamings": streamings_names,
                "synopsis_content": synopsis_content,
                "synopsis_lemming": synopsis_lemming,
                "synopsis_stemming": synopsis_stemming,
                "just_watch_rating": rating_just_watch,
                "rotten_tomatoes_rating": rating_rotten_tomatoes,
                "imdb_ratings": rating_imdb,
                "genres": genres,
                "movie_duration": movie_duration,
                "age_classification": age_classification
            }])], ignore_index=True)

    # no final, salva num csv

    df.to_csv("data/movies_info.csv", index=False, encoding="utf-8", sep=";")

def clean_synopis(sinopse):
    # Verificar se a sinopse não é None ou vazia
    if not sinopse or pd.isna(sinopse):
        return ""
    
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
    
    return palavras_filtradas 


def lemma(palavras_filtradas: list[str]) -> list:
    """
    Feito o processo de lematização.

    Args:
        palavras_filtradas (list[str]): palavras com a remoção dos stopwords e pontuação.  
    """
    lemmatizer = WordNetLemmatizer()

    lemmas = [lemmatizer.lemmatize(palavra) for palavra in palavras_filtradas]

    palavras_finais = [
        palavra for palavra in lemmas 
        if len(palavra) > 2 and palavra.isalpha()  # só letras
    ]
    
    return palavras_finais 


def stemming(palavras_filtradas: list[str]) -> list:
    """
    Feito o processo de stematização.

    Args:
        palavras_filtradas (list[str]): palavras com a remoção dos stopwords e pontuação.  
    """
    stemmer = RSLPStemmer()

    palavras_stemmed = [stemmer.stem(palavra) for palavra in palavras_filtradas]

    return palavras_stemmed

get_movies_info()