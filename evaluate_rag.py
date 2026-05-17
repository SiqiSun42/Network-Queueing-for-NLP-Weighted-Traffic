from semantic_simulator import SemanticCommunicationSimulator


def run_rag_evaluation():
    
    print("\n" + "=" * 70)
    print("Phase 3: RAG-based Semantic Reconstruction Evaluation")
    print("=" * 70)
    
    scenarios = [
        {
            "name": "Semantic weights with RAG (light congestion)",
            "link_capacity": 50,
            "arrival_rate": 60,
            "weight_dist": "semantic",
            "corpus_file": "corpus.txt"
        },
        {
            "name": "Bimodal weights with RAG (light congestion)",
            "link_capacity": 50,
            "arrival_rate": 60,
            "weight_dist": "bimodal"
        },
        {
            "name": "Semantic weights with RAG (heavy congestion)",
            "link_capacity": 50,
            "arrival_rate": 100,
            "weight_dist": "semantic",
            "corpus_file": "corpus.txt"
        }
    ]
    
    for scenario in scenarios:
        print("\n" + "=" * 70)
        print(f"Scenario: {scenario['name']}")
        print("=" * 70)
        
        simulator = SemanticCommunicationSimulator(
            link_capacity=scenario['link_capacity'],
            arrival_rate=scenario['arrival_rate'],
            weight_dist=scenario['weight_dist'],
            sim_time=500,
            corpus_file=scenario.get('corpus_file')
        )
        
        simulator.run_with_evaluation()


if __name__ == '__main__':
    run_rag_evaluation()
