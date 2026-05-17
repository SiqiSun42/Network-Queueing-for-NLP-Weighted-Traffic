import random

STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'are', 'was', 'were',
    'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
    'may', 'might', 'must', 'can', 'it', 'its', 'that', 'this', 'these', 'those', 'i', 'you', 'he', 'she',
    'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how'
}

IMPORTANT_KEYWORDS = {
    'algorithm', 'network', 'scheduling', 'optimization', 'performance', 'system',
    'communication', 'routing', 'packet', 'data', 'transmission', 'resource',
    'queue', 'traffic', 'latency', 'throughput', 'efficient', 'scalable',
    'secure', 'robust', 'intelligent', 'adaptive', 'machine', 'learning',
    'artificial', 'intelligence', 'model', 'analysis', 'framework', 'protocol'
}

def tokenize(text):
    text = text.lower()
    tokens = []
    current_token = ""
    for char in text:
        if char.isalnum():
            current_token += char
        else:
            if current_token:
                tokens.append(current_token)
            current_token = ""
    if current_token:
        tokens.append(current_token)
    return tokens

def calculate_token_weight(token):
    if token in STOPWORDS:
        return 0.1
    elif token in IMPORTANT_KEYWORDS:
        return 0.9
    elif len(token) > 6:
        return 0.7
    elif len(token) > 3:
        return 0.5
    else:
        return 0.3

def extract_text_segments(text, segment_size=3):
    tokens = tokenize(text)
    segments = []
    
    for i in range(0, len(tokens), segment_size):
        segment_tokens = tokens[i:i+segment_size]
        segment_text = ' '.join(segment_tokens)
        weights = [calculate_token_weight(t) for t in segment_tokens]
        segment_weight = sum(weights) / len(weights) if weights else 0.1
        
        segments.append({
            'text': segment_text,
            'weight': min(1.0, segment_weight),
            'token_count': len(segment_tokens)
        })
    
    return segments

def load_corpus(filename):
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        return [line.strip() for line in lines if line.strip()]
    except FileNotFoundError:
        return []
