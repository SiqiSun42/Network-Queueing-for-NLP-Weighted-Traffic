import random
from nlp_weight import tokenize, STOPWORDS, IMPORTANT_KEYWORDS


def get_token_weight(token: str) -> float:
    if token in STOPWORDS:
        return 0.1
    elif token in IMPORTANT_KEYWORDS:
        return 1.0
    elif len(token) > 6:
        return 0.6
    elif len(token) > 3:
        return 0.4
    else:
        return 0.2


def weighted_similarity(text1: str, text2: str) -> float:
    tokens1_list = tokenize(text1)
    tokens2_list = tokenize(text2)
    
    if not tokens1_list or not tokens2_list:
        return 0.0
    
    tokens1_set = set(tokens1_list)
    tokens2_set = set(tokens2_list)
    
    token_weights = {}
    for t in tokens1_set | tokens2_set:
        token_weights[t] = get_token_weight(t)
    
    intersection_tokens = tokens1_set & tokens2_set
    
    if not intersection_tokens:
        return 0.0
    
    intersection_weight = sum(token_weights.get(t, 0.1) for t in intersection_tokens)
    
    tokens1_weight = sum(token_weights.get(t, 0.1) for t in tokens1_set)
    tokens2_weight = sum(token_weights.get(t, 0.1) for t in tokens2_set)
    
    recall = intersection_weight / tokens1_weight if tokens1_weight > 0 else 0.0
    precision = intersection_weight / tokens2_weight if tokens2_weight > 0 else 0.0
    
    f_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return min(1.0, f_score * 1.5)


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
        sim = weighted_similarity(original, reconstructed)
        return sim
    
    @staticmethod
    def calculate_semantic_preservation(original_tokens: set, 
                                       reconstructed_tokens: set) -> float:
        if not original_tokens:
            return 0.0
        
        intersection = len(original_tokens & reconstructed_tokens)
        return intersection / len(original_tokens)
