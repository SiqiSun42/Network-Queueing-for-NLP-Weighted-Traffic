from traffic import PoissonTrafficGenerator
from maxweight_scheduler import MaxWeightScheduler
from num_scheduler import NUMScheduler
from receiver import Receiver
from rag import RAGReconstructor, TaskSuccessRateCalculator
from nlp_weight import load_corpus, tokenize


class SemanticCommunicationSimulator:
    
    def __init__(self, 
                 link_capacity: int,
                 arrival_rate: float,
                 weight_dist: str = "uniform",
                 sim_time: int = 1000,
                 corpus_file: str = None):
        self.link_capacity = link_capacity
        self.arrival_rate = arrival_rate
        self.sim_time = sim_time
        self.corpus_file = corpus_file
        
        self.traffic_gen = PoissonTrafficGenerator(arrival_rate, weight_dist, corpus_file)
        self.maxweight_scheduler = MaxWeightScheduler(link_capacity)
        self.num_scheduler = NUMScheduler(link_capacity)
        
        self.corpus = load_corpus(corpus_file) if corpus_file else []
        self.rag_reconstructor = RAGReconstructor(self.corpus)
        
        self.metrics = {
            'maxweight': {
                'packets_transmitted': 0,
                'packets_dropped': 0,
                'tsr_scores': [],
                'semantic_preservation': []
            },
            'num': {
                'packets_transmitted': 0,
                'packets_dropped': 0,
                'tsr_scores': [],
                'semantic_preservation': []
            }
        }
    
    def run_with_evaluation(self):
        print("=" * 70)
        print("Semantic Communication Simulation with RAG Evaluation")
        print("=" * 70)
        
        self._run_maxweight_with_rag()
        print()
        self._run_num_with_rag()
        
        self._print_evaluation_summary()
    
    def _run_maxweight_with_rag(self):
        print("Max-Weight Scheduler with RAG Evaluation...")
        self.maxweight_scheduler = MaxWeightScheduler(self.link_capacity)
        self.traffic_gen = PoissonTrafficGenerator(self.arrival_rate, self.traffic_gen.weight_dist, self.corpus_file)
        receiver = Receiver(self.corpus)
        
        transmitted_ids = set()
        
        for t in range(self.sim_time):
            arrivals = self.traffic_gen.generate_arrivals(t)
            self.maxweight_scheduler.enqueue(arrivals)
            transmitted = self.maxweight_scheduler.schedule()
            
            for pkt in transmitted:
                receiver.receive([pkt])
                transmitted_ids.add(pkt.packet_id)
            
            if (t + 1) % 100 == 0:
                print(f"  Time {t+1}/{self.sim_time} - "
                      f"Transmitted: {len(transmitted_ids)} - "
                      f"Dropped: {self.maxweight_scheduler.total_dropped}")
        
        self._evaluate_reconstruction('maxweight', receiver, self.maxweight_scheduler.total_dropped)
    
    def _run_num_with_rag(self):
        print("NUM Scheduler with RAG Evaluation...")
        self.num_scheduler = NUMScheduler(self.link_capacity)
        self.traffic_gen = PoissonTrafficGenerator(self.arrival_rate, self.traffic_gen.weight_dist, self.corpus_file)
        receiver = Receiver(self.corpus)
        
        transmitted_ids = set()
        
        for t in range(self.sim_time):
            arrivals = self.traffic_gen.generate_arrivals(t)
            self.num_scheduler.enqueue(arrivals)
            transmitted = self.num_scheduler.schedule()
            
            for pkt in transmitted:
                receiver.receive([pkt])
                transmitted_ids.add(pkt.packet_id)
            
            if (t + 1) % 100 == 0:
                print(f"  Time {t+1}/{self.sim_time} - "
                      f"Transmitted: {len(transmitted_ids)} - "
                      f"Dropped: {self.num_scheduler.total_dropped}")
        
        self._evaluate_reconstruction('num', receiver, self.num_scheduler.total_dropped)
    
    def _evaluate_reconstruction(self, scheduler_name: str, receiver: Receiver, total_dropped: int):
        if not self.corpus:
            return
        
        received_content = receiver.get_received_content()
        
        for original_text in self.corpus[:3]:
            reconstructed = self.rag_reconstructor.reconstruct(received_content)
            tsr = TaskSuccessRateCalculator.calculate_tsr(original_text, reconstructed)
            
            original_tokens = set(tokenize(original_text))
            reconstructed_tokens = set(tokenize(reconstructed))
            preservation = TaskSuccessRateCalculator.calculate_semantic_preservation(
                original_tokens, reconstructed_tokens
            )
            
            self.metrics[scheduler_name]['tsr_scores'].append(tsr)
            self.metrics[scheduler_name]['semantic_preservation'].append(preservation)
        
        self.metrics[scheduler_name]['packets_dropped'] = total_dropped
    
    def _print_evaluation_summary(self):
        print("\n" + "=" * 70)
        print("Task Success Rate (TSR) Evaluation Summary")
        print("=" * 70)
        
        for scheduler_name in ['maxweight', 'num']:
            metrics = self.metrics[scheduler_name]
            
            if metrics['tsr_scores']:
                avg_tsr = sum(metrics['tsr_scores']) / len(metrics['tsr_scores'])
                avg_preservation = sum(metrics['semantic_preservation']) / len(metrics['semantic_preservation'])
                
                print(f"\n{scheduler_name.upper()} Scheduler:")
                print(f"  Average TSR: {avg_tsr:.4f}")
                print(f"  Semantic Preservation: {avg_preservation:.4f}")
                print(f"  Total Dropped Packets: {metrics['packets_dropped']}")
