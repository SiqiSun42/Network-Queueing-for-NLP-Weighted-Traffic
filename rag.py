import random
from nlp_weight import tokenize


def simple_similarity(text1: str, text2: str) -> float:
    tokens1 = set(tokenize(text1))
    tokens2 = set(tokenize(text2))
    
    if not tokens1 or not tokens2:
        return 0.0
    
    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)
    
    return intersection / union if union > 0 else 0.0


class RAGReconstructor:
    
    def __init__(self, corpus_texts: list[str]):
        self.corpus = corpus_texts
        self.corpus_tokens = [set(tokenize(text)) for text in corpus_texts]
    
    def reconstruct(self, received_fragment: str) -> str:
        if not received_fragment.strip():
            return self._sample_corpus()
        
        received_tokens = set(tokenize(received_fragment))
        
        if not received_tokens:
            return self._sample_corpus()
        
        best_match_idx = 0
        best_score = 0
        
        for idx, corpus_token_set in enumerate(self.corpus_tokens):
            intersection = len(received_tokens & corpus_token_set)
            similarity = intersection / len(corpus_token_set) if corpus_token_set else 0
            
            if similarity > best_score:
                best_score = similarity
                best_match_idx = idx
        
        return self.corpus[best_match_idx]
    
    def _sample_corpus(self) -> str:
        return random.choice(self.corpus) if self.corpus else "reconstruction failed"


class TaskSuccessRateCalculator:
    
    @staticmethod
    def calculate_tsr(original: str, reconstructed: str) -> float:
        sim = simple_similarity(original, reconstructed)
        return min(1.0, sim * 1.5)
    
    @staticmethod
    def calculate_semantic_preservation(original_tokens: set, 
                                       reconstructed_tokens: set) -> float:
        if not original_tokens:
            return 0.0
        
        intersection = len(original_tokens & reconstructed_tokens)
        return intersection / len(original_tokens)
