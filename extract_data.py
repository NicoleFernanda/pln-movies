from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import csv

def ler_links_csv(arquivo_csv):
    try:
        df = pd.read_csv(arquivo_csv, encoding='utf-8')
        links = df['link'].dropna().str.strip().tolist()
        print(f"Total de links carregados: {len(links)}")
        testar_extracao_basica(links[1])
    except FileNotFoundError:
        print(f"Arquivo {arquivo_csv} não encontrado!")
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")

def testar_extracao_basica(url_teste):
    print(f"Testando extração em: {url_teste}")

    conatador = 0

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(url_teste)

        # (Opcional) pequena espera inicial para JS pesados
        time.sleep(1.5)

        # --- Título, ano, etc. (se quiser manter BeautifulSoup para estático) ---
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        titulo = soup.select_one("h1.title-detail-hero__details__title.has-original-title")
        print(f"Título encontrado: {titulo.text.strip() if titulo else 'NÃO ENCONTRADO'}")

        ano = soup.select_one("span.release-year")
        print(f"Ano encontrado: {ano.text.strip() if ano else 'NÃO ENCONTRADO'}")

        direcao = soup.select_one("span.title-credit-name")
        print(f"Direção encontrada: {direcao.text.strip() if direcao else 'NÃO ENCONTRADO'}")

        try: 
            generos = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div[3]/div[1]/div[6]/aside/div/div[3]/div[3]/div/div/span[1]') 
            print(f"Gêneros encontrados: {generos.text.strip() if generos else 'NÃO ENCONTRADO'}") 
        except: 
            print("Erro ao extrair gêneros")


        container = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.buybox-container"))
        )

        # garantir que o container esteja visível e forçar lazy-load dos ícones
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)
        # aguarde as imagens com title ficarem visíveis
        imgs = wait.until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.buybox-container img[title]"))
        )

        titles = []
        for img in imgs:
            t = (img.get_attribute("title") or "").strip()
            if not t:
                t = (img.get_attribute("alt") or "").strip()  # fallback
            if t:
                titles.append(t)

        # remover duplicados mantendo ordem
        seen = set()
        unique_titles = [t for t in titles if not (t in seen or seen.add(t))]

        print("Canais/serviços :", unique_titles if unique_titles else "NENHUM ENCONTRADO")

        with open("dados_filmes.csv", "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if(conatador < 1):
                writer.writerow(["Título", "Ano", "Direção", "Gênero", "Canais/serviços"])
            
            writer.writerow([titulo.text.strip(), ano.text.strip(), direcao.text.strip(), generos.text.strip(), unique_titles])
            conatador += 1

    except Exception as e:
        print(f"Falha durante a extração: {e}")
    finally:
        driver.quit()


ler_links_csv("links_filmes.csv")