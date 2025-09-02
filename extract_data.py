from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import pandas as pd


        
def ler_links_csv(arquivo_csv):
    # Ler os links do arquivo CSV gerado anteriormente
    try:
        df = pd.read_csv(arquivo_csv, encoding='utf-8')
        links = df['link'].dropna().str.strip().tolist()

        print(f"Total de links carregados: {len(links)}")
        testar_extracao_basica(links[1])

    except FileExistsError:
        print(f"Arquivo {arquivo_csv} não encontrado!")
        return []
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return []

def testar_extracao_basica(url_teste):

    #Método para testar a extração em uma URL específica

    print(f"Testando extração em: {url_teste}")

    driver = webdriver.Chrome()
    driver.get(url_teste)
    time.sleep(3) 

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    try:
        titulo = soup.find("h1", class_="title-detail-hero__details__title has-original-title")
        print(f"Título encontrado: {titulo.text.strip() if titulo else 'NÃO ENCONTRADO'}")
    except:
        print("Erro ao extrair título")

    try:
        generos = soup.find("div", class_="poster-detail-infos__value")
        #lista_generos = [g.text.strip() for g in generos]
        print(f"Gêneros encontrados: {generos.text.strip() if titulo else 'NÃO ENCONTRADO'}")
    except:
        print("Erro ao extrair gêneros")


    driver.quit()


ler_links_csv("links_filmes.csv")