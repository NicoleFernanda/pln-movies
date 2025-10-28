# 🎬 PLN Movies

Repositório criado para a disciplina de **Processamento de Linguagem Natural (PLN)**.

O objetivo deste projeto é **coletar, estruturare trabalhar em cima de informações sobre filmes** a partir do site [JustWatch](https://www.justwatch.com/br/filmes).

## Como funciona

O fluxo atual é composto por **duas etapas principais de coleta**, responsáveis por extrair e estruturar os dados necessários para análise.
Depois disso, ...

---

### 1. Coleta dos links de filmes e de suas informações

**Arquivo:** `get_movies_links.py`

Este script realiza a navegação automática na página principal do JustWatch e extrai os links de todos os filmes exibidos.

* Utiliza **Selenium** para rolar a página inicial dinamicamente, garantindo que "todos" os títulos sejam carregados, considerando sua limitação de scrolls.
* Localiza os elementos HTML correspondentes aos links dos filmes.
* Gera o arquivo `data/movies_links.csv`, contendo os links individuais de cada título encontrado — este arquivo é **essencial para a próxima etapa** da coleta.

**Arquivo:** `get_movies_info.py`

Com base nos links coletados anteriormente, este script acessa cada página individual de filme e extrai suas **informações detalhadas**.

* Utiliza **Requests** e **BeautifulSoup** para acessar e interpretar o conteúdo HTML de cada página.
* Extrai informações como:
  * Título 
  * Ano de lançamento
  * Plataformas de streaming disponíveis
  * Sinopse original -> **lemmatizada** e **com stemming**
  * Avaliações (JustWatch, Rotten Tomatoes, IMDb)
  * Gêneros
  * Duração do filme
  * Classificação indicativa

* Realiza o pré-processamento textual utilizando **NLTK**, aplicando *tokenização*, *remoção de stopwords*, *lemmatização* e *stemming*.
* Salva todas as informações no arquivo `data/movies_info.csv`, gerando o dataset consolidado.

> IMPORTANTE: Antes da primeira execução, é necessário baixar os recursos do NLTK (comentados no início do script). Após a primeira execução, essas linhas podem ser comentadas novamente.

### 🎞️ 2. Coleta das informações dos filmes

*(em desenvolvimento)*

---

## 📂 Estrutura dos arquivos gerados

| Arquivo                | Descrição                                                         |
| ---------------------- | ----------------------------------------------------------------- |
| **`movies_links.csv`** | Contém os links individuais de cada filme coletado no JustWatch.  |
| **`movies_info.csv`**  | Dataset com os metadados e informações detalhadas de cada título. |

---

Perfeito, Nicole! Mantendo o mesmo padrão do README e atualizando com o nome correto do arquivo (`analyze_movies.py`), a seção de vetorização e recomendação ficaria assim:

---

### 2. Vetorização, análise e sistema de recomendação

**Arquivo:** `analyze_movies.py`

Este script realiza o **pipeline completo de análise** a partir do dataset consolidado `movies_info.csv`:

* **Carrega os dados** previamente coletados (`movies_info.csv`).
* **Pré-processa os textos** (sinopses lemmatizadas), mantendo o pipeline pronto para análises posteriores.
* **Cria representações vetoriais** dos textos de filmes utilizando diferentes abordagens:
  * **Bag-of-Words (BoW)**
  * **TF-IDF**
  * **Sentence-BERT embeddings** (para similaridade semântica entre sinopses)

* **Executa o sistema de recomendação**:
  * Agrupa filmes em **clusters** com base na similaridade de conteúdo
  * Cria **projeções PCA** para visualização
  * Permite recomendar filmes similares por **título** ou por **query textual**

* **Salva os resultados**:
  * Vetores de representação (BoW, TF-IDF e SBERT) na pasta `data/vectorized/`
  * Resultados de clustering e projeções PCA na mesma pasta

**Exemplos de uso:**
* Recomendar filmes similares a um título específico e por uma consuta textual:

```python
recommend_movies("Superman(2025)", recommender)
search_movies("Heróis", recommender)
```

> IMPORTANTE: Os módulos `Vectorizer` e `RecommendationSystem` contêm a lógica de vetorização e recomendação. O pré-processamento textual completo, incluindo tokenização, lemmatização e stemming, pode ser integrado usando `TextPreprocessor` (atualmente comentado no script).

---

Perfeito! Esse `vetorize.py` é **o módulo de vetorização** usado pelo seu `analyze_movies.py`.

Em termos de documentação, podemos descrever assim:

---

### 3. Vetorização de textos e cálculo de similaridade

**Arquivo:** `vetorize.py`

Este módulo fornece uma classe `Vectorizer` para transformar as sinopses de filmes em **representações vetoriais**, essenciais para análise e recomendação:

* **BoW (Bag-of-Words)**: cria uma matriz de frequência de palavras, ignorando palavras muito raras ou muito frequentes.
* **TF-IDF**: cria uma matriz ponderada de termos, considerando sua importância relativa no corpus.
* **SBERT (Sentence-BERT)**: gera embeddings semânticos das sinopses para cálculo de similaridade mais avançado.

**Funcionalidades principais:**

* `create_bow_vectors(corpus)`: gera a matriz BoW e retorna os recursos (palavras).
* `create_tfidf_vectors(corpus)`: gera a matriz TF-IDF e retorna os recursos.
* `create_sbert_embeddings(corpus)`: gera embeddings SBERT normalizados para cada documento.
* `calculate_similarity_matrix(method="sbert")`: calcula matriz de similaridade entre todos os documentos (`bow`, `tfidf` ou `sbert`).
* `search_similar_documents(query, top_k=5)`: retorna os índices e similaridades dos documentos mais próximos a uma query.
* `save_vectors(output_dir)`: salva matrizes BoW, TF-IDF e embeddings SBERT em arquivos CSV e `.npy` na pasta especificada.

* Gera arquivos de vetores na pasta `data/vectorized/`:

| Arquivo                | Descrição                                                                              |
| ---------------------- | -------------------------------------------------------------------------------------- |
| `bow_matrix.csv`       | Matriz **Bag-of-Words** das sinopses, representando a frequência de palavras.          |
| `tfidf_matrix.csv`     | Matriz **TF-IDF** das sinopses, com a importância relativa de cada termo.       |
| `sbert_embeddings.npy` | Embeddings **SBERT** normalizados das sinopses para cálculo de similaridade semântica. |
| `sbert_embeddings.csv` | Versão em CSV dos embeddings SBERT             |


> IMPORTANTE: SBERT requer download do modelo `"sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"` na primeira execução, o que pode levar alguns minutos dependendo da conexão.

---

## Dependências

Selenium – automação da navegação web.
BeautifulSoup – extração de informações do HTML.
pandas – manipulação e estruturação de dados.
requests – requisições HTTP.
nltk – pré-processamento de texto (lemmatização, stemming, tokenização).
scikit-learn – ferramentas de machine learning e pré-processamento.
scipy – funções científicas e estatísticas.
numpy – operações numéricas e matrizes.
sentence-transformers – embeddings de sentenças e similaridade semântica.
matplotlib – visualização de dados.
seaborn – visualização estatística de dados.

