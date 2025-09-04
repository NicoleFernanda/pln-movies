from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv

def ler_links_csv(arquivo_csv):
    try:
        df = pd.read_csv(arquivo_csv, encoding='utf-8')
        links = df['link'].dropna().str.strip().tolist()
        print(f"Total de links carregados: {len(links)}")
        testar_extracao_basica(links)
    except FileNotFoundError:
        print(f"Arquivo {arquivo_csv} não encontrado!")
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")

# ---------- helpers seguros ----------
def get_text_xpath(driver, xpath, wait=None, timeout=10, must_be_visible=False):
    """Tenta pegar o texto de um XPath. Retorna None se não achar."""
    try:
        if wait:
            cond = EC.visibility_of_element_located if must_be_visible else EC.presence_of_element_located
            el = wait.until(cond((By.XPATH, xpath)))
        else:
            el = driver.find_element(By.XPATH, xpath)
        txt = (el.text or "").strip()
        return txt if txt else None
    except Exception:
        return None

def first_not_empty(*values):
    for v in values:
        if v and str(v).strip():
            return str(v).strip()
    return None

def testar_extracao_basica(links):
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(60)
    wait = WebDriverWait(driver, 20)

    try:
        with open("dados_filmes.csv", "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(["Título", "Ano", "Direção", "Gênero", "Canais/serviços"])

            for url_teste in links:
                try:
                    driver.get(url_teste)
                    # Dê um respiro se a página é JS pesada
                    #time.sleep(1.5)

                    html = driver.page_source
                    soup = BeautifulSoup(html, "html.parser")

                    # ----- Título -----
                    titulo_txt = get_text_xpath(
                        driver,
                        '/html/body/div/div[3]/div[2]/div[2]/div[1]/div[1]/h1',
                        wait=wait, must_be_visible=True
                    ) or "NÃO ENCONTRADO"

                    # ----- Ano (via soup) -----
                    ano_el = soup.select_one("span.release-year")
                    ano_txt = (ano_el.get_text(strip=True) if ano_el else None) or "NÃO ENCONTRADO"

                    # ----- Direção (via soup) -----
                    dir_el = soup.select_one("span.title-credit-name")
                    direcao_txt = (dir_el.get_text(strip=True) if dir_el else None) or "NÃO ENCONTRADO"

                    # ----- Gênero (use vários XPaths, do mais específico para o mais genérico) -----
                    genero_candidates = [
                        '/html/body/div[1]/div[3]/div[2]/div[3]/div[1]/div[6]/aside/div/div[3]/div[3]/div/div/span[1]', # seu original
                        "//aside//span[contains(@class,'genre')]",           # comum em muitos sites
                        "//span[contains(@data-qa,'genres')]",               # data-qa
                        "//div[contains(@class,'genres')]//span",            # container de gêneros
                        "//li[contains(@class,'genre')]/a | //li[contains(@class,'genre')]/span"
                    ]
                    generos_txt = None
                    for xp in genero_candidates:
                        txt = get_text_xpath(driver, xp, wait=wait, must_be_visible=False)
                        if txt:
                            generos_txt = txt
                            break
                    generos_txt = generos_txt or "NÃO ENCONTRADO"

                    # ----- Canais/serviços -----
                    canais_txt = "NÃO ENCONTRADO"
                    try:
                        container = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.buybox-container"))
                        )
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)

                        imgs = wait.until(
                            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.buybox-container img[title]"))
                        )

                        titles = []
                        for img in imgs:
                            t = (img.get_attribute("title") or "").strip()
                            if not t:
                                t = (img.get_attribute("alt") or "").strip()
                            if t:
                                titles.append(t)

                        # remove duplicados mantendo ordem
                        seen = set()
                        unique_titles = [t for t in titles if not (t in seen or seen.add(t))]
                        if unique_titles:
                            canais_txt = ", ".join(unique_titles)
                    except TimeoutException:
                        # deixa "NÃO ENCONTRADO" se não aparecer
                        pass

                    # ----- Escreve uma linha por link -----
                    writer.writerow([titulo_txt, ano_txt, direcao_txt, generos_txt, canais_txt])
                    print(f"OK: {url_teste}")

                except Exception as e:
                    # Não derruba tudo se um link falhar
                    print(f"Falha nesse link ({url_teste}): {e}")
                    writer.writerow(["ERRO", "", "", "", f"Falha ao processar: {url_teste}"])

    except Exception as e:
        print(f"Falha durante a extração: {e}")
    finally:
        driver.quit()

ler_links_csv("links_filmes.csv")
