"""Text comparison utilities for detecting slide changes"""

from typing import List, Set
import Levenshtein
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class TextComparator:
    """Compare text between frames to detect slide changes"""
    
    def __init__(self):
        """Initialize text comparator"""
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words=None,  # Keep all words for educational content
            max_features=1000
        )
    
    def calculate_similarity(self, text1: str, text2: str, method: str = "hybrid") -> float:
        """
        Calculate similarity between two text strings
        
        Args:
            text1: First text
            text2: Second text
            method: Comparison method ("levenshtein", "tfidf", "hybrid")
            
        Returns:
            Similarity score (0-1, where 1 is identical)
        """
        # Handle empty strings
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
        
        if method == "levenshtein":
            return self._levenshtein_similarity(text1, text2)
        elif method == "tfidf":
            return self._tfidf_similarity(text1, text2)
        elif method == "hybrid":
            # Use both methods and average
            lev_sim = self._levenshtein_similarity(text1, text2)
            tfidf_sim = self._tfidf_similarity(text1, text2)
            return (lev_sim + tfidf_sim) / 2
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _levenshtein_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity using Levenshtein distance
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        # Normalize texts
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        # Calculate Levenshtein distance
        distance = Levenshtein.distance(text1, text2)
        
        # Normalize by maximum possible distance
        max_len = max(len(text1), len(text2))
        if max_len == 0:
            return 1.0
        
        similarity = 1 - (distance / max_len)
        return max(0.0, min(1.0, similarity))
    
    def _tfidf_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity using TF-IDF and cosine similarity
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        try:
            # Create TF-IDF vectors
            vectors = self.vectorizer.fit_transform([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            
            return float(similarity)
        except Exception:
            # Fallback to simple word overlap if TF-IDF fails
            return self._word_overlap_similarity(text1, text2)
    
    def _word_overlap_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity based on word overlap (Jaccard similarity)
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        # Split into words and create sets
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def is_incremental_slide(
        self, 
        text1: str, 
        text2: str, 
        threshold: float = 0.7
    ) -> bool:
        """
        Detect if text2 is an incremental version of text1
        (e.g., bullet points appearing one by one)
        
        Args:
            text1: Earlier text
            text2: Later text
            threshold: Similarity threshold
            
        Returns:
            True if text2 appears to be incremental addition
        """
        # Check if text2 contains most of text1
        if text1 in text2:
            return True
        
        # Check word overlap
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1:
            return False
        
        # If most words from text1 appear in text2, it's likely incremental
        overlap = len(words1.intersection(words2)) / len(words1)
        
        return overlap >= threshold
    
    def extract_key_terms(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract key terms from text
        
        Args:
            text: Input text
            top_n: Number of top terms to extract
            
        Returns:
            List of key terms
        """
        try:
            # Fit vectorizer
            vectors = self.vectorizer.fit_transform([text])
            
            # Get feature names and scores
            feature_names = self.vectorizer.get_feature_names_out()
            scores = vectors.toarray()[0]
            
            # Get top terms
            top_indices = np.argsort(scores)[-top_n:][::-1]
            top_terms = [feature_names[i] for i in top_indices if scores[i] > 0]
            
            return top_terms
        except Exception:
            # Fallback: return most frequent words
            words = text.lower().split()
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_words[:top_n]]
