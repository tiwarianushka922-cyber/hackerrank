from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class TFIDFRetriever:
    def __init__(self):
        # We use a standard english stop words list
        self.vectorizer = TfidfVectorizer(stop_words='english', max_df=0.85)
        self.tfidf_matrix = None
        self.documents = []
        
    def fit(self, documents):
        """
        Fit the vectorizer on the corpus documents.
        documents: list of dicts [{'doc_id', 'text', 'source'}]
        """
        self.documents = documents
        if not self.documents:
            print("Warning: No documents provided to fit the retriever.")
            return
            
        corpus_texts = [doc['text'] for doc in self.documents]
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus_texts)
        
    def search(self, query, top_k=3):
        """
        Search for the most relevant documents given a query.
        Returns a list of dicts with the document and its confidence score.
        """
        if self.tfidf_matrix is None or not self.documents:
            return []
            
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarity between the query and all documents
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get the indices of the top_k most similar documents
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score > 0.0:  # Only return documents that have some overlap
                results.append({
                    'document': self.documents[idx],
                    'score': score
                })
                
        return results
