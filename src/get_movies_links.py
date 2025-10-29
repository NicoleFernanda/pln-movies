import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import csv


def get_movies_links():
    """
    Encontra os links a partir da página principal de filmes do justwatch.
    Salva numa lista e, depois, adiciona no arquivo data/movies_links.py
    """

    driver = webdriver.Chrome()
    url = "https://www.justwatch.com/br/filmes"
    driver.get(url)

    # rola até o final da página
    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolls = 0
    while scrolls < 60:  # Limita a 60 rolagens
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(15)  # espera carregar mais filmes por 15 s
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        scrolls += 1

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", class_="title-list-grid__item--link")
    todos_links = []
    for link in links:
        href = link.get("href")
        if href:
            todos_links.append("https://www.justwatch.com" + href)

    print(f"total de filmes encontrados: {len(todos_links)}")

    # grava os links em um arquivo CSV
    with open("data/movies_links.csv", "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for l in todos_links:
            writer.writerow([l])

    driver.quit()


get_movies_links()