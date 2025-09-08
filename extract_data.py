from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv

def configurar_driver():
    """Configura o driver Chrome com opções otimizadas"""
    chrome_options = Options()
    # Opções para velocidade - REMOVIDO --disable-javascript
    chrome_options.add_argument("--disable-images")  # Não carrega imagens
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")  # Descomente para rodar sem interface
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

def extrair_dados_filme(driver, url):
    """Extrai dados de um filme específico"""
    try:
        print(f"Processando: {url}")
        driver.get(url)
        
        # Aguarda mais tempo para carregar (JS precisa funcionar)
        #time.sleep(4)
        
        # Cria wait para elementos dinâmicos
        wait = WebDriverWait(driver, 15)
        
        # ----- Título (usando Selenium direto) -----
        try:
            titulo_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.title-detail-hero__details__title")))
            titulo = titulo_el.text.strip() if titulo_el.text else "NÃO ENCONTRADO"
        except:
            titulo = "NÃO ENCONTRADO"
        
        # ----- Ano -----
        try:
            ano_el = driver.find_element(By.CSS_SELECTOR, "span.release-year")
            ano = ano_el.text.strip() if ano_el.text else "NÃO ENCONTRADO"
        except:
            ano = "NÃO ENCONTRADO"
        
        # ----- Direção -----
        try:
            dir_el = driver.find_element(By.CSS_SELECTOR, "span.title-credit-name")
            direcao = dir_el.text.strip() if dir_el.text else "NÃO ENCONTRADO"
        except:
            direcao = "NÃO ENCONTRADO"
        
        # ----- Gêneros (XPath CORRIGIDO) -----
        generos = "NÃO ENCONTRADO"
        
        # Lista de XPaths para testar
        xpaths_generos = [
            '/html/body/div[1]/div[3]/div[2]/div[3]/div[1]/div[6]/aside/div/div[3]/div[3]/div/div/span[1]',  # Seu XPath
            '//*[@id="base"]//aside//div[3]/div[3]/div/div/span[1]',  # Mais flexível
            '//aside//span[contains(text(),"Ficção") or contains(text(),"Ação") or contains(text(),"Drama")]',  # Por conteúdo
            '//div[contains(@class,"detail-infos")]//span[1]',  # Genérico
            '//*[@id="base"]/div[2]/div[3]/div[1]/div[6]/aside/div/div[3]/div[1]/div/div/span[1]'
        ]
        
        for xpath in xpaths_generos:
            try:
                genero_el = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                texto_genero = genero_el.text.strip()
                
                # Verifica se o texto parece ser gênero
                palavras_generos = ["Ficção", "Ação", "Drama", "Comédia", "Terror", "Romance", "Aventura", "Fantasia"]
                if any(palavra in texto_genero for palavra in palavras_generos) and len(texto_genero) < 200:
                    generos = texto_genero
                    print(f"✓ Gêneros encontrados: {generos}")
                    break
                    
            except Exception as e:
                print(f"XPath falhou: {str(e)[:50]}...")
                continue
        
        # ----- Canais/Serviços -----
        canais = "NÃO ENCONTRADO"
        try:
            # Aguarda o container aparecer
            container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.buybox-container")))
            
            # Busca por imagens com título
            imgs = driver.find_elements(By.CSS_SELECTOR, "div.buybox-container img[title], div.streaming-offer img[title]")
            
            if imgs:
                titles = []
                for img in imgs:
                    title = img.get_attribute("title") or img.get_attribute("alt") or ""
                    if title and title not in titles:
                        titles.append(title)
                canais = ", ".join(titles) if titles else "NÃO ENCONTRADO"
                
        except:
            pass  # Mantém "NÃO ENCONTRADO"
        
        return {
            "titulo": titulo,
            "ano": ano,
            "direcao": direcao,
            "generos": generos,
            "canais": canais,
            "status": "OK"
        }
        
    except Exception as e:
        print(f"Erro ao processar {url}: {str(e)}")
        return {
            "titulo": "ERRO",
            "ano": "",
            "direcao": "",
            "generos": "",
            "canais": f"Erro: {str(e)}",
            "status": "ERRO"
        }

def ler_links_csv(arquivo_csv):
    """Lê links do CSV"""
    try:
        df = pd.read_csv(arquivo_csv, encoding='utf-8')
        links = df['link'].dropna().str.strip().tolist()
        print(f"Total de links carregados: {len(links)}")
        return links
    except FileNotFoundError:
        print(f"Arquivo {arquivo_csv} não encontrado!")
        return []
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return []

def processar_filmes(links, limite=None, delay=1):
    """Processa lista de filmes com controle de velocidade"""
    driver = configurar_driver()
    
    # Limita quantidade para teste
    if limite:
        links = links[:limite]
        print(f"Processando apenas os primeiros {limite} links")
    
    dados_filmes = []
    
    try:
        for i, url in enumerate(links, 1):
            print(f"\n[{i}/{len(links)}] Processando filme...")
            
            dados = extrair_dados_filme(driver, url)
            dados_filmes.append(dados)
            
            # Log do resultado
            if dados["status"] == "OK":
                print(f"✓ Sucesso: {dados['titulo']} | Gêneros: {dados['generos']}")
            else:
                print(f"✗ Falha: {url}")
            
            # Delay entre requisições para não sobrecarregar o servidor
            if i < len(links):  # Não precisa delay no último
                time.sleep(delay)
                
    except KeyboardInterrupt:
        print("\nProcessamento interrompido pelo usuário")
    except Exception as e:
        print(f"Erro geral: {e}")
    finally:
        driver.quit()
    
    return dados_filmes

def salvar_dados_csv(dados_filmes, arquivo_saida="dados_filmes_otimizado.csv"):
    """Salva dados em CSV"""
    try:
        with open(arquivo_saida, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(["Título", "Ano", "Direção", "Gêneros", "Canais/Serviços", "Status"])
            
            for dados in dados_filmes:
                writer.writerow([
                    dados["titulo"],
                    dados["ano"], 
                    dados["direcao"],
                    dados["generos"],
                    dados["canais"],
                    dados["status"]
                ])
        
        print(f"\nDados salvos em: {arquivo_saida}")
        
        # Estatísticas
        sucessos = sum(1 for d in dados_filmes if d["status"] == "OK")
        erros = len(dados_filmes) - sucessos
        print(f"Sucessos: {sucessos}, Erros: {erros}")
        
    except Exception as e:
        print(f"Erro ao salvar CSV: {e}")

def main():
    """Função principal"""
    print("=== EXTRATOR DE DADOS DE FILMES ===\n")
    
    # Lê os links
    links = ler_links_csv("links_filmes.csv")
    if not links:
        return
    
    # TESTE COM POUCOS LINKS PRIMEIRO
    print("Iniciando teste com 3 primeiros links...")
    dados = processar_filmes(links, limite=10, delay=10)
    
    # Salva os dados
    salvar_dados_csv(dados)
    
    # Mostra resultado dos gêneros
    print("\n=== RESULTADO DOS GÊNEROS ===")
    for i, dados in enumerate(dados, 1):
        print(f"{i}. {dados['titulo']} -> {dados['generos']}")
    
    # Pergunta se quer continuar com todos
    resposta = input(f"\nTeste concluído! Processar todos os {len(links)} links? (s/n): ")
    if resposta.lower() == 's':
        print("Processando todos os links...")
        dados_completos = processar_filmes(links, delay=2)
        salvar_dados_csv(dados_completos, "dados_filmes_completo.csv")

if __name__ == "__main__":
    main()