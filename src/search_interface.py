import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pandas as pd
import os
import webbrowser
import threading
from vectorizer import Vectorizer
from recommendation_system import RecommendationSystem
from knn import KNN
from dotenv import load_dotenv
import google.generativeai as genai


class MovieSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Busca de Filmes - PLN Movies com Gemini AI")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)

        self.df = None
        self.vectorizer = None
        self.recommender = None
        self.knn_classifier = None
        self.clusters = None
        self.search_results = []
        self.gemini_model = None
        self.gemini_enabled = False
        self.embeddings_loaded = False

        self.setup_styles()
        self.setup_gemini()
        self.create_widgets()
        self.load_data()

    def setup_gemini(self):
        """Configura a API do Gemini."""
        try:
            load_dotenv()
            api_key = os.getenv("GOOGLE_API_KEY")

            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash-lite")
                self.gemini_enabled = True
                print("Gemini API configurada com sucesso!")
            else:
                print("Aviso: GOOGLE_API_KEY não encontrada no arquivo .env")
                self.gemini_enabled = False
        except Exception as e:
            print(f"Aviso: Não foi possível configurar Gemini: {e}")
            self.gemini_enabled = False

    def setup_styles(self):
        """Configura estilos e cores da interface."""
        style = ttk.Style()
        style.theme_use("clam")

        bg_color = "#f0f0f0"
        fg_color = "#333333"

        self.bg_color = bg_color
        self.fg_color = fg_color

        self.root.configure(bg=bg_color)

    def create_widgets(self):
        """Cria todos os widgets da interface."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        title_label = ttk.Label(
            header_frame, text="Buscar Filmes", font=("Arial", 20, "bold")
        )
        title_label.pack(side=tk.LEFT)

        search_frame = ttk.LabelFrame(
            main_frame, text="Critérios de Busca", padding="10"
        )
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Tipo de Busca:", font=("Arial", 10)).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )

        self.search_type_var = tk.StringVar(value="Gênero")
        search_types = ["Gênero", "Título de Filme", "Sinopse"]

        self.search_type_combo = ttk.Combobox(
            search_frame,
            textvariable=self.search_type_var,
            values=search_types,
            state="readonly",
            width=25,
            font=("Arial", 10),
        )
        self.search_type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.search_type_combo.bind(
            "<<ComboboxSelected>>", lambda e: self.update_input_label()
        )
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Buscar por:", font=("Arial", 10)).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0)
        )

        self.input_label = ttk.Label(
            search_frame, text="Digite o gênero", font=("Arial", 9), foreground="gray"
        )
        self.input_label.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))

        input_frame = ttk.Frame(search_frame)
        input_frame.grid(
            row=2, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(5, 10)
        )
        input_frame.columnconfigure(0, weight=1)

        self.search_input = tk.Text(
            input_frame, height=3, width=80, font=("Arial", 10), wrap=tk.WORD
        )
        self.search_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            input_frame, orient=tk.VERTICAL, command=self.search_input.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.search_input.config(yscrollcommand=scrollbar.set)

        controls_frame = ttk.Frame(search_frame)
        controls_frame.grid(
            row=3, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(10, 0)
        )

        ttk.Label(controls_frame, text="Resultados:", font=("Arial", 9)).pack(
            side=tk.LEFT, padx=(0, 10)
        )

        self.results_count_var = tk.StringVar(value="5")
        spinbox = ttk.Spinbox(
            controls_frame,
            from_=1,
            to=20,
            textvariable=self.results_count_var,
            width=5,
            font=("Arial", 9),
        )
        spinbox.pack(side=tk.LEFT, padx=(0, 20))

        self.use_gemini_var = tk.BooleanVar(value=self.gemini_enabled)
        gemini_check = ttk.Checkbutton(
            controls_frame,
            text="Usar Gemini AI",
            variable=self.use_gemini_var,
            state=tk.NORMAL if self.gemini_enabled else tk.DISABLED,
        )
        gemini_check.pack(side=tk.LEFT, padx=(0, 20))
        
        self.use_knn_var = tk.BooleanVar(value=True)
        knn_check = ttk.Checkbutton(
            controls_frame,
            text="Usar Filtro KNN",
            variable=self.use_knn_var,
        )
        knn_check.pack(side=tk.LEFT, padx=(0, 20))

        self.search_button = ttk.Button(
            controls_frame, text="Buscar", command=self.perform_search
        )
        self.search_button.pack(side=tk.LEFT, padx=5)

        self.loading_label = ttk.Label(
            controls_frame, text="", font=("Arial", 9), foreground="blue"
        )
        self.loading_label.pack(side=tk.LEFT, padx=10)

        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        results_frame.grid(
            row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        canvas = tk.Canvas(results_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            results_frame, orient=tk.VERTICAL, command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.results_frame = scrollable_frame

        # self.no_results_label = ttk.Label(
        #     scrollable_frame,
        #     text="",
        #     font=("Arial", 11),
        #     foreground="gray",
        # )
        # self.no_results_label.pack(pady=20)

        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        self.info_label = ttk.Label(
            info_frame, text="", font=("Arial", 9), foreground="gray"
        )
        self.info_label.pack(side=tk.LEFT)

    def update_input_label(self):
        """Atualiza o rótulo do campo de entrada baseado no tipo de busca."""
        search_type = self.search_type_var.get()
        labels = {
            "Gênero": "Digite o gênero",
            "Título de Filme": "Digite o título do filme",
            "Sinopse": "Digite ou cole a sinopse",
        }
        self.input_label.config(text=labels.get(search_type, "Buscar por:"))

    def load_data(self):
        """Carrega dados dos filmes em background."""

        def load():
            try:
                self.loading_label.config(text="Carregando dados...")
                self.root.update()

                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                df_path = os.path.join(base_path, "data", "movies_info.csv")

                self.df = pd.read_csv(df_path, sep=";", encoding="utf-8")

                self.vectorizer = Vectorizer()

                # Criar textos enriquecidos com gêneros para melhor precisão
                enriched_texts = []
                for idx, row in self.df.iterrows():
                    synopsis = str(row.get("synopsis_content", "")).strip()
                    genres = str(row.get("genres", "")).strip()
                    enriched_text = f"{synopsis}. Gêneros: {genres}. {genres}."
                    enriched_texts.append(enriched_text)

                self.vectorizer.create_sbert_embeddings(enriched_texts)

                self.recommender = RecommendationSystem(self.df, self.vectorizer)

                self._load_knn_model()

                self.embeddings_loaded = True
                self.loading_label.config(text="Pronto!")
                self.root.after(2000, lambda: self.loading_label.config(text=""))

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")

        thread = threading.Thread(target=load, daemon=True)
        thread.start()

    def _load_knn_model(self):
        """Carrega o modelo KNN e os clusters."""
        try:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Carrega clusters
            cluster_path = os.path.join(base_path, "data", "vectorized", "cluster_labels.csv")
            cluster_df = pd.read_csv(cluster_path, sep=";")
            self.clusters = cluster_df["cluster"].values
            
            # Carrega modelo KNN
            self.knn_classifier = KNN(k_neighbors=5, metric="cosine")
            self.knn_classifier.load_and_train(base_path=base_path)
            
            print(f"KNN carregado com {len(set(self.clusters))} clusters")
        except Exception as e:
            print(f"Aviso: KNN não disponível: {e}")

    def search_with_knn_boost(self, query, top_k=5, use_cluster_filter=True):
        """
        Busca melhorada usando KNN para filtrar por cluster.
        
        Args:
            query: Texto da busca
            top_k: Número de resultados
            use_cluster_filter: Se True, filtra por cluster
        
        Returns:
            Lista de (idx, similarity) dos filmes mais relevantes
        """
        if self.knn_classifier is None or self.clusters is None:
            # Fallback: busca normal sem KNN
            return self.vectorizer.search_similar_documents(query, top_k)
        
        # 1. Determinar cluster da query
        query_embedding = self.vectorizer.sbert_model.encode([query], normalize_embeddings=True)
        query_cluster = self.knn_classifier.predict(query_embedding)[0]
        
        print(f"KNN: Query classificada no cluster {query_cluster}")
        
        if use_cluster_filter:
            # 2. Buscar mais candidatos para filtrar
            candidates = self.vectorizer.search_similar_documents(query, top_k * 10)
            
            # 3. Filtrar por cluster e pegar melhores
            same_cluster = []
            other_clusters = []
            
            for idx, sim in candidates:
                if self.clusters[idx] == query_cluster:
                    same_cluster.append((idx, sim))
                else:
                    other_clusters.append((idx, sim))
            
            # 4. Priorizar filmes do mesmo cluster, depois outros
            # 70% do mesmo cluster, 30% de outros clusters para diversidade
            n_same = int(top_k * 0.7)
            n_other = top_k - n_same
            
            results = same_cluster[:n_same] + other_clusters[:n_other]
            
            # Se não houver filmes suficientes do mesmo cluster
            if len(results) < top_k:
                results = (same_cluster + other_clusters)[:top_k]
            
            print(f"KNN: {len(same_cluster)} filmes no mesmo cluster, retornando {len(results)} resultados")
            return results[:top_k]
        else:
            # Re-ranking: aumentar score de filmes do mesmo cluster
            candidates = self.vectorizer.search_similar_documents(query, top_k * 3)
            
            reranked = []
            for idx, sim in candidates:
                # Boost de 10% para filmes do mesmo cluster
                boost = 1.1 if self.clusters[idx] == query_cluster else 1.0
                reranked.append((idx, sim * boost))
            
            # Reordenar por novo score
            reranked.sort(key=lambda x: x[1], reverse=True)
            return reranked[:top_k]
    
    def refine_query_with_gemini(self, search_text, search_type):
        """Refina a query usando Gemini AI."""
        if not self.gemini_enabled or not self.use_gemini_var.get():
            print(f"Gemini AI: DESATIVADO - Usando busca direta: '{search_text}'")
            return search_text

        try:
            print(f"Gemini AI: ATIVADO - Refinando query '{search_text}' para tipo '{search_type}'...")
            
            prompts = {
                "keyword": f"Você é um assistente especializado em recomendação de filmes. O usuário digitou: '{search_text}'. Refine este texto em uma busca otimizada para encontrar filmes similares. Responda apenas com a query refinada, sem explicações.",
                "genre": f"Você é um assistente especializado em recomendação de filmes. O usuário quer filmes do gênero: '{search_text}'. Refine esta busca para melhor capturar filmes deste gênero. Responda apenas com a query refinada.",
                "title": f"Você é um assistente especializado em recomendação de filmes. O usuário quer o filme com nome de '{search_text}'. Tente localizar o filme com esse nome. Responda apenas com a query refinada.",
                "synopsis": f"Você é um assistente especializado em recomendação de filmes. O usuário forneceu esta sinopse: '{search_text}'. Resuma os temas principais em palavras-chave para buscar filmes similares. Responda apenas com as palavras-chave refinadas.",
            }

            prompt = prompts.get(search_type, search_text)
            
            response = self.gemini_model.generate_content(prompt)
            refined_text = response.text.strip()
            print(f"\u2713 Query refinada por Gemini: '{refined_text}'")
            return refined_text

        except Exception as e:
            print(f"\u2717 Erro ao refinar com Gemini: {e}")
            return search_text

    def perform_search(self):
        """Executa a busca."""
        if self.df is None or not self.embeddings_loaded:
            messagebox.showwarning(
                "Aviso",
                "Dados ainda estão carregando. Tente novamente em alguns segundos.",
            )
            return

        search_text = self.search_input.get("1.0", tk.END).strip()
        if not search_text:
            messagebox.showwarning("Aviso", "Digite algo para buscar!")
            return

        try:
            top_k = int(self.results_count_var.get())
        except ValueError:
            top_k = 5

        search_type_display = self.search_type_var.get()

        # Mapear labels de exibição para tipos internos
        type_mapping = {
            "Gênero": "genre",
            "Título de Filme": "title",
            "Sinopse": "synopsis",
        }
        search_type = type_mapping.get(search_type_display, "genre")

        self.loading_label.config(text="Buscando...")
        self.root.update()

        def search():
            try:
                refined_search_text = self.refine_query_with_gemini(
                    search_text, search_type
                )

                # Usar busca com KNN se disponível e ativado
                if self.knn_classifier is not None and self.use_knn_var.get():
                    print("Usando busca com KNN para melhor precisão...")
                    self.search_results = self.search_with_knn_boost(
                        refined_search_text, top_k, use_cluster_filter=True
                    )
                else:
                    if self.knn_classifier is None:
                        print("KNN não disponível, usando busca padrão...")
                    else:
                        print("KNN desativado pelo usuário, usando busca padrão...")
                    
                    self.search_results = self.vectorizer.search_similar_documents(
                        refined_search_text, top_k
                    )

                self.root.after(0, self.display_results)

            except ValueError as e:
                error_msg = str(e)
                self.root.after(
                    0, lambda msg=error_msg: messagebox.showerror("Erro", msg)
                )
            except Exception as e:
                error_msg = f"Erro na busca: {e}"
                self.root.after(
                    0, lambda msg=error_msg: messagebox.showerror("Erro", msg)
                )
            finally:
                self.root.after(0, lambda: self.loading_label.config(text=""))

        thread = threading.Thread(target=search, daemon=True)
        thread.start()

    def display_results(self):
        """Exibe os resultados da busca."""
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not self.search_results:
            no_results = ttk.Label(
                self.results_frame,
                text="Nenhum resultado encontrado.",
                font=("Arial", 11),
                foreground="gray",
            )
            no_results.pack(pady=20)
            return

        for rank, (idx, similarity) in enumerate(self.search_results, 1):
            movie_data = self.df.iloc[idx]
            self.create_movie_card(rank, idx, movie_data, similarity)

        self.info_label.config(text=f"Encontrados {len(self.search_results)} filmes")

    def create_movie_card(self, rank, idx, movie_data, similarity):
        """Cria um card com informações do filme."""
        card_frame = ttk.Frame(self.results_frame, relief=tk.RIDGE, borderwidth=1)
        card_frame.pack(fill=tk.X, padx=5, pady=5)

        left_frame = ttk.Frame(card_frame)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        rank_label = ttk.Label(
            left_frame,
            text=f"#{rank}",
            font=("Arial", 14, "bold"),
            foreground="#2E86AB",
        )
        rank_label.pack()

        middle_frame = ttk.Frame(card_frame)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        title_text = str(movie_data.get("title", "N/A"))
        title_label = ttk.Label(
            middle_frame,
            text=title_text,
            font=("Arial", 12, "bold"),
            foreground="#333333",
        )
        title_label.pack(anchor=tk.W)

        info_text = f"Ano: {movie_data.get('year', 'N/A')} | Duração: {movie_data.get('movie_duration', 'N/A')} | Classificação: {movie_data.get('age_classification', 'N/A')}"
        info_label = ttk.Label(
            middle_frame, text=info_text, font=("Arial", 9), foreground="gray"
        )
        info_label.pack(anchor=tk.W, pady=(2, 5))

        genres_text = str(movie_data.get("genres", "N/A"))[:60]
        genres_label = ttk.Label(
            middle_frame,
            text=f"Gêneros: {genres_text}",
            font=("Arial", 9),
            foreground="#555555",
        )
        genres_label.pack(anchor=tk.W)

        streamings_text = str(movie_data.get("streamings", "N/A"))[:60]
        streaming_label = ttk.Label(
            middle_frame,
            text=f"Plataformas: {streamings_text}",
            font=("Arial", 9),
            foreground="#555555",
        )
        streaming_label.pack(anchor=tk.W, pady=(2, 5))

        synopsis_text = str(movie_data.get("synopsis_content", "N/A"))[:120] + "..."
        synopsis_label = ttk.Label(
            middle_frame,
            text=f"Sinopse: {synopsis_text}",
            font=("Arial", 8),
            foreground="#777777",
            wraplength=500,
            justify=tk.LEFT,
        )
        synopsis_label.pack(anchor=tk.W, pady=(5, 0))

        right_frame = ttk.Frame(card_frame)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        sim_label = ttk.Label(
            right_frame,
            text=f"Similaridade\n{similarity:.1%}",
            font=("Arial", 10, "bold"),
            foreground="#A23B72",
            justify=tk.CENTER,
        )
        sim_label.pack(pady=(0, 10))

        link = movie_data.get("link", None)
        if link:
            visit_button = tk.Button(
                right_frame,
                text="Visitar Site",
                font=("Arial", 10, "bold"),
                bg="#2E86AB",
                fg="white",
                padx=10,
                pady=5,
                cursor="hand2",
                command=lambda: webbrowser.open(link),
            )
            visit_button.pack()

        details_button = tk.Button(
            right_frame,
            text="Detalhes",
            font=("Arial", 10),
            bg="#F18F01",
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2",
            command=lambda: self.show_movie_details(idx, movie_data),
        )
        details_button.pack(pady=(5, 0))

    def show_movie_details(self, idx, movie_data):
        """Mostra uma janela com detalhes completos do filme."""
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Detalhes - {movie_data.get('title', 'Filme')}")
        details_window.geometry("600x600")

        main_frame = ttk.Frame(details_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(
            main_frame,
            text=movie_data.get("title", "N/A"),
            font=("Arial", 16, "bold"),
            foreground="#2E86AB",
        )
        title_label.pack(anchor=tk.W, pady=(0, 10))

        details_text = f"""
Ano: {movie_data.get('year', 'N/A')}
Duração: {movie_data.get('movie_duration', 'N/A')}
Classificação: {movie_data.get('age_classification', 'N/A')}

Gêneros:
{movie_data.get('genres', 'N/A')}

Plataformas de Streaming:
{movie_data.get('streamings', 'N/A')}

Avaliações:
  JustWatch: {movie_data.get('just_watch_rating', 'N/A')}
  Rotten Tomatoes: {movie_data.get('rotten_tomatoes_rating', 'N/A')}
  IMDb: {movie_data.get('imdb_ratings', 'N/A')}

Sinopse Completa:
"""

        details_label = ttk.Label(
            main_frame, text=details_text, font=("Arial", 10), justify=tk.LEFT
        )
        details_label.pack(anchor=tk.W, fill=tk.X, pady=(0, 10))

        synopsis_frame = ttk.Frame(main_frame)
        synopsis_frame.pack(fill=tk.BOTH, expand=True)

        synopsis_text = scrolledtext.ScrolledText(
            synopsis_frame,
            height=10,
            width=70,
            font=("Arial", 9),
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        synopsis_text.pack(fill=tk.BOTH, expand=True)

        synopsis_text.config(state=tk.NORMAL)
        synopsis_text.insert(tk.END, str(movie_data.get("synopsis_content", "N/A")))
        synopsis_text.config(state=tk.DISABLED)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        link = movie_data.get("link", None)
        if link:
            visit_button = tk.Button(
                button_frame,
                text="Visitar Site do Filme",
                font=("Arial", 11, "bold"),
                bg="#2E86AB",
                fg="white",
                padx=15,
                pady=8,
                cursor="hand2",
                command=lambda: webbrowser.open(link),
            )
            visit_button.pack(side=tk.LEFT, padx=5)

        close_button = tk.Button(
            button_frame,
            text="Fechar",
            font=("Arial", 11),
            bg="#666666",
            fg="white",
            padx=15,
            pady=8,
            cursor="hand2",
            command=details_window.destroy,
        )
        close_button.pack(side=tk.LEFT, padx=5)


def main():
    root = tk.Tk()
    app = MovieSearchGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
