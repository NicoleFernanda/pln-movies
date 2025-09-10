Show, Nicole 🙌
Dá pra deixar esse **README.md** bem mais organizado e explicativo, com seções, exemplos de execução e até uns blocos de código. Aqui vai uma versão mais bonitinha:

---

````markdown
# 🎬 PLN Movies
Repositório criado para a disciplina de **Processamento de Linguagem Natural (PLN)**.

O objetivo deste projeto é coletar informações de filmes a partir do site [JustWatch](https://www.justwatch.com/br/filmes), gerando datasets que podem ser utilizados em análises posteriores.

---

## 🚀 Como funciona

O fluxo é dividido em **duas etapas principais**:

1. **Coleta dos links dos filmes**  
   Arquivo: `get_movies_links.py`  
   - Usa **Selenium** para rolar a página inicial do JustWatch.  
   - Extrai todos os links de filmes encontrados.  
   - Gera o arquivo `movies_links.csv`.  

   ```bash
   python get_movies_links.py
````

> Resultado: um CSV com todos os links de filmes coletados.

---

2. **Coleta das informações dos filmes**
   Arquivo: `get_movies_info.py`

   * Usa **Requests + BeautifulSoup** para acessar cada link da lista.
   * Extrai:

     * 🎥 Título e ano
     * 📺 Plataformas de streaming
     * 📝 Sinopse
     * ⭐ Avaliações (JustWatch, Rotten Tomatoes, IMDb)
     * 🎭 Gêneros
     * ⏱️ Duração
     * 🔞 Classificação indicativa
   * Gera o arquivo `movies_info.csv`.

   ```bash
   python get_movies_info.py
   ```

   > Resultado: um CSV tabular com os detalhes de cada filme.

---

## 📂 Estrutura dos arquivos gerados

* **`movies_links.csv`** → lista de links de filmes.
* **`movies_info.csv`** → dataset com os metadados de cada filme.

---

## ⚙️ Dependências

* [Selenium](https://selenium.dev/)
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [pandas](https://pandas.pydata.org/)
* [requests](https://docs.python-requests.org/)

