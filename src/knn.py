import numpy as np
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix

from vectorizer import Vectorizer


class KNN:
    def __init__(self, k_neighbors: int = 5, metric: str = "cosine"):
        """
        Inicializa o modelo KNN.

        Args:
            k_neighbors: Número de vizinhos para o KNN
            metric: Métrica de distância (padrão: 'cosine')
        """
        self.k_neighbors = k_neighbors
        self.metric = metric
        self.model = None

    def load_data(self, base_path: str = None) -> tuple:
        """
        Carrega os dados de embeddings e clusters.

        Args:
            base_path: Caminho base do projeto. Se None, usa caminho relativo.

        Returns:
            Tupla (x, y) com embeddings e labels de cluster
        """
        if base_path:
            x_path = os.path.join(
                base_path, "data", "vectorized", "sbert_embeddings.npy"
            )
            y_path = os.path.join(base_path, "data", "vectorized", "cluster_labels.csv")
        else:
            x_path = "data/vectorized/sbert_embeddings.npy"
            y_path = "data/vectorized/cluster_labels.csv"

        x = np.load(x_path)
        y = pd.read_csv(y_path, sep=";")["cluster"]

        return x, y

    def train(self, x, y):
        """
        Treina o modelo KNN com os dados fornecidos.

        Args:
            x: Features (embeddings)
            y: Labels (clusters)
        """
        self.model = KNeighborsClassifier(
            n_neighbors=self.k_neighbors, metric=self.metric
        )
        self.model.fit(x, y)

    def train_and_evaluate(
        self, test_size: float = 0.2, random_state: int = 42
    ) -> KNeighborsClassifier:
        """
        Carrega dados, treina o modelo e avalia sua performance.

        Args:
            test_size: Porcentagem dos dados para teste
            random_state: Seed para reprodutibilidade

        Returns:
            Modelo KNN treinado
        """
        x, y = self.load_data()
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=test_size, random_state=random_state
        )

        self.train(x_train, y_train)

        y_pred = self.model.predict(x_test)

        print("Veracidade entre os dados reais e os preditos:")
        print(classification_report(y_test, y_pred))

        return self.model

    def load_and_train(self, base_path: str = None):
        """
        Carrega dados e treina o modelo com todos os dados disponíveis.
        Útil para uso em produção.

        Args:
            base_path: Caminho base do projeto
        """
        x, y = self.load_data(base_path)
        self.train(x, y)

    def predict(self, embeddings):
        """
        Faz predições usando o modelo treinado.

        Args:
            embeddings: Embeddings para classificar

        Returns:
            Predições de cluster
        """
        if self.model is None:
            raise ValueError(
                "Modelo não foi treinado. Chame train() ou train_and_evaluate() primeiro."
            )
        return self.model.predict(embeddings)

    def get_model(self):
        """
        Retorna o modelo sklearn subjacente.

        Returns:
            Modelo KNeighborsClassifier
        """
        return self.model


def load_knn_data() -> list:
    """
    como já foi feito em 'vectorize', vamos reutilizar.
    lá, ele utilizou o KMeans, o que significa que fez grupos pela semelhança entre filmes.
    então, será utilizado os filmes e seus os grupos.
    """
    x = np.load("data/vectorized/sbert_embeddings.npy")  # pega o arquivo gerado
    y = pd.read_csv("data/vectorized/cluster_labels.csv", sep=";")["cluster"]

    return x, y


def train_and_avaluate(k_neighbors: int = 5):
    """
    Chama a função que separa os dados x e y a partir do arquivo.
    Treina os dados de entrada. Predita e avalia.
    """
    x, y = load_knn_data()
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )

    # modelo (usa a similaridade do cosseno)
    knn = KNeighborsClassifier(n_neighbors=k_neighbors, metric="cosine")

    # treina
    knn.fit(x_train, y_train)

    # predita
    y_pred = knn.predict(x_test)

    print("Veracidade entre os dados reais e os preditos:")
    print(classification_report(y_test, y_pred))

    return knn


if __name__ == "__main__":
    # Testar usando a nova classe KNN
    knn_classifier = KNN(k_neighbors=5)
    knn = knn_classifier.train_and_evaluate()

    # testar o modelo com um filme novo
    vectorizer = Vectorizer()
    vectorizer.create_sbert_embeddings([""])

    new_synopsys_1 = (
        "Mariazinha comprou um jogo de tabuleiro e foi levada para outro mundo."
    )
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

    new_embedding = vectorizer.sbert_model.encode(
        new_synopsys, normalize_embeddings=True
    )
    predict = knn_classifier.predict(new_embedding)

    for synopsys, prediction in zip(new_synopsys, predict):
        print(
            "----------------------------------------------------------------------------------------------"
        )
        print("Sinopse: ", synopsys)
        print("Cluster predito: ", prediction)
    print(
        "----------------------------------------------------------------------------------------------"
    )
