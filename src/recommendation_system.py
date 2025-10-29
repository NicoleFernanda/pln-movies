"""Sistema de recomendação simples para filmes."""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

class RecommendationSystem:
    def __init__(self, df, vectorizer):
        self.df = df
        self.vectorizer = vectorizer
        self.clusters = None
        self.similarity_matrix = None
        self.pca_coords = None
    
    def perform_clustering(self, method="sbert", n_clusters=10):
        # Determinar número de clusters automaticamente
        if n_clusters is None:
            n_samples = len(self.df)
            if n_samples <= 10:
                n_clusters = 3
            elif n_samples <= 30:
                n_clusters = 4
            elif n_samples <= 60:
                n_clusters = 5
            else:
                n_clusters = 6
        
        # Obter embeddings
        if method == "sbert":
            embeddings = self.vectorizer.sbert_embeddings
        elif method == "tfidf":
            embeddings = self.vectorizer.tfidf_matrix.toarray()
        else:
            embeddings = self.vectorizer.bow_matrix.toarray()
        
        # Clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.clusters = kmeans.fit_predict(embeddings)
        
        return pd.DataFrame({
            'title': self.df['title'],
            'cluster': self.clusters
        })
    
    def create_pca_projection(self, method="sbert"):
        # Obter embeddings
        if method == "sbert":
            embeddings = self.vectorizer.sbert_embeddings
        elif method == "tfidf":
            embeddings = self.vectorizer.tfidf_matrix.toarray()
        else:
            embeddings = self.vectorizer.bow_matrix.toarray()
        
        # PCA
        pca = PCA(n_components=2, random_state=42)
        self.pca_coords = pca.fit_transform(embeddings)
        
        pca_df = pd.DataFrame(self.pca_coords, columns=["pc1", "pc2"])
        pca_df.insert(0, 'title', self.df['title'])
        if self.clusters is not None:
            pca_df.insert(1, 'cluster', self.clusters)
        
        return pca_df
    
    def recommend_by_title(self, title, method="sbert", top_k=5):
        # Encontrar índice do filme
        titles = self.df['title'].tolist()
        try:
            movie_idx = titles.index(title)
        except ValueError:
            raise ValueError(f"Filme '{title}' não encontrado")
        
        # Calcular similaridade
        if self.similarity_matrix is None:
            self.similarity_matrix = self.vectorizer.calculate_similarity_matrix(method)
        
        similarities = self.similarity_matrix[movie_idx]
        sim_scores = [(i, sim) for i, sim in enumerate(similarities) if i != movie_idx]
        sim_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Retornar recomendações
        recommendations = []
        for i, (idx, similarity) in enumerate(sim_scores[:top_k]):
            movie_data = self.df.iloc[idx]
            recommendations.append({
                'rank': i + 1,
                'title': movie_data['title'],
                'similarity': float(similarity),
                'genres': movie_data.get('genres', 'N/A')
            })
        
        return recommendations
    
    def recommend_by_query(self, query, top_k=5):
        similar_docs = self.vectorizer.search_similar_documents(query, top_k)
        
        recommendations = []
        for i, (idx, similarity) in enumerate(similar_docs):
            movie_data = self.df.iloc[idx]
            recommendations.append({
                'rank': i + 1,
                'title': movie_data['title'],
                'similarity': float(similarity),
                'synopsis': movie_data.get('synopsis_content', 'N/A')[:100] + "...",
                'genres': movie_data.get('genres', 'N/A')
            })
        
        return recommendations
    
    def save_results(self, output_dir):
        from pathlib import Path
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if self.clusters is not None:
            cluster_df = pd.DataFrame({
                'title': self.df['title'],
                'cluster': self.clusters
            })
            cluster_df.to_csv(output_path / "cluster_labels.csv", index=False, sep=";")
        
        if self.pca_coords is not None:
            pca_df = self.create_pca_projection()
            pca_df.to_csv(output_path / "cluster_pca2d.csv", index=False, sep=";")
        
        if self.similarity_matrix is not None:
            sim_df = pd.DataFrame(
                self.similarity_matrix,
                index=self.df['title'],
                columns=self.df['title']
            )
            sim_df.to_csv(output_path / "similarity_matrix.csv", sep=";")