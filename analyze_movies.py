import pandas as pd
#from src.text_preprocessor import TextPreprocessor
from src.vectorizer import Vectorizer
from src.recommendation_system import RecommendationSystem

def load_data():
    """Carrega dados dos filmes."""
    df = pd.read_csv("data/movies_info.csv", sep=";", encoding='utf-8')
    return df

def analyze_movies():
    """Pipeline completo de análise."""
    print("Analisando filmes...")
    
    # 1. Carregar dados
    df = load_data()
    print(f"Carregados {len(df)} filmes")
    
    # 2. Preprocessar textos
    #preprocessor = TextPreprocessor()
    processed_texts = []
    for text in df['synopsis_lemming'].fillna(""):
        #tokens = preprocessor.preprocess_text(text)
        processed_texts.append(text)
    
    # 3. Criar vetores
    vectorizer = Vectorizer()
    vectorizer.create_bow_vectors(processed_texts)
    vectorizer.create_tfidf_vectors(processed_texts)
    vectorizer.create_sbert_embeddings(df['synopsis_content'].fillna("").tolist())
    
    # 4. Sistema de recomendação
    recommender = RecommendationSystem(df, vectorizer)
    recommender.perform_clustering()
    recommender.create_pca_projection()
    
    # 5. Salvar resultados
    vectorizer.save_vectors("data/vectorized")
    recommender.save_results("data/vectorized")
    
    print("Análise concluída! Resultados salvos em data/vectorized/")
    
    return df, recommender

def recommend_movies(title, recommender, top_k=5):
    """Recomenda filmes similares."""
    try:
        recommendations = recommender.recommend_by_title(title, top_k=top_k)
        
        print(f"\n Filmes similares a '{title}':")
        print("=" * 50)
        
        for rec in recommendations:
            print(f"{rec['rank']}. {rec['title']} (similaridade: {rec['similarity']:.3f})")
            print(f"   Gêneros: {rec['genres']}\n")
            
    except ValueError as e:
        print(f"Erro: {e}")

def search_movies(query, recommender, top_k=5):
    """Busca filmes por query."""
    recommendations = recommender.recommend_by_query(query, top_k)
    
    print(f"\n Resultados para '{query}':")
    print("=" * 50)
    
    for rec in recommendations:
        print(f"{rec['rank']}. {rec['title']} (similaridade: {rec['similarity']:.3f})")
        print(f"   Sinopse: {rec['synopsis']}")
        print(f"   Gêneros: {rec['genres']}\n")

def main():
    """Função principal."""
    # Executar análise
    df, recommender = analyze_movies()
    
    # Exemplos de uso
    print("\n" + "="*60)
    print("EXEMPLOS DE USO")
    print("="*60)
    
    # Recomendação por títul o
    recommend_movies("Superman(2025)", recommender)
    
    # Busca por query
    search_movies("Heróis", recommender)

if __name__ == "__main__":
    main()