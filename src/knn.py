import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix

from vectorizer import Vectorizer



def load_knn_data() -> list:
    """
    como já foi feito em 'vectorize', vamos reutilizar.
    lá, ele utilizou o KMeans, o que significa que fez grupos pela semelhança entre filmes.
    então, será utilizado os filmes e seus os grupos.
    """
    x = np.load("data/vectorized/sbert_embeddings.npy") # pega o arquivo gerado
    y = pd.read_csv(
        "data/vectorized/cluster_labels.csv",
        sep=";"
    )["cluster"]

    return x, y


def train_and_avaluate(k_neighbors: int = 5):
    """
    Chama a função que separa os dados x e y a partir do arquivo.
    Treina os dados de entrada. Predita e avalia.
    """
    x, y = load_knn_data()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    # modelo (usa a similaridade do cosseno)
    knn = KNeighborsClassifier(n_neighbors=k_neighbors, metric="cosine")

    # treina
    knn.fit(x_train, y_train)

    # predita
    y_pred = knn.predict(x_test)

    print("Veracidade entre os dados reais e os preditos:")
    print(classification_report(y_test, y_pred))

    return knn

    
knn = train_and_avaluate()

# testar o modelo com um filme novo
vectorizer = Vectorizer()
vectorizer.create_sbert_embeddings([""])

new_synopsys_1 = "Mariazinha comprou um jogo de tabuleiro e foi levada para outro mundo."
new_synopsys_2 = """
    Dois jovens de mundos diferentes se conhecem por acaso e acabam vivendo um romance intenso, 
    enfrentando desafios familiares e sociais para ficarem juntos. 
    Com esse amor, eles podem enfrentar qualquer barreira.
"""
new_synopsys_3 = """
    A vida de um músico talentoso é cercada de dúvidas. 
    Essa é a realidade que John vive: cheia de incertezas, mas com muita notas no coração. 
    Em meio de um turbilhão de emoções, surge uma proposta que mudará o seu mundo e, com isso, 
    quem está em sua órbita.
"""
new_synopsys = [new_synopsys_1, new_synopsys_2, new_synopsys_3]

new_embedding = vectorizer.sbert_model.encode(new_synopsys, normalize_embeddings=True)
predict = knn.predict(new_embedding)

for synopsys, prediction in zip(new_synopsys, predict):
    print("----------------------------------------------------------------------------------------------")
    print("Sinopse: ", synopsys)
    print("Cluster predito: ", prediction)
print("----------------------------------------------------------------------------------------------")
