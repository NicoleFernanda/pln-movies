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

Estrutura dos arquivos gerados:

| Arquivo                | Descrição                                                         |
| ---------------------- | ----------------------------------------------------------------- |
| **`movies_links.csv`** | Contém os links individuais de cada filme coletado no JustWatch.  |
| **`movies_info.csv`**  | Dataset com os metadados e informações detalhadas de cada título. |

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

### 4. Modelo de Classificação - KNN

**Arquivo:** `knn.py`

O modelo **KNN (K-Nearest Neighbors)** é utilizado para **classificação** dos filmes com base nos *embeddings* gerados pelo modelo SBERT.
Cada filme já pertence a um **cluster** (grupo) criado anteriormente pelo `KMeans`, representando conjuntos de filmes similares.
Portanto, o KNN tenta **aprender a relação entre os embeddings e esses grupos**, de modo que seja possível prever a qual grupo um novo filme (ou sinopse) pertence.

Os arquivos utilizados nesta etapa são:

| Arquivo                | Descrição                                                                    |
| ---------------------- | ---------------------------------------------------------------------------- |
| `sbert_embeddings.npy` | Matriz de vetores gerados pelo modelo SBERT. Cada linha representa um filme. |
| `cluster_labels.csv`   | Contém o rótulo (cluster) atribuído a cada filme no processo de agrupamento. |


### 5. Testes

#### 5.1 Testes com KNN

Foram realizados testes com **10 clusters** e os resultados gerais de classificação foram:

```
              precision    recall  f1-score   support

           0       0.36      0.89      0.52         9
           1       1.00      0.50      0.67         8
           2       0.78      1.00      0.88        14
           3       0.71      0.56      0.62         9
           4       0.50      0.50      0.50        10
           5       0.62      0.56      0.59         9
           6       0.75      0.38      0.50         8
           7       0.86      0.33      0.48        18
           8       0.60      0.82      0.69        11
           9       0.67      0.75      0.71         8

    accuracy                           0.62       104
   macro avg       0.69      0.63      0.61       104
weighted avg       0.70      0.62      0.62       104
```

**Interpretação dos resultados:**

* **Precision:** porcentagem de filmes preditos corretamente em cada cluster.
* **Recall:** proporção de filmes reais de um cluster que foram corretamente identificados pelo modelo.
* **F1-score:** média harmônica entre precision e recall.
* **Support:** número de filmes reais em cada cluster.

Alguns clusters (como 0 e 2) possuem recall alto, indicando que o KNN consegue identificar bem os filmes que pertencem a esses grupos. Outros clusters têm valores mais baixos, sugerindo maior heterogeneidade de filmes ou menos exemplos de treinamento.

---

### 4.2 Exemplos de clusters

Abaixo estão alguns filmes com seus clusters preditos, para exemplificar o tipo de agrupamento feito pelo KMeans:

| Filme                                                  | Cluster |
| ------------------------------------------------------ | ------- |
| Hora do Desaparecimento (2025)                         | 8       |
| O Match Perfeito (2025)                                | 2       |
| Batalha Atrás de Batalha (2025)                        | 7       |
| A Mulher do Camarote 10 (2025)                         | 1       |
| Código Preto (2025)                                    | 0       |
| Extermínio: A Evolução (2025)                          | 8       |
| Superman (2025)                                        | 7       |
| Volta Para Mim (2025)                                  | 2       |
| Caramelo (2025)                                        | 5       |
| Pecadores (2025)                                       | 2       |
| F1 - O Filme (2025)                                    | 7       |
| Dias Perfeitos (2023)                                  | 1       |
| A Vizinha Perfeita (2025)                              | 9       |
| *Os Novos Vingadores (2025)                            | 3       |
| O Telefone Negro (2022)                                | 9       |
| O Quarteto Fantástico: Primeiros Passos (2025)         | 4       |
| Demon Slayer: Kimetsu no Yaiba Castelo Infinito (2025) | 6       |
| Mundo Jurássico - Renascimento (2025)                  | 6       |
| The Conjuring 4: Extrema-Unção (2025)                  | 4       |
| Lilo e Stitch (2025)                                   | 2       |

> Observação: clusters próximos (mesmo número) possuem similaridade semântica mais alta entre as sinopses dos filmes.

---

### 4.3 Exemplos de predições com KNN

```python
----------------------------------------------------------------------------------------------
Sinopse:  "Mariazinha comprou um jogo de tabuleiro e foi levada para outro mundo."
Cluster predito:  5
----------------------------------------------------------------------------------------------
Sinopse:"""
    Dois jovens de mundos diferentes se conhecem por acaso e acabam vivendo um romance intenso,
    enfrentando desafios familiares e sociais para ficarem juntos.
    Com esse amor, eles podem enfrentar qualquer barreira.
  """

Cluster predito:  2
----------------------------------------------------------------------------------------------
Sinopse: """
    A vida de um músico talentoso é cercada de dúvidas.
    Essa é a realidade que John vive: cheia de incertezas, mas com muita notas no coração.
    Em meio de um turbilhão de emoções, surge uma proposta que mudará o seu mundo e, com isso,
    quem está em sua órbita.
"""

Cluster predito:  1
----------------------------------------------------------------------------------------------
```
**Conclusões:**
- Ao visualizar os filmes que também pertencem ao cluster `5`, foi observado que as obras inseridas não tem tanta relação entre si (exemplos: Gladiador, Midsommar, África Minha, Amores Brutos). Como a sinopse fala sobre viagem, pode ser que tenha se encaixado nesta categoria exatamente por isso. Porém, não existe tanta similaridade entre essa sinopse e os outros filmes também do mesmo grupo.

- Em contra partida, a similaridade entre a segunda sinopse e os filmes do cluster `2` é bem alta. Isto é, a maior parte das obras do grupo estão na categoria de romance. Além disso, esse comportamente pode ser observado na sessão `5.1`.

- Por fim, filmes do grupo 1, envolvem filmes fictícios. Enquanto a sinopse apresentada não faz menção disso. No caso, não fala sobre uma realidade alternativa ou nada que envolva muita ação. Porém, esse resultado pode ter sido causado por conta das palavras "órbita", "mundo" e "realidade".

## Conclusões

Com o desenvolvimento do modelo e a análise dos resultados finais (dentro do arquivo CSV `cluster_labels.csv`), é possível observar que, embora a precisão não seja perfeita, o modelo consegue agrupar os filmes seguindo uma lógica "razoável". Por exemplo, ele apresenta maior facilidade em identificar filmes de romance, enquanto outros clusters contêm obras com maior diversidade, podendo ser uma certa aleatoriedade na classificação.

Com isso, podemos concluir que os resultados ainda não são ideais. Considerando que utilizamos 10 clusters para classificar mais de 500 filmes, é provável que aumentar o número de clusters resulte em uma segmentação mais refinada e precisa.

Ainda assim, os testes indicam que o modelo apresenta resultados satisfatórios dentro das limitações do número de clusters e da complexidade do dataset, mostrando que a abordagem tem potencial e pode ser aprimorada com ajustes nos parâmetros de clusterização.

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

