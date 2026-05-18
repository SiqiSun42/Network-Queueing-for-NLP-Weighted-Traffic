from run_experiment import run_comprehensive_experiment, save_results
from evaluate_rag import run_rag_evaluation


def run_complete_pipeline():
    
    print("\n" + "=" * 80)
    print(" " * 15 + "COMPLETE SEMANTIC COMMUNICATION SIMULATION PIPELINE")
    print("=" * 80)
    
    print("\n" + "█" * 80)
    print("PHASE 1 & 2: Network Scheduling with Weighted Traffic")
    print("█" * 80)
    run_comprehensive_experiment()
    
    print("\n\n" + "█" * 80)
    print("PHASE 3: End-to-end semantic TSR evaluation (delivered payloads vs corpus)")
    print("█" * 80)
    run_rag_evaluation()
    
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE - All phases executed successfully!")
    print("=" * 80)


if __name__ == '__main__':
    run_complete_pipeline()
