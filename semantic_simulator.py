import copy

from traffic import PoissonTrafficGenerator
from maxweight_scheduler import MaxWeightScheduler
from num_scheduler import NUMScheduler
from receiver import Receiver
from rag import TaskSuccessRateCalculator
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
        print("Semantic Communication Simulation — TSR on delivered aggregate text")
        print("=" * 70)
        
        arrivals_trace = self._build_arrivals_trace()
        self._run_maxweight_with_rag(arrivals_trace)
        print()
        self._run_num_with_rag(arrivals_trace)
        
        self._print_evaluation_summary()
    
    def _build_arrivals_trace(self):
        gen = PoissonTrafficGenerator(
            self.arrival_rate,
            self.traffic_gen.weight_dist,
            self.corpus_file,
        )
        return [gen.generate_arrivals(t) for t in range(self.sim_time)]
    
    def _run_maxweight_with_rag(self, arrivals_trace):
        print("Max-Weight scheduler — Phase 3 TSR path...")
        self.metrics["maxweight"]["tsr_scores"] = []
        self.metrics["maxweight"]["semantic_preservation"] = []
        self.maxweight_scheduler = MaxWeightScheduler(self.link_capacity)
        receiver = Receiver(self.corpus)
        
        transmitted_ids = set()
        
        for t in range(self.sim_time):
            arrivals = copy.deepcopy(arrivals_trace[t])
            self.maxweight_scheduler.enqueue(arrivals)
            transmitted = self.maxweight_scheduler.schedule(t)
            
            for pkt in transmitted:
                receiver.receive([pkt])
                transmitted_ids.add(pkt.packet_id)
            
            if (t + 1) % 100 == 0:
                print(f"  Time {t+1}/{self.sim_time} - "
                      f"Transmitted: {len(transmitted_ids)} - "
                      f"Dropped: {self.maxweight_scheduler.total_dropped}")
        
        self._evaluate_reconstruction('maxweight', receiver, self.maxweight_scheduler.total_dropped)
    
    def _run_num_with_rag(self, arrivals_trace):
        print("NUM scheduler — Phase 3 TSR path...")
        self.metrics["num"]["tsr_scores"] = []
        self.metrics["num"]["semantic_preservation"] = []
        self.num_scheduler = NUMScheduler(self.link_capacity)
        receiver = Receiver(self.corpus)
        
        transmitted_ids = set()
        
        for t in range(self.sim_time):
            arrivals = copy.deepcopy(arrivals_trace[t])
            self.num_scheduler.enqueue(arrivals)
            transmitted = self.num_scheduler.schedule(t)
            
            for pkt in transmitted:
                receiver.receive([pkt])
                transmitted_ids.add(pkt.packet_id)
            
            if (t + 1) % 100 == 0:
                print(f"  Time {t+1}/{self.sim_time} - "
                      f"Transmitted: {len(transmitted_ids)} - "
                      f"Dropped: {self.num_scheduler.total_dropped}")
        
        self._evaluate_reconstruction('num', receiver, self.num_scheduler.total_dropped)
    
    def _evaluate_reconstruction(self, scheduler_name: str, receiver: Receiver, total_dropped: int):
        self.metrics[scheduler_name]["packets_dropped"] = total_dropped
        if not self.corpus:
            self.metrics[scheduler_name]["tsr_scores"] = []
            self.metrics[scheduler_name]["semantic_preservation"] = []
            return
        
        received_content = receiver.get_received_content()
        tsr_scores = []
        semantic_preservation = []
        
        for original_text in self.corpus[:3]:
            tsr = TaskSuccessRateCalculator.calculate_tsr(original_text, received_content)
            
            original_tokens = set(tokenize(original_text))
            received_tokens = set(tokenize(received_content))
            preservation = TaskSuccessRateCalculator.calculate_semantic_preservation(
                original_tokens, received_tokens
            )
            
            tsr_scores.append(tsr)
            semantic_preservation.append(preservation)
        
        self.metrics[scheduler_name]["tsr_scores"] = tsr_scores
        self.metrics[scheduler_name]["semantic_preservation"] = semantic_preservation
    
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
    
    def export_metrics_snapshot(self, scenario_name: str | None = None) -> dict:
        snap = {
            "scenario_name": scenario_name,
            "sim_time": self.sim_time,
            "link_capacity": self.link_capacity,
            "arrival_rate": self.arrival_rate,
            "lambda_over_c": self.arrival_rate / self.link_capacity,
            "weight_dist": self.traffic_gen.weight_dist,
            "corpus_file": self.corpus_file,
            "corpus_samples_used_for_tsr": min(3, len(self.corpus)),
            "same_arrival_trace_for_both_schedulers": True,
            "tsr_definition_ref": "rag.py weighted_similarity(original_corpus_line, received_aggregate_text); received text joins delivered packet payloads (semantic segments when weight_dist is semantic)",
            "schedulers": {},
        }
        for scheduler_name in ["maxweight", "num"]:
            m = self.metrics[scheduler_name]
            tsr_scores = list(m["tsr_scores"])
            sem_p = list(m["semantic_preservation"])
            row = {
                "packets_dropped": m["packets_dropped"],
                "tsr_per_corpus_sample": tsr_scores,
                "semantic_preservation_per_corpus_sample": sem_p,
            }
            if tsr_scores:
                row["average_tsr"] = sum(tsr_scores) / len(tsr_scores)
                row["average_semantic_preservation"] = sum(sem_p) / len(sem_p)
            else:
                row["average_tsr"] = None
                row["average_semantic_preservation"] = None
            snap["schedulers"][scheduler_name] = row
        return snap
