"""Vectorizador simples para análise de filmes."""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

class Vectorizer:
    def __init__(self):
        self.sbert_model = None
        self.bow_matrix = None
        self.tfidf_matrix = None
        self.sbert_embeddings = None
        self.bow_features = None
        self.tfidf_features = None
    
    def create_bow_vectors(self, corpus):
        text_corpus = [" ".join(doc) if isinstance(doc, list) else doc for doc in corpus]
        vectorizer = CountVectorizer(lowercase=True, min_df=2, max_df=0.95)
        self.bow_matrix = vectorizer.fit_transform(text_corpus)
        self.bow_features = vectorizer.get_feature_names_out()
        return self.bow_matrix, self.bow_features
    
    def create_tfidf_vectors(self, corpus):
        text_corpus = [" ".join(doc) if isinstance(doc, list) else doc for doc in corpus]
        vectorizer = TfidfVectorizer(lowercase=True, min_df=2, max_df=0.95)
        self.tfidf_matrix = vectorizer.fit_transform(text_corpus)
        self.tfidf_features = vectorizer.get_feature_names_out()
        return self.tfidf_matrix, self.tfidf_features
    
    def create_sbert_embeddings(self, corpus):
        if self.sbert_model is None:
            self.sbert_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        
        text_corpus = [" ".join(doc) if isinstance(doc, list) else doc for doc in corpus]
        self.sbert_embeddings = self.sbert_model.encode(text_corpus, normalize_embeddings=True)
        return self.sbert_embeddings
    
    def calculate_similarity_matrix(self, method="sbert"):
        if method == "bow" and self.bow_matrix is not None:
            return cosine_similarity(self.bow_matrix)
        elif method == "tfidf" and self.tfidf_matrix is not None:
            return cosine_similarity(self.tfidf_matrix)
        elif method == "sbert" and self.sbert_embeddings is not None:
            return cosine_similarity(self.sbert_embeddings)
        else:
            raise ValueError(f"Método '{method}' não disponível")
    
    def search_similar_documents(self, query, top_k=5):
        if self.sbert_embeddings is None:
            raise ValueError("Embeddings SBERT não disponíveis")
        
        query_vector = self.sbert_model.encode([query], normalize_embeddings=True)
        similarities = cosine_similarity(query_vector, self.sbert_embeddings)[0]
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [(int(idx), float(similarities[idx])) for idx in top_indices]
    
    def save_vectors(self, output_dir):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if self.bow_matrix is not None:
            bow_df = pd.DataFrame.sparse.from_spmatrix(self.bow_matrix, columns=self.bow_features)
            bow_df.to_csv(output_path / "bow_matrix.csv", index=False, sep=";")
        
        if self.tfidf_matrix is not None:
            tfidf_df = pd.DataFrame.sparse.from_spmatrix(self.tfidf_matrix, columns=self.tfidf_features)
            tfidf_df.to_csv(output_path / "tfidf_matrix.csv", index=False, sep=";")
        
        if self.sbert_embeddings is not None:
            np.save(output_path / "sbert_embeddings.npy", self.sbert_embeddings)
            sbert_df = pd.DataFrame(self.sbert_embeddings)
            sbert_df.to_csv(output_path / "sbert_embeddings.csv", index=False, sep=";")